"""The common-drugs deck: which drugs count, which pairs qualify, and the draw."""
import os

import numpy as np
import pandas as pd
import pytest

from ml.common_deck import MIN_BRANDS, brand_counts, common_drugs, common_pairs, draw_question

MEDS = pd.DataFrame({
    "brand": ["a", "b", "c", "d", "e", "f"],
    "ing1_dd": ["aspirin", "aspirin", "aspirin", "warfarin", "warfarin", "aspirin"],
    "ing2_dd": ["warfarin", None, "aspirin", "warfarin", None, None],
    "discontinued": [False, False, False, False, True, True],
})


def test_brand_counts_skip_discontinued_and_count_a_row_once_per_drug():
    counts = brand_counts(MEDS)
    assert counts == {"aspirin": 3, "warfarin": 2}


def test_threshold_is_at_least_not_more_than():
    assert common_drugs(MEDS, 3) == {"aspirin"}
    assert common_drugs(MEDS, 2) == {"aspirin", "warfarin"}
    assert common_drugs(MEDS, 4) == set()


def test_a_pair_needs_both_drugs():
    graded = pd.DataFrame({"drug_a": ["aspirin", "aspirin", "x"],
                           "drug_b": ["warfarin", "x", "y"],
                           "severity": ["Major", "Minor", "Moderate"]})
    out = common_pairs(graded, {"aspirin", "warfarin"})
    assert out["drug_b"].tolist() == ["warfarin"]


def test_draw_gives_each_severity_the_same_chance_and_only_deck_pairs():
    rows = ([("a", "b%d" % i, "Major") for i in range(500)]
            + [("c", "d%d" % i, "Moderate") for i in range(50)]
            + [("e", "f%d" % i, "Minor") for i in range(5)])
    pairs = pd.DataFrame(rows, columns=["drug_a", "drug_b", "severity"])
    rng = np.random.default_rng(0)
    seen = [draw_question(pairs, rng) for _ in range(3000)]
    share = {s: sum(1 for x in seen if x[2] == s) / 3000 for s in ("Major", "Moderate", "Minor")}
    assert all(0.28 < v < 0.38 for v in share.values())
    assert all((a, b, s) in set(rows) for a, b, s in seen)


def test_draw_with_no_pairs_raises():
    empty = pd.DataFrame({"drug_a": [], "drug_b": [], "severity": []})
    with pytest.raises(ValueError):
        draw_question(empty, np.random.default_rng(0))


@pytest.mark.skipif(not os.path.exists("data/app/medicines.csv.gz"), reason="app data missing")
def test_numbers_on_the_committed_data():
    meds = pd.read_csv("data/app/medicines.csv.gz")
    pairs = pd.read_csv("data/app/pairs.csv.gz")
    graded = pairs[pairs["severity"] != "Unknown"]
    assert MIN_BRANDS == 50
    drugs = common_drugs(meds)
    deck = common_pairs(graded, drugs)
    assert (len(drugs), len(deck), int((deck["severity"] == "Major").sum())) == (336, 6741, 996)
    drugs100 = common_drugs(meds, 100)
    deck100 = common_pairs(graded, drugs100)
    assert (len(drugs100), len(deck100), int((deck100["severity"] == "Major").sum())) == (248, 3628, 498)