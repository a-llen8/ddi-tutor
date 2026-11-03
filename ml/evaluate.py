import argparse

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

from ml.splits import cold_start_splits, load_graded_pairs, random_split

NPZ = "data/processed/fingerprints.npz"
OUT = "data/processed/results_severity.csv"
LABEL = {"Minor": 0, "Moderate": 1, "Major": 2}


def pair_features(fps, ia, ib):
    """Order-free pair features: 0 = neither drug has the bit, 1 = one, 2 = both."""
    return fps[ia] + fps[ib]


def tanimoto(F):
    F = F.astype(np.float32)
    inter = F @ F.T
    n = F.sum(axis=1)
    union = n[:, None] + n[None, :] - inter
    return np.where(union > 0, inter / union, 0).astype(np.float32)


def knn_predict(S, ia, ib, y, train, test, k=5, chunk=100):
    ta, tb, ty = ia[train][None, :], ib[train][None, :], y[train]
    preds = []
    for s in range(0, len(test), chunk):
        t = test[s:s + chunk]
        a, b = ia[t][:, None], ib[t][:, None]
        sc = np.maximum(S[a, ta] * S[b, tb], S[a, tb] * S[b, ta])
        nn = np.argpartition(-sc, k, axis=1)[:, :k]
        w = np.take_along_axis(sc, nn, 1)
        lab = ty[nn]
        votes = np.stack([(w * (lab == c)).sum(axis=1) for c in range(3)], axis=1)
        preds.append(votes.argmax(axis=1))
    return np.concatenate(preds)


def score(y_true, y_pred):
    return {"accuracy": accuracy_score(y_true, y_pred),
            "balanced_acc": balanced_accuracy_score(y_true, y_pred),
            "macro_f1": f1_score(y_true, y_pred, average="macro")}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="50 trees, first 2000 test pairs")
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

    tr, te = random_split(pairs)
    ctr, one, both, held = cold_start_splits(pairs)
    settings = [("random", "random", tr, te),
                ("one drug unseen", "cold", ctr, one),
                ("both drugs unseen", "cold", ctr, both)]

    models = {}
    rows = []
    for name, key, train, test in settings:
        if args.quick:
            test = test[:2000]
        yt = y[test]
        majority = np.full(len(test), np.bincount(y[train]).argmax())
        knn = knn_predict(S, ia, ib, y, train, test)
        if key not in models:
            m = XGBClassifier(n_estimators=50 if args.quick else 300, max_depth=6,
                              learning_rate=0.1, subsample=0.8, colsample_bytree=0.5,
                              tree_method="hist", n_jobs=-1, random_state=42)
            m.fit(X[train], y[train], sample_weight=compute_sample_weight("balanced", y[train]))
            models[key] = m
        xgb = models[key].predict(X[test])
        for model_name, pred in [("majority", majority), ("nearest neighbour", knn), ("xgboost", xgb)]:
            rows.append({"split": name, "model": model_name, "n_test": len(test),
                         **{k: round(v, 3) for k, v in score(yt, pred).items()}})
        print("done:", name)

    res = pd.DataFrame(rows)
    res.to_csv(OUT, index=False)
    print()
    print(res.to_string(index=False))