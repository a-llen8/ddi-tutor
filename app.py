import numpy as np
import pandas as pd
import streamlit as st

from pipeline.lookup import Checker

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

st.title("💊 DDI Tutor")
st.caption("A drug-drug interaction learning tool for medical students. Educational use only.")

tab_check, tab_quiz, tab_about = st.tabs(["Interaction checker", "Quiz", "About & limits"])

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
            st.success("No interaction found in DDInter for these medicines.")
            st.caption("This does not prove the combination is safe. See 'About & limits'.")
        else:
            st.subheader(f"{len(inter)} interaction(s) found")
            for _, r in inter.iterrows():
                with st.expander(
                    f"{BADGE[r['severity']]}: {r['ingredient_1']} + {r['ingredient_2']}"
                    f"  ({r['item_1']} / {r['item_2']})",
                    expanded=r["severity"] == "Major",
                ):
                    st.write(MEANING[r["severity"]])

        if not res["duplicates"].empty:
            st.warning("Same ingredient in more than one medicine (duplicate therapy):")
            st.dataframe(res["duplicates"], hide_index=True, use_container_width=True)
        if not res["no_data"].empty:
            st.info("Ingredients not covered by DDInter (could not be checked):")
            st.dataframe(res["no_data"], hide_index=True, use_container_width=True)

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
- "No interaction found" means none is listed in DDInter, not that the combination is safe.
- Brand names are mapped to DDInter ingredient names automatically; some ingredients (especially Indian-market ones) are not covered and are shown as "could not be checked".
- Severity levels follow DDInter and do not account for dose, patient age, kidney or liver function, or other conditions.
"""
    )
