"""Flashcards: the common-drugs deck is the default, switching decks works,
and a card from outside the chosen deck is not shown."""
from pathlib import Path

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from ml.common_deck import common_drugs

APP = str(Path(__file__).resolve().parent.parent / "app.py")
COMMON = common_drugs(pd.read_csv("data/app/medicines.csv.gz"))


def start(deck=None, seed=1):
    at = AppTest.from_file(APP, default_timeout=120)
    at.session_state["main_tabs"] = "Flashcards"
    at.session_state["fc_cards"] = {}
    at.session_state["fc_current"] = None
    at.session_state["fc_result"] = None
    at.session_state["fc_rng"] = np.random.default_rng(seed)
    if deck:
        at.session_state["fc_deck"] = deck
    return at.run()


def current_pair(at):
    """Drugs of the card on screen, read from the subheader."""
    names = at.subheader[0].value.lower().split("  +  ")
    return names[0], names[1]


def test_common_drugs_is_the_default_deck_and_cards_come_from_it():
    for seed in range(8):
        at = start(seed=seed)
        assert not at.exception
        assert at.radio(key="fc_deck").value == "Common drugs"
        a, b = current_pair(at)
        assert a in COMMON and b in COMMON


def test_all_graded_pairs_deck_draws_beyond_the_common_list():
    outside = 0
    for seed in range(8):
        at = start("All graded pairs", seed)
        assert not at.exception
        a, b = current_pair(at)
        outside += not (a in COMMON and b in COMMON)
    assert outside >= 1


def test_switching_deck_hides_a_due_card_that_is_outside_it():
    for seed in range(12):
        at = start("All graded pairs", seed)
        a, b = current_pair(at)
        if a in COMMON and b in COMMON:
            continue
        old_id = at.session_state["fc_current"]
        at.radio(key="fc_deck").set_value("Common drugs").run()
        assert not at.exception
        new_id = at.session_state["fc_current"]
        assert new_id != old_id
        a2, b2 = current_pair(at)
        assert a2 in COMMON and b2 in COMMON
        assert old_id in at.session_state["fc_cards"]
        return
    raise AssertionError("no card outside the common deck was drawn")


def test_deck_choice_survives_leaving_the_tab():
    at = start("All graded pairs")
    at.session_state["main_tabs"] = "Quiz"
    at.run()
    at.session_state["main_tabs"] = "Flashcards"
    at.run()
    assert at.radio(key="fc_deck").value == "All graded pairs"