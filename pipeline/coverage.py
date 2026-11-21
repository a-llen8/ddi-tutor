"""Work out which drugs the 8 DDInter class files cover completely.

Run from the repo root:  python -m pipeline.coverage

Rule: a file for class X holds every interaction where at least one drug is in
class X. So a drug is covered when ONE file holds all of its partners, meaning
that file's partner list for the drug equals its partner list over all 8 files.
A drug from a missing class shows up only through partners in the 8 files, so
no single file holds all of its pairs (uncovered).

Output: data/app/coverage.csv.gz with columns drug, covered
(drug is the lowercase generic name, covered is True or False).
"""
import glob
import os
from collections import defaultdict

import pandas as pd

RAW = "data/raw"
OUT = "data/app/coverage.csv.gz"


def read_files():
    """[(class letter, dataframe)] for the 8 DDInter files, sorted by letter."""
    out = []
    for f in sorted(glob.glob(f"{RAW}/ddinter_downloads_code_*.csv")):
        letter = os.path.basename(f).split("_")[-1].split(".")[0]
        out.append((letter, pd.read_csv(f)))
    return out


def partners_per_file(frames):
    """{letter: {drug id: set of partner ids}} for every file."""
    res = {}
    for letter, df in frames:
        d = defaultdict(set)
        for a, b in zip(df["DDInterID_A"], df["DDInterID_B"]):
            d[a].add(b)
            d[b].add(a)
        res[letter] = d
    return res


def covered_ids(per_file):
    """Ids of drugs for which at least one file holds every partner."""
    total = defaultdict(set)
    for d in per_file.values():
        for k, v in d.items():
            total[k] |= v
    covered = set()
    for drug, partners in total.items():
        if any(d.get(drug) == partners for d in per_file.values()):
            covered.add(drug)
    return set(total), covered


def id_names(frames):
    """{drug id: set of lowercase names}."""
    out = defaultdict(set)
    for _, df in frames:
        for col_id, col_name in (("DDInterID_A", "Drug_A"), ("DDInterID_B", "Drug_B")):
            for i, n in zip(df[col_id], df[col_name]):
                out[i].add(str(n).strip().lower())
    return out


def build_table(all_ids, covered, names):
    """One row per drug name. A name is covered only if every id behind it is."""
    state = defaultdict(list)
    for i in all_ids:
        for n in names[i]:
            state[n].append(i in covered)
    rows = [(n, all(v)) for n, v in sorted(state.items())]
    return pd.DataFrame(rows, columns=["drug", "covered"])


def pairs_both_uncovered(frames, covered):
    seen = set()
    for _, df in frames:
        for a, b in zip(df["DDInterID_A"], df["DDInterID_B"]):
            seen.add((min(a, b), max(a, b)))
    return sum(1 for a, b in seen if a not in covered and b not in covered), len(seen)


def main():
    frames = read_files()
    per_file = partners_per_file(frames)
    all_ids, covered = covered_ids(per_file)
    names = id_names(frames)
    bad, n_pairs = pairs_both_uncovered(frames, covered)
    multi = sum(1 for v in names.values() if len(v) > 1)
    table = build_table(all_ids, covered, names)

    print("files read:", [l for l, _ in frames])
    print("unique pairs:", n_pairs)
    print(f"drugs: {len(all_ids)} | covered: {len(covered)} | not covered: {len(all_ids) - len(covered)}")
    print("documented pairs where both drugs are not covered:", bad)
    print("names with more than one id:", multi)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    table.to_csv(OUT, index=False)
    print(f"rows written: {len(table)} | covered names: {int(table['covered'].sum())} -> {OUT}")


if __name__ == "__main__":
    main()