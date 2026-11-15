import os

import numpy as np
import pandas as pd
import streamlit as st

from pipeline.lookup import Checker
from ml.lookup_predictions import PAIRS as LOOKUP_PAIRS, DB as LOOKUP_DB
from ml.case_simulator import check_case, id_names, MAX_DRUGS
from ml.lookup_predictions import load_pairs, lookup, open_db, resolve

st.set_page_config(page_title="DDI Tutor", page_icon="💊", layout="wide")

BADGE = {"Major": "🔴 Major", "Moderate": "🟠 Moderate", "Minor": "🟡 Minor", "Unknown": "⚪ Unknown"}
MEANING = {
    "Major": "Potentially life-threatening or may need medical intervention. Usually avoid the combination.",
    "Moderate": "May worsen the patient's condition or need a change in therapy or monitoring.",
    "Minor": "Limited clinical effect. Be aware; usually no change needed.",
    "Unknown": "An interaction is listed, but its severity is not classified in DDInter.",
}


@st.cache_resource
def load_checker():
    pairs = pd.read_csv("data/app/pairs.csv.gz")
    meds = pd.read_csv("data/app/medicines.csv.gz")
    return Checker(pairs, meds)


chk = load_checker()


def case_ready():
    return os.path.exists(LOOKUP_PAIRS)


@st.cache_resource
def load_case_names():
    return id_names()


def lookup_ready():
    return os.path.exists(LOOKUP_PAIRS) and os.path.exists(LOOKUP_DB)


@st.cache_resource
def load_lookup_data():
    return load_pairs()

st.title("💊 DDI Tutor")
st.caption("A drug-drug interaction learning tool for medical students. Educational use only.")

tab_check, tab_lookup, tab_case, tab_quiz, tab_about = st.tabs(["Interaction checker", "Pair lookup", "Case simulator", "Quiz", "About & limits"])

# ------------------------------------------------------------------ checker
with tab_check:
    if "items" not in st.session_state:
        st.session_state["items"] = []

    c1, c2 = st.columns([3, 2])
    with c1:
        q = st.text_input("Search a brand (e.g. Ecosprin) or generic (e.g. warfarin)", key="search_text")
        options = chk.search(q) if q else []
        choice = st.selectbox("Matches", options, index=None, placeholder="Type above to see matches")
        if st.button("Add to list", disabled=choice is None):
            item = chk.resolve(choice)
            if item and item.label not in [i.label for i in st.session_state["items"]]:
                st.session_state["items"].append(item)
            st.rerun()

    with c2:
        st.subheader("Medicines to check")
        if not st.session_state["items"]:
            st.info("Add at least two medicines.")
        for n, it in enumerate(st.session_state["items"]):
            cols = st.columns([5, 1])
            ingr = ", ".join(it.ingredients + it.unmatched) or "no ingredients found"
            cols[0].write(f"**{it.label}**  \n_{ingr}_")
            if cols[1].button("✕", key=f"rm{n}"):
                st.session_state["items"].pop(n)
                st.rerun()
        if st.session_state["items"] and st.button("Clear all"):
            st.session_state["items"] = []
            st.rerun()

    if len(st.session_state["items"]) >= 2:
        st.divider()
        res = chk.check(st.session_state["items"])
        inter = res["interactions"]

        if inter.empty:
            st.info("No record in DDInter for these medicines. Not documented does not mean safe.")
            st.caption("See 'About & limits'.")
        else:
            st.subheader(f"{len(inter)} interaction(s) found")
            for _, r in inter.iterrows():
                with st.expander(
                    f"{BADGE[r['severity']]}: {r['ingredient_1']} + {r['ingredient_2']}"
                    f"  ({r['item_1']} / {r['item_2']})",
                    expanded=r["severity"] == "Major",
                ):
                    st.write(MEANING[r["severity"]])

        if not res["no_record"].empty:
            st.info("No record in DDInter for these pairs. Not documented does not mean safe:")
            st.dataframe(res["no_record"], hide_index=True, use_container_width=True)
        if not res["duplicates"].empty:
            st.warning("Same ingredient in more than one medicine (duplicate therapy):")
            st.dataframe(res["duplicates"], hide_index=True, use_container_width=True)
        if not res["no_data"].empty:
            st.info("Ingredients not covered by DDInter (could not be checked):")
            st.dataframe(res["no_data"], hide_index=True, use_container_width=True)

# ------------------------------------------------------------------- lookup
with tab_lookup:
    st.write("Check one pair by generic name. Documented pairs come from DDInter. "
             "A pair with no record may get a prediction band.")
    if not lookup_ready():
        st.info("Prediction data is not available in this version of the app.")
    else:
        lk_ids, lk_sev = load_lookup_data()
        lc1, lc2 = st.columns(2)
        name_a = lc1.text_input("First drug (generic name)", key="lk_a")
        name_b = lc2.text_input("Second drug (generic name)", key="lk_b")
        if name_a.strip() and name_b.strip():
            con = open_db()
            try:
                lk = lookup(name_a, name_b, lk_ids, lk_sev, con)
            finally:
                con.close()
            if lk["status"] == "documented":
                st.write(BADGE[lk["severity"]])
                st.write(MEANING[lk["severity"]])
                st.caption(lk["text"])
            elif lk["status"] == "predicted":
                (st.warning if lk["band"] == "High" else st.info)(lk["text"])
            elif lk["status"] == "no_prediction":
                st.info(lk["text"])
            else:
                st.warning(lk["text"])
                if lk["status"] == "not_found":
                    for typed in (name_a, name_b):
                        if resolve(typed, lk_ids)[2] is None:
                            continue
                        hits = [b for b in chk.search(typed, limit=3)
                                if not b.endswith(" (generic)")
                                and b.lower().startswith(typed.strip().lower())]
                        item = chk.resolve(hits[0]) if hits else None
                        if item and item.ingredients:
                            st.caption(f"{typed.strip()} looks like a brand name ({item.label}). "
                                       f"Its ingredients: {', '.join(item.ingredients)}. "
                                       "Enter a generic name here, or use the Interaction checker tab for brands.")

# --------------------------------------------------------------- case simulator
with tab_case:
    st.write(f"Type 2 to {MAX_DRUGS} generic names, one per line. "
             "Only confirmed DDInter records are shown. No prediction is used here.")
    if not case_ready():
        st.info("The case simulator data is not available in this version of the app.")
    else:
        cs_ids, cs_sev = load_lookup_data()
        cs_names = load_case_names()
        text = st.text_area("Drugs, one per line", key="case_text", height=180)
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        if lines:
            r = check_case(lines, cs_ids, cs_sev, cs_names)
            if r["status"] != "ok":
                for m in r["messages"]:
                    st.warning(m)
            else:
                st.write("Drugs: " + ", ".join(r["drugs"]))
                for n in r["notes"]:
                    st.caption(n)
                c = r["counts"]
                n_pairs = len(r["pairs"])
                word = "pair" if n_pairs == 1 else "pairs"
                st.subheader(f"{n_pairs} {word}")
                st.write(f"Major {c['Major']}, Moderate {c['Moderate']}, Minor {c['Minor']}, "
                         f"Unknown {c['Unknown']}, no record {c['no_record']}")
                for pr in r["pairs"]:
                    if pr["severity"] is None:
                        st.info(f"No record: {pr['drug_a']} + {pr['drug_b']}. "
                                "Not documented does not mean safe.")
                    else:
                        with st.expander(f"{BADGE[pr['severity']]}: {pr['drug_a']} + {pr['drug_b']}",
                                         expanded=pr["severity"] == "Major"):
                            st.write(MEANING[pr["severity"]])
                st.caption(r["limits"])

# --------------------------------------------------------------------- quiz
with tab_quiz:
    st.write("Guess the severity DDInter assigns to each pair.")
    if "rng" not in st.session_state:
        st.session_state["rng"] = np.random.default_rng()
        st.session_state["score"] = [0, 0]
        st.session_state["quiz_q"] = chk.quiz_question(st.session_state["rng"])
        st.session_state["answered"] = None

    a, b, truth = st.session_state["quiz_q"]
    st.subheader(f"{a.title()}  +  {b.title()}")
    guess = st.radio("Severity", ["Major", "Moderate", "Minor"], horizontal=True, index=None,
                     key=f"guess_{a}_{b}")

    if st.button("Check answer", disabled=guess is None or st.session_state["answered"] is not None):
        st.session_state["answered"] = guess == truth
        st.session_state["score"][1] += 1
        st.session_state["score"][0] += int(guess == truth)
        st.rerun()

    if st.session_state["answered"] is not None:
        (st.success if st.session_state["answered"] else st.error)(
            f"{'Correct' if st.session_state['answered'] else 'Not quite'}: {truth}. {MEANING[truth]}"
        )
        if st.button("Next question"):
            st.session_state["quiz_q"] = chk.quiz_question(st.session_state["rng"])
            st.session_state["answered"] = None
            st.rerun()

    s, t = st.session_state["score"]
    st.caption(f"Score: {s} / {t}")

# -------------------------------------------------------------------- about
with tab_about:
    st.markdown(
        """
**Data sources:** DDInter (drug-drug interaction database) and the A-Z Medicines Dataset of India (brand to ingredient mapping).

**Important limits**
- Built for learning. **Not for clinical decisions.** Always check a current drug reference and consult a pharmacist or doctor.
- "No record" means the pair is not documented in DDInter. It does not mean the combination is safe.
- Pair lookup predictions are bands (Low, Medium, High) based on similarity to documented pairs. They are always Predicted, not confirmed. Low does not mean safe.
- Brand names are mapped to DDInter ingredient names automatically; some ingredients (especially Indian-market ones) are not covered and are shown as "could not be checked".
- Severity levels follow DDInter and do not account for dose, patient age, kidney or liver function, or other conditions.
"""
    )
