import argparse

import numpy as np
import pandas as pd
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

from ml.evaluate import NPZ, LABEL, pair_features, tanimoto, knn_predict, score
from ml.splits import load_graded_pairs, random_split, cold_start_splits, fingerprint_groups

OUT = "results/results_severity_seeds.csv"

def fit_xgb(X, y, train):
    m = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.1, subsample=0.8,
                      colsample_bytree=0.5, tree_method="hist", n_jobs=-1, random_state=42)
    m.fit(X[train], y[train], sample_weight=compute_sample_weight("balanced", y[train]))
    return m

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--sample", type=int, default=5000, help="max test pairs scored per split")
    args = ap.parse_args()

    pairs = load_graded_pairs()
    d = np.load(NPZ)
    fps, ids = d["fps"], d["drug_ids"]
    row_of = {str(i): r for r, i in enumerate(ids)}
    ia = pairs["drug_a_id"].map(row_of).to_numpy()
    ib = pairs["drug_b_id"].map(row_of).to_numpy()
    y = pairs["severity"].map(LABEL).to_numpy()
    X = pair_features(fps, ia, ib)
    S = tanimoto(fps)
    group_of = fingerprint_groups()

    rows = []
    for seed in range(42, 42 + args.seeds):
        tr, te = random_split(pairs, seed=seed)
        ctr, one, both, _ = cold_start_splits(pairs, seed=seed, group_of=group_of)
        xgb_random = fit_xgb(X, y, tr)
        xgb_cold = fit_xgb(X, y, ctr)
        rng = np.random.default_rng(seed)
        settings = [("random", tr, te, xgb_random),
                    ("one drug unseen", ctr, one, xgb_cold),
                    ("both drugs unseen", ctr, both, xgb_cold)]
        for name, train, test, xgb in settings:
            if len(test) > args.sample:
                test = rng.choice(test, size=args.sample, replace=False)
            yt = y[test]
            preds = {
                "majority": np.full(len(test), np.bincount(y[train]).argmax()),
                "nearest neighbour": knn_predict(S, ia, ib, y, train, test),
                "xgboost": xgb.predict(X[test]),
            }
            for model_name, p in preds.items():
                rows.append({"seed": seed, "split": name, "model": model_name,
                             "n_test": len(test), **score(yt, p)})
            print("done: seed", seed, name, flush=True)

    res = pd.DataFrame(rows)
    res.to_csv(OUT, index=False)
    summary = (res.groupby(["split", "model"])[["macro_f1", "balanced_acc"]]
               .agg(["mean", "std"]).round(3))
    print()
    print(summary.to_string())
