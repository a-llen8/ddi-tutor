import argparse
import itertools

import pandas as pd

from ml.lookup_predictions import PAIRS, load_pairs, resolve

MAX_DRUGS = 8
ORDER = {"Major": 0, "Moderate": 1, "Minor": 2, "Unknown": 3, None: 4}
NOT_SAFE = "No record in DDInter. Not documented does not mean safe."
LIMITS = ("This checks pairs only, not effects of three or more drugs together. "
          "For learning only, not for treating patients.")


def id_names():
    p = pd.read_csv(PAIRS)
    out = {}
    for col_id, col_name in [("drug_a_id", "drug_a"), ("drug_b_id", "drug_b")]:
        for i, n in zip(p[col_id], p[col_name]):
            out[str(i)] = str(n).strip()
    return out


def pair_text(severity):
    if severity is None:
        return NOT_SAFE
    if severity == "Unknown":
        return "Listed in DDInter, severity not graded."
    return f"Documented in DDInter: {severity}."


def check_case(names, ids, sev, names_of):
    """Returns a dict. status is ok or needs_fix. Confirmed DDInter records only."""
    names = [n for n in names if n.strip()]
    if len(names) < 2:
        return {"status": "needs_fix", "messages": ["Enter at least 2 drugs."]}
    if len(names) > MAX_DRUGS:
        return {"status": "needs_fix", "messages": [f"Enter at most {MAX_DRUGS} drugs."]}

    drugs, notes, problems = [], [], []
    for n in names:
        A, note, prob = resolve(n, ids)
        if prob:
            problems.append(prob[1])
            continue
        if note:
            notes.append(note)
        display = names_of[sorted(A)[0]]
        if any(A & other for _, other in drugs):
            notes.append(f"{n.strip()} is the same drug as {display}. Counted once.")
            continue
        drugs.append((display, A))
    if problems:
        return {"status": "needs_fix", "messages": problems}
    if len(drugs) < 2:
        return {"status": "needs_fix", "messages": ["Enter at least 2 different drugs."]}

    rows = []
    for (na, A), (nb, B) in itertools.combinations(drugs, 2):
        found = [sev[frozenset((x, y))] for x in A for y in B
                 if x != y and frozenset((x, y)) in sev]
        s = min(found, key=ORDER.get) if found else None
        rows.append({"drug_a": na, "drug_b": nb, "severity": s, "text": pair_text(s)})
    rows.sort(key=lambda r: (ORDER[r["severity"]], r["drug_a"], r["drug_b"]))

    counts = {k: 0 for k in ["Major", "Moderate", "Minor", "Unknown", "no_record"]}
    for r in rows:
        counts[r["severity"] or "no_record"] += 1
    return {"status": "ok", "drugs": [d for d, _ in drugs], "notes": notes,
            "pairs": rows, "counts": counts, "limits": LIMITS}


def show(r):
    if r["status"] != "ok":
        for m in r["messages"]:
            print(m)
        return
    c = r["counts"]
    print("Drugs:", ", ".join(r["drugs"]))
    for n in r["notes"]:
        print(n)
    print(f"{len(r['pairs'])} pairs: Major {c['Major']}, Moderate {c['Moderate']}, "
          f"Minor {c['Minor']}, Unknown {c['Unknown']}, no record {c['no_record']}")
    for p in r["pairs"]:
        print(f"  {p['drug_a']} + {p['drug_b']}: {p['text']}")
    print(r["limits"])


def verify(r, df):
    """Re-reads every pair straight from pairs.csv by name. Returns the number of mismatches."""
    bad = 0
    k = len(r["drugs"])
    if len(r["pairs"]) != k * (k - 1) // 2:
        bad += 1
    for p in r["pairs"]:
        a, b = p["drug_a"], p["drug_b"]
        m = ((df["drug_a"] == a) & (df["drug_b"] == b)) | ((df["drug_a"] == b) & (df["drug_b"] == a))
        found = df[m]["severity"].tolist()
        expected = min(found, key=ORDER.get) if found else None
        if expected != p["severity"]:
            bad += 1
    return bad


TESTS = [
    ["Warfarin", "Metformin", "Simvastatin"],
    ["Aspirin", "Warfarin", "Paracetamol"],
    ["Warfarin", "Warfarine", "Salicylic acid"],
    ["Aspirin", "Acetylsalicylic acid", "Warfarin"],
]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="2 to 8 drug names")
    ap.add_argument("--test", action="store_true", help="run 4 test cases")
    args = ap.parse_args()

    ids, sev = load_pairs()
    names_of = id_names()
    if args.test:
        df = pd.read_csv(PAIRS)
        df["drug_a"] = df["drug_a"].astype(str).str.strip()
        df["drug_b"] = df["drug_b"].astype(str).str.strip()
        for case in TESTS:
            print()
            print("Case:", " | ".join(case))
            r = check_case(case, ids, sev, names_of)
            show(r)
            if r["status"] == "ok":
                bad = verify(r, df)
                print("check against pairs.csv:", "OK" if bad == 0 else f"MISMATCH ({bad})")
    elif args.names:
        show(check_case(args.names, ids, sev, names_of))
    else:
        print('Give 2 to 8 drug names, or use --test. Example: '
              'python -m ml.case_simulator "Warfarin" "Metformin" "Simvastatin"')