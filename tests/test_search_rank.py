"""Checker search order: generic prefix, brand prefix, generic contains, brand contains, typos."""
import pandas as pd

from pipeline.lookup import Checker


def make_checker():
    pairs = pd.DataFrame({
        "drug_a": ["nadolol", "pindolol", "acetaminophen"],
        "drug_b": ["warfarin", "warfarin", "warfarin"],
        "severity": ["Moderate", "Minor", "Moderate"],
    })
    brands = ["Dolo 650", "Dolo 500", "Parodolo"]
    meds = pd.DataFrame({
        "brand": brands,
        "ing1": ["paracetamol"] * 3,
        "ing1_dd": ["acetaminophen"] * 3,
        "ing2": [None] * 3,
        "ing2_dd": [None] * 3,
        "discontinued": [False] * 3,
    })
    return Checker(pairs, meds)


def test_dolo_first_result_is_a_dolo_brand():
    res = make_checker().search("dolo")
    assert res[0] == "Dolo 650"


def test_brand_prefix_ranks_above_generic_that_only_contains_the_text():
    res = make_checker().search("dolo")
    assert res.index("Dolo 500") < res.index("nadolol (generic)")


def test_generic_prefix_ranks_first():
    assert make_checker().search("nado")[0] == "nadolol (generic)"


def test_brand_that_only_contains_the_text_comes_after_generics_that_contain_it():
    res = make_checker().search("dolo")
    assert res.index("pindolol (generic)") < res.index("Parodolo")


def test_paracetamol_still_finds_acetaminophen():
    assert "acetaminophen (generic)" in make_checker().search("paracetamol")


def test_short_text_gives_nothing():
    assert make_checker().search("d") == []


def test_no_duplicates():
    res = make_checker().search("dolo")
    assert len(res) == len(set(res))


def test_generic_tag_is_kept_exactly():
    res = make_checker().search("warf")
    assert res[0] == "warfarin (generic)"