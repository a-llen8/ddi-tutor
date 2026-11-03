import pandas as pd
from ml.splits import cold_start_splits, random_split


def tiny():
    ids = [f"D{i}" for i in range(10)]
    rows = [(a, b) for i, a in enumerate(ids) for b in ids[i + 1:]]
    return pd.DataFrame(rows, columns=["drug_a_id", "drug_b_id"])


def test_cold_start_has_no_leak():
    p = tiny()
    group_of = {d: i for i, d in enumerate(sorted(set(p["drug_a_id"]) | set(p["drug_b_id"])))}
    train, one, both, held = cold_start_splits(p, drug_frac=0.3, seed=1, group_of=group_of)
    tr, o, bo = p.iloc[train], p.iloc[one], p.iloc[both]
    assert not (tr["drug_a_id"].isin(held) | tr["drug_b_id"].isin(held)).any()
    assert ((o["drug_a_id"].isin(held).astype(int) + o["drug_b_id"].isin(held).astype(int)) == 1).all()
    assert (bo["drug_a_id"].isin(held) & bo["drug_b_id"].isin(held)).all()
    assert len(train) + len(one) + len(both) == len(p)


def test_random_split_covers_every_pair_once():
    p = tiny()
    train, test = random_split(p)
    assert len(set(train) & set(test)) == 0
    assert len(train) + len(test) == len(p)