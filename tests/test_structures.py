from pipeline.structures import clean_query, parse_smiles


def test_clean_query_drops_brackets():
    assert clean_query("Beclomethasone dipropionate (nasal)") == "Beclomethasone dipropionate"
    assert clean_query("Warfarin") == "Warfarin"


def test_parse_smiles_reads_any_smiles_key():
    ok = {"PropertyTable": {"Properties": [{"CID": 1, "SMILES": "CCO"}]}}
    old = {"PropertyTable": {"Properties": [{"CID": 2, "IsomericSMILES": "CCN"}]}}
    assert parse_smiles(ok) == (1, "CCO")
    assert parse_smiles(old) == (2, "CCN")


def test_parse_smiles_handles_bad_reply():
    assert parse_smiles({}) == (None, None)
    assert parse_smiles({"PropertyTable": {"Properties": []}}) == (None, None)