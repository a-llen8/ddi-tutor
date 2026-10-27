"""Build the two small files the web app needs.

Run from the repo root:  python -m pipeline.build_app_data

Outputs (committed to git so the hosted app can load them):
  data/app/pairs.csv.gz      one row per unique drug pair + severity
  data/app/medicines.csv.gz  one row per brand medicine + its ingredients
"""
import os

import pandas as pd

from pipeline.build_pairs import build_pairs, load_ddinter
from pipeline.names import KAGGLE, build_table, ddinter_names

OUT_DIR = "data/app"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1) interaction pairs, keyed by lowercase generic name
    pairs, _, _ = build_pairs(load_ddinter())
    pairs = pairs[["drug_a", "drug_b", "severity"]].copy()
    pairs["drug_a"] = pairs["drug_a"].str.lower().str.strip()
    pairs["drug_b"] = pairs["drug_b"].str.lower().str.strip()
    pairs.to_csv(f"{OUT_DIR}/pairs.csv.gz", index=False)

    # 2) brand -> ingredients table (reuses Allen's name-matching code)
    kg = pd.read_csv(KAGGLE)
    t = build_table(kg, ddinter_names())
    t["brand"] = t["name"].str.strip()
    t["discontinued"] = t["Is_discontinued"].astype(str).str.lower().eq("true")
    keep = t["ing1_dd"].notna() | t["ing2_dd"].notna()
    meds = t.loc[keep, ["brand", "ing1", "ing1_dd", "ing2", "ing2_dd", "discontinued"]]
    meds = meds.drop_duplicates(["brand", "ing1", "ing2"]).reset_index(drop=True)
    meds.to_csv(f"{OUT_DIR}/medicines.csv.gz", index=False)

    print("pairs:", len(pairs), "| medicines:", len(meds))


if __name__ == "__main__":
    main()
