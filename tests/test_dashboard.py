from ml.dashboard import topic_of, build_dashboard, format_dashboard


def card(cid, seen, wrong):
    return {"card_id": cid, "ease": 2.5, "reps": 0, "interval": 0,
            "due": "2026-11-12", "seen": seen, "wrong": wrong}


def test_topic_of_prefix():
    assert topic_of("severity:warfarin-zidovudine") == "severity"


def test_topic_of_no_colon():
    assert topic_of("abc123") == "other"


def test_topic_of_empty_prefix():
    assert topic_of(":abc") == "other"


def test_only_first_colon_splits():
    assert topic_of("pair:a:b") == "pair"


def test_sums_per_topic():
    rows = build_dashboard([card("brand:a", 4, 1), card("brand:b", 6, 3)])
    assert len(rows) == 1
    assert rows[0]["cards"] == 2
    assert rows[0]["seen"] == 10
    assert rows[0]["wrong"] == 4
    assert rows[0]["wrong_rate"] == 0.4


def test_worst_first():
    rows = build_dashboard([card("brand:a", 10, 2), card("severity:a", 10, 7)])
    assert [r["topic"] for r in rows] == ["severity", "brand"]


def test_too_few_goes_last_and_unranked():
    rows = build_dashboard([card("case:a", 2, 2), card("brand:a", 10, 1)])
    assert [r["topic"] for r in rows] == ["brand", "case"]
    assert rows[1]["wrong_rate"] is None


def test_min_seen_is_adjustable():
    rows = build_dashboard([card("case:a", 2, 2)], min_seen=2)
    assert rows[0]["wrong_rate"] == 1.0


def test_tie_sorted_by_topic_name():
    rows = build_dashboard([card("pair:a", 10, 5), card("brand:a", 10, 5)])
    assert [r["topic"] for r in rows] == ["brand", "pair"]


def test_empty_cards():
    assert build_dashboard([]) == []
    assert format_dashboard([]) == "No cards yet."


def test_format_shows_not_enough_data():
    text = format_dashboard(build_dashboard([card("case:a", 1, 1)]))
    assert "not enough data" in text


def test_format_shows_percent():
    text = format_dashboard(build_dashboard([card("brand:a", 10, 3)]))
    assert "30%" in text