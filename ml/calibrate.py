import argparse

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss
from xgboost import XGBClassifier

from ml.evaluate import pair_features, tanimoto
from ml.interact import make_negatives
from ml.splits import NPZ, PAIRS, cold_start_splits, load_graded_pairs

SEED = 42
OUT = "data/processed/results_calibration.csv"
OUT_BINS = "data/processed/results_calibration_bins.csv"


def knn_score(S, ia, ib, y, train, test, k=5, chunk=100):
    """Similarity-weighted share of positive neighbours among the k nearest training pairs."""
    ta, tb, ty = ia[train][None, :], ib[train][None, :], y[train]
    out = []
    for s in range(0, len(test), chunk):
        t = test[s:s + chunk]
        a, b = ia[t][:, None], ib[t][:, None]
        sc = np.maximum(S[a, ta] * S[b, tb], S[a, tb] * S[b, ta])
        nn = np.argpartition(-sc, k, axis=1)[:, :k]
        w = np.take_along_axis(sc, nn, 1)
        lab = ty[nn]
        tot = w.sum(axis=1)
        share = (w * lab).sum(axis=1) / np.where(tot > 0, tot, 1)
        out.append(np.where(tot > 0, share, 0.5))
    return np.concatenate(out)


def bins_table(y, p, n_bins=10):
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, n_bins - 1)
    rows = []
    for b in range(n_bins):
        m = idx == b
        if m.sum() > 0:
            rows.append((b, int(m.sum()), float(p[m].mean()), float(y[m].mean())))
    return rows


def ece(y, p):
    return sum(n * abs(c - f) for _, n, c, f in bins_table(y, p)) / len(y)


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

    ctr, one, both, held = cold_start_splits(pairs, seed=SEED)
    sub = pairs.iloc[ctr].reset_index(drop=True)
    s_tr, s_one, s_both, _ = cold_start_splits(sub, seed=SEED + 1)
    fit_idx = ctr[s_tr]
    cal_idx = ctr[np.concatenate([s_one, s_both])]

    rng = np.random.default_rng(0)
    cap_cal, cap_test = (2000, 2000) if args.quick else (30000, 20000)

    def cap(idx, n):
        return rng.permutation(idx)[:n] if len(idx) > n else idx

    cal_idx = cap(cal_idx, cap_cal)
    tests = {"one drug unseen": cap(one, cap_test), "both drugs unseen": cap(both, cap_test)}

    assert not (set(fit_idx) & set(cal_idx))
    for t in tests.values():
        assert not (set(t) & set(fit_idx)) and not (set(t) & set(cal_idx))
    print("fit:", len(fit_idx), " calibration:", len(cal_idx),
          " calibration positives:", int(y[cal_idx].sum()))
    for name, t in tests.items():
        print(name, "test:", len(t), " positives:", int(y[t].sum()))

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
        for split, t in tests.items():
            raw = fn(t)
            for version, p in [("raw", np.clip(raw, 0, 1)), ("calibrated", np.clip(iso.predict(raw), 0, 1))]:
                rows.append({"model": model, "split": split, "version": version,
                             "n_test": len(t),
                             "ece": round(ece(y[t], p), 3),
                             "brier": round(brier_score_loss(y[t], p), 3),
                             "balanced_acc": round(balanced_accuracy_score(y[t], p >= 0.5), 3)})
                for b, n, c, f in bins_table(y[t], p):
                    bin_rows.append({"model": model, "split": split, "version": version,
                                     "bin": b, "n": n, "mean_confidence": round(c, 3),
                                     "actual_positive_rate": round(f, 3)})
        print("done:", model)

    res = pd.DataFrame(rows)
    res.to_csv(OUT, index=False)
    pd.DataFrame(bin_rows).to_csv(OUT_BINS, index=False)
    print()
    print(res.to_string(index=False))