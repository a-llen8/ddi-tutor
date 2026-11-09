import argparse

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, roc_auc_score
from xgboost import XGBClassifier

from ml.calibrate import bins_table, ece, knn_score
from ml.evaluate import pair_features, tanimoto
from ml.interact import make_negatives
from ml.splits import NPZ, PAIRS, load_graded_pairs, random_split

SEED = 42
OUT = "data/processed/results_calibration_known.csv"
OUT_BINS = "data/processed/results_calibration_known_bins.csv"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="50 trees, 2000 pairs per set")
    args = ap.parse_args()

    allp = pd.read_csv(PAIRS)
    documented = {frozenset((a, b)) for a, b in zip(allp["drug_a_id"], allp["drug_b_id"])}
    pos = load_graded_pairs()
    neg = make_negatives(pos, documented, SEED)
    pairs = pd.concat([pos[["drug_a_id", "drug_b_id"]].assign(label=1),
                       neg.assign(label=0)], ignore_index=True)

    d = np.load(NPZ)
    fps, ids = d["fps"], d["drug_ids"]
    row_of = {str(i): r for r, i in enumerate(ids)}
    ia = pairs["drug_a_id"].map(row_of).to_numpy()
    ib = pairs["drug_b_id"].map(row_of).to_numpy()
    y = pairs["label"].to_numpy()
    X = pair_features(fps, ia, ib)
    S = tanimoto(fps)

    tr, te = random_split(pairs, seed=SEED)
    rng = np.random.default_rng(0)
    perm = rng.permutation(tr)
    n_cal = int(0.2 * len(tr))
    cal_full, fit_idx = perm[:n_cal], perm[n_cal:]
    cap_cal, cap_test = (2000, 2000) if args.quick else (30000, 20000)

    def cap(idx, n):
        return rng.permutation(idx)[:n] if len(idx) > n else idx

    cal_idx = cap(cal_full, cap_cal)
    test = cap(te, cap_test)

    assert not (set(fit_idx) & set(cal_idx))
    assert not (set(test) & set(fit_idx)) and not (set(test) & set(cal_idx))
    print("fit:", len(fit_idx), " calibration:", len(cal_idx),
          " calibration positives:", int(y[cal_idx].sum()))
    print("test:", len(test), " positives:", int(y[test].sum()))

    xgb = XGBClassifier(n_estimators=50 if args.quick else 300, max_depth=6,
                        learning_rate=0.1, subsample=0.8, colsample_bytree=0.5,
                        tree_method="hist", n_jobs=-1, random_state=SEED)
    xgb.fit(X[fit_idx], y[fit_idx])

    scorers = {"xgboost": lambda idx: xgb.predict_proba(X[idx])[:, 1],
               "nearest neighbour": lambda idx: knn_score(S, ia, ib, y, fit_idx, idx)}

    rows, bin_rows = [], []
    for model, fn in scorers.items():
        iso = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1)
        iso.fit(fn(cal_idx), y[cal_idx])
        raw = fn(test)
        for version, p in [("raw", np.clip(raw, 0, 1)),
                           ("calibrated", np.clip(iso.predict(raw), 0, 1))]:
            rows.append({"model": model, "split": "both drugs known", "version": version,
                         "n_test": len(test),
                         "ece": round(ece(y[test], p), 3),
                         "brier": round(brier_score_loss(y[test], p), 3),
                         "balanced_acc": round(balanced_accuracy_score(y[test], p >= 0.5), 3)})
            for b, n, c, f in bins_table(y[test], p):
                bin_rows.append({"model": model, "split": "both drugs known", "version": version,
                                 "bin": b, "n": n, "mean_confidence": round(c, 3),
                                 "actual_positive_rate": round(f, 3)})
        print("done:", model)

    t = pairs.iloc[fit_idx]
    t = t[t["label"] == 1]
    counts = pd.concat([t["drug_a_id"], t["drug_b_id"]]).value_counts()
    da = pairs["drug_a_id"].map(counts).fillna(0).to_numpy()
    db = pairs["drug_b_id"].map(counts).fillna(0).to_numpy()
    D = np.log1p(np.stack([np.minimum(da, db), np.maximum(da, db)], axis=1))
    pop = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1,
                        tree_method="hist", n_jobs=-1, random_state=SEED)
    pop.fit(D[fit_idx], y[fit_idx])
    pp = pop.predict_proba(D[test])[:, 1]

    res = pd.DataFrame(rows)
    res.to_csv(OUT, index=False)
    pd.DataFrame(bin_rows).to_csv(OUT_BINS, index=False)
    print()
    print(res.to_string(index=False))
    print()
    print(f"popularity only: balanced_acc {balanced_accuracy_score(y[test], pp >= 0.5):.3f}"
          f"  roc_auc {roc_auc_score(y[test], pp):.3f}")