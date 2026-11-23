"""Look and feel: styles, the learning-only notice and severity pills.
No Streamlit code here, so everything can be tested on its own."""
import html

SEVERITY_WORDS = {"Major": "Major", "Moderate": "Moderate", "Minor": "Minor",
                  "Unknown": "Listed, not graded"}

# Only our own class names are styled. A pill carries its own background and white text,
# so it reads the same in light and dark mode. The word is always printed, colour is extra.
CSS = """
.ddi-notice{border-left:4px solid #0f766e;border-radius:6px;padding:.55rem .9rem;
margin:.2rem 0 1rem 0;background:rgba(15,118,110,.12);font-size:.92rem}
.ddi-pill{display:inline-block;padding:.12rem .7rem;border-radius:999px;color:#fff;
font-weight:600;font-size:.85rem;margin:0 .35rem .25rem 0}
.ddi-major{background:#b91c1c}
.ddi-moderate{background:#c2410c}
.ddi-minor{background:#8a5a00}
.ddi-unknown{background:#475569}
"""

NOTICE = ("<b>Learning only.</b> Not for treating patients. \"No record\" means not documented "
          "in the 8 DDInter files used here. It never means safe.")


def severity_pill(severity):
    if severity not in SEVERITY_WORDS:
        raise ValueError("unknown severity: " + str(severity))
    return (f'<span class="ddi-pill ddi-{severity.lower()}">'
            f'{html.escape(SEVERITY_WORDS[severity])}</span>')


def severity_summary(severities):
    """One pill per level present, with how many. For example: Major 2  Moderate 5."""
    counts = {}
    for s in severities:
        counts[s] = counts.get(s, 0) + 1
    parts = []
    for level in ("Major", "Moderate", "Minor", "Unknown"):
        if counts.get(level):
            parts.append(severity_pill(level) + f"{counts[level]}&nbsp;&nbsp;")
    return "".join(parts)