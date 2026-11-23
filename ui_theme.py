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

/* Tabs */
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

/* Buttons */
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

/* Inputs */
[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"] {{
    border-radius: 10px;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {{
    box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.18);
}}

/* Alerts, expanders, metrics */
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

/* Reusable classes for later parts */
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
</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)