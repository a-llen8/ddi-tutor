import numpy as np

from ml.calibrate import knn_score
from ml.lookalike import closest_pairs


def make(seed=0, n_drugs=30, n_pairs=200):
    rng = np.random.default_rng(seed)
    S = rng.random((n_drugs, n_drugs)).astype(np.float32)
    S = (S + S.T) / 2
    np.fill_diagonal(S, 1.0)
    ia = rng.integers(0, n_drugs, n_pairs + 1)
    ib = rng.integers(0, n_drugs, n_pairs + 1)
    y = rng.integers(0, 2, n_pairs + 1)
    fit = np.arange(n_pairs)
    return S, ia, ib, y, fit


def test_raw_score_matches_the_model_score():
    S, ia, ib, y, fit = make()
    q = len(ia) - 1
    _, raw = closest_pairs(S, ia, ib, y, fit, ia[q], ib[q])
    expected = knn_score(S, ia, ib, y, fit, np.array([q]))[0]
    assert abs(raw - expected) < 1e-5


def test_neighbours_are_sorted_most_similar_first():
    S, ia, ib, y, fit = make(seed=1)
    found, _ = closest_pairs(S, ia, ib, y, fit, ia[-1], ib[-1], k=5)
    sims = [f["similarity"] for f in found]
    assert len(found) == 5
    assert sims == sorted(sims, reverse=True)


def test_documented_flag_matches_label():
    S, ia, ib, y, fit = make(seed=2)
    found, _ = closest_pairs(S, ia, ib, y, fit, ia[-1], ib[-1])
    for f in found:
        assert f["documented"] == bool(y[f["row"]])


def test_crossed_match_swaps_the_like_drugs():
    S = np.eye(4, dtype=np.float32)
    S[0, 3] = S[3, 0] = 0.9
    S[1, 2] = S[2, 1] = 0.8
    ia = np.array([2, 0])
    ib = np.array([3, 1])
    y = np.array([1, 0])
    found, _ = closest_pairs(S, ia, ib, y, np.array([0]), 0, 1, k=1)
    assert found[0]["like_a"] == 3
    assert found[0]["like_b"] == 2
    assert abs(found[0]["sim_a"] - 0.9) < 1e-6
    assert abs(found[0]["sim_b"] - 0.8) < 1e-6


def test_all_zero_similarity_gives_half():
    S = np.eye(3, dtype=np.float32)
    ia = np.array([0, 0])
    ib = np.array([1, 1])
    y = np.array([1, 1])
    _, raw = closest_pairs(S, ia, ib, y, np.array([0, 1]), 2, 2, k=2)
    assert raw == 0.5