"""The notice at the top and the severity pills in the lookup and in Flashcards."""
from pathlib import Path

import numpy as np
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def page_html(at):
    return " ".join(m.value for m in at.markdown)


def test_every_page_shows_the_notice():
    at = AppTest.from_file(APP, default_timeout=120).run()
    assert not at.exception
    html = page_html(at)
    assert "Learning only" in html and "never means safe" in html


def test_pair_lookup_shows_a_severity_pill():
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["main_tabs"] = "Pair lookup"
    at.session_state["lk_a"] = "warfarin"
    at.session_state["lk_b"] = "amiodarone"
    at.run()
    assert not at.exception
    html = page_html(at)
    assert "ddi-pill" in html and "ddi-major" in html


def test_flashcard_answer_shows_a_pill_with_the_true_level():
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["main_tabs"] = "Flashcards"
    at.session_state["fc_cards"] = {}
    at.session_state["fc_current"] = None
    at.session_state["fc_result"] = None
    at.session_state["fc_rng"] = np.random.default_rng(1)
    at.run()
    assert "ddi-pill" not in page_html(at).replace("ddi-pill{", "")
    card = list(at.session_state["fc_cards"])[0]
    at.radio(key=f"fc_guess_{card}").set_value("Major").run()
    at.radio(key=f"fc_sure_{card}").set_value("Fairly sure").run()
    at.button(key="fc_check").click().run()
    assert not at.exception
    level = card.split(":")[0].split("-")[1]
    assert f"ddi-{level}" in page_html(at).replace("ddi-" + level + "{", "")