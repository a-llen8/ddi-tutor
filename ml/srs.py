import math
from datetime import timedelta

START_EASE = 2.5
MIN_EASE = 1.3


def new_card(card_id, today):
    """A card nobody has answered yet. Due today. A plain dictionary, safe to save as JSON."""
    return {"card_id": card_id, "ease": START_EASE, "reps": 0, "interval": 0,
            "due": today.isoformat(), "seen": 0, "wrong": 0}


def review(card, grade, today):
    """Returns a new card after one answer. today is a date. grade is a whole number 0 to 5.
    0 to 2 is wrong. 3 is hard, 4 is good, 5 is easy.
    A wrong answer starts the card again at 1 day and leaves the ease unchanged."""
    if isinstance(grade, bool) or not isinstance(grade, int) or not 0 <= grade <= 5:
        raise ValueError("grade must be a whole number from 0 to 5")
    c = dict(card)
    c["seen"] += 1
    if grade < 3:
        c["reps"] = 0
        c["interval"] = 1
        c["wrong"] += 1
    else:
        if c["reps"] == 0:
            interval = 1
        elif c["reps"] == 1:
            interval = 6
        else:
            interval = max(1, math.floor(c["interval"] * c["ease"] + 0.5))
        c["interval"] = interval
        c["reps"] += 1
        d = 5 - grade
        c["ease"] = round(max(MIN_EASE, c["ease"] + 0.1 - d * (0.08 + d * 0.02)), 4)
    c["due"] = (today + timedelta(days=c["interval"])).isoformat()
    return c


def due_cards(cards, today, limit=None):
    """Cards due on or before today, the most overdue first. limit caps how many are returned."""
    t = today.isoformat()
    due = sorted((c for c in cards if c["due"] <= t), key=lambda c: (c["due"], c["card_id"]))
    return due if limit is None else due[:limit]