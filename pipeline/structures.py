import argparse
import os
import re
import time
from urllib.parse import quote

import pandas as pd
import requests
from rdkit import Chem

PAIRS = "data/processed/pairs.csv"
OUT = "data/processed/structures.csv"
URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/{prop}/JSON"
PROPS = ["SMILES", "IsomericSMILES"]   # second is the older name, used if the first gives HTTP 400
PAUSE = 0.25                           # about 4 requests per second, under PubChem's limit


def clean_query(name):
    """Drop brackets like '(nasal)' before searching."""
    return re.sub(r"\s*\(.*?\)", "", str(name)).strip()


def parse_smiles(payload):
    """Return (cid, smiles) from a PubChem property reply, or (None, None)."""
    try:
        props = payload["PropertyTable"]["Properties"][0]
    except (KeyError, IndexError, TypeError):
        return None, None
    smiles = next((v for k, v in props.items() if "SMILES" in k and v), None)
    return props.get("CID"), smiles


def fetch(name):
    """Return (status, cid, smiles). status is found, not_found or error."""
    q = quote(clean_query(name), safe="")
    for prop in PROPS:
        for attempt in range(3):
            try:
                r = requests.get(URL.format(name=q, prop=prop), timeout=20)
            except requests.RequestException:
                time.sleep(2)
                continue
            if r.status_code == 200:
                cid, smiles = parse_smiles(r.json())
                return ("found", cid, smiles) if smiles else ("not_found", None, None)
            if r.status_code == 404:
                return "not_found", None, None
            if r.status_code == 400:
                break                      # try the next property name
            time.sleep(2 * (attempt + 1))  # 429 or 5xx: wait and retry
        else:
            return "error", None, None
    return "error", None, None


def drug_list():
    p = pd.read_csv(PAIRS)
    a = p[["drug_a_id", "drug_a"]].set_axis(["drug_id", "drug"], axis=1)
    b = p[["drug_b_id", "drug_b"]].set_axis(["drug_id", "drug"], axis=1)
    return pd.concat([a, b]).drop_duplicates("drug_id").sort_values("drug_id").reset_index(drop=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="only the first N drugs (for a test run)")
    args = ap.parse_args()

    drugs = drug_list()
    if args.limit:
        drugs = drugs.head(args.limit)

    done = pd.DataFrame()
    if os.path.exists(OUT):
        done = pd.read_csv(OUT)
        done = done[done["status"].isin(["found", "not_found"])]   # retry errors
    seen = set(done["drug_id"]) if len(done) else set()

    rows = done.to_dict("records")
    todo = drugs[~drugs["drug_id"].isin(seen)]
    print(f"drugs: {len(drugs)}, already done: {len(seen)}, to fetch: {len(todo)}")

    for i, (drug_id, drug) in enumerate(zip(todo["drug_id"], todo["drug"]), start=1):
        status, cid, smiles = fetch(drug)
        ok = bool(smiles) and Chem.MolFromSmiles(smiles) is not None
        rows.append({"drug_id": drug_id, "drug": drug, "status": status,
                     "cid": cid, "smiles": smiles, "rdkit_ok": ok})
        if args.limit or i % 50 == 0:
            print(i, drug, status, cid)
        if i % 25 == 0:
            pd.DataFrame(rows).to_csv(OUT, index=False)
        time.sleep(PAUSE)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    print("\nstatus counts:")
    print(out["status"].value_counts())
    print("RDKit can read the SMILES:", int(out["rdkit_ok"].sum()), "of", len(out))
    print("\nnot found (first 40):")
    print(out.loc[out["status"] == "not_found", "drug"].head(40).to_string(index=False))