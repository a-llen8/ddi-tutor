import pandas as pd

from ml.splits import cold_start_splits


def test_twin_drugs_are_held_out_together():
    pairs = pd.DataFrame({
        "drug_a_id": ["D1", "D1", "D2", "D3", "D3", "D4"],
        "drug_b_id": ["D2", "D3", "D4", "D4", "D5", "D5"],
        "severity": ["Major"] * 6,
    })
    group_of = {"D1": 0, "D2": 1, "D3": 1, "D4": 2, "D5": 3}  # D2 and D3 are twins
    for seed in range(20):
        _, _, _, held = cold_start_splits(pairs, drug_frac=0.4, seed=seed, group_of=group_of)
        assert ("D2" in held) == ("D3" in held)