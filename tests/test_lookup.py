import numpy as np
import pandas as pd
import pytest

from pipeline.lookup import Checker

PAIRS = pd.DataFrame({
    "drug_a": ["aspirin", "warfarin", "metformin"],
    "drug_b": ["warfarin", "fluconazole", "alcohol"],
    "severity": ["Major", "Moderate", "Unknown"],
})
MEDS = pd.DataFrame({
    "brand": ["Ecosprin 75 Tablet", "Warf 5 Tablet", "Glycomet 500 Tablet", "Combo Tablet"],
    "ing1": ["aspirin", "warfarin", "metformin", "aspirin"],
    "ing1_dd": ["aspirin", "warfarin", "metformin", "aspirin"],
    "ing2": [None, None, None, "thiocolchicoside"],
    "ing2_dd": [None, None, None, None],
    "discontinued": [False] * 4,
})


@pytest.fixture
def chk():
    return Checker(PAIRS, MEDS)


def test_order_of_pair_does_not_matter(chk):
    a, b = chk.resolve("Warf 5 Tablet"), chk.resolve("Ecosprin 75 Tablet")
    res = chk.check([a, b])["interactions"]
    assert len(res) == 1 and res.loc[0, "severity"] == "Major"


def test_generic_and_brand_mix(chk):
    res = chk.check([chk.resolve("warfarin (generic)"), chk.resolve("Ecosprin 75 Tablet")])
    assert res["interactions"].loc[0, "severity"] == "Major"


def test_duplicate_ingredient_flagged(chk):
    res = chk.check([chk.resolve("Ecosprin 75 Tablet"), chk.resolve("Combo Tablet")])
    assert res["duplicates"].loc[0, "ingredient"] == "aspirin"
    assert res["interactions"].empty


def test_unmatched_ingredient_reported_as_no_data(chk):
    res = chk.check([chk.resolve("Combo Tablet"), chk.resolve("Warf 5 Tablet")])
    assert "thiocolchicoside" in res["no_data"]["ingredient"].tolist()


def test_search_prefix_and_generic(chk):
    assert "Ecosprin 75 Tablet" in chk.search("ecos")
    assert "warfarin (generic)" in chk.search("warf")
    assert chk.search("a") == []


def test_search_finds_generic_by_alias():
    pairs = pd.DataFrame({"drug_a": ["acetaminophen"], "drug_b": ["warfarin"], "severity": ["Moderate"]})
    c = Checker(pairs, MEDS)
    assert "acetaminophen (generic)" in c.search("paracetamol")


def test_unknown_label_returns_none(chk):
    assert chk.resolve("Nonexistent Tablet") is None


def test_quiz_never_returns_unknown(chk):
    rng = np.random.default_rng(0)
    for _ in range(20):
        assert chk.quiz_question(rng)[2] in {"Major", "Moderate", "Minor"}
