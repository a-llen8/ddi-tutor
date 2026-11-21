import pandas as pd

from pipeline.coverage import (build_table, covered_ids, id_names,
                               pairs_both_uncovered, partners_per_file)


def frame(rows):
    return pd.DataFrame(rows, columns=["DDInterID_A", "Drug_A", "DDInterID_B", "Drug_B"])


# class X owns d1 and d2; d3 and d4 belong to a class with no file
FILE_X = frame([("d1", "Aaa", "d3", "Ccc"), ("d1", "Aaa", "d4", "Ddd"), ("d2", "Bbb", "d3", "Ccc")])
FILE_Y = frame([("d2", "Bbb", "d5", "Eee")])
FRAMES = [("X", FILE_X), ("Y", FILE_Y)]


def run():
    per = partners_per_file(FRAMES)
    ids, cov = covered_ids(per)
    return per, ids, cov


def test_partners_are_symmetric():
    per, _, _ = run()
    assert per["X"]["d3"] == {"d1", "d2"}
    assert per["X"]["d1"] == {"d3", "d4"}


def test_all_ids_found():
    _, ids, _ = run()
    assert ids == {"d1", "d2", "d3", "d4", "d5"}


def test_drug_with_all_pairs_in_one_file_is_covered():
    _, _, cov = run()
    assert "d1" in cov


def test_drug_split_over_two_files_is_not_covered():
    _, _, cov = run()
    assert "d2" not in cov


def test_known_limit_drug_seen_in_one_file_only_counts_as_covered():
    # d4 is from a missing class but all its partners sit in one file, so the
    # rule cannot tell. The real data decides how often this happens.
    _, _, cov = run()
    assert "d4" in cov


def test_uncovered_drug_with_partners_in_two_files():
    frames = [("X", frame([("d1", "A", "d3", "C")])), ("Y", frame([("d2", "B", "d3", "C")]))]
    _, cov = covered_ids(partners_per_file(frames))
    assert "d3" not in cov
    assert {"d1", "d2"} <= cov


def test_duplicate_rows_change_nothing():
    twice = [("X", pd.concat([FILE_X, FILE_X], ignore_index=True)), ("Y", FILE_Y)]
    assert covered_ids(partners_per_file(twice))[1] == run()[2]


def test_reversed_pair_order_changes_nothing():
    flipped = FILE_X.rename(columns={"DDInterID_A": "DDInterID_B", "DDInterID_B": "DDInterID_A",
                                     "Drug_A": "Drug_B", "Drug_B": "Drug_A"})
    got = covered_ids(partners_per_file([("X", flipped), ("Y", FILE_Y)]))[1]
    assert got == run()[2]


def test_names_are_lowercase_and_stripped():
    f = frame([("d1", " Aaa ", "d2", "BBB")])
    n = id_names([("X", f)])
    assert n["d1"] == {"aaa"} and n["d2"] == {"bbb"}


def test_table_has_one_row_per_name():
    _, ids, cov = run()
    t = build_table(ids, cov, id_names(FRAMES))
    assert list(t.columns) == ["drug", "covered"]
    assert len(t) == 5 and t["drug"].is_unique


def test_table_values():
    _, ids, cov = run()
    t = build_table(ids, cov, id_names(FRAMES)).set_index("drug")["covered"]
    assert bool(t["aaa"]) is True
    assert bool(t["bbb"]) is False


def test_name_with_two_ids_needs_both_covered():
    t = build_table({"i1", "i2"}, {"i1"}, {"i1": {"same"}, "i2": {"same"}})
    assert bool(t.iloc[0]["covered"]) is False


def test_no_documented_pair_has_two_uncovered_drugs():
    _, _, cov = run()
    bad, n = pairs_both_uncovered(FRAMES, cov)
    assert bad == 0 and n == 4