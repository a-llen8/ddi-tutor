import json
from datetime import date

import pytest

from ml.progress import (MAX_CARDS, export_progress, import_progress, merge_cards,
                         parse_progress)
from ml.srs import new_card, review

TODAY = date(2026, 11, 10)


def card(cid, seen=0):
    c = new_card(cid, TODAY)
    for _ in range(seen):
        c = review(c, 4, TODAY)
    return c


def file_text(cards, **over):
    data = {"app": "ddi-tutor", "version": 1, "cards": cards}
    data.update(over)
    return json.dumps(data)


def test_round_trip():
    cards = [card("b", 2), card("a", 0), review(card("c", 3), 0, TODAY)]
    got, errors = parse_progress(export_progress(cards))
    assert errors == []
    assert got == sorted(cards, key=lambda c: c["card_id"])


def test_export_rejects_bad_card():
    bad = card("a")
    bad["ease"] = 99
    with pytest.raises(ValueError):
        export_progress([bad])


def test_export_rejects_duplicate_ids():
    with pytest.raises(ValueError):
        export_progress([card("a"), card("a")])


@pytest.mark.parametrize("text", ["", "not json", "[]", "null", "{}", None, 5, pytest.param("x" * 2_000_001, id="too_big")])
def test_bad_text(text):
    got, errors = parse_progress(text)
    assert got == [] and errors


def test_wrong_app_version_or_top_level():
    for text in (file_text([], app="other"), file_text([], version=2),
                 file_text([], version="1"), file_text([], version=True),
                 file_text([], extra=1)):
        got, errors = parse_progress(text)
        assert got == [] and errors


def test_missing_and_unknown_fields():
    c = card("a")
    del c["due"]
    assert any("missing" in e for e in parse_progress(file_text([c]))[1])
    c = card("a")
    c["note"] = "hi"
    assert any("unknown" in e for e in parse_progress(file_text([c]))[1])


@pytest.mark.parametrize("field,value", [
    ("card_id", "<script>"), ("card_id", ""), ("card_id", "a" * 65), ("card_id", 7),
    ("card_id", "a\n"),
    ("ease", 0.5), ("ease", "2.5"), ("ease", True), ("ease", 99),
    ("reps", -1), ("reps", 1.5),
    ("seen", True),
    ("wrong", "0"),
    ("interval", 40000),
    ("due", "20261110"), ("due", "2026-13-40"), ("due", "1999-01-01"), ("due", 5),
    ("due", "2026-11-10\n"),
])
def test_bad_values(field, value):
    c = card("a", 1)
    c[field] = value
    got, errors = parse_progress(file_text([c]))
    assert got == [] and errors


@pytest.mark.parametrize("literal", ["NaN", "Infinity", "-Infinity"])
def test_non_finite_ease(literal):
    text = ('{"app":"ddi-tutor","version":1,"cards":[{"card_id":"a","ease":%s,"reps":0,'
            '"interval":0,"due":"2026-11-10","seen":0,"wrong":0}]}' % literal)
    got, errors = parse_progress(text)
    assert got == [] and errors


def test_reps_and_wrong_cannot_exceed_seen():
    c = card("a", 1)
    c["wrong"] = 1
    got, errors = parse_progress(file_text([c]))
    assert got == [] and errors


def test_duplicate_ids_in_file():
    got, errors = parse_progress(file_text([card("a"), card("a")]))
    assert got == [] and errors


def test_too_many_cards():
    cards = [new_card(f"q{i}", TODAY) for i in range(MAX_CARDS + 1)]
    got, errors = parse_progress(file_text(cards))
    assert got == [] and errors


def test_error_list_is_capped():
    cards = [dict(card(f"q{i}"), ease=99) for i in range(50)]
    errors = parse_progress(file_text(cards))[1]
    assert len(errors) == 11 and errors[-1].startswith("and ")


def test_merge_rule():
    existing = [card("a", 3), card("c", 4), card("d", 6)]
    incoming = [card("a", 5), card("b", 1), card("c", 4), card("d", 2)]
    incoming[2]["due"] = "2030-01-01"
    merged, stats = merge_cards(existing, incoming)
    by = {c["card_id"]: c for c in merged}
    assert by["a"]["seen"] == 5
    assert by["b"]["seen"] == 1
    assert by["c"]["due"] == existing[1]["due"]
    assert by["d"]["seen"] == 6
    assert stats == {"added": 1, "updated": 1, "kept": 2}
    assert [c["card_id"] for c in merged] == ["a", "b", "c", "d"]


def test_merge_does_not_change_inputs():
    existing = [card("a", 3)]
    incoming = [card("a", 5)]
    before = json.dumps([existing, incoming])
    merge_cards(existing, incoming)
    assert json.dumps([existing, incoming]) == before


def test_bad_file_changes_nothing():
    existing = [card("a", 2)]
    before = json.dumps(existing)
    res = import_progress("garbage", existing)
    assert res["ok"] is False and res["errors"]
    assert res["cards"] == existing
    assert json.dumps(existing) == before


def test_import_good_file():
    existing = [card("a", 1)]
    text = export_progress([card("a", 3), card("b", 1)])
    res = import_progress(text, existing)
    assert res["ok"] and res["errors"] == []
    assert {c["card_id"]: c["seen"] for c in res["cards"]} == {"a": 3, "b": 1}
    assert (res["added"], res["updated"], res["kept"]) == (1, 1, 0)
