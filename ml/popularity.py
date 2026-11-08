import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from xgboost import XGBClassifier

from ml.interact import make_negatives
from ml.splits import PAIRS, cold_start_splits, load_graded_pairs, random_split

SEED = 42

allp = pd.read_csv(PAIRS)
documented = {frozenset((a, b)) for a, b in zip(allp["drug_a_id"], allp["drug_b_id"])}
pos = load_graded_pairs()
neg = make_negatives(pos, documented, SEED)
pairs = pd.concat([pos[["drug_a_id", "drug_b_id"]].assign(label=1),
                   neg.assign(label=0)], ignore_index=True)
y = pairs["label"].to_numpy()

tr, te = random_split(pairs, seed=SEED)
ctr, one, both, held = cold_start_splits(pairs, seed=SEED)


def degree_features(train):
    t = pairs.iloc[train]
    t = t[t["label"] == 1]
    counts = pd.concat([t["drug_a_id"], t["drug_b_id"]]).value_counts()
    da = pairs["drug_a_id"].map(counts).fillna(0).to_numpy()
    db = pairs["drug_b_id"].map(counts).fillna(0).to_numpy()
    return np.log1p(np.stack([np.minimum(da, db), np.maximum(da, db)], axis=1))


for name, train, test in [("random", tr, te), ("one drug unseen", ctr, one),
                          ("both drugs unseen", ctr, both)]:
    X = degree_features(train)
    m = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1,
                      tree_method="hist", n_jobs=-1, random_state=SEED)
    m.fit(X[train], y[train])
    prob = m.predict_proba(X[test])[:, 1]
    print(f"{name:<20} balanced_acc {balanced_accuracy_score(y[test], prob >= 0.5):.3f}"
          f"  roc_auc {roc_auc_score(y[test], prob):.3f}")