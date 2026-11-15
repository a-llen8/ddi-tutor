import pandas as pd
import pytest

from pipeline.lookup import Checker

PAIRS = pd.DataFrame({
    "drug_a": ["aspirin", "warfarin", "metformin"],
    "drug_b": ["warfarin", "fluconazole", "alcohol"],
    "severity": ["Major", "Moderate", "Unknown"],
})
MEDS = pd.DataFrame({
    "brand": ["Ecosprin 75 Tablet", "Warf 5 Tablet", "Glycomet 500 Tablet",
              "Combo Tablet", "Odd Tablet"],
    "ing1": ["aspirin", "warfarin", "metformin", "aspirin", "zzz"],
    "ing1_dd": ["aspirin", "warfarin", "metformin", "aspirin", None],
    "ing2": [None, None, None, "thiocolchicoside", None],
    "ing2_dd": [None, None, None, None, None],
    "discontinued": [False] * 5,
})


@pytest.fixture
def chk():
    return Checker(PAIRS, MEDS)


def items(chk, *names):
    return [chk.resolve(n) for n in names]


def test_pair_without_record_is_listed(chk):
    res = chk.check(items(chk, "Warf 5 Tablet", "Glycomet 500 Tablet"))
    assert res["interactions"].empty
    assert len(res["no_record"]) == 1
    assert res["no_record"].loc[0, "item_1"] == "Warf 5 Tablet"
    assert res["no_record"].loc[0, "item_2"] == "Glycomet 500 Tablet"


def test_documented_pair_is_not_listed(chk):
    res = chk.check(items(chk, "Warf 5 Tablet", "Ecosprin 75 Tablet"))
    assert len(res["interactions"]) == 1
    assert res["no_record"].empty


def test_three_items_mix(chk):
    res = chk.check(items(chk, "Warf 5 Tablet", "Ecosprin 75 Tablet", "Glycomet 500 Tablet"))
    assert len(res["interactions"]) == 1
    assert len(res["no_record"]) == 2


def test_shared_ingredient_is_not_no_record(chk):
    res = chk.check(items(chk, "Ecosprin 75 Tablet", "Combo Tablet"))
    assert res["no_record"].empty
    assert len(res["duplicates"]) == 1


def test_unchecked_item_is_not_no_record(chk):
    res = chk.check(items(chk, "Odd Tablet", "Warf 5 Tablet"))
    assert res["no_record"].empty
    assert len(res["no_data"]) == 1


def test_no_record_has_expected_columns(chk):
    res = chk.check(items(chk, "Warf 5 Tablet", "Ecosprin 75 Tablet"))
    assert list(res["no_record"].columns) == ["item_1", "item_2"]