import argparse

import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, balanced_accuracy_score,
                             f1_score, roc_auc_score)
from xgboost import XGBClassifier

from ml.evaluate import knn_predict, pair_features, tanimoto
from ml.splits import NPZ, PAIRS, cold_start_splits, load_graded_pairs, random_split

OUT = "data/processed/results_interact.csv"


def make_negatives(pos, documented, seed):
    """One negative per positive. Keeps one drug, draws the other by how often drugs appear."""
    rng = np.random.default_rng(seed)
    endpoints = np.concatenate([pos["drug_a_id"].to_numpy(), pos["drug_b_id"].to_numpy()])
    seen = set()
    rows = []
    for a, b in zip(pos["drug_a_id"], pos["drug_b_id"]):
        if rng.random() < 0.5:
            a = b
        while True:
            c = endpoints[rng.integers(len(endpoints))]
            key = frozenset((a, c))
            if c != a and key not in documented and key not in seen:
                break
        seen.add(key)
        rows.append((a, c))
    return pd.DataFrame(rows, columns=["drug_a_id", "drug_b_id"])


def scores(y_true, pred, prob=None):
    out = {"balanced_acc": balanced_accuracy_score(y_true, pred),
           "macro_f1": f1_score(y_true, pred, average="macro")}
    if prob is not None:
        out["roc_auc"] = roc_auc_score(y_true, prob)
        out["pr_auc"] = average_precision_score(y_true, prob)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="50 trees, first 2000 test pairs")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    allp = pd.read_csv(PAIRS)
    documented = {frozenset((a, b)) for a, b in zip(allp["drug_a_id"], allp["drug_b_id"])}
    pos = load_graded_pairs()
    neg = make_negatives(pos, documented, args.seed)
    assert not any(frozenset((a, b)) in documented
                   for a, b in zip(neg["drug_a_id"], neg["drug_b_id"]))

    pairs = pd.concat([pos[["drug_a_id", "drug_b_id"]].assign(label=1),
                       neg.assign(label=0)], ignore_index=True)
    print("positives:", len(pos), " negatives:", len(neg))

    d = np.load(NPZ)
    fps, ids = d["fps"], d["drug_ids"]
    row_of = {str(i): r for r, i in enumerate(ids)}
    ia = pairs["drug_a_id"].map(row_of).to_numpy()
    ib = pairs["drug_b_id"].map(row_of).to_numpy()
    y = pairs["label"].to_numpy()
    X = pair_features(fps, ia, ib)
    S = tanimoto(fps)

    tr, te = random_split(pairs, seed=args.seed)
    ctr, one, both, held = cold_start_splits(pairs, seed=args.seed)
    settings = [("random", "random", tr, te),
                ("one drug unseen", "cold", ctr, one),
                ("both drugs unseen", "cold", ctr, both)]

    models = {}
    rows = []
    for name, key, train, test in settings:
        print(name, "train:", len(train), "test:", len(test),
              "test positives:", int(y[test].sum()))
        if args.quick:
            test = np.random.default_rng(0).permutation(test)[:2000]
        if key not in models:
            m = XGBClassifier(n_estimators=50 if args.quick else 300, max_depth=6,
                              learning_rate=0.1, subsample=0.8, colsample_bytree=0.5,
                              tree_method="hist", n_jobs=-1, random_state=args.seed)
            m.fit(X[train], y[train])
            models[key] = m
        prob = models[key].predict_proba(X[test])[:, 1]
        knn = knn_predict(S, ia, ib, y, train, test)
        rows.append({"split": name, "model": "xgboost", "n_test": len(test),
                     **{k: round(v, 3) for k, v in scores(y[test], (prob >= 0.5).astype(int), prob).items()}})
        rows.append({"split": name, "model": "nearest neighbour", "n_test": len(test),
                     **{k: round(v, 3) for k, v in scores(y[test], knn).items()}})
        print("done:", name)

    res = pd.DataFrame(rows)
    res.to_csv(OUT, index=False)
    print()
    print(res.to_string(index=False))