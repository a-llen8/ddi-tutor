"""Popularity-matched negative pairs. Needs only numpy and pandas."""
import numpy as np
import pandas as pd


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
