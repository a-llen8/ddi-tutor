from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def test_pair_lookup_boxes_keep_their_text_when_the_tab_is_left():
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["main_tabs"] = "Pair lookup"
    at.run()
    at.text_input(key="lk_a").set_value("abacavir")
    at.text_input(key="lk_b").set_value("ixazomib")
    at.run()
    at.session_state["main_tabs"] = "Flashcards"
    at.run()
    at.session_state["main_tabs"] = "Pair lookup"
    at.run()
    assert at.text_input(key="lk_a").value == "abacavir"
    assert at.text_input(key="lk_b").value == "ixazomib"