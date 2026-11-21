"""A pair of two uncovered drugs must get no band, only the outside-files message."""
import sqlite3

import pytest

from ml.lookup_predictions import covered_id_set, decide, lookup

IDS = {"digoxin": {"D1"}, "amiodarone": {"D2"}, "warfarin": {"D3"}}
SEV = {frozenset(("D3", "D2")): "Major"}
COVERAGE = {"digoxin": False, "amiodarone": False, "warfarin": True}


@pytest.fixture
def con():
    """Every drug has a row and every pair has a band, so a band is always available."""
    c = sqlite3.connect(":memory:")
    c.execute("create table drugs (drug_id text, idx integer)")
    c.execute("create table predictions (drug_a integer, drug_b integer, "
              "score_pct integer, band text)")
    c.executemany("insert into drugs values (?,?)",
                  [("D1", 0), ("D2", 1), ("D3", 2)])
    c.executemany("insert into predictions values (?,?,?,?)",
                  [(0, 1, 91, "High"), (0, 2, 44, "Medium"), (1, 2, 20, "Low")])
    return c


def test_covered_id_set():
    assert covered_id_set(IDS, COVERAGE) == {"D3"}


def test_unknown_name_counts_as_covered():
    assert covered_id_set({"mystery": {"D9"}}, {}) == {"D9"}


def test_two_uncovered_drugs_get_no_band(con):
    covered = covered_id_set(IDS, COVERAGE)
    r = decide({"D1"}, {"D2"}, SEV, con, covered)
    assert r["status"] == "outside_files"
    assert "band" not in r
    assert "outside the 8 DDInter class files" in r["text"]


def test_one_covered_drug_still_gets_a_band(con):
    covered = covered_id_set(IDS, COVERAGE)
    r = decide({"D1"}, {"D3"}, SEV, con, covered)
    assert r["status"] == "predicted"
    assert r["band"] == "Medium"


def test_documented_pair_is_unaffected(con):
    covered = covered_id_set(IDS, COVERAGE)
    r = decide({"D3"}, {"D2"}, SEV, con, covered)
    assert r["status"] == "documented"
    assert r["severity"] == "Major"


def test_no_coverage_table_keeps_old_behaviour(con):
    r = decide({"D1"}, {"D2"}, SEV, con, None)
    assert r["status"] == "predicted"


def test_lookup_passes_coverage_through(con):
    covered = covered_id_set(IDS, COVERAGE)
    r = lookup("digoxin", "amiodarone", IDS, SEV, con, covered)
    assert r["status"] == "outside_files"