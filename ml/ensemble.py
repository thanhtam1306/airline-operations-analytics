"""
Ensemble model combining diverse gradient-boosted predictors for flight delay risk.
"""
from __future__ import annotations

import numpy as np


class SoftVotingEnsemble:
    """
    Weighted soft-voting ensemble combining predictions from diverse classifiers
    (e.g., LightGBM, CatBoost, XGBoost) to reduce variance and improve generalization.
    """

    def __init__(self, models: dict[str, any], weights: dict[str, float] | None = None):
        self.models = models
        if weights is None:
            self.weights = {m: 1.0 / len(models) for m in models}
        else:
            total = sum(weights.values())
            self.weights = {m: w / total for m, w in weights.items()}

    def predict_proba(self, X) -> np.ndarray:
        prob = np.zeros(len(X), dtype=float)
        for name, model in self.models.items():
            w = self.weights.get(name, 1.0 / len(self.models))
            prob += w * model.predict_proba(X)[:, 1]
        prob = np.clip(prob, 0.0, 1.0)
        return np.column_stack([1.0 - prob, prob])

    def predict(self, X, threshold: float = 0.5) -> np.ndarray:
        return (self.predict_proba(X)[:, 1] >= threshold).astype(int)
