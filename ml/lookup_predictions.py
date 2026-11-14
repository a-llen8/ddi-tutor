import argparse
import difflib
import sqlite3

import pandas as pd

PAIRS = "data/processed/pairs.csv"
DB = "data/processed/predictions.db"

BAND_TEXT = {
    "Low": "Low similarity to documented interactions. This does not mean the pair is safe.",
    "Medium": "Medium similarity to documented interactions.",
    "High": "High similarity to documented interactions. This is not a confirmed interaction.",
}
NOT_SAFE = "No record in DDInter. Not documented does not mean safe."

ALIASES = {
    "aspirin": "Acetylsalicylic acid",
    "paracetamol": "Acetaminophen",
    "adrenaline": "Epinephrine",
    "noradrenaline": "Norepinephrine",
    "albuterol": "Salbutamol",
    "frusemide": "Furosemide",
    "glyceryl trinitrate": "Nitroglycerin",
    "pethidine": "Meperidine",
    "rifampin": "Rifampicin",
    "ciclosporin": "Cyclosporine",
    "lignocaine": "Lidocaine",
    "penicillin g": "Benzylpenicillin",
    "vitamin c": "Ascorbic acid",
}

SHOWN = {}


def load_pairs():
    p = pd.read_csv(PAIRS)
    ids = {}
    for col_id, col_name in [("drug_a_id", "drug_a"), ("drug_b_id", "drug_b")]:
        for i, n in zip(p[col_id], p[col_name]):
            k = str(n).strip().lower()
            ids.setdefault(k, set()).add(str(i))
            SHOWN[k] = str(n).strip()
    sev = {}
    for a, b, s in zip(p["drug_a_id"], p["drug_b_id"], p["severity"]):
        sev[frozenset((str(a), str(b)))] = s
    return ids, sev


def open_db():
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)


def idx_of(con, drug_id):
    r = con.execute("select idx from drugs where drug_id=?", (drug_id,)).fetchone()
    return r[0] if r else None


def resolve(name, ids):
    """Returns (drug ids, note, problem). Problem is None when the name was understood."""
    k = name.strip().lower()
    if k in ids:
        return ids[k], None, None
    alias = ALIASES.get(k)
    if alias and alias.lower() in ids:
        return ids[alias.lower()], f"{name.strip()} is listed in DDInter as {alias}.", None
    near = sorted(n for n in ids if n.startswith(k + ",") or n.startswith(k + " ("))
    if len(near) == 1:
        return ids[near[0]], f"{name.strip()} is listed in DDInter as {SHOWN[near[0]]}.", None
    if len(near) > 1:
        return None, None, ("ambiguous", f"{name.strip()} matches several DDInter entries: "
                            + ", ".join(SHOWN[n] for n in near[:6]) + ". Please pick one.")
    pool = list(ids)
    labels = {n: SHOWN.get(n, n) for n in ids}
    for a, target in ALIASES.items():
        if a not in ids and target.lower() in ids:
            pool.append(a)
            shown = SHOWN.get(target.lower(), target)
            labels[a] = f"{a.title()} (listed in DDInter as {shown})"
    close = difflib.get_close_matches(k, pool, n=3, cutoff=0.75)
    suggestions = []
    for c in close:
        if labels[c] not in suggestions:
            suggestions.append(labels[c])
    msg = f"Drug name not found: {name.strip()}."
    if suggestions:
        msg += " Did you mean: " + ", ".join(suggestions) + "?"
    return None, None, ("not_found", msg)


def decide(A, B, sev, con):
    if A == B:
        return {"status": "same_drug", "text": "These are the same drug."}

    for x in A:
        for y in B:
            if x != y and frozenset((x, y)) in sev:
                s = sev[frozenset((x, y))]
                if s == "Unknown":
                    text = "Listed in DDInter, severity not graded."
                else:
                    text = f"Documented in DDInter: {s}."
                return {"status": "documented", "severity": s, "text": text}

    for x in A:
        for y in B:
            ix, iy = idx_of(con, x), idx_of(con, y)
            if ix is None or iy is None:
                continue
            lo, hi = min(ix, iy), max(ix, iy)
            r = con.execute("select score_pct, band from predictions "
                            "where drug_a=? and drug_b=?", (lo, hi)).fetchone()
            if r:
                return {"status": "predicted", "band": r[1], "score_pct": r[0],
                        "text": "Predicted, not confirmed. " + BAND_TEXT[r[1]]
                                + " No DDInter record."}

    have_a = any(idx_of(con, x) is not None for x in A)
    have_b = any(idx_of(con, y) is not None for y in B)
    if have_a and have_b:
        reason = "this pair is outside what the model covers."
    else:
        reason = "at least one of these drugs has no structure on file."
    return {"status": "no_prediction",
            "text": f"No prediction available: {reason} {NOT_SAFE}"}


def lookup(name_a, name_b, ids, sev, con):
    """Returns a dict with status and text. For predictions it also has band and score_pct.
    score_pct is for checking only. The app should not show it."""
    A, na, pa = resolve(name_a, ids)
    B, nb, pb = resolve(name_b, ids)
    problems = [p for p in (pa, pb) if p]
    if problems:
        status = "ambiguous" if any(p[0] == "ambiguous" for p in problems) else "not_found"
        return {"status": status, "text": " ".join(p[1] for p in problems)}
    notes = " ".join(x for x in (na, nb) if x)
    r = decide(A, B, sev, con)
    if notes:
        r["text"] = notes + " " + r["text"]
    return r


TESTS = [
    ("Warfarin", "Zidovudine", ("documented", "Unknown")),
    ("Metformin", "Cyclosporine", ("documented", "Unknown")),
    ("Simvastatin", "Goserelin", ("documented", "Unknown")),
    ("Abacavir", "Ixabepilone", ("predicted", "Medium", 44)),
    ("Abacavir", "Ixazomib", ("predicted", "High", 91)),
    ("Abacavir", "Ivosidenib", ("predicted", "Low", 20)),
    ("Vasopressin", "Abacavir", ("no_prediction",)),
    ("Dextrose", "Warfarin", None),
    ("Aspirin", "Warfarin", None),
    ("Paracetamol", "Warfarin", None),
    ("Aspirin", "Acetylsalicylic acid", ("same_drug",)),
    ("Salicylic acid", "Warfarin", ("ambiguous",)),
    ("Warfarine", "Zidovudine", ("not_found",)),
    ("Asprin", "Warfarin", ("not_found",)),
]


def check(r, exp):
    if exp is None:
        return ""
    if r["status"] != exp[0]:
        return "MISMATCH"
    if exp[0] == "documented" and r["severity"] != exp[1]:
        return "MISMATCH"
    if exp[0] == "predicted" and (r["band"] != exp[1] or r["score_pct"] != exp[2]):
        return "MISMATCH"
    return "OK"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="two drug names")
    ap.add_argument("--test", action="store_true", help="run the test pairs")
    args = ap.parse_args()

    ids, sev = load_pairs()
    con = open_db()
    if args.test:
        for a, b, exp in TESTS:
            r = lookup(a, b, ids, sev, con)
            extra = f" (score {r['score_pct']})" if "score_pct" in r else ""
            print(f"{a} + {b}: {r['status']}{extra} {check(r, exp)}")
            print("   ", r["text"])
    elif len(args.names) == 2:
        r = lookup(args.names[0], args.names[1], ids, sev, con)
        print(r["text"])
    else:
        print('Give two drug names, or use --test. Example: python -m ml.lookup_predictions "Warfarin" "Zidovudine"')
    con.close()