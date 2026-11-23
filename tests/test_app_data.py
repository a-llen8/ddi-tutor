"""Pair lookup, Case simulator and random cases must work from data/app only."""
import os

import pytest

from ml.case_simulator import check_case, verify
from ml.lookup_predictions import (BANDS, BAND_DRUGS, APP_PAIRS, BandFile, covered_id_set,
                                   load_coverage, load_pairs_app, lookup, names_app)
import ml.random_case as rc

pytestmark = pytest.mark.skipif(
    not all(os.path.exists(f) for f in (BANDS, BAND_DRUGS, APP_PAIRS)),
    reason="app data files missing")


@pytest.fixture(scope="module")
def app():
    ids, sev = load_pairs_app()
    return ids, sev, BandFile()


def run(app, a, b):
    ids, sev, bands = app
    return lookup(a, b, ids, sev, bands)


@pytest.mark.parametrize("a,b,status,extra", [
    ("Abacavir", "Ixazomib", "predicted", "High"),
    ("Abacavir", "Ixabepilone", "predicted", "Medium"),
    ("Abacavir", "Ivosidenib", "predicted", "Low"),
    ("Warfarin", "Zidovudine", "documented", "Unknown"),
    ("Vasopressin", "Abacavir", "no_prediction", None),
    ("Aspirin", "Acetylsalicylic acid", "same_drug", None),
    ("Salicylic acid", "Warfarin", "ambiguous", None),
    ("Warfarine", "Zidovudine", "not_found", None),
])
def test_statuses_and_bands_from_app_files(app, a, b, status, extra):
    r = run(app, a, b)
    assert r["status"] == status
    if status == "predicted":
        assert r["band"] == extra
    if status == "documented":
        assert r["severity"] == extra


def test_no_score_ever_leaves_the_band_files(app):
    r = run(app, "Abacavir", "Ixazomib")
    assert "score_pct" not in r


def test_band_lookup_is_symmetric_and_unknown_names_give_none(app):
    bands = app[2]
    assert bands.find("abacavir", "ixazomib") == bands.find("ixazomib", "abacavir") == "High"
    assert bands.find("abacavir", "no such drug") is None
    assert bands.find("abacavir", "abacavir") is None


def test_two_uncovered_drugs_get_outside_files_from_app_files(app):
    ids, sev, bands = app
    cov = covered_id_set(ids, load_coverage())
    r = lookup("digoxin", "amiodarone", ids, sev, bands, cov)
    assert r["status"] == "outside_files"
    assert "band" not in r


def test_case_simulator_from_app_files(app):
    ids, sev, _ = app
    r = check_case(["Warfarin", "Metformin", "Simvastatin"], ids, sev, names_app(ids))
    assert r["status"] == "ok" and len(r["pairs"]) == 3
    import pandas as pd
    df = pd.read_csv(APP_PAIRS)
    df["drug_a"] = df["drug_a"].astype(str).str.strip().str.lower()
    df["drug_b"] = df["drug_b"].astype(str).str.strip().str.lower()
    assert verify(r, df) == 0


def test_random_cases_from_app_files():
    ctx = rc.load_context()
    assert len(ctx["pool"]) > 500
    for seed in range(30):
        names, _ = rc.random_case(ctx, seed)
        assert names is not None
        r = check_case(names, ctx["ids"], ctx["sev"], ctx["names_of"])
        assert r["counts"]["Major"] >= 1 and r["counts"]["no_record"] >= 1