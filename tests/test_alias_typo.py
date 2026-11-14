from ml import lookup_predictions as lp

SHOWN = {"acetylsalicylic acid": "Acetylsalicylic acid", "warfarin": "Warfarin"}

def ids_both():
    return {"acetylsalicylic acid": {"1"}, "warfarin": {"2"}}

def test_alias_typo_gets_suggestion(monkeypatch):
    monkeypatch.setattr(lp, "SHOWN", SHOWN)
    A, note, prob = lp.resolve("Asprin", ids_both())
    assert A is None
    assert prob[0] == "not_found"
    assert ("Did you mean: Aspirin (listed in DDInter as "
            "Acetylsalicylic acid)?") in prob[1]

def test_real_name_typo_still_works(monkeypatch):
    monkeypatch.setattr(lp, "SHOWN", SHOWN)
    A, note, prob = lp.resolve("Warfarine", ids_both())
    assert prob[0] == "not_found"
    assert "Did you mean: Warfarin?" in prob[1]

def test_alias_missing_from_data_gives_no_suggestion(monkeypatch):
    monkeypatch.setattr(lp, "SHOWN", SHOWN)
    A, note, prob = lp.resolve("Asprin", {"warfarin": {"2"}})
    assert prob[0] == "not_found"
    assert "Did you mean" not in prob[1]

def test_exact_alias_still_works(monkeypatch):
    monkeypatch.setattr(lp, "SHOWN", SHOWN)
    A, note, prob = lp.resolve("Aspirin", ids_both())
    assert A == {"1"}
    assert prob is None
    assert note == "Aspirin is listed in DDInter as Acetylsalicylic acid."
