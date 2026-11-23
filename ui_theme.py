import html

import streamlit as st

TEAL = "#0f766e"
TEAL_DARK = "#115e59"
TEAL_SOFT = "#e6f4f1"
INK = "#0f172a"
MUTED = "#64748b"
BORDER = "#e2e8f0"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {{
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: {INK};
}}

.block-container {{
    max-width: 1180px;
    padding-top: 2.2rem;
    padding-bottom: 4rem;
    animation: ddiFade 0.5s ease both;
}}

@keyframes ddiFade {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

footer {{ visibility: hidden; }}

h1, h2, h3 {{
    font-weight: 700;
    letter-spacing: -0.02em;
}}

button[data-baseweb="tab"] {{
    font-weight: 600;
    padding: 0.7rem 1.1rem;
    border-radius: 10px 10px 0 0;
    transition: background 0.2s ease, color 0.2s ease;
}}
button[data-baseweb="tab"]:hover {{
    background: {TEAL_SOFT};
    color: {TEAL_DARK};
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {TEAL};
}}

.stButton > button {{
    border-radius: 10px;
    font-weight: 600;
    border: 1px solid {BORDER};
    padding: 0.5rem 1.2rem;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}}
.stButton > button:hover:not(:disabled) {{
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(15, 118, 110, 0.18);
    border-color: {TEAL};
    color: {TEAL};
}}
.stButton > button:active:not(:disabled) {{
    transform: translateY(0);
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {TEAL}, #14b8a6);
    color: #ffffff;
    border: none;
}}
.stButton > button[kind="primary"]:hover:not(:disabled) {{
    color: #ffffff;
    box-shadow: 0 8px 20px rgba(15, 118, 110, 0.35);
}}

[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"] {{
    border-radius: 10px;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {{
    box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.18);
}}

[data-testid="stAlert"] {{
    border-radius: 12px;
}}
[data-testid="stExpander"] {{
    border: 1px solid {BORDER};
    border-radius: 12px;
    background: #ffffff;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    transition: box-shadow 0.2s ease;
}}
[data-testid="stExpander"]:hover {{
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
}}
[data-testid="stMetric"] {{
    background: #ffffff;
    border: 1px solid {BORDER};
    border-radius: 14px;
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
    border-radius: 14px;
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
    border-radius: 18px;
    color: #ffffff;
    background: linear-gradient(135deg, {TEAL_DARK} 0%, {TEAL} 55%, #14b8a6 100%);
    box-shadow: 0 12px 30px rgba(15, 118, 110, 0.28);
    animation: ddiFade 0.6s ease both;
}}
.ddi-hero-icon {{
    font-size: 2.6rem;
    line-height: 1;
    background: rgba(255, 255, 255, 0.16);
    border-radius: 16px;
    padding: 0.8rem 0.95rem;
}}
.ddi-hero-title {{
    margin: 0;
    padding: 0;
    color: #ffffff;
    font-size: 2.3rem;
    font-weight: 800;
    letter-spacing: -0.02em;
}}
.ddi-hero-sub {{
    margin: 0.25rem 0 0.7rem 0;
    color: rgba(255, 255, 255, 0.88);
    font-size: 1rem;
}}
.ddi-badge {{
    display: inline-block;
    margin-right: 0.5rem;
    padding: 0.2rem 0.75rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.18);
    border: 1px solid rgba(255, 255, 255, 0.35);
    font-size: 0.78rem;
    font-weight: 600;
}}

.ddi-stats {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.9rem;
    margin: 0.6rem 0 1rem 0;
}}
@media (max-width: 700px) {{
    .ddi-stats {{ grid-template-columns: repeat(2, 1fr); }}
}}
.ddi-stat {{
    background: #ffffff;
    border: 1px solid {BORDER};
    border-left: 6px solid {MUTED};
    border-radius: 14px;
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
    font-size: 0.82rem;
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