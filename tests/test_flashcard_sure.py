"""Flashcards: the How sure? choice is needed, and it reaches the scheduler and the table."""
from pathlib import Path

import numpy as np
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def start(seed=1):
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["main_tabs"] = "Flashcards"
    at.session_state["fc_cards"] = {}
    at.session_state["fc_current"] = None
    at.session_state["fc_result"] = None
    at.session_state["fc_rng"] = np.random.default_rng(seed)
    return at.run()


def truth_of(cid):
    return cid.split(":")[0].replace("severity-", "").capitalize()


def answer_card(at, guess, sure):
    cid = at.session_state["fc_current"]
    at.radio(key=f"fc_guess_{cid}").set_value(guess)
    at.radio(key=f"fc_sure_{cid}").set_value(sure)
    at.run()
    at.button(key="fc_check").click().run()
    return cid


def test_check_answer_needs_both_a_severity_and_a_sureness():
    at = start()
    assert not at.exception
    cid = at.session_state["fc_current"]
    assert at.button(key="fc_check").disabled
    at.radio(key=f"fc_guess_{cid}").set_value("Major").run()
    assert at.button(key="fc_check").disabled
    at.radio(key=f"fc_sure_{cid}").set_value("Certain").run()
    assert not at.button(key="fc_check").disabled


def test_nothing_is_preselected():
    at = start()
    cid = at.session_state["fc_current"]
    assert at.radio(key=f"fc_sure_{cid}").value is None
    assert at.radio(key=f"fc_sure_{cid}").options == ["Not sure", "Fairly sure", "Certain"]


def test_certain_and_right_raises_the_ease_on_the_card():
    at = start()
    cid = at.session_state["fc_current"]
    answer_card(at, truth_of(cid), "Certain")
    card = at.session_state["fc_cards"][cid]
    assert card["ease"] > 2.5
    assert "sure_wrong" not in card


def test_not_sure_and_right_lowers_the_ease_on_the_card():
    at = start()
    cid = at.session_state["fc_current"]
    answer_card(at, truth_of(cid), "Not sure")
    assert at.session_state["fc_cards"][cid]["ease"] < 2.5


def test_certain_and_wrong_is_counted_and_shown_in_the_table():
    at = start()
    cid = at.session_state["fc_current"]
    wrong = next(x for x in ("Major", "Moderate", "Minor") if x != truth_of(cid))
    answer_card(at, wrong, "Certain")
    card = at.session_state["fc_cards"][cid]
    assert card["sure_wrong"] == 1
    assert card["ease"] == 2.5
    assert any("sure but wrong" in c.value for c in at.caption)
    table = at.dataframe[0].value
    assert "sure but wrong" in table.columns
    assert int(table["sure but wrong"].sum()) == 1