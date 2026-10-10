import re
import pandas as pd
from pipeline.build_pairs import load_ddinter

KAGGLE = "data/raw/A_Z_medicines_dataset_of_India.csv"
OUT = "data/processed/brand_generic.csv"
UNMATCHED = "data/processed/unmatched.csv"

SYNONYMS = {
    "paracetamol": "acetaminophen",
    "amoxycillin": "amoxicillin",
    "aspirin": "acetylsalicylic acid",
    "methylcobalamin": "mecobalamin",              # confirm
    "lactobacillus": "lactobacillus acidophilus", 
    "beclometasone": "beclomethasone dipropionate",
    "beclometasone dipropionate": "beclomethasone dipropionate",
    "vitamin b6": "pyridoxine", # confirm
}
SALTS = {"hydrochloride", "hcl", "maleate", "succinate", "oxalate", "medoxomil",
         "proxetil", "decanoate", "tartrate", "besylate", "fumarate", "mesylate",
         "sulphate", "sulfate", "phosphate", "citrate", "acetate", "axetil",
         "dihydrate", "monohydrate", "sodium", "potassium", "calcium"}


def ddinter_names():
    dd = load_ddinter()
    return set(pd.concat([dd["Drug_A"], dd["Drug_B"]]).str.lower().str.strip())


def clean(x):
    if pd.isna(x):
        return None
    x = re.sub(r"\(.*?\)", "", str(x))
    x = re.sub(r"\s+", " ", x).strip().lower()
    return x or None


def strip_salts(n):
    words = [w for w in n.split() if w not in SALTS]
    return " ".join(words) or n


def to_ddinter(n, names):
    if n is None or pd.isna(n):
            return None
    s = strip_salts(n)
    for cand in (n, SYNONYMS.get(n, n), s, SYNONYMS.get(s, s)):
        if cand in names:
            return cand
    return None


def build_table(kg, names):
    out = kg[["id", "name", "Is_discontinued"]].copy()
    for i, c in enumerate(("short_composition1", "short_composition2"), start=1):
        out[f"ing{i}"] = kg[c].map(clean)
        out[f"ing{i}_dd"] = out[f"ing{i}"].map(lambda n: to_ddinter(n, names))
    return out


if __name__ == "__main__":
    names = ddinter_names()
    kg = pd.read_csv(KAGGLE)
    t = build_table(kg, names)
    t.to_csv(OUT, index=False)

    ok1 = t["ing1_dd"].notna()
    ok2 = t["ing2_dd"].notna() | t["ing2"].isna()
    print("medicines, ALL listed ingredients in DDInter:", round((ok1 & ok2).mean(), 3))
    print("medicines, AT LEAST ONE ingredient in DDInter:",
          round((ok1 | t["ing2_dd"].notna()).mean(), 3))

    ings = pd.concat([t["ing1"], t["ing2"]]).dropna()
    hit = pd.concat([t["ing1_dd"], t["ing2_dd"]]).dropna()
    print("ingredient mentions matched:", round(len(hit) / len(ings), 3))

    un = pd.concat([t.loc[t["ing1_dd"].isna(), "ing1"],
                    t.loc[t["ing2_dd"].isna(), "ing2"]]).dropna().value_counts()
    un.to_csv(UNMATCHED, header=["count"])
    print("\nTop 30 still unmatched:")
    print(un.head(30))