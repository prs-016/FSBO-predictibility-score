"""Feature builder — produces PredictionInput rows matching the training schema.

Mirrors `extract_team_features` + `add_memory` from the training notebook,
applied incrementally to a live Touch stream instead of batch-applied to a
finished DataFrame.

The single trigger that produces a PredictionInput:
    opponent reception with evaluation_code in {'#', '+'}

For every Touch:
  - Update match state (set_number, point_id, score, segment, timeout window).
  - If the Touch is an attack BY THE OPPONENT in Reception phase, push its
    category onto the rolling attack history (prev_1..prev_5).
  - If the Touch is an opponent reception with good eval, build and return
    the PredictionInput; otherwise return None.

Configuration: by default the opponent is the visiting side. Override via
the `opponent_side` constructor argument.
"""
from __future__ import annotations

from typing import Optional

from .schemas import PredictionInput, TeamSide, Touch
from .state import GOOD_RECEPTION, MatchState, categorize_attack


class FeatureBuilder:
    def __init__(self, opponent_side: TeamSide = "visiting") -> None:
        self.opponent_side = opponent_side
        self.state = MatchState()

    def update(self, touch: Touch) -> Optional[PredictionInput]:
        """Consume a Touch; return a PredictionInput iff the trigger fires."""
        # 1. Track set/match transitions for segment_id.
        if touch.set_number is not None:
            self.state.on_set_change(touch.match_id, touch.set_number)

        # 2. Track timeouts (timeout markers come through as Touch.is_timeout = True).
        if touch.is_timeout:
            self.state.on_timeout()

        # 3. Track new points for the timeout window counter.
        self.state.on_point_seen(touch.match_id, touch.point_id)

        # 4. Update canonical score from the Touch context.
        if touch.home_score is not None:
            self.state.home_score = touch.home_score
        if touch.visiting_score is not None:
            self.state.visiting_score = touch.visiting_score
        if touch.home_setter_position is not None:
            self.state.home_setter_position = touch.home_setter_position
        if touch.visiting_setter_position is not None:
            self.state.visiting_setter_position = touch.visiting_setter_position

        # 5. If this is an opponent attack in Reception phase, record its
        #    category in the rolling window — that's what the training pipeline
        #    feeds into prev_1..prev_5 / consecutive_same.
        if (
            touch.team_side == self.opponent_side
            and touch.skill == "A"
            and (touch.phase or "").lower() == "reception"
        ):
            category = categorize_attack(touch.attack_code)
            self.state.record_attack(category)

        # 6. The single prediction trigger: opponent good reception.
        if not self._is_prediction_trigger(touch):
            return None

        self.state.prediction_count += 1
        return self._build_input(touch)

    def _is_prediction_trigger(self, touch: Touch) -> bool:
        return (
            touch.team_side == self.opponent_side
            and touch.skill == "R"
            and touch.evaluation_code in GOOD_RECEPTION
        )

    def _build_input(self, touch: Touch) -> PredictionInput:
        is_opponent_home = self.opponent_side == "home"
        setter_position = (
            self.state.home_setter_position if is_opponent_home else self.state.visiting_setter_position
        )
        setter_id = self.state.home_setter_id if is_opponent_home else self.state.visiting_setter_id

        # score_diff from the opponent's perspective (mirrors point_differential
        # convention in the CSV — we use the per-Touch value when present).
        if touch.point_differential is not None:
            score_diff = touch.point_differential
        else:
            score_diff = (
                self.state.home_score - self.state.visiting_score
                if is_opponent_home
                else self.state.visiting_score - self.state.home_score
            )

        return PredictionInput(
            match_id=self.state.match_id,
            segment_id=self.state.segment_id,
            set_number=self.state.current_set,
            point_id=self.state.current_point,
            score_diff=score_diff,
            setter_position=setter_position,
            consecutive_same=self.state.consecutive_same(),
            timeout_active_3=self.state.timeout_active_3,
            prev_1=self.state.prev_n(1),
            prev_2=self.state.prev_n(2),
            prev_3=self.state.prev_n(3),
            prev_4=self.state.prev_n(4),
            prev_5=self.state.prev_n(5),
            setter_id=setter_id,
            reception_quality=touch.evaluation_code,
        )

    @property
    def prediction_count(self) -> int:
        return self.state.prediction_count
