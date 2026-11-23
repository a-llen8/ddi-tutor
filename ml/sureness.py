"""How sure the student was, turned into a scheduler grade."""
from ml.srs import review

# Grades follow ml/srs.py: 3 is hard, 4 is good, 5 is easy.
SURENESS = {"Not sure": 3, "Fairly sure": 4, "Certain": 5}


def grade_for(right, sureness):
    """A wrong answer is always grade 1, whatever the student picked."""
    if sureness not in SURENESS:
        raise ValueError("unknown sureness: " + str(sureness))
    return SURENESS[sureness] if right else 1


def answer(card, right, sureness, today):
    """Returns the card after one answer. A wrong answer given as Certain also adds one to
    sure_wrong. Cards from older progress files have no sure_wrong, which counts as 0."""
    new = review(card, grade_for(right, sureness), today)
    if not right and sureness == "Certain":
        new["sure_wrong"] = card.get("sure_wrong", 0) + 1
    return new