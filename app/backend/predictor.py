"""Predictor — STUB.

The real predictor will load a trained model (GBM/MLP/BiLSTM_CNN from the
notebook) and call `model.predict_proba(...)` on the encoded feature row.

The stub returns a uniform distribution over the four training categories
so the frontend and SSE plumbing are testable without the model artifact.

When the real model arrives:
    1. Load it at module import time and cache the handle.
    2. Encode `PredictionInput` the same way training did (the categorical
       encoders + scaler should be saved alongside the model).
    3. Return real top-K probabilities ordered descending.
    4. Update `Prediction.note` with the model identifier (e.g. "gbm-v3").
"""
from __future__ import annotations

from .schemas import Prediction, PredictionInput

_CATEGORIES: tuple[str, ...] = ("Front", "Middle", "Back", "Pipe")


def predict(features: PredictionInput, *, prediction_count: int) -> Prediction:
    """Stub predictor. Uniform distribution until the real model is wired in."""
    prob = 1.0 / len(_CATEGORIES)
    return Prediction(
        prediction_count=prediction_count,
        top_k=[(cat, prob) for cat in _CATEGORIES],
        note="stub-predictor",
    )
