"""The common-drugs flashcard deck: graded pairs where both drugs are on sale in many brands."""
import pandas as pd

# A drug is common when at least this many current (not discontinued) brands contain it.
# My choice, a guess about what students meet. To review with the pharmacology reviewer.
MIN_BRANDS = 50

LEVELS = ("Major", "Moderate", "Minor")


def brand_counts(meds):
    """{drug: number of current brand rows that contain it}. A row counts once per drug.
    meds is data/app/medicines.csv.gz (columns ing1_dd, ing2_dd, discontinued)."""
    current = meds[~meds["discontinued"].astype(str).str.lower().eq("true")]
    first = current["ing1_dd"]
    second = current["ing2_dd"].where(current["ing2_dd"] != current["ing1_dd"])
    names = pd.concat([first, second]).dropna().astype(str).str.strip().str.lower()
    return names.value_counts().to_dict()


def common_drugs(meds, min_brands=MIN_BRANDS):
    return {d for d, n in brand_counts(meds).items() if n >= min_brands}


def common_pairs(graded, drugs):
    """Rows of a pairs table where both drugs are in the set."""
    a = graded["drug_a"].astype(str).str.strip().str.lower().isin(drugs)
    b = graded["drug_b"].astype(str).str.strip().str.lower().isin(drugs)
    return graded[a & b]


def draw_question(pairs, rng):
    """(drug_a, drug_b, severity). Each severity level present is equally likely,
    the same rule as Checker.quiz_question."""
    sev = pairs["severity"]
    levels = [s for s in LEVELS if (sev == s).any()]
    if not levels:
        raise ValueError("no graded pairs")
    level = levels[int(rng.integers(len(levels)))]
    pool = pairs[sev == level]
    row = pool.iloc[int(rng.integers(len(pool)))]
    return row["drug_a"], row["drug_b"], row["severity"]