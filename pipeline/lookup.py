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


class Checker:
    def __init__(self, pairs: pd.DataFrame, meds: pd.DataFrame):
        self.pairs = pairs
        # {frozenset({a, b}): severity}
        self._sev = {
            frozenset((a, b)): s
            for a, b, s in zip(pairs["drug_a"], pairs["drug_b"], pairs["severity"])
        }
        self.generics = sorted(set(pairs["drug_a"]) | set(pairs["drug_b"]))
        self._generic_set = set(self.generics)

        meds = meds.copy()
        meds["key"] = meds["brand"].str.lower()
        self.meds = meds.drop_duplicates("key").reset_index(drop=True)
        self._by_key = self.meds.set_index("key")
        self._keys = self.meds["key"].tolist()

    # ---------- searching ----------
    def search(self, text: str, limit: int = 15) -> list:
        """Return display labels. Generics are tagged '(generic)'."""
        q = text.strip().lower()
        if len(q) < 2:
            return []
        out = []
        gen = [g for g in self.generics if g.startswith(q)] + \
              [g for g in self.generics if q in g and not g.startswith(q)]
        # alias search: "paracetamol" -> acetaminophen, "aspirin" -> acetylsalicylic acid
        for alias, canonical in SYNONYMS.items():
            if alias.startswith(q) and canonical in self._generic_set and canonical not in gen:
                gen.insert(0, canonical)
        out += [f"{g} (generic)" for g in gen[:5]]

        starts = self.meds[self.meds["key"].str.startswith(q)]["brand"]
        has = self.meds[self.meds["key"].str.contains(q, regex=False)]["brand"]
        for b in list(starts) + list(has):
            if b not in out:
                out.append(b)
            if len(out) >= limit:
                return out[:limit]
        if len(out) < 3:  # typo fallback
            for key, score, _ in process.extract(q, self._keys, scorer=fuzz.WRatio, limit=limit):
                if score >= 80:
                    b = self._by_key.loc[key, "brand"]
                    if b not in out:
                        out.append(b)
        return out[:limit]

    def resolve(self, label: str):
        """Turn a chosen label into an Item, or None if unknown."""
        if label.endswith(" (generic)"):
            g = label[: -len(" (generic)")].lower()
            return Item(label=g, ingredients=[g], unmatched=[]) if g in self._generic_set else None
        key = label.lower()
        if key not in self._by_key.index:
            return None
        row = self._by_key.loc[key]
        ing, unmatched = [], []
        for raw, dd in ((row["ing1"], row["ing1_dd"]), (row["ing2"], row["ing2_dd"])):
            if pd.isna(raw):
                continue
            (ing if pd.notna(dd) else unmatched).append(dd if pd.notna(dd) else raw)
        return Item(label=row["brand"], ingredients=list(dict.fromkeys(ing)), unmatched=unmatched)

    # ---------- checking ----------
    def check(self, items: list) -> dict:
        """Compare every pair of items. Returns interactions, duplicates, no_data."""
        interactions, duplicates = [], []
        for x, y in combinations(items, 2):
            for a in x.ingredients:
                for b in y.ingredients:
                    if a == b:
                        duplicates.append({"item_1": x.label, "item_2": y.label, "ingredient": a})
                        continue
                    sev = self._sev.get(frozenset((a, b)))
                    if sev:
                        interactions.append({
                            "item_1": x.label, "item_2": y.label,
                            "ingredient_1": a, "ingredient_2": b, "severity": sev,
                        })
        df = pd.DataFrame(
            interactions,
            columns=["item_1", "item_2", "ingredient_1", "ingredient_2", "severity"],
        )
        if not df.empty:
            df = df.sort_values("severity", key=lambda s: s.map(SEVERITY_ORDER)).reset_index(drop=True)
        no_data = [{"item": i.label, "ingredient": u} for i in items for u in i.unmatched]
        return {"interactions": df, "duplicates": pd.DataFrame(duplicates), "no_data": pd.DataFrame(no_data)}

    # ---------- quiz ----------
    def quiz_question(self, rng):
        """Random pair with a known severity (Unknown excluded)."""
        known = self.pairs[self.pairs["severity"] != "Unknown"]
        row = known.iloc[int(rng.integers(len(known)))]
        return row["drug_a"], row["drug_b"], row["severity"]
