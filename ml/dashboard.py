MIN_SEEN = 5


def topic_of(card_id):
    if ":" in card_id:
        head = card_id.split(":", 1)[0]
        if head:
            return head
    return "other"


def build_dashboard(cards, min_seen=MIN_SEEN):
    totals = {}
    for c in cards:
        t = topic_of(c["card_id"])
        row = totals.setdefault(t, {"topic": t, "cards": 0, "seen": 0, "wrong": 0})
        row["cards"] += 1
        row["seen"] += c["seen"]
        row["wrong"] += c["wrong"]

    ranked = []
    too_few = []
    for row in totals.values():
        if row["seen"] >= min_seen:
            row["wrong_rate"] = row["wrong"] / row["seen"]
            ranked.append(row)
        else:
            row["wrong_rate"] = None
            too_few.append(row)

    ranked.sort(key=lambda r: (-r["wrong_rate"], r["topic"]))
    too_few.sort(key=lambda r: r["topic"])
    return ranked + too_few


def format_dashboard(rows):
    if not rows:
        return "No cards yet."
    lines = ["topic | cards | seen | wrong | wrong rate"]
    for r in rows:
        if r["wrong_rate"] is None:
            rate = "not enough data"
        else:
            rate = str(round(100 * r["wrong_rate"])) + "%"
        lines.append(" | ".join([r["topic"], str(r["cards"]), str(r["seen"]),
                                 str(r["wrong"]), rate]))
    return "\n".join(lines)