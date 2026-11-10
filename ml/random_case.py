import argparse
from collections import Counter

import numpy as np
import pandas as pd

from ml.case_simulator import check_case, id_names, show, verify
from ml.lookup_predictions import PAIRS, load_pairs

BRANDS = "data/processed/brand_generic.csv"


def build_pool(ids):
    """Drugs found in brands that are still sold. Weight = square root of brand count."""
    b = pd.read_csv(BRANDS)
    b = b[b["Is_discontinued"].astype(str).str.lower() != "true"]
    vals = pd.concat([b["ing1_dd"], b["ing2_dd"]]).dropna().astype(str).str.strip().str.lower()
    counts = vals[vals.isin(set(ids))].value_counts()
    alone = set(b.loc[b["ing2"].isna(), "ing1_dd"].dropna().astype(str).str.strip().str.lower())
    counts = counts[counts.index.isin(alone)]
    return list(counts.index), np.sqrt(counts.to_numpy(dtype=float))


def load_context():
    ids, sev = load_pairs()
    pool, weights = build_pool(ids)
    return {"ids": ids, "sev": sev, "names_of": id_names(), "pool": pool, "weights": weights}


def random_case(ctx, seed, max_tries=200):
    """Returns (drug names, tries). Names is None if no valid case was found.
    A valid case has 3 to 5 drugs, at least one Major pair and at least one pair with no record.
    The answers are not returned. Use check_case(names, ...) for them."""
    rng = np.random.default_rng(seed)
    pool = ctx["pool"]
    p = ctx["weights"] / ctx["weights"].sum()
    for attempt in range(1, max_tries + 1):
        k = int(rng.integers(3, 6))
        pick = rng.choice(len(pool), size=k, replace=False, p=p)
        names = [ctx["names_of"][sorted(ctx["ids"][pool[i]])[0]] for i in pick]
        r = check_case(names, ctx["ids"], ctx["sev"], ctx["names_of"])
        if (r["status"] == "ok" and len(r["drugs"]) == k
                and r["counts"]["Major"] >= 1 and r["counts"]["no_record"] >= 1
                and r["counts"]["Unknown"] <= 1):
            return names, attempt
    return None, max_tries


def run_test(ctx, n=1000):
    df = pd.read_csv(PAIRS)
    df["drug_a"] = df["drug_a"].astype(str).str.strip()
    df["drug_b"] = df["drug_b"].astype(str).str.strip()

    tries, failed, mismatches = [], 0, 0
    by_k, sev_total, used = Counter(), Counter(), Counter()
    examples = []
    for seed in range(n):
        names, t = random_case(ctx, seed)
        tries.append(t)
        if names is None:
            failed += 1
            continue
        r = check_case(names, ctx["ids"], ctx["sev"], ctx["names_of"])
        mismatches += verify(r, df)
        by_k[len(names)] += 1
        for p in r["pairs"]:
            sev_total[p["severity"] or "no record"] += 1
        used.update(r["drugs"])
        if len(examples) < 5:
            examples.append(r)

    ok = n - failed
    total_pairs = sum(sev_total.values())
    print("pool size:", len(ctx["pool"]), "drugs")
    print(f"cases made: {ok} of {n}  (no valid case found: {failed})")
    print(f"tries per case: average {np.mean(tries):.1f}, most {max(tries)}")
    print("cases by number of drugs:", dict(sorted(by_k.items())))
    print("share of all pairs:", {k: round(v / total_pairs, 3) for k, v in sev_total.most_common()})
    print(f"different drugs used: {len(used)} of {len(ctx['pool'])}")
    print("most common drugs:", used.most_common(10))
    print("pairs that differ from pairs.csv:", mismatches)
    for r in examples:
        print()
        show(r)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=None, help="make one case from this seed")
    ap.add_argument("--answers", action="store_true", help="show the answers for --seed")
    ap.add_argument("--test", action="store_true", help="make 1000 cases and print checks")
    args = ap.parse_args()

    ctx = load_context()
    if args.test:
        run_test(ctx)
    elif args.seed is not None:
        names, t = random_case(ctx, args.seed)
        if names is None:
            print("No valid case found for this seed.")
        else:
            print("Drugs:", ", ".join(names))
            if args.answers:
                show(check_case(names, ctx["ids"], ctx["sev"], ctx["names_of"]))
    else:
        print("Use --test, or --seed 7, or --seed 7 --answers")