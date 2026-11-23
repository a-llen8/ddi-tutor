"""Tanimoto similarity. Needs only numpy, so the app can use it without xgboost."""
import numpy as np


def tanimoto(F):
    F = F.astype(np.float32)
    inter = F @ F.T
    n = F.sum(axis=1)
    union = n[:, None] + n[None, :] - inter
    return np.where(union > 0, inter / union, 0).astype(np.float32)
