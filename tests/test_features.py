from pipeline.features import featurize


def test_fingerprint_shape_and_not_empty():
    fp, heavy, n_frag = featurize("CCO")
    assert fp.shape == (2048,)
    assert fp.sum() > 0 and heavy == 3 and n_frag == 1


def test_salt_keeps_largest_fragment():
    fp, heavy, n_frag = featurize("CC(=O)[O-].[Na+]")
    assert n_frag == 2 and heavy == 4


def test_bad_smiles_gives_none():
    assert featurize("not a smiles") is None