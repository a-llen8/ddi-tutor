from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")

TABS = ["Interaction checker", "Pair lookup", "Case simulator",
        "Flashcards", "Quiz", "About & limits"]


def run(tab=None):
    at = AppTest.from_file(APP, default_timeout=120)
    if tab:
        at.session_state["main_tabs"] = tab
    return at.run()


def test_no_flashcard_is_made_on_load():
    at = run()
    assert not at.exception
    assert "fc_cards" not in at.session_state


def test_flashcard_is_made_when_the_tab_is_opened():
    at = run("Flashcards")
    assert not at.exception
    assert len(at.session_state["fc_cards"]) == 1


def test_every_tab_opens_without_error():
    for tab in TABS:
        assert not run(tab).exception, tab