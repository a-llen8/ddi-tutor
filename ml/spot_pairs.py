def neutral_pairs(r):
    """Pairs of a checked case in alphabetical order, so the order gives no hint about severity."""
    out = []
    for p in r["pairs"]:
        a, b = sorted((p["drug_a"], p["drug_b"]), key=str.lower)
        out.append((a, b))
    return sorted(out, key=lambda t: (t[0].lower(), t[1].lower()))


def score_ticks(r, ticked):
    """r is the result of check_case. ticked is a set of frozenset((drug_a, drug_b)).
    Returns the Major pairs found and missed, and the ticked pairs that are not Major."""
    truth = {frozenset((p["drug_a"], p["drug_b"])): p["severity"] for p in r["pairs"]}
    found, missed, false_alarms = [], [], []
    for a, b in neutral_pairs(r):
        key = frozenset((a, b))
        sev = truth[key]
        label = f"{a} + {b}"
        if sev == "Major":
            (found if key in ticked else missed).append(label)
        elif key in ticked:
            false_alarms.append(f"{label} ({sev or 'no record'})")
    return {"n_major": len(found) + len(missed), "found": found,
            "missed": missed, "false_alarms": false_alarms}