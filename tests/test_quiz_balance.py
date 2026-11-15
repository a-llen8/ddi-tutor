import numpy as np
import pandas as pd
import pytest

from pipeline.lookup import Checker

MEDS = pd.DataFrame({
    "brand": ["Warf 5 Tablet"],
    "ing1": ["warfarin"],
    "ing1_dd": ["warfarin"],
    "ing2": [None],
    "ing2_dd": [None],
    "discontinued": [False],
})


def make(severities):
    n = len(severities)
    pairs = pd.DataFrame({
        "drug_a": [f"a{i}" for i in range(n)],
        "drug_b": [f"b{i}" for i in range(n)],
        "severity": severities,
    })
    return Checker(pairs, MEDS)


def draws(chk, n=3000, seed=0):
    rng = np.random.default_rng(seed)
    return [chk.quiz_question(rng) for _ in range(n)]


def test_levels_are_balanced_even_when_data_is_not():
    chk = make(["Major"] + ["Moderate"] * 5 + ["Minor"])
    out = draws(chk)
    for level in ("Major", "Moderate", "Minor"):
        share = sum(1 for _, _, s in out if s == level) / len(out)
        assert 0.28 < share < 0.39


def test_unknown_is_never_asked():
    chk = make(["Major", "Moderate", "Minor", "Unknown", "Unknown", "Unknown"])
    assert all(s != "Unknown" for _, _, s in draws(chk, n=500))


def test_missing_level_is_skipped():
    chk = make(["Major", "Moderate", "Moderate"])
    out = draws(chk, n=500)
    assert {s for _, _, s in out} == {"Major", "Moderate"}


def test_returned_pair_matches_its_severity():
    chk = make(["Major", "Moderate", "Minor"])
    for a, b, s in draws(chk, n=100):
        assert chk._sev[frozenset((a, b))] == s


def test_no_graded_pairs_raises():
    chk = make(["Unknown", "Unknown"])
    with pytest.raises(ValueError):
        chk.quiz_question(np.random.default_rng(0))