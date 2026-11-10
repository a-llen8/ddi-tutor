import json
from datetime import date, timedelta

import pytest

from ml.srs import due_cards, new_card, review

START = date(2026, 11, 10)


def run(grades):
    card = new_card("q1", START)
    day = START
    out = []
    for g in grades:
        card = review(card, g, day)
        out.append((card["interval"], card["ease"]))
        day = date.fromisoformat(card["due"])
    return card, out


def test_new_card():
    c = new_card("q1", START)
    assert c == {"card_id": "q1", "ease": 2.5, "reps": 0, "interval": 0,
                 "due": "2026-11-10", "seen": 0, "wrong": 0}


def test_good_answers():
    card, out = run([4, 4, 4, 4])
    assert [i for i, _ in out] == [1, 6, 15, 38]
    assert card["ease"] == 2.5
    assert card["due"] == (START + timedelta(days=1 + 6 + 15 + 38)).isoformat()


def test_easy_answers():
    card, out = run([5, 5, 5])
    assert [i for i, _ in out] == [1, 6, 16]
    assert card["ease"] == pytest.approx(2.8)


def test_hard_answers():
    card, out = run([3, 3, 3, 3])
    assert [i for i, _ in out] == [1, 6, 13, 27]
    assert card["ease"] == pytest.approx(1.94)


def test_ease_never_below_floor():
    card, _ = run([3] * 10)
    assert card["ease"] == pytest.approx(1.3)


def test_wrong_answer_restarts():
    card, _ = run([4, 4, 4])
    assert card["interval"] == 15 and card["reps"] == 3
    day = date.fromisoformat(card["due"])
    card = review(card, 0, day)
    assert card["reps"] == 0 and card["interval"] == 1
    assert card["ease"] == 2.5
    assert card["wrong"] == 1 and card["seen"] == 4
    assert card["due"] == (day + timedelta(days=1)).isoformat()
    card = review(card, 4, date.fromisoformat(card["due"]))
    assert card["interval"] == 1 and card["reps"] == 1


def test_review_does_not_change_input():
    c = new_card("q1", START)
    before = dict(c)
    review(c, 4, START)
    assert c == before


@pytest.mark.parametrize("bad", [-1, 6, 4.0, "4", True, None])
def test_bad_grade(bad):
    with pytest.raises(ValueError):
        review(new_card("q1", START), bad, START)


def test_due_cards():
    a = new_card("a", START)
    b = review(new_card("b", START), 4, START)
    c = new_card("c", START - timedelta(days=3))
    got = due_cards([a, b, c], START)
    assert [x["card_id"] for x in got] == ["c", "a"]
    assert [x["card_id"] for x in due_cards([a, b, c], START, limit=1)] == ["c"]
    assert [x["card_id"] for x in due_cards([a, b, c], START + timedelta(days=1))] == ["c", "a", "b"]


def test_json_round_trip():
    card, _ = run([4, 5, 0])
    assert json.loads(json.dumps(card)) == card