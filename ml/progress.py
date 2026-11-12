import json
import re
from datetime import date

from ml.srs import MIN_EASE, START_EASE

APP = "ddi-tutor"
VERSION = 1
MAX_TEXT = 2_000_000
MAX_CARDS = 5000
MAX_ERRORS = 10
FIELDS = {"card_id", "ease", "reps", "interval", "due", "seen", "wrong"}
ID_RE = re.compile(r"[A-Za-z0-9_.:-]{1,64}")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
TOP_KEYS = {"app", "version", "cards"}


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def validate_card(card):
    """Returns a list of problems. An empty list means the card is valid."""
    if not isinstance(card, dict):
        return ["not a card"]
    keys = set(card)
    if keys != FIELDS:
        out = []
        missing = sorted(FIELDS - keys)
        extra = sorted(str(k) for k in keys - FIELDS)
        if missing:
            out.append("missing fields: " + ", ".join(missing))
        if extra:
            out.append("unknown fields: " + ", ".join(extra))
        return out

    problems = []
    cid = card["card_id"]
    if not isinstance(cid, str) or not ID_RE.fullmatch(cid):
        problems.append("card_id must be 1 to 64 letters, digits or _ . : -")

    ints_ok = all(_is_int(card[k]) and card[k] >= 0 for k in ("reps", "interval", "seen", "wrong"))
    if not ints_ok:
        problems.append("reps, interval, seen and wrong must be whole numbers, 0 or more")

    ease = card["ease"]
    ease_ok = isinstance(ease, (int, float)) and not isinstance(ease, bool)
    if not ease_ok:
        problems.append("ease must be a number")

    due = card["due"]
    if not (isinstance(due, str) and DATE_RE.fullmatch(due)):
        problems.append("due must look like 2026-11-10")
    else:
        try:
            d = date.fromisoformat(due)
        except ValueError:
            problems.append("due is not a real date")
        else:
            if not 2000 <= d.year <= 2100:
                problems.append("due year is out of range")

    if ints_ok:
        if card["interval"] > 36500 or card["seen"] > 1_000_000:
            problems.append("interval or seen is too large")
        if card["reps"] + card["wrong"] > card["seen"]:
            problems.append("reps and wrong add up to more than seen")
        if ease_ok and not (MIN_EASE - 1e-6 <= ease <= START_EASE + 0.1 * card["seen"] + 1e-6):
            problems.append("ease is outside what the scheduler can produce")
    return problems


def parse_progress(text):
    """Returns (cards, errors). If errors is not empty, the file must not be used."""
    if not isinstance(text, str):
        return [], ["the file is not text"]
    if len(text) > MAX_TEXT:
        return [], ["the file is too large"]
    try:
        data = json.loads(text)
    except (ValueError, RecursionError):
        return [], ["the file is not valid JSON"]
    if not isinstance(data, dict) or set(data) != TOP_KEYS:
        return [], ["the file does not look like a DDI Tutor progress file"]
    if data["app"] != APP:
        return [], ["the file is not from DDI Tutor"]
    if type(data["version"]) is not int or data["version"] != VERSION:
        return [], ["unsupported file version"]
    cards = data["cards"]
    if not isinstance(cards, list):
        return [], ["the card list is missing"]
    if len(cards) > MAX_CARDS:
        return [], [f"too many cards (the limit is {MAX_CARDS})"]

    errors, seen_ids = [], set()
    for i, c in enumerate(cards, start=1):
        probs = validate_card(c)
        if not probs:
            if c["card_id"] in seen_ids:
                probs = ["duplicate card_id"]
            else:
                seen_ids.add(c["card_id"])
        for p in probs:
            errors.append(f"card {i}: {p}")
    if errors:
        more = len(errors) - MAX_ERRORS
        errors = errors[:MAX_ERRORS] + ([f"and {more} more problems"] if more > 0 else [])
        return [], errors
    return [dict(c) for c in cards], []


def export_progress(cards):
    """Returns the text of a progress file. Raises ValueError if any card is invalid."""
    cards = list(cards)
    if len(cards) > MAX_CARDS:
        raise ValueError("too many cards")
    ids = set()
    for c in cards:
        problems = validate_card(c)
        if problems:
            raise ValueError("invalid card: " + problems[0])
        if c["card_id"] in ids:
            raise ValueError("duplicate card_id")
        ids.add(c["card_id"])
    data = {"app": APP, "version": VERSION,
            "cards": sorted((dict(c) for c in cards), key=lambda c: c["card_id"])}
    return json.dumps(data, separators=(",", ":"))


def merge_cards(existing, incoming):
    """Card by card. The card with more answers seen wins. On a tie the existing card stays."""
    by_id = {c["card_id"]: dict(c) for c in existing}
    added = updated = kept = 0
    for c in incoming:
        old = by_id.get(c["card_id"])
        if old is None:
            by_id[c["card_id"]] = dict(c)
            added += 1
        elif c["seen"] > old["seen"]:
            by_id[c["card_id"]] = dict(c)
            updated += 1
        else:
            kept += 1
    merged = sorted(by_id.values(), key=lambda c: c["card_id"])
    return merged, {"added": added, "updated": updated, "kept": kept}


def import_progress(text, existing):
    """A bad file never changes existing progress. Returns a dict with ok, cards, errors and counts."""
    incoming, errors = parse_progress(text)
    if errors:
        return {"ok": False, "cards": list(existing), "errors": errors}
    merged, stats = merge_cards(existing, incoming)
    return {"ok": True, "cards": merged, "errors": [], **stats}