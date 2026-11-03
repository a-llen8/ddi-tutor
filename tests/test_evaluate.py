import numpy as np
from ml.evaluate import pair_features, tanimoto


def test_tanimoto_identical_is_one():
    F = np.array([[1, 0, 1], [1, 0, 1], [0, 1, 0]], dtype=np.uint8)
    S = tanimoto(F)
    assert S[0, 1] == 1.0 and S[0, 2] == 0.0


def test_pair_features_do_not_depend_on_order():
    F = np.array([[1, 0], [0, 1]], dtype=np.uint8)
    a = pair_features(F, np.array([0]), np.array([1]))
    b = pair_features(F, np.array([1]), np.array([0]))
    assert (a == b).all()