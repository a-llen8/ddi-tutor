import numpy as np
import pandas as pd

PAIRS = "data/processed/pairs.csv"
INFO = "data/processed/fingerprint_info.csv"
GRADED = ["Minor", "Moderate", "Major"]
SEED = 42


def load_graded_pairs():
    """Graded pairs where both drugs have a fingerprint."""
    p = pd.read_csv(PAIRS)
    ok = set(pd.read_csv(INFO)["drug_id"])
    m = p["drug_a_id"].isin(ok) & p["drug_b_id"].isin(ok) & p["severity"].isin(GRADED)
    return p[m].reset_index(drop=True)


def random_split(pairs, test_frac=0.2, seed=SEED):
    rng = np.random.default_rng(seed)
    is_test = rng.random(len(pairs)) < test_frac
    return np.where(~is_test)[0], np.where(is_test)[0]


def cold_start_splits(pairs, drug_frac=0.2, seed=SEED):
    """Hold out some drugs. Returns train, one_unseen, both_unseen row numbers and the held drugs."""
    rng = np.random.default_rng(seed)
    drugs = np.array(sorted(set(pairs["drug_a_id"]) | set(pairs["drug_b_id"])))
    held = set(map(str, rng.choice(drugs, size=int(len(drugs) * drug_frac), replace=False)))
    a = pairs["drug_a_id"].isin(held).to_numpy()
    b = pairs["drug_b_id"].isin(held).to_numpy()
    return np.where(~a & ~b)[0], np.where(a ^ b)[0], np.where(a & b)[0], held


def describe(name, pairs, idx):
    sev = pairs.iloc[idx]["severity"].value_counts().to_dict()
    print(f"{name:<22} {len(idx):>7} pairs  {sev}")


if __name__ == "__main__":
    pairs = load_graded_pairs()
    print("graded pairs with both structures:", len(pairs))
    tr, te = random_split(pairs)
    describe("random train", pairs, tr)
    describe("random test", pairs, te)
    ctr, one, both, held = cold_start_splits(pairs)
    print("held-out drugs:", len(held))
    describe("cold-start train", pairs, ctr)
    describe("one drug unseen", pairs, one)
    describe("both drugs unseen", pairs, both)