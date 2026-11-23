import html

import streamlit as st

BLUE = "#0a2a8f"
BLUE_DARK = "#061a5c"
BLUE_MID = "#2f55d4"
BLUE_SOFT = "#e8edff"
INK = "#0f172a"
MUTED = "#5b6478"
BORDER = "#dde3f0"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700;800&display=swap');

.stApp {{
    font-family: 'Source Sans 3', 'Segoe UI', Arial, sans-serif;
    color: {INK};
    background: #ffffff;
}}

.block-container {{
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 4rem;
    animation: ddiFade 0.5s ease both;
}}

@keyframes ddiFade {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes ddiGrow {{
    from {{ transform: scaleX(0); }}
    to   {{ transform: scaleX(1); }}
}}

@keyframes ddiFlip {{
    from {{ opacity: 0; transform: perspective(600px) rotateX(-80deg); }}
    to   {{ opacity: 1; transform: perspective(600px) rotateX(0deg); }}
}}

footer {{ visibility: hidden; }}

h1, h2, h3 {{
    font-weight: 700;
    letter-spacing: -0.01em;
    color: {BLUE_DARK};
}}

a {{ color: {BLUE_MID}; }}

[data-baseweb="tab-list"] {{
    border-bottom: 1px solid {BORDER};
    gap: 0.2rem;
}}
button[data-baseweb="tab"] {{
    font-weight: 600;
    font-size: 1rem;
    padding: 0.7rem 1.1rem;
    border-radius: 8px 8px 0 0;
    transition: background 0.2s ease, color 0.2s ease;
}}
button[data-baseweb="tab"]:hover {{
    background: {BLUE_SOFT};
    color: {BLUE};
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {BLUE};
    background: {BLUE_SOFT};
}}
[data-baseweb="tab-highlight"] {{
    background-color: {BLUE};
    height: 3px;
}}

.stButton > button {{
    border-radius: 8px;
    font-weight: 600;
    border: 1px solid {BORDER};
    padding: 0.5rem 1.2rem;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}}
.stButton > button:hover:not(:disabled) {{
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(10, 42, 143, 0.18);
    border-color: {BLUE};
    color: {BLUE};
}}
.stButton > button:active:not(:disabled) {{
    transform: translateY(0);
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {BLUE_DARK}, {BLUE});
    color: #ffffff;
    border: none;
}}
.stButton > button[kind="primary"]:hover:not(:disabled) {{
    color: #ffffff;
    box-shadow: 0 8px 20px rgba(10, 42, 143, 0.35);
}}

[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"] {{
    border-radius: 8px;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {{
    box-shadow: 0 0 0 3px rgba(47, 85, 212, 0.22);
}}

[data-testid="stAlert"] {{
    border-radius: 10px;
    animation: ddiFade 0.4s ease both;
}}
[data-testid="stExpander"] {{
    border: 1px solid {BORDER};
    border-radius: 10px;
    background: #ffffff;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    transition: box-shadow 0.2s ease;
}}
[data-testid="stExpander"]:hover {{
    box-shadow: 0 6px 18px rgba(10, 42, 143, 0.10);
}}
[data-testid="stMetric"] {{
    background: #ffffff;
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
[data-testid="stMetric"]:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.10);
}}

.ddi-card {{
    background: #ffffff;
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.ddi-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.10);
}}
.ddi-pill {{
    display: inline-block;
    padding: 0.18rem 0.7rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    animation: ddiFlip 0.5s ease both;
}}
.pill-major    {{ background: #fee2e2; color: #b91c1c; }}
.pill-moderate {{ background: #fef3c7; color: #b45309; }}
.pill-minor    {{ background: #dcfce7; color: #15803d; }}
.pill-none     {{ background: #e2e8f0; color: #475569; }}

.ddi-hero {{
    display: flex;
    align-items: center;
    gap: 1.4rem;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
    border-radius: 12px;
    color: #ffffff;
    background: linear-gradient(135deg, {BLUE_DARK} 0%, {BLUE} 70%, {BLUE_MID} 100%);
    box-shadow: 0 12px 30px rgba(6, 26, 92, 0.30);
    animation: ddiFade 0.6s ease both;
}}
.ddi-hero-icon {{
    font-size: 2.6rem;
    line-height: 1;
    background: rgba(255, 255, 255, 0.14);
    border-radius: 12px;
    padding: 0.8rem 0.95rem;
}}
.ddi-hero-title {{
    margin: 0;
    padding: 0;
    color: #ffffff;
    font-size: 2.3rem;
    font-weight: 800;
    letter-spacing: -0.01em;
}}
.ddi-hero-sub {{
    margin: 0.25rem 0 0.7rem 0;
    color: rgba(255, 255, 255, 0.90);
    font-size: 1.05rem;
}}
.ddi-badge {{
    display: inline-block;
    margin-right: 0.5rem;
    padding: 0.2rem 0.75rem;
    border-radius: 6px;
    background: {BLUE_SOFT};
    color: {BLUE};
    font-size: 0.8rem;
    font-weight: 700;
}}

.ddi-stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.9rem;
    margin: 0.6rem 0 1rem 0;
}}
.ddi-stat {{
    background: #ffffff;
    border: 1px solid {BORDER};
    border-left: 6px solid {MUTED};
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    animation: ddiFade 0.5s ease both;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.ddi-stat:hover {{
    transform: translateY(-3px);
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.10);
}}
.ddi-stat-value {{
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.1;
}}
.ddi-stat-label {{
    margin-top: 0.2rem;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    color: {MUTED};
}}
.stat-major    {{ border-left-color: #dc2626; background: #fff5f5; }}
.stat-major .ddi-stat-value    {{ color: #b91c1c; }}
.stat-moderate {{ border-left-color: #f59e0b; background: #fffbeb; }}
.stat-moderate .ddi-stat-value {{ color: #b45309; }}
.stat-minor    {{ border-left-color: #22c55e; background: #f3fbf5; }}
.stat-minor .ddi-stat-value    {{ color: #15803d; }}
.stat-none     {{ border-left-color: #94a3b8; background: #f8fafc; }}
.stat-none .ddi-stat-value     {{ color: #475569; }}
.stat-brand    {{ border-left-color: {BLUE}; background: {BLUE_SOFT}; }}
.stat-brand .ddi-stat-value    {{ color: {BLUE_DARK}; }}
.stat-due      {{ border-left-color: #f59e0b; background: #fffbeb; }}
.stat-due .ddi-stat-value      {{ color: #b45309; }}

.ddi-dist {{
    display: flex;
    height: 30px;
    border-radius: 999px;
    overflow: hidden;
    margin: 0 0 1.1rem 0;
    box-shadow: inset 0 1px 3px rgba(15, 23, 42, 0.15);
    transform-origin: left center;
    animation: ddiGrow 0.7s ease both;
}}
.ddi-seg {{
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 28px;
    color: #ffffff;
    font-size: 0.8rem;
    font-weight: 700;
    transition: filter 0.2s ease;
}}
.ddi-seg:hover {{ filter: brightness(1.12); }}
.seg-major    {{ background: #dc2626; }}
.seg-moderate {{ background: #f59e0b; }}
.seg-minor    {{ background: #22c55e; }}
.seg-none     {{ background: #94a3b8; }}
.seg-nr       {{ background: #64748b; }}

.ddi-progress-wrap {{
    margin: 0.4rem 0 1rem 0;
}}
.ddi-progress-label {{
    font-size: 0.88rem;
    font-weight: 600;
    color: {MUTED};
    margin-bottom: 0.35rem;
}}
.ddi-progress {{
    height: 12px;
    border-radius: 999px;
    background: {BORDER};
    overflow: hidden;
}}
.ddi-progress-fill {{
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, {BLUE}, {BLUE_MID});
    transform-origin: left center;
    animation: ddiGrow 0.8s ease both;
}}

.ddi-score {{
    background: #ffffff;
    border: 1px solid {BORDER};
    border-left: 6px solid {BLUE};
    border-radius: 12px;
    padding: 1rem 1.3rem;
    margin: 1rem 0 0.4rem 0;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    animation: ddiFade 0.5s ease both;
}}
.ddi-score-row {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
}}
.ddi-score-label {{
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    color: {MUTED};
}}
.ddi-score-value {{
    font-size: 2rem;
    font-weight: 800;
    color: {BLUE_DARK};
}}
.ddi-score-pct {{
    font-size: 1.1rem;
    font-weight: 700;
    color: {BLUE_MID};
}}

.ddi-flashcard {{
    background: linear-gradient(135deg, #ffffff 0%, {BLUE_SOFT} 100%);
    border: 1px solid {BORDER};
    border-top: 5px solid {BLUE};
    border-radius: 14px;
    padding: 2rem 1.5rem;
    margin: 0.6rem 0 1rem 0;
    text-align: center;
    font-size: 1.6rem;
    font-weight: 700;
    color: {BLUE_DARK};
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
    animation: ddiFlip 0.55s ease both;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.ddi-flashcard:hover {{
    transform: translateY(-3px);
    box-shadow: 0 14px 32px rgba(10, 42, 143, 0.20);
}}

.ddi-topics {{
    margin: 0.5rem 0 1rem 0;
}}
.ddi-trow {{
    display: flex;
    align-items: center;
    gap: 0.9rem;
    margin-bottom: 0.55rem;
}}
.ddi-tname {{
    flex: 0 0 170px;
    font-size: 0.92rem;
    font-weight: 600;
    color: {INK};
}}
.ddi-ttrack {{
    flex: 1;
    height: 22px;
    border-radius: 999px;
    background: #f1f5f9;
    overflow: hidden;
}}
.ddi-tbar {{
    display: flex;
    height: 100%;
    border-radius: 999px;
    overflow: hidden;
    transform-origin: left center;
    animation: ddiGrow 0.7s ease both;
}}
.ddi-tright {{ background: #22c55e; transition: filter 0.2s ease; }}
.ddi-twrong {{ background: #dc2626; transition: filter 0.2s ease; }}
.ddi-tright:hover, .ddi-twrong:hover {{ filter: brightness(1.12); }}
.ddi-tcount {{
    flex: 0 0 90px;
    font-size: 0.85rem;
    color: {MUTED};
}}
.ddi-legend {{
    font-size: 0.85rem;
    color: {MUTED};
    margin-bottom: 0.5rem;
}}
.ddi-dot {{
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin: 0 0.3rem 0 0.8rem;
}}
</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title, subtitle, badges=None):
    badge_html = "".join(
        '<span class="ddi-badge">' + html.escape(b) + "</span>" for b in (badges or [])
    )
    block = (
        '<div class="ddi-hero">'
        '<div class="ddi-hero-icon">&#128138;</div>'
        "<div>"
        '<h1 class="ddi-hero-title">' + html.escape(title) + "</h1>"
        '<p class="ddi-hero-sub">' + html.escape(subtitle) + "</p>"
        "<div>" + badge_html + "</div>"
        "</div>"
        "</div>"
    )
    st.markdown(block, unsafe_allow_html=True)


def stat_cards(items):
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


STAT_CLASS = {
    "Major": "stat-major",
    "Moderate": "stat-moderate",
    "Minor": "stat-minor",
    "Unknown": "stat-none",
    "No record": "stat-none",
    "Cards started": "stat-brand",
    "Due today": "stat-due",
}

SEG_CLASS = {
    "Major": "seg-major",
    "Moderate": "seg-moderate",
    "Minor": "seg-minor",
    "Unknown": "seg-none",
    "No record": "seg-nr",
}


def severity_stats(counts):
    """Colored stat cards. counts is a dict like {"Major": 2, "Moderate": 1, ...}."""
    cards = "".join(
        '<div class="ddi-stat ' + STAT_CLASS.get(label, "stat-none") + '">'
        '<div class="ddi-stat-value">' + html.escape(str(value)) + "</div>"
        '<div class="ddi-stat-label">' + html.escape(str(label)) + "</div>"
        "</div>"
        for label, value in counts.items()
    )
    st.markdown('<div class="ddi-stats">' + cards + "</div>", unsafe_allow_html=True)


def distribution_bar(counts):
    """One stacked bar showing how the counts split. Hover a segment for its label."""
    total = sum(int(v) for v in counts.values())
    if total <= 0:
        return
    segs = "".join(
        '<div class="ddi-seg ' + SEG_CLASS.get(label, "seg-none") + '" style="width:'
        + "{:.2f}".format(100.0 * int(value) / total) + '%" title="'
        + html.escape(str(label)) + ": " + str(int(value)) + '">'
        + str(int(value)) + "</div>"
        for label, value in counts.items()
        if int(value) > 0
    )
    st.markdown('<div class="ddi-dist">' + segs + "</div>", unsafe_allow_html=True)


def progress_bar(value, total, label):
    pct = 0.0 if total <= 0 else max(0.0, min(100.0, 100.0 * value / total))
    st.markdown(
        '<div class="ddi-progress-wrap">'
        '<div class="ddi-progress-label">' + html.escape(label) + "</div>"
        '<div class="ddi-progress"><div class="ddi-progress-fill" style="width:'
        + "{:.1f}".format(pct) + '%"></div></div>'
        "</div>",
        unsafe_allow_html=True,
    )


def score_card(correct, total):
    pct = 0.0 if total <= 0 else 100.0 * correct / total
    pct_text = "" if total <= 0 else str(round(pct)) + "%"
    st.markdown(
        '<div class="ddi-score">'
        '<div class="ddi-score-row">'
        '<div><div class="ddi-score-label">Score</div>'
        '<div class="ddi-score-value">' + str(int(correct)) + " / " + str(int(total)) + "</div></div>"
        '<div class="ddi-score-pct">' + pct_text + "</div>"
        "</div>"
        '<div class="ddi-progress"><div class="ddi-progress-fill" style="width:'
        + "{:.1f}".format(pct) + '%"></div></div>'
        "</div>",
        unsafe_allow_html=True,
    )


def flashcard_face(text):
    st.markdown('<div class="ddi-flashcard">' + html.escape(text) + "</div>", unsafe_allow_html=True)


def topic_bars(rows):
    """Right vs wrong answers per topic. rows come from build_dashboard."""
    top = max([int(r["seen"]) for r in rows] + [0])
    if top <= 0:
        return
    out = []
    for r in rows:
        seen = int(r["seen"])
        if seen <= 0:
            continue
        wrong = min(int(r["wrong"]), seen)
        right = seen - wrong
        width = "{:.1f}".format(100.0 * seen / top)
        out.append(
            '<div class="ddi-trow">'
            '<div class="ddi-tname">' + html.escape(str(r["topic"])) + "</div>"
            '<div class="ddi-ttrack"><div class="ddi-tbar" style="width:' + width + '%">'
            '<div class="ddi-tright" style="flex:' + str(right) + '" title="Right: '
            + str(right) + '"></div>'
            '<div class="ddi-twrong" style="flex:' + str(wrong) + '" title="Wrong: '
            + str(wrong) + '"></div>'
            "</div></div>"
            '<div class="ddi-tcount">' + str(seen) + " answers</div>"
            "</div>"
        )
    if not out:
        return
    legend = (
        '<div class="ddi-legend">'
        '<span class="ddi-dot" style="background:#22c55e;margin-left:0"></span>Right'
        '<span class="ddi-dot" style="background:#dc2626"></span>Wrong</div>'
    )
    st.markdown('<div class="ddi-topics">' + legend + "".join(out) + "</div>", unsafe_allow_html=True)