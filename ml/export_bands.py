"""Export the prediction bands to two small files the hosted app can load.

Run from the repo root:  python -m ml.export_bands

Reads  data/processed/predictions.db (read-only) and data/processed/pairs.csv.
Writes data/app/band_drugs.csv.gz  one column, drug: lowercase generic names, sorted
       data/app/bands.csv.gz       columns a, b, band
a and b are row numbers into band_drugs.csv.gz (a is always less than b).
band is 0 for Low, 1 for Medium, 2 for High.
The score (score_pct) is never exported, so the app cannot show a number.
"""
import os
import sqlite3
import sys

import numpy as np
import pandas as pd

PAIRS = "data/processed/pairs.csv"
DB = "data/processed/predictions.db"
OUT_DIR = "data/app"
BANDS = f"{OUT_DIR}/bands.csv.gz"
DRUGS = f"{OUT_DIR}/band_drugs.csv.gz"
CODE = {"Low": 0, "Medium": 1, "High": 2}
GZIP = {"method": "gzip", "compresslevel": 9, "mtime": 0}


def names_by_id(pairs):
    """{DDInter id: lowercase generic name}. Stops if an id has two names."""
    seen = {}
    for col_id, col_name in (("drug_a_id", "drug_a"), ("drug_b_id", "drug_b")):
        for i, n in zip(pairs[col_id], pairs[col_name]):
            seen.setdefault(str(i), set()).add(str(n).strip().lower())
    clash = {i: v for i, v in seen.items() if len(v) > 1}
    if clash:
        sys.exit(f"STOP: {len(clash)} ids have more than one name, for example {next(iter(clash.items()))}")
    return {i: next(iter(v)) for i, v in seen.items()}


def build(drugs, pred, names):
    """drugs: idx, drug_id. pred: drug_a, drug_b, band (database row numbers).
    Returns (list of drug names sorted, DataFrame a, b, band)."""
    drugs = drugs.copy()
    drugs["name"] = drugs["drug_id"].astype(str).map(names)
    if drugs["name"].isna().any():
        sys.exit(f"STOP: {int(drugs['name'].isna().sum())} database drugs have no name in pairs.csv")
    if drugs["name"].duplicated().any():
        sys.exit("STOP: two database drugs share one name")
    bad = ~pred["band"].isin(CODE)
    if bad.any():
        sys.exit(f"STOP: {int(bad.sum())} rows have a band that is not Low, Medium or High")

    old_to_name = dict(zip(drugs["idx"], drugs["name"]))
    used = sorted({old_to_name[i] for i in pd.unique(np.concatenate(
        [pred["drug_a"].to_numpy(), pred["drug_b"].to_numpy()]))})
    new_of = {n: k for k, n in enumerate(used)}
    remap = np.full(int(drugs["idx"].max()) + 1, -1, dtype=np.int64)
    for old, n in old_to_name.items():
        if n in new_of:
            remap[old] = new_of[n]

    a = remap[pred["drug_a"].to_numpy()]
    b = remap[pred["drug_b"].to_numpy()]
    out = pd.DataFrame({"a": np.minimum(a, b), "b": np.maximum(a, b),
                        "band": pred["band"].map(CODE).to_numpy()})
    out = out.sort_values(["a", "b"]).reset_index(drop=True)
    if (out["a"] >= out["b"]).any():
        sys.exit("STOP: a pair has the same drug on both sides")
    if out.duplicated(["a", "b"]).any():
        sys.exit("STOP: duplicate pairs after renumbering")
    return used, out


def main():
    for f in (PAIRS, DB):
        if not os.path.exists(f):
            sys.exit(f"STOP: {f} not found. Run from the project root.")
    names = names_by_id(pd.read_csv(PAIRS))
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        drugs = pd.read_sql("select idx, drug_id from drugs", con)
        pred = pd.read_sql("select drug_a, drug_b, band from predictions", con)
    finally:
        con.close()

    used, out = build(drugs, pred, names)
    os.makedirs(OUT_DIR, exist_ok=True)
    pd.DataFrame({"drug": used}).to_csv(DRUGS, index=False, compression=GZIP)
    out.to_csv(BANDS, index=False, compression=GZIP)

    share = out["band"].value_counts(normalize=True).sort_index() * 100
    print("drugs:", len(used))
    print("pairs:", f"{len(out):,}")
    print("band split: Low {:.1f}%, Medium {:.1f}%, High {:.1f}%".format(
        share.get(0, 0), share.get(1, 0), share.get(2, 0)))
    for f in (DRUGS, BANDS):
        print(f"{f}: {os.path.getsize(f) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()