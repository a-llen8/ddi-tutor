import pandas as pd
from pipeline.build_pairs import build_pairs


def test_pair_order_and_dedupe():
    df = pd.DataFrame({
        "DDInterID_A": ["DDInter2", "DDInter1"],
        "Drug_A": ["B", "A"],
        "DDInterID_B": ["DDInter1", "DDInter2"],
        "Drug_B": ["A", "B"],
        "Level": ["Major", "Major"],
    })
    out, _, _ = build_pairs(df)
    assert len(out) == 1
    assert out.iloc[0]["drug_a_id"] < out.iloc[0]["drug_b_id"]