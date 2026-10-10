import glob
import os
import pandas as pd

RAW = "data/raw"
OUT = "data/processed/pairs.csv"


def load_ddinter():
    files = sorted(glob.glob(f"{RAW}/ddinter_downloads_code_*.csv"))
    print("files found:", len(files))
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True)


def build_pairs(df):
    a, b = df["DDInterID_A"], df["DDInterID_B"]
    swap = a > b
    out = pd.DataFrame({
        "drug_a_id": a.where(~swap, b),
        "drug_b_id": b.where(~swap, a),
        "drug_a": df["Drug_A"].where(~swap, df["Drug_B"]),
        "drug_b": df["Drug_B"].where(~swap, df["Drug_A"]),
        "severity": df["Level"],
    })
    n_before = len(out)
    conflicts = int(out.groupby(["drug_a_id", "drug_b_id"])["severity"].nunique().gt(1).sum())
    out = out.drop_duplicates(["drug_a_id", "drug_b_id"]).reset_index(drop=True)
    return out, n_before, conflicts


if __name__ == "__main__":
    os.makedirs("data/processed", exist_ok=True)
    pairs, n_before, conflicts = build_pairs(load_ddinter())
    pairs.to_csv(OUT, index=False)
    print("rows before:", n_before)
    print("unique pairs:", len(pairs))
    print("conflicting severities:", conflicts)
    print(pairs["severity"].value_counts())