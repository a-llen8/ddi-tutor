"""How sure: grades, the sure_wrong count, old progress files, and the dashboard."""
import json
from datetime import date

import pytest

from ml.dashboard import build_dashboard
from ml.progress import export_progress, import_progress, parse_progress, validate_card
from ml.srs import new_card, review
from ml.sureness import SURENESS, answer, grade_for

TODAY = date(2026, 11, 23)


def fresh():
    return new_card("severity-major:a-b-12345678", TODAY)


def test_the_three_grades():
    assert SURENESS == {"Not sure": 3, "Fairly sure": 4, "Certain": 5}


def test_unknown_sureness_is_refused():
    with pytest.raises(ValueError):
        grade_for(True, "Very")


def test_certain_and_right_raises_ease_above_start():
    assert answer(fresh(), True, "Certain", TODAY)["ease"] > 2.5


def test_not_sure_and_right_lowers_ease_below_start():
    assert answer(fresh(), True, "Not sure", TODAY)["ease"] < 2.5


def test_fairly_sure_and_right_leaves_ease_alone():
    assert answer(fresh(), True, "Fairly sure", TODAY)["ease"] == 2.5


@pytest.mark.parametrize("sureness", list(SURENESS))
def test_a_wrong_answer_is_grade_1_whatever_was_picked(sureness):
    assert grade_for(False, sureness) == 1
    c = answer(fresh(), False, sureness, TODAY)
    assert (c["ease"], c["reps"], c["interval"], c["wrong"], c["seen"]) == (2.5, 0, 1, 1, 1)


def test_only_a_certain_wrong_answer_counts_as_sure_but_wrong():
    assert answer(fresh(), False, "Certain", TODAY)["sure_wrong"] == 1
    assert "sure_wrong" not in answer(fresh(), False, "Fairly sure", TODAY)
    assert "sure_wrong" not in answer(fresh(), False, "Not sure", TODAY)
    assert "sure_wrong" not in answer(fresh(), True, "Certain", TODAY)


def test_sure_wrong_adds_up_and_is_kept_by_later_answers():
    c = answer(fresh(), False, "Certain", TODAY)
    c = answer(c, False, "Certain", TODAY)
    c = answer(c, True, "Fairly sure", TODAY)
    assert c["sure_wrong"] == 2


def test_certain_answers_change_the_interval_from_the_third_review():
    fixed, sure = fresh(), fresh()
    for _ in range(3):
        fixed = review(fixed, 4, TODAY)
        sure = answer(sure, True, "Certain", TODAY)
    assert fixed["interval"] == 15
    assert sure["interval"] > fixed["interval"]


def test_a_card_after_many_certain_answers_is_still_valid():
    c = fresh()
    for _ in range(8):
        c = answer(c, True, "Certain", TODAY)
    assert validate_card(c) == []


def test_an_old_progress_file_without_the_field_still_imports():
    text = json.dumps({"app": "ddi-tutor", "version": 1, "cards": [fresh()]})
    res = import_progress(text, [])
    assert res["ok"] and res["added"] == 1


def test_a_card_with_sure_wrong_survives_export_and_import():
    c = answer(fresh(), False, "Certain", TODAY)
    cards, errors = parse_progress(export_progress([c]))
    assert errors == []
    assert cards == [c]


@pytest.mark.parametrize("value", [-1, 1.5, "1", True, None])
def test_a_bad_sure_wrong_is_refused(value):
    c = answer(fresh(), False, "Certain", TODAY)
    c["sure_wrong"] = value
    assert validate_card(c)


def test_sure_wrong_cannot_be_more_than_wrong():
    c = answer(fresh(), False, "Certain", TODAY)
    c["sure_wrong"] = 2
    assert "sure_wrong is more than wrong" in validate_card(c)


def test_other_unknown_fields_are_still_refused():
    c = fresh()
    c["extra"] = 1
    assert "unknown fields: extra" in validate_card(c)


def test_missing_required_fields_are_still_reported():
    c = fresh()
    del c["due"]
    assert "missing fields: due" in validate_card(c)


def test_dashboard_adds_up_sure_wrong_and_old_cards_count_as_zero():
    rows = build_dashboard([answer(fresh(), False, "Certain", TODAY), fresh()])
    assert len(rows) == 1
    assert rows[0]["sure_wrong"] == 1