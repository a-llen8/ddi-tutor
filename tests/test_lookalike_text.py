from ml.lookalike import format_lines


IDS = ["d1", "d2", "d3", "d4"]
NAMES = {"d1": "Abacavir", "d2": "Nelarabine", "d3": "Ixazomib", "d4": "Entecavir"}


def found(like_a, like_b, documented):
    return {"like_a": like_a, "like_b": like_b, "documented": documented}


def test_same_drug_and_closest_drug_in_words():
    out = format_lines([found(1, 2, True)], IDS, NAMES, 0, 2, "Abacavir", "Ixazomib")
    assert out["n"] == 1 and out["n_documented"] == 1
    line = out["lines"][0]
    assert line.startswith("Nelarabine + Ixazomib: listed in DDInter.")
    assert "closest to Abacavir: Nelarabine" in line
    assert "Ixazomib is the same drug" in line


def test_no_record_pair_is_labelled():
    out = format_lines([found(3, 2, False)], IDS, NAMES, 0, 2, "Abacavir", "Ixazomib")
    assert out["n_documented"] == 0
    assert "no record in DDInter" in out["lines"][0]


def test_no_numbers_in_lines():
    out = format_lines([found(1, 2, True), found(3, 2, False)], IDS, NAMES, 0, 2, "Abacavir", "Ixazomib")
    for line in out["lines"]:
        assert not any(ch.isdigit() for ch in line)
