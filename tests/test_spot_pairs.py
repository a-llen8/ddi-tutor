from ml.spot_pairs import neutral_pairs, score_ticks

CASE = {"status": "ok", "pairs": [
    {"drug_a": "Warfarin", "drug_b": "Aspirin", "severity": "Major"},
    {"drug_a": "Aspirin", "drug_b": "Metformin", "severity": "Moderate"},
    {"drug_a": "Warfarin", "drug_b": "Metformin", "severity": None},
    {"drug_a": "Zinc", "drug_b": "Warfarin", "severity": "Major"},
]}


def key(a, b):
    return frozenset((a, b))


def test_order_is_alphabetical_not_by_severity():
    assert neutral_pairs(CASE) == [("Aspirin", "Metformin"), ("Aspirin", "Warfarin"),
                                   ("Metformin", "Warfarin"), ("Warfarin", "Zinc")]


def test_all_major_found():
    r = score_ticks(CASE, {key("Aspirin", "Warfarin"), key("Warfarin", "Zinc")})
    assert r["n_major"] == 2 and len(r["found"]) == 2
    assert r["missed"] == [] and r["false_alarms"] == []


def test_missed_and_false_alarm():
    r = score_ticks(CASE, {key("Aspirin", "Warfarin"), key("Metformin", "Warfarin")})
    assert r["found"] == ["Aspirin + Warfarin"]
    assert r["missed"] == ["Warfarin + Zinc"]
    assert r["false_alarms"] == ["Metformin + Warfarin (no record)"]


def test_nothing_ticked():
    r = score_ticks(CASE, set())
    assert r["found"] == [] and len(r["missed"]) == 2 and r["false_alarms"] == []