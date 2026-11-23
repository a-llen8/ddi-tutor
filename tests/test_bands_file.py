"""The committed band files: only bands, never scores, and the three known pairs are right."""
import os

import pandas as pd
import pytest

BANDS = "data/app/bands.csv.gz"
DRUGS = "data/app/band_drugs.csv.gz"

pytestmark = pytest.mark.skipif(
    not (os.path.exists(BANDS) and os.path.exists(DRUGS)),
    reason="band files not built yet")


@pytest.fixture(scope="module")
def files():
    bands = pd.read_csv(BANDS)
    drugs = pd.read_csv(DRUGS)["drug"].tolist()
    return bands, drugs


def band_of(files, x, y):
    bands, drugs = files
    pos = {d: i for i, d in enumerate(drugs)}
    a, b = sorted((pos[x], pos[y]))
    hit = bands[(bands["a"] == a) & (bands["b"] == b)]
    return None if hit.empty else int(hit["band"].iloc[0])


def test_only_the_three_columns_and_no_score(files):
    bands, _ = files
    assert list(bands.columns) == ["a", "b", "band"]


def test_band_holds_only_0_1_2(files):
    bands, _ = files
    assert set(bands["band"].unique()) <= {0, 1, 2}


def test_indexes_are_in_range(files):
    bands, drugs = files
    assert bands["a"].min() >= 0 and bands["b"].min() >= 0
    assert bands["a"].max() < len(drugs) and bands["b"].max() < len(drugs)


def test_a_is_less_than_b_on_every_row(files):
    bands, _ = files
    assert (bands["a"] < bands["b"]).all()


def test_no_pair_appears_twice(files):
    bands, _ = files
    assert not bands.duplicated(["a", "b"]).any()


def test_drug_list_is_lowercase_sorted_and_unique(files):
    _, drugs = files
    assert drugs == sorted(drugs)
    assert len(drugs) == len(set(drugs))
    assert all(d == d.strip().lower() for d in drugs)


def test_band_split_matches_the_database(files):
    bands, _ = files
    share = bands["band"].value_counts(normalize=True) * 100
    assert abs(share[0] - 64.6) < 0.3
    assert abs(share[1] - 27.2) < 0.3
    assert abs(share[2] - 8.2) < 0.3


def test_known_pairs_come_back_with_their_bands(files):
    assert band_of(files, "abacavir", "ixazomib") == 2       # High
    assert band_of(files, "abacavir", "ixabepilone") == 1    # Medium
    assert band_of(files, "abacavir", "ivosidenib") == 0     # Low


def test_order_of_the_two_names_does_not_matter(files):
    assert band_of(files, "ixazomib", "abacavir") == 2


def test_a_documented_pair_is_not_in_the_file(files):
    # DDInter lists abacavir + naltrexone, so it never gets a prediction
    _, drugs = files
    if "abacavir" in drugs and "naltrexone" in drugs:
        assert band_of(files, "abacavir", "naltrexone") is None