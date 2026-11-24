import html

import streamlit as st

BLUE = "#0a2a8f"
BLUE_DARK = "#061a5c"
BLUE_MID = "#2f55d4"
BLUE_SOFT = "#e8edff"
CYAN = "#0891b2"
INK = "#0f172a"
MUTED = "#5b6478"
BORDER = "#dde3f0"


def _uri(svg):
    return ('url("data:image/svg+xml,'
            + svg.replace("<", "%3C").replace(">", "%3E").replace("#", "%23") + '")')


def _line_icon(inner, color="black"):
    return _uri(
        "<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' "
        "fill='none' stroke='" + color + "' stroke-width='2' stroke-linecap='round' "
        "stroke-linejoin='round'>" + inner + "</svg>"
    )


HERO_IMG = _uri(
    "<svg xmlns='http://www.w3.org/2000/svg' width='180' height='180' viewBox='0 0 180 180'>"
    "<g fill='none' stroke='white' stroke-opacity='0.10' stroke-width='2'>"
    "<path d='M22 10v24M10 22h24'/>"
    "<circle cx='120' cy='36' r='10'/>"
    "<circle cx='152' cy='62' r='6'/>"
    "<circle cx='96' cy='70' r='5'/>"
    "<path d='M128 43l18 14M112 40l-12 25'/>"
    "<rect x='30' y='100' width='52' height='20' rx='10' transform='rotate(-30 56 110)'/>"
    "<path d='M136 126v26M123 139h26'/>"
    "<circle cx='96' cy='150' r='7'/>"
    "</g></svg>"
)

HERO_ART = _uri(
    "<svg xmlns='http://www.w3.org/2000/svg' width='340' height='270' viewBox='0 0 340 270'>"
    "<g fill='none' stroke='white' stroke-opacity='0.28' stroke-width='2.5' "
    "stroke-linejoin='round' stroke-linecap='round'>"
    "<path d='M130 64l48.5 28v56L130 176l-48.5-28V92z'/>"
    "<path d='M227 64l48.5 28v56L227 176l-48.5-28V92z'/>"
    "<path d='M227 64v-34M81.5 92L44 70M227 176v46M130 176v38'/>"
    "<circle cx='227' cy='18' r='11'/>"
    "<circle cx='34' cy='64' r='11'/>"
    "<circle cx='227' cy='236' r='13'/>"
    "<circle cx='130' cy='228' r='10'/>"
    "<path d='M300 214v30M285 229h30'/>"
    "</g></svg>"
)

ICON_IMG = _uri(
    "<svg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 64 64'>"
    "<path d='M32 5l21 8v16c0 14-9 24-21 30C20 53 11 43 11 29V13z' "
    "fill='white' fill-opacity='0.16' stroke='white' stroke-width='3' stroke-linejoin='round'/>"
    "<path d='M28 20h8v9h9v8h-9v9h-8v-9h-9v-8h9z' fill='white'/>"
    "</svg>"
)

INFO_IMG = _uri(
    "<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'>"
    "<circle cx='12' cy='12' r='10' fill='#0a2a8f'/>"
    "<rect x='10.8' y='10' width='2.4' height='7' rx='1.2' fill='white'/>"
    "<circle cx='12' cy='6.8' r='1.5' fill='white'/>"
    "</svg>"
)

PAGE_IMG = _uri(
    "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240' viewBox='0 0 240 240'>"
    "<g fill='none' stroke='#0a2a8f' stroke-opacity='0.06' stroke-width='2'>"
    "<path d='M30 16v28M16 30h28'/>"
    "<circle cx='160' cy='50' r='12'/>"
    "<circle cx='200' cy='84' r='7'/>"
    "<circle cx='128' cy='92' r='6'/>"
    "<path d='M170 59l24 18M152 56l-18 30'/>"
    "<rect x='40' y='130' width='64' height='24' rx='12' transform='rotate(-30 72 142)'/>"
    "<path d='M180 160v30M165 175h30'/>"
    "<circle cx='120' cy='200' r='9'/>"
    "</g></svg>"
)

TAB_ICONS = [
    "<path d='M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z'/><path d='M8.5 12l2.5 2.5 5-5'/>",
    "<circle cx='11' cy='11' r='6.5'/><path d='M16 16l5 5'/>",
    "<rect x='5' y='4' width='14' height='17' rx='2'/><path d='M9 4V3h6v1M9 11h6M9 15h6'/>",
    "<rect x='3' y='7' width='14' height='13' rx='2'/>"
    "<path d='M7 7V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2'/>",
    "<circle cx='12' cy='12' r='9'/>"
    "<path d='M9.6 9.4a2.6 2.6 0 1 1 3.6 2.4c-.8.4-1.2.9-1.2 1.8M12 17h.01'/>",
    "<circle cx='12' cy='12' r='9'/><path d='M12 11v6M12 7.5h.01'/>",
]

TAB_ICON_CSS = "".join(
    "[data-testid='stTab']:nth-child(" + str(n + 1) + ")::before { "
    "-webkit-mask-image: " + _line_icon(inner) + "; mask-image: " + _line_icon(inner) + "; }\n"
    for n, inner in enumerate(TAB_ICONS)
)

STAT_ICONS = {
    "major": ("#dc2626", "#fee2e2",
              "<path d='M12 3.5L2.8 19.5h18.4z'/><path d='M12 10v4.5M12 17.2h.01'/>"),
    "moderate": ("#b45309", "#fef3c7",
                 "<circle cx='12' cy='12' r='9'/><path d='M12 7.5v5M12 16h.01'/>"),
    "minor": ("#15803d", "#dcfce7",
              "<circle cx='12' cy='12' r='9'/><path d='M8 12.3l2.8 2.8 5.5-5.6'/>"),
    "none": ("#475569", "#e2e8f0",
             "<circle cx='12' cy='12' r='9'/>"
             "<path d='M9.6 9.4a2.6 2.6 0 1 1 3.6 2.4c-.8.4-1.2.9-1.2 1.8M12 17h.01'/>"),
    "brand": ("#0a2a8f", "#e8edff",
              "<path d='M12 3l9 5-9 5-9-5z'/><path d='M3 12.5l9 5 9-5'/>"),
    "due": ("#b45309", "#fef3c7",
            "<circle cx='12' cy='12' r='9'/><path d='M12 7v5l3.2 2'/>"),
}

STAT_ICON_CSS = "".join(
    ".stat-" + key + "::after { background-color: " + tint + "; background-image: "
    + _line_icon(inner, color) + "; }\n"
    for key, (color, tint, inner) in STAT_ICONS.items()
)

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700;800&display=swap');

[data-testid="stElementContainer"]:has(style),
[data-testid="element-container"]:has(style) {{
    display: none;
}}

.stApp {{
    font-family: 'Source Sans 3', 'Segoe UI', Arial, sans-serif;
    color: {INK};
    background-color: #f2f5fb;
    background-image: {PAGE_IMG};
    background-size: 240px 240px;
    background-attachment: fixed;
}}

[data-testid="stMain"] {{
    overflow-x: hidden;
}}

[data-testid="stDecoration"] {{
    display: none;
}}

[data-testid="stHeader"] {{
    background: {BLUE_DARK} !important;
    height: 3.4rem;
    box-shadow: 0 2px 12px rgba(6, 26, 92, 0.25);
}}
[data-testid="stHeader"] *, [data-testid="stToolbar"] * {{
    color: #ffffff !important;
}}

.block-container, [data-testid="stMainBlockContainer"] {{
    max-width: 1180px;
    padding: 3.2rem 1.5rem 4rem 1.5rem !important;
    background: transparent;
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

.block-container h3 {{
    border-left: 4px solid {BLUE};
    border-image: linear-gradient(180deg, {BLUE}, {CYAN}) 1;
    padding-left: 0.75rem;
}}

a {{ color: {BLUE_MID}; }}

hr {{
    border-color: {BORDER};
}}

/* ---------------------------------------------------------- hero */
.ddi-hero {{
    box-sizing: border-box;
    position: relative;
    display: flex;
    align-items: center;
    gap: 1.8rem;
    width: 100vw;
    margin: 0 0 0 calc(50% - 50vw);
    padding: 2.8rem max(1.5rem, calc(50vw - 590px)) 5rem max(1.5rem, calc(50vw - 590px));
    border-radius: 0 0 32px 32px;
    color: #ffffff;
    background-image:
        {HERO_ART},
        {HERO_IMG},
        radial-gradient(circle at 82% 60%, rgba(34, 211, 238, 0.28) 0%, rgba(34, 211, 238, 0) 42%),
        linear-gradient(180deg, {BLUE_DARK} 0%, {BLUE} 62%, #1d44c4 100%);
    background-size: 340px 270px, 180px 180px, 100% 100%, 100% 100%;
    background-position: right max(1rem, calc(50vw - 590px)) bottom 3.6rem, 0 0, 0 0, 0 0;
    background-repeat: no-repeat, repeat, no-repeat, no-repeat;
    box-shadow: 0 18px 40px rgba(6, 26, 92, 0.30);
    animation: ddiFade 0.6s ease both;
}}
@media (max-width: 900px) {{
    .ddi-hero {{
        background-size: 0 0, 180px 180px, 100% 100%, 100% 100%;
        padding-bottom: 4.4rem;
    }}
    .ddi-hero-title {{
        font-size: 2.2rem !important;
    }}
}}
.ddi-hero-icon {{
    flex: 0 0 92px;
    width: 92px;
    height: 92px;
    border-radius: 22px;
    background-color: rgba(255, 255, 255, 0.14);
    background-image: {ICON_IMG};
    background-repeat: no-repeat;
    background-position: center;
    background-size: 58px 58px;
    border: 1px solid rgba(255, 255, 255, 0.34);
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.22);
}}
.ddi-hero-title {{
    margin: 0;
    padding: 0;
    color: #ffffff;
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.02em;
}}
.ddi-hero-sub {{
    max-width: 640px;
    margin: 0.35rem 0 0.9rem 0;
    color: rgba(255, 255, 255, 0.92);
    font-size: 1.12rem;
}}
.ddi-badge {{
    display: inline-flex;
    align-items: center;
    margin-right: 0.55rem;
    padding: 0.3rem 0.9rem 0.3rem 0.75rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.38);
    color: #ffffff;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}}
.ddi-badge::before {{
    content: "";
    width: 8px;
    height: 8px;
    margin-right: 0.5rem;
    border-radius: 50%;
    background: #22d3ee;
    box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.25);
}}

/* -------------------------------------------------------- notice */
[data-testid="stElementContainer"]:has(.ddi-notice),
[data-testid="element-container"]:has(.ddi-notice) {{
    position: relative;
    z-index: 3;
    margin-top: -3.2rem;
}}
.ddi-notice {{
    background-color: #ffffff !important;
    background-image: {INFO_IMG} !important;
    background-repeat: no-repeat !important;
    background-position: 1.2rem center !important;
    background-size: 26px 26px !important;
    border: 1px solid #c9d5f7 !important;
    border-left: 6px solid {BLUE} !important;
    border-radius: 14px !important;
    box-shadow: 0 14px 34px rgba(6, 26, 92, 0.18) !important;
    color: {INK} !important;
    padding: 1.05rem 1.4rem 1.05rem 3.8rem !important;
    font-size: 1.02rem !important;
}}

/* ------------------------------------------------------ nav tabs */
[data-testid="stTabs"] [role="tablist"] {{
    gap: 0.3rem !important;
    padding: 0.4rem !important;
    background: #ffffff !important;
    border: 1px solid {BORDER} !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 24px rgba(6, 26, 92, 0.08);
}}
[data-testid="stTabs"] [role="tablist"]::after {{
    display: none !important;
}}
[data-testid="stTab"] .react-aria-SelectionIndicator {{
    display: none !important;
}}
[data-testid="stTab"] {{
    height: auto !important;
    padding: 0.65rem 1.25rem !important;
    border-radius: 10px !important;
    background: transparent !important;
    color: #34436a !important;
    transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}}
[data-testid="stTab"] * {{
    color: inherit !important;
}}
[data-testid="stTab"] p {{
    margin: 0 !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
}}
[data-testid="stTab"]::before {{
    content: "";
    flex: 0 0 18px;
    width: 18px;
    height: 18px;
    margin-right: 0.55rem;
    background-color: currentColor;
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    -webkit-mask-position: center;
    mask-position: center;
    -webkit-mask-size: contain;
    mask-size: contain;
}}
{TAB_ICON_CSS}
[data-testid="stTab"]:hover:not([data-selected]):not([aria-selected="true"]) {{
    background: {BLUE_SOFT} !important;
    color: {BLUE} !important;
}}
[data-testid="stTab"][data-selected], [data-testid="stTab"][aria-selected="true"] {{
    background: linear-gradient(135deg, {BLUE_DARK}, {BLUE}) !important;
    color: #ffffff !important;
    box-shadow: 0 2px 5px rgba(10, 42, 143, 0.30);
}}
[data-testid="stTabPanel"] {{
    margin-top: 1rem;
    padding: 1.8rem 1.8rem 2rem 1.8rem !important;
    background: #ffffff;
    border: 1px solid {BORDER};
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(6, 26, 92, 0.07);
}}

/* -------------------------------------------------------- inputs */
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button {{
    border-radius: 10px;
    font-weight: 600;
    border: 1px solid #c3cde6;
    padding: 0.5rem 1.3rem;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}}
[data-testid="stButton"] button:hover:not(:disabled),
[data-testid="stDownloadButton"] button:hover:not(:disabled) {{
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(10, 42, 143, 0.18);
    border-color: {BLUE};
    color: {BLUE};
}}
[data-testid="stButton"] button:active:not(:disabled) {{
    transform: translateY(0);
}}
[data-testid="stButton"] button[kind="primary"], [data-testid="stBaseButton-primary"] {{
    background: linear-gradient(135deg, {BLUE_DARK}, {BLUE}) !important;
    color: #ffffff !important;
    border: none !important;
}}

[data-testid="stTextInputRootElement"],
[data-testid="stTextAreaRootElement"],
[data-testid="stSelectbox"] div:has(> input) {{
    background-color: #ffffff !important;
    border-color: #c3cde6 !important;
    border-radius: 10px !important;
    box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.04);
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}}
[data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stTextAreaRootElement"]:focus-within,
[data-testid="stSelectbox"] div:has(> input):focus-within {{
    border-color: {BLUE_MID} !important;
    box-shadow: 0 0 0 3px rgba(47, 85, 212, 0.22);
}}

[role="radiogroup"] {{
    gap: 0.5rem;
}}
[role="radiogroup"] label {{
    margin: 0 !important;
    padding: 0.3rem 1rem 0.3rem 0.7rem;
    background: #ffffff;
    border: 1px solid #c3cde6;
    border-radius: 999px;
    cursor: pointer;
    transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}}
[role="radiogroup"] label:hover {{
    background: {BLUE_SOFT};
    border-color: {BLUE_MID};
}}
[role="radiogroup"] label:has(input:checked) {{
    background: {BLUE_SOFT};
    border-color: {BLUE};
    box-shadow: 0 0 0 3px rgba(10, 42, 143, 0.12);
}}
[data-testid="stRadioOption"][data-selected] > div > div:first-child {{
    background-color: {BLUE} !important;
    border-color: {BLUE} !important;
}}
[data-testid="stRadioOption"][data-selected] > div > div:first-child > div {{
    background-color: #ffffff !important;
}}

[data-testid="stFileUploaderDropzone"] {{
    background: #f7f9ff;
    border: 2px dashed #b9c6ea;
    border-radius: 12px;
}}

[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER};
    border-radius: 12px;
    overflow: hidden;
}}

/* --------------------------------------------------------- alerts */
[data-testid="stAlertContainer"] {{
    border-radius: 12px;
    animation: ddiFade 0.4s ease both;
}}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {{
    border-left: 5px solid {BLUE_MID};
}}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {{
    border-left: 5px solid #f59e0b;
}}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {{
    border-left: 5px solid #16a34a;
}}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {{
    border-left: 5px solid #dc2626;
}}

[data-testid="stExpander"] {{
    border: 1px solid {BORDER};
    border-left: 4px solid {BLUE};
    border-radius: 12px;
    background: #ffffff;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    transition: box-shadow 0.2s ease;
}}
[data-testid="stExpander"] summary {{
    background: #f5f8ff;
    font-weight: 600;
}}
[data-testid="stExpander"]:hover {{
    box-shadow: 0 8px 22px rgba(10, 42, 143, 0.12);
}}
[data-testid="stMetric"] {{
    background: #ffffff;
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
}}

/* ---------------------------------------------------- components */
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

.ddi-stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 1rem;
    margin: 0.8rem 0 1.1rem 0;
}}
.ddi-stat {{
    position: relative;
    background: #ffffff;
    border: 1px solid {BORDER};
    border-top: 4px solid {MUTED};
    border-radius: 14px;
    padding: 1rem 4.8rem 0.95rem 1.2rem;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
    animation: ddiFade 0.5s ease both;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.ddi-stat::after {{
    content: "";
    position: absolute;
    top: 50%;
    right: 1rem;
    width: 44px;
    height: 44px;
    margin-top: -22px;
    border-radius: 12px;
    background-repeat: no-repeat;
    background-position: center;
    background-size: 24px 24px;
}}
.ddi-stat:hover {{
    transform: translateY(-3px);
    box-shadow: 0 12px 26px rgba(15, 23, 42, 0.12);
}}
.ddi-stat-value {{
    font-size: 2.2rem;
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
.stat-major    {{ border-top-color: #dc2626; background: linear-gradient(180deg, #fff5f5 0%, #ffffff 100%); }}
.stat-major .ddi-stat-value    {{ color: #b91c1c; }}
.stat-moderate {{ border-top-color: #f59e0b; background: linear-gradient(180deg, #fffbeb 0%, #ffffff 100%); }}
.stat-moderate .ddi-stat-value {{ color: #b45309; }}
.stat-minor    {{ border-top-color: #22c55e; background: linear-gradient(180deg, #f3fbf5 0%, #ffffff 100%); }}
.stat-minor .ddi-stat-value    {{ color: #15803d; }}
.stat-none     {{ border-top-color: #94a3b8; background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%); }}
.stat-none .ddi-stat-value     {{ color: #475569; }}
.stat-brand    {{ border-top-color: {BLUE}; background: linear-gradient(180deg, {BLUE_SOFT} 0%, #ffffff 100%); }}
.stat-brand .ddi-stat-value    {{ color: {BLUE_DARK}; }}
.stat-due      {{ border-top-color: #f59e0b; background: linear-gradient(180deg, #fffbeb 0%, #ffffff 100%); }}
.stat-due .ddi-stat-value      {{ color: #b45309; }}
{STAT_ICON_CSS}
.ddi-dist {{
    display: flex;
    gap: 3px;
    height: 32px;
    border-radius: 999px;
    overflow: hidden;
    margin: 0 0 1.1rem 0;
    background: #e8edf7;
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
    font-size: 0.82rem;
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
    background: linear-gradient(90deg, {BLUE}, {BLUE_MID}, {CYAN});
    transform-origin: left center;
    animation: ddiGrow 0.8s ease both;
}}

.ddi-score {{
    background: linear-gradient(180deg, #f5f8ff 0%, #ffffff 100%);
    border: 1px solid {BORDER};
    border-left: 6px solid {BLUE};
    border-radius: 14px;
    padding: 1.1rem 1.4rem;
    margin: 1rem 0 0.4rem 0;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
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
    font-size: 2.2rem;
    font-weight: 800;
    color: {BLUE_DARK};
}}
.ddi-score-pct {{
    font-size: 1.2rem;
    font-weight: 700;
    color: {CYAN};
}}

.ddi-flashcard {{
    position: relative;
    overflow: hidden;
    background-image:
        {PAGE_IMG},
        linear-gradient(135deg, #ffffff 0%, {BLUE_SOFT} 100%);
    background-size: 240px 240px, 100% 100%;
    border: 1px solid {BORDER};
    border-radius: 18px;
    padding: 2.8rem 1.5rem 2.4rem 1.5rem;
    margin: 0.6rem 0 1rem 0;
    text-align: center;
    font-size: 1.9rem;
    font-weight: 700;
    color: {BLUE_DARK};
    box-shadow: 0 10px 28px rgba(6, 26, 92, 0.10);
    animation: ddiFlip 0.55s ease both;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.ddi-flashcard::before {{
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    height: 6px;
    background: linear-gradient(90deg, {BLUE}, {BLUE_MID}, {CYAN});
}}
.ddi-flashcard:hover {{
    transform: translateY(-3px);
    box-shadow: 0 16px 36px rgba(10, 42, 143, 0.20);
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
    background: #eef2f9;
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
        '<div class="ddi-hero-icon" aria-hidden="true"></div>'
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