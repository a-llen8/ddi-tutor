import argparse
import os
import sqlite3
import time

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression

from ml.calibrate import ece, knn_score
from ml.evaluate import tanimoto
from ml.interact import make_negatives
from ml.splits import INFO, NPZ, PAIRS, load_graded_pairs, random_split

SEED = 42
LOW_MAX = 0.4
HIGH_MIN = 0.7
STEP = 20000
DIR = "data/processed/"


def band_of(p):
    return np.where(p < LOW_MAX, "Low", np.where(p < HIGH_MIN, "Medium", "High"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0,
                    help="test run: score only this many absent pairs")
    args = ap.parse_args()
    tag = "_test" if args.limit else ""
    prog = f"{DIR}predict_scores{tag}.npy"
    prog_tmp = f"{DIR}predict_scores{tag}_tmp.npy"
    calf = f"{DIR}predict_cal{tag}.npz"
    dbf = f"{DIR}predictions{tag}.db"
    cap_cal, cap_test = (2000, 2000) if args.limit else (30000, 20000)

    allp = pd.read_csv(PAIRS)
    documented = {frozenset((str(a), str(b)))
                  for a, b in zip(allp["drug_a_id"], allp["drug_b_id"])}
    pos = load_graded_pairs()
    neg = make_negatives(pos, documented, SEED)
    pairs = pd.concat([pos[["drug_a_id", "drug_b_id"]].assign(label=1),
                       neg.assign(label=0)], ignore_index=True)

    d = np.load(NPZ)
    fps = d["fps"]
    ids = [str(x) for x in d["drug_ids"]]
    n = len(ids)
    row_of = {x: r for r, x in enumerate(ids)}
    ia = pairs["drug_a_id"].map(row_of).to_numpy()
    ib = pairs["drug_b_id"].map(row_of).to_numpy()
    y = pairs["label"].to_numpy()
    S = tanimoto(fps)

    tr, te = random_split(pairs, seed=SEED)
    rng = np.random.default_rng(0)
    perm = rng.permutation(tr)
    n_cal = int(0.2 * len(tr))
    cal_full, fit_idx = perm[:n_cal], perm[n_cal:]
    cal_idx = rng.permutation(cal_full)[:cap_cal]
    test = rng.permutation(te)[:cap_test]
    assert not (set(fit_idx) & set(cal_idx))
    assert not (set(test) & set(fit_idx)) and not (set(test) & set(cal_idx))
    print("fit:", len(fit_idx), " calibration:", len(cal_idx), " test:", len(test))

    if os.path.exists(calf):
        z = np.load(calf)
        cal_raw, test_raw = z["cal_raw"], z["test_raw"]
        print("loaded saved calibration scores")
    else:
        t0 = time.time()
        cal_raw = knn_score(S, ia, ib, y, fit_idx, cal_idx)
        test_raw = knn_score(S, ia, ib, y, fit_idx, test)
        np.savez(calf, cal_raw=cal_raw, test_raw=test_raw)
        print(f"scored calibration and test sets in {time.time() - t0:.0f} s")

    iso = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1)
    iso.fit(cal_raw, y[cal_idx])
    test_cal = np.clip(iso.predict(test_raw), 0, 1)
    print("check on test set: ECE", round(ece(y[test], test_cal), 3))
    tb = band_of(test_cal)
    rows = []
    for b in ["Low", "Medium", "High"]:
        m = tb == b
        rows.append({"band": b, "n_test": int(m.sum()),
                     "share_documented": round(float(y[test][m].mean()), 3) if m.sum() else None,
                     "mean_score": round(float(test_cal[m].mean()), 3) if m.sum() else None})
    summary = pd.DataFrame(rows)
    summary.to_csv(f"{DIR}band_summary{tag}.csv", index=False)
    print()
    print(summary.to_string(index=False))
    print()

    a = allp["drug_a_id"].astype(str).map(row_of)
    b = allp["drug_b_id"].astype(str).map(row_of)
    ok = a.notna() & b.notna()
    a = a[ok].astype(int).to_numpy()
    b = b[ok].astype(int).to_numpy()
    D = np.zeros((n, n), dtype=bool)
    D[a, b] = True
    D[b, a] = True
    seen = set(pos["drug_a_id"].astype(str)) | set(pos["drug_b_id"].astype(str))
    seen_arr = np.array([x in seen for x in ids])
    i, j = np.triu_indices(n, k=1)
    sel = np.flatnonzero(~D[i, j] & seen_arr[i] & seen_arr[j])
    print("absent pairs with both drugs known:", len(sel))
    if args.limit:
        sel = np.sort(np.random.default_rng(1).choice(sel, args.limit, replace=False))
    ai, bj = i[sel], j[sel]

    IA = np.concatenate([ia, ai])
    IB = np.concatenate([ib, bj])
    Y = np.concatenate([y, np.zeros(len(sel), dtype=y.dtype)])
    base = len(ia)

    if os.path.exists(prog):
        scores = np.load(prog)
        assert len(scores) == len(sel), "progress file does not match, delete it"
        print("resuming from saved progress")
    else:
        scores = np.full(len(sel), np.nan, dtype=np.float32)
    t0 = time.time()
    done_now = 0
    for s in range(0, len(sel), STEP):
        e = min(s + STEP, len(sel))
        if not np.isnan(scores[s:e]).any():
            continue
        scores[s:e] = knn_score(S, IA, IB, Y, fit_idx, base + np.arange(s, e))
        done_now += e - s
        np.save(prog_tmp, scores)
        os.replace(prog_tmp, prog)
        left = int(np.isnan(scores).sum())
        rate = done_now / (time.time() - t0)
        print(f"scored {len(sel) - left} of {len(sel)}, about {left / rate / 60:.0f} min left")
    assert not np.isnan(scores).any()

    p = np.clip(iso.predict(scores), 0, 1)
    pct = np.rint(p * 100).astype(int)
    bands = band_of(p)
    print()
    print("band share among absent pairs:")
    print(pd.Series(bands).value_counts(normalize=True).round(3).to_string())

    if os.path.exists(dbf):
        os.remove(dbf)
    info = pd.read_csv(INFO).set_index("drug_id")["drug"]
    con = sqlite3.connect(dbf)
    con.execute("create table drugs (idx integer primary key, drug_id text, drug text)")
    con.executemany("insert into drugs values (?, ?, ?)",
                    [(r, x, str(info.get(x, ""))) for r, x in enumerate(ids)])
    con.execute("create table predictions (drug_a integer, drug_b integer, "
                "score_pct integer, band text, primary key (drug_a, drug_b)) without rowid")
    rows = list(zip(ai.tolist(), bj.tolist(), pct.tolist(), bands.tolist()))
    for s in range(0, len(rows), 100000):
        con.executemany("insert into predictions values (?, ?, ?, ?)", rows[s:s + 100000])
    con.execute("create table meta (key text, value text)")
    con.executemany("insert into meta values (?, ?)", [
        ("label", "Predicted, not confirmed"),
        ("meaning", "Looks like a pair documented in DDInter. Not a confirmed interaction. Not safe if low."),
        ("scope", "Only pairs with no DDInter record where both drugs have a structure and a graded pair."),
        ("model", "Nearest neighbour on Morgan fingerprints, isotonic calibration, seed 42"),
        ("band_cutoffs", f"Low < {LOW_MAX} <= Medium < {HIGH_MIN} <= High"),
    ])
    con.commit()

    cnt = con.execute("select count(*) from predictions").fetchone()[0]
    assert cnt == len(sel)
    samp = np.random.default_rng(5).choice(len(sel), min(2000, len(sel)), replace=False)
    for k in samp:
        assert frozenset((ids[ai[k]], ids[bj[k]])) not in documented
    print()
    print("rows in database:", cnt, " (checked 2000 random rows: none is documented in DDInter)")
    print("file size MB:", round(os.path.getsize(dbf) / 1e6, 1))
    q = ("select a.drug, b.drug, p.score_pct, p.band from predictions p "
         "join drugs a on a.idx = p.drug_a join drugs b on b.idx = p.drug_b limit 5")
    for r in con.execute(q):
        print(r)
    con.close()