import argparse
import sqlite3

import numpy as np
import pandas as pd

from ml.evaluate import tanimoto
from ml.interact import make_negatives
from ml.lookup_predictions import PAIRS, load_pairs, lookup, open_db, resolve
from ml.splits import INFO, NPZ, SEED, load_graded_pairs, random_split

NOTE = ("Similarity is Tanimoto on structure fingerprints, 0 to 1. It means a similar chemical "
        "structure, not the same drug class or the same effect.")


def closest_pairs(S, ia, ib, y, fit, ra, rb, k=5):
    """The k known pairs most like the pair (ra, rb), found the same way the band is scored.
    fit holds the row numbers of the known pairs. Returns (list of dicts, raw score)."""
    ta, tb = ia[fit], ib[fit]
    straight = S[ra, ta] * S[rb, tb]
    crossed = S[ra, tb] * S[rb, ta]
    sc = np.maximum(straight, crossed)
    top = np.argsort(-sc, kind="stable")[:k]
    w = sc[top]
    lab = y[fit][top]
    tot = w.sum()
    raw = float((w * lab).sum() / tot) if tot > 0 else 0.5
    out = []
    for t in top:
        if straight[t] >= crossed[t]:
            like_a, like_b = int(ta[t]), int(tb[t])
        else:
            like_a, like_b = int(tb[t]), int(ta[t])
        out.append({"row": int(fit[t]), "documented": bool(y[fit][t]),
                    "like_a": like_a, "like_b": like_b,
                    "sim_a": float(S[ra, like_a]), "sim_b": float(S[rb, like_b]),
                    "similarity": float(sc[t])})
    return out, raw


def build_context():
    """Rebuilds the same known pairs the stored bands were scored against (seed 42)."""
    allp = pd.read_csv(PAIRS)
    documented = {frozenset((str(a), str(b)))
                  for a, b in zip(allp["drug_a_id"], allp["drug_b_id"])}
    severity = {frozenset((str(a), str(b))): s
                for a, b, s in zip(allp["drug_a_id"], allp["drug_b_id"], allp["severity"])}
    pos = load_graded_pairs()
    neg = make_negatives(pos, documented, SEED)
    pairs = pd.concat([pos[["drug_a_id", "drug_b_id"]].assign(label=1),
                       neg.assign(label=0)], ignore_index=True)
    d = np.load(NPZ)
    fps = d["fps"]
    ids = [str(x) for x in d["drug_ids"]]
    row_of = {x: r for r, x in enumerate(ids)}
    ia = pairs["drug_a_id"].map(row_of).to_numpy()
    ib = pairs["drug_b_id"].map(row_of).to_numpy()
    y = pairs["label"].to_numpy()
    tr, _ = random_split(pairs, seed=SEED)
    perm = np.random.default_rng(0).permutation(tr)
    fit = perm[int(0.2 * len(tr)):]
    info = pd.read_csv(INFO)
    names = {str(i): str(n) for i, n in zip(info["drug_id"], info["drug"])}
    lk_ids, lk_sev = load_pairs()
    return {"S": tanimoto(fps), "ia": ia, "ib": ib, "y": y, "fit": fit, "ids": ids,
            "row_of": row_of, "names": names, "severity": severity,
            "lk_ids": lk_ids, "lk_sev": lk_sev}


def first_row(drug_ids, row_of):
    for i in sorted(drug_ids):
        if i in row_of:
            return row_of[i]
    return None


def describe(ctx, name_a, name_b, k=5):
    A, _, pa = resolve(name_a, ctx["lk_ids"])
    B, _, pb = resolve(name_b, ctx["lk_ids"])
    problems = [p[1] for p in (pa, pb) if p]
    if problems:
        print(" ".join(problems))
        return
    ra, rb = first_row(A, ctx["row_of"]), first_row(B, ctx["row_of"])
    if ra is None or rb is None:
        print(f"{name_a} + {name_b}: at least one drug has no structure on file.")
        return
    found, raw = closest_pairs(ctx["S"], ctx["ia"], ctx["ib"], ctx["y"], ctx["fit"], ra, rb, k)
    print()
    print(f"{name_a.strip()} + {name_b.strip()}")
    print(f"  raw score before calibration: {raw:.2f}")
    try:
        con = open_db()
        try:
            r = lookup(name_a, name_b, ctx["lk_ids"], ctx["lk_sev"], con)
        finally:
            con.close()
        extra = f", score {r['score_pct']}" if "score_pct" in r else ""
        print(f"  stored result: {r['status']} {r.get('band', '')}{extra}")
    except sqlite3.OperationalError:
        print("  stored result: predictions.db not found")
    print(f"  the {k} closest known pairs:")
    for n, f in enumerate(found, start=1):
        ia_, ib_ = ctx["ids"][f["like_a"]], ctx["ids"][f["like_b"]]
        pa_, pb_ = ctx["names"].get(ia_, ia_), ctx["names"].get(ib_, ib_)
        if f["documented"]:
            sev = ctx["severity"].get(frozenset((ia_, ib_)), "?")
            label = f"documented, {sev}"
        else:
            label = "not documented"
        print(f"  {n}. {label}: {pa_} + {pb_}")
        print(f"     {name_a.strip()} is like {pa_} ({f['sim_a']:.2f}), "
              f"{name_b.strip()} is like {pb_} ({f['sim_b']:.2f})")
    print("  " + NOTE)


def format_lines(found, ids, names, ra, rb, name_a, name_b):
    """Plain words for the closest known pairs. No scores, no severities."""
    lines = []
    for f in found:
        pa, pb = ids[f["like_a"]], ids[f["like_b"]]
        la, lb = names.get(pa, pa), names.get(pb, pb)
        status = "listed in DDInter" if f["documented"] else "no record in DDInter"
        parts = []
        for typed, like_name, like_row, my_row in ((name_a, la, f["like_a"], ra),
                                                    (name_b, lb, f["like_b"], rb)):
            if like_row == my_row:
                parts.append(f"{typed.strip()} is the same drug")
            else:
                parts.append(f"closest to {typed.strip()}: {like_name}")
        lines.append(f"{la} + {lb}: {status}. " + "; ".join(parts) + ".")
    return {"n": len(found), "n_documented": sum(1 for f in found if f["documented"]),
            "lines": lines}


def plain_summary(ctx, name_a, name_b, k=5):
    """Returns the format_lines result, or None if a name is not found or has no structure."""
    A, _, pa = resolve(name_a, ctx["lk_ids"])
    B, _, pb = resolve(name_b, ctx["lk_ids"])
    if pa or pb:
        return None
    ra, rb = first_row(A, ctx["row_of"]), first_row(B, ctx["row_of"])
    if ra is None or rb is None:
        return None
    found, _ = closest_pairs(ctx["S"], ctx["ia"], ctx["ib"], ctx["y"], ctx["fit"], ra, rb, k)
    return format_lines(found, ctx["ids"], ctx["names"], ra, rb, name_a, name_b)


TESTS = [("Abacavir", "Ixazomib"), ("Abacavir", "Ixabepilone"), ("Abacavir", "Ivosidenib")]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="two drug names")
    ap.add_argument("--test", action="store_true", help="show three pairs from the earlier checks")
    args = ap.parse_args()
    ctx = build_context()
    if args.test:
        for a, b in TESTS:
            describe(ctx, a, b)
    elif len(args.names) == 2:
        describe(ctx, args.names[0], args.names[1])
    else:
        print('Give two drug names, or use --test. Example: python -m ml.lookalike "Abacavir" "Ixazomib"')