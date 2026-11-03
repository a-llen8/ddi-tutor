import numpy as np
import pandas as pd

PAIRS = "data/processed/pairs.csv"
INFO = "data/processed/fingerprint_info.csv"
NPZ = "data/processed/fingerprints.npz"
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


def fingerprint_groups():
    """Map each drug_id (as text) to a group number. Drugs with the same fingerprint share a group."""
    d = np.load(NPZ)
    seen, group_of = {}, {}
    for drug_id, fp in zip(d["drug_ids"], d["fps"]):
        group_of[str(drug_id)] = seen.setdefault(fp.tobytes(), len(seen))
    return group_of


def cold_start_splits(pairs, drug_frac=0.2, seed=SEED, group_of=None):
    """Hold out some drugs. Drugs with the same fingerprint (twins) are held out together.
    Returns train, one_unseen, both_unseen row numbers and the held drugs."""
    rng = np.random.default_rng(seed)
    if group_of is None:
        group_of = fingerprint_groups()
    drugs = sorted(set(pairs["drug_a_id"]) | set(pairs["drug_b_id"]))
    groups = np.array(sorted({group_of[str(d)] for d in drugs}))
    n_held = int(len(groups) * drug_frac)
    held_groups = set(rng.choice(groups, size=n_held, replace=False).tolist())
    held = {str(d) for d in drugs if group_of[str(d)] in held_groups}
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