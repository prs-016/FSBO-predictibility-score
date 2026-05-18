"""Predictor — STUB.

The real predictor will load a trained model (scikit-learn pipeline or PyTorch
network) and return calibrated probabilities over the next-attack categories.

The stub returns a uniform distribution over three placeholder categories
so the frontend and SSE plumbing are testable without the model artifact.

When the real model arrives:
    1. Load it at module import time (or first call) and cache the handle.
    2. Implement `predict(features)` to call `model.predict_proba(...)` and
       sort the (class, probability) pairs descending.
    3. Update `Prediction.note` with the model identifier (e.g. "gbm-v3").
"""
from __future__ import annotations

from typing import Any, Optional

from .schemas import Play, Prediction

_PLACEHOLDER_CATEGORIES: tuple[tuple[str, float], ...] = (
    ("Middle", 1 / 3),
    ("Front", 1 / 3),
    ("Back", 1 / 3),
)


def predict(features: dict[str, Any], *, last_play: Optional[Play] = None) -> Prediction:
    """Stub predictor. Returns a uniform distribution until the real model is wired in."""
    return Prediction(
        play_count=features.get("play_count", 0),
        last_play=last_play,
        top_k=list(_PLACEHOLDER_CATEGORIES),
        note="stub-predictor",
    )
