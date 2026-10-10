import pandas as pd
from pipeline.names import clean, to_ddinter, build_table
from pipeline.names import clean, to_ddinter

NAMES = {"acetaminophen", "amoxicillin", "metoprolol", "sodium bicarbonate"}


def test_clean_removes_strength_and_spaces():
    assert clean("Azithromycin  (500mg)") == "azithromycin"
    assert clean(None) is None


def test_synonym_and_salt():
    assert to_ddinter("paracetamol", NAMES) == "acetaminophen"
    assert to_ddinter("metoprolol succinate", NAMES) == "metoprolol"


def test_protected_and_unknown():
    assert to_ddinter("sodium bicarbonate", NAMES) == "sodium bicarbonate"
    assert to_ddinter("thiocolchicoside", NAMES) is None

def test_build_table_handles_missing_second_ingredient():
    kg = pd.DataFrame({
        "id": [1], "name": ["X"], "Is_discontinued": [False],
        "short_composition1": ["Paracetamol (500mg)"],
        "short_composition2": [None],
    })
    t = build_table(kg, NAMES)
    assert t.loc[0, "ing1_dd"] == "acetaminophen"
    assert pd.isna(t.loc[0, "ing2_dd"])

def test_new_synonyms():
    names = {"beclomethasone dipropionate", "pyridoxine"}
    assert to_ddinter("beclometasone", names) == "beclomethasone dipropionate"
    assert to_ddinter("beclometasone dipropionate", names) == "beclomethasone dipropionate"
    assert to_ddinter("vitamin b6", names) == "pyridoxine"