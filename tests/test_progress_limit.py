from datetime import date
from pathlib import Path

import numpy as np
from streamlit.testing.v1 import AppTest

from ml.progress import MAX_CARDS
from ml.srs import new_card

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def run_with_cards(n):
    at = AppTest.from_file(APP, default_timeout=120)
    today = date.today()
    at.session_state["fc_cards"] = {f"c{i}": new_card(f"c{i}", today) for i in range(n)}
    at.session_state["fc_current"] = None
    at.session_state["fc_result"] = None
    at.session_state["fc_rng"] = np.random.default_rng(0)
    at.session_state["main_tabs"] = "Flashcards"
    return at.run()


def test_too_many_cards_shows_a_message_not_a_crash():
    at = run_with_cards(MAX_CARDS + 1)
    assert not at.exception
    texts = [w.value for w in at.warning]
    assert any("cannot be downloaded" in t and str(MAX_CARDS) in t for t in texts)


def test_a_normal_number_of_cards_shows_no_warning():
    at = run_with_cards(3)
    assert not at.exception
    assert not any("cannot be downloaded" in w.value for w in at.warning)