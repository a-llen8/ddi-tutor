"""Interaction lookup logic (no Streamlit code here, so it is easy to test)."""
from dataclasses import dataclass
from itertools import combinations

import pandas as pd
from rapidfuzz import fuzz, process

from pipeline.names import SYNONYMS

SEVERITY_ORDER = {"Major": 0, "Moderate": 1, "Minor": 2, "Unknown": 3}


@dataclass
class Item:
    """One thing the student typed in: a brand (many ingredients) or a generic."""
    label: str
    ingredients: list      # names that exist in DDInter
    unmatched: list        # ingredients we could not map to DDInter


def build_variants(meds):
    """One row per brand name and ingredient set, each with a display label.

    A brand name that is sold with different ingredient sets keeps every variant and shows its
    ingredients in the label. A brand with every row discontinued gets "(discontinued)".
    """
    meds = meds.copy()
    meds["key"] = meds["brand"].str.lower()
    shown, same = [], []
    for i1, d1, i2, d2 in zip(meds["ing1"], meds["ing1_dd"], meds["ing2"], meds["ing2_dd"]):
        got = []
        for raw, dd in ((i1, d1), (i2, d2)):
            if pd.isna(raw):
                continue
            name = dd if pd.notna(dd) else raw
            if name not in got:
                got.append(name)
        shown.append(" + ".join(got) or "no ingredient listed")
        same.append(" + ".join(sorted(got)))
    meds["_shown"] = shown
    meds["_same"] = same
    if "discontinued" in meds.columns:
        gone = meds["discontinued"].astype(str).str.lower().eq("true")
    else:
        gone = pd.Series(False, index=meds.index)
    meds["_gone"] = gone.groupby([meds["key"], meds["_same"]]).transform("all")
    meds = meds.drop_duplicates(["key", "_same"]).reset_index(drop=True)
    several = meds.groupby("key")["key"].transform("size") > 1
    label = meds["brand"].where(~several, meds["brand"] + " (" + meds["_shown"] + ")")
    meds["label"] = label.where(~meds["_gone"], label + " (discontinued)")
    return meds


class Checker:
    def __init__(self, pairs: pd.DataFrame, meds: pd.DataFrame, coverage: dict = None):
        self.pairs = pairs
        # {lowercase generic name: covered by the 8 DDInter files}. None turns the
        # coverage warning off completely.
        self.coverage = coverage
        # {frozenset({a, b}): severity}
        self._sev = {
            frozenset((a, b)): s
            for a, b, s in zip(pairs["drug_a"], pairs["drug_b"], pairs["severity"])
        }
        self.generics = sorted(set(pairs["drug_a"]) | set(pairs["drug_b"]))
        self._generic_set = set(self.generics)

        self.meds = build_variants(meds)
        self._by_label = {lab.lower(): i for i, lab in enumerate(self.meds["label"])}
        self._first_of_key = {}
        for i, k in enumerate(self.meds["key"]):
            self._first_of_key.setdefault(k, i)
        self._keys = self.meds["key"].tolist()

    # ---------- searching ----------
    def search(self, text: str, limit: int = 15) -> list:
        """Return display labels. Generics are tagged '(generic)'."""
        q = text.strip().lower()
        if len(q) < 2:
            return []
        out = []

        def add(label):
            if label not in out:
                out.append(label)

        # 1. generics that start with the text, and aliases that start with it
        #    ("paracetamol" -> acetaminophen, "aspirin" -> acetylsalicylic acid)
        aliased = []
        for alias, canonical in SYNONYMS.items():
            if (alias.startswith(q) and canonical in self._generic_set
                    and canonical not in aliased):
                aliased.append(canonical)
        for g in aliased + [g for g in self.generics if g.startswith(q)]:
            add(f"{g} (generic)")
        # 2. brands that start with the text
        starts = self.meds[self.meds["key"].str.startswith(q)]["label"]
        for b in starts:
            add(b)
        # 3. generics that contain the text
        for g in self.generics:
            if q in g:
                add(f"{g} (generic)")
        # 4. brands that contain the text
        has = self.meds[self.meds["key"].str.contains(q, regex=False)]["label"]
        for b in has:
            add(b)
        if len(out) >= limit:
            return out[:limit]
        # 5. typo fallback, only when there are few matches
        if len(out) < 3:
            for _, score, idx in process.extract(q, self._keys, scorer=fuzz.WRatio, limit=limit):
                if score >= 80:
                    b = self.meds.at[idx, "label"]
                    if b not in out:
                        out.append(b)
        return out[:limit]

    def resolve(self, label: str):
        """Turn a chosen label into an Item, or None if unknown."""
        if label.endswith(" (generic)"):
            g = label[: -len(" (generic)")].lower()
            return Item(label=g, ingredients=[g], unmatched=[]) if g in self._generic_set else None
        key = label.lower()
        i = self._by_label.get(key, self._first_of_key.get(key))
        if i is None:
            return None
        row = self.meds.loc[i]
        ing, unmatched = [], []
        for raw, dd in ((row["ing1"], row["ing1_dd"]), (row["ing2"], row["ing2_dd"])):
            if pd.isna(raw):
                continue
            (ing if pd.notna(dd) else unmatched).append(dd if pd.notna(dd) else raw)
        return Item(label=row["label"], ingredients=list(dict.fromkeys(ing)), unmatched=unmatched)

    # ---------- coverage ----------
    def is_covered(self, name: str) -> bool:
        """A name missing from the table counts as covered, so the app never
        claims a pair is outside the files without proof."""
        if not self.coverage:
            return True
        return bool(self.coverage.get(str(name).strip().lower(), True))

    def all_outside(self, names: list) -> bool:
        return bool(names) and not any(self.is_covered(n) for n in names)

    # ---------- checking ----------
    def check(self, items: list) -> dict:
        """Compare every pair of items. Returns interactions, duplicates, no_record, no_data."""
        interactions, duplicates, no_record, outside = [], [], [], []
        for x, y in combinations(items, 2):
            found = shared = False
            for a in x.ingredients:
                for b in y.ingredients:
                    if a == b:
                        duplicates.append({"item_1": x.label, "item_2": y.label, "ingredient": a})
                        shared = True
                        continue
                    sev = self._sev.get(frozenset((a, b)))
                    if sev:
                        interactions.append({
                            "item_1": x.label, "item_2": y.label,
                            "ingredient_1": a, "ingredient_2": b, "severity": sev,
                        })
                        found = True
            if x.ingredients and y.ingredients and not found and not shared:
                row = {"item_1": x.label, "item_2": y.label}
                if self.all_outside(x.ingredients) and self.all_outside(y.ingredients):
                    outside.append(row)
                else:
                    no_record.append(row)
        df = pd.DataFrame(
            interactions,
            columns=["item_1", "item_2", "ingredient_1", "ingredient_2", "severity"],
        )
        if not df.empty:
            df = df.sort_values("severity", key=lambda s: s.map(SEVERITY_ORDER)).reset_index(drop=True)
        no_data = [{"item": i.label, "ingredient": u} for i in items for u in i.unmatched]
        return {
            "interactions": df,
            "duplicates": pd.DataFrame(duplicates),
            "no_record": pd.DataFrame(no_record, columns=["item_1", "item_2"]),
            "outside_files": pd.DataFrame(outside, columns=["item_1", "item_2"]),
            "no_data": pd.DataFrame(no_data),
        }

    # ---------- quiz ----------
    def quiz_question(self, rng):
        """Random pair with a known severity (Unknown excluded). Each level is equally likely."""
        sev = self.pairs["severity"]
        levels = [s for s in ("Major", "Moderate", "Minor") if (sev == s).any()]
        if not levels:
            raise ValueError("no graded pairs")
        level = levels[int(rng.integers(len(levels)))]
        pool = self.pairs[sev == level]
        row = pool.iloc[int(rng.integers(len(pool)))]
        return row["drug_a"], row["drug_b"], row["severity"]
