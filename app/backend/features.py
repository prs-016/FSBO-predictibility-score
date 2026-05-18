"""Feature builder — STUB.

This is the stateful bridge between the live play stream and the model. It
maintains rolling state per match (prev_1..prev_5 attack categories, current
rotation, score, streak counter, etc.) and produces the feature row the
predictor expects.

The real implementation depends on the trained model's exact feature list,
which you said you'll provide later. The current stub returns an empty dict
so the pipeline can run end-to-end without it.

When the real model arrives, fill in `FeatureBuilder.update`:
    1. Update internal state from the incoming Play.
    2. Return the dict of features the predictor needs for the *next* prediction.
"""
from __future__ import annotations

from typing import Any

from .schemas import Play


class FeatureBuilder:
    """Maintains rolling match state across plays."""

    def __init__(self) -> None:
        self._play_count = 0

    def update(self, play: Play) -> dict[str, Any]:
        """Consume a play, return the feature row to pass to the predictor.

        Stub: returns minimal context. Replace when the real model is wired in.
        """
        self._play_count += 1
        return {
            "play_count": self._play_count,
            "last_skill": play.skill,
            "last_evaluation": play.evaluation_code,
        }

    @property
    def play_count(self) -> int:
        return self._play_count
