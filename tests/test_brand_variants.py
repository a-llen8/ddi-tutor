import pandas as pd

from pipeline.lookup import Checker

PAIRS = pd.DataFrame({"drug_a": ["caffeine"], "drug_b": ["cetirizine"], "severity": ["Minor"]})
COLUMNS = ["brand", "ing1", "ing1_dd", "ing2", "ing2_dd", "discontinued"]
ROWS = [
    ["Abi Tablet", "caffeine", "caffeine", "chlorpheniramine", "chlorpheniramine", False],
    ["Abi Tablet", "caffeine", "caffeine", "cetirizine", "cetirizine", False],
    ["Solo Tablet", "caffeine", "caffeine", None, None, False],
    ["Gone Tablet", "cetirizine", "cetirizine", None, None, True],
    ["Mixed Tablet", "caffeine", "caffeine", None, None, True],
    ["MIXED TABLET", "caffeine", "caffeine", None, None, False],
]


def make_checker():
    return Checker(PAIRS, pd.DataFrame(ROWS, columns=COLUMNS))


def test_a_brand_with_two_ingredient_sets_keeps_both_variants():
    found = make_checker().search("abi")
    assert "Abi Tablet (caffeine + chlorpheniramine)" in found
    assert "Abi Tablet (caffeine + cetirizine)" in found
    assert "Abi Tablet" not in found


def test_each_variant_resolves_to_its_own_ingredients():
    c = make_checker()
    assert c.resolve("Abi Tablet (caffeine + chlorpheniramine)").ingredients == ["caffeine", "chlorpheniramine"]
    assert c.resolve("Abi Tablet (caffeine + cetirizine)").ingredients == ["caffeine", "cetirizine"]


def test_the_bare_brand_name_still_resolves_to_the_first_variant():
    item = make_checker().resolve("Abi Tablet")
    assert item.ingredients == ["caffeine", "chlorpheniramine"]


def test_a_brand_with_one_variant_keeps_its_plain_label():
    assert "Solo Tablet" in make_checker().search("solo")


def test_a_discontinued_brand_is_marked_and_still_found():
    c = make_checker()
    assert "Gone Tablet (discontinued)" in c.search("gone")
    assert c.resolve("Gone Tablet (discontinued)").ingredients == ["cetirizine"]
    assert c.resolve("Gone Tablet").ingredients == ["cetirizine"]


def test_a_brand_with_one_active_row_is_not_marked_discontinued():
    found = make_checker().search("mixed")
    assert found == ["Mixed Tablet"]