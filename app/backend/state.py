"""Match-level state tracking — mirrors extract_team_features + add_memory."""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Optional

# Exact mapping from fsbo_final_model.py
ATTACK_MAPPING: dict[str, str] = {
    "X6": "Front", "X5": "Front", "V5": "Front", "X9": "Front", "X0": "Front", "V0": "Front",
    "XM": "Middle", "X1": "Middle", "X2": "Middle", "XR": "Middle", "XB": "Middle",
    "X7": "Middle", "X3": "Middle",
    "X8": "Back", "V8": "Back", "XO": "Back", "XS": "Back", "CF": "Back", "CB": "Back",
    "VP": "Pipe", "XP": "Pipe",
}

GOOD_RECEPTION: frozenset[str] = frozenset({"#", "+"})


def categorize_attack(attack_code: Optional[str]) -> str:
    if not attack_code:
        return "Other"
    return ATTACK_MAPPING.get(attack_code, "Other")


@dataclass
class MatchState:
    match_id: Optional[str] = None
    current_set: int = 1
    current_point: Optional[int] = None
    home_score: int = 0
    visiting_score: int = 0
    home_setter_position: Optional[int] = None
    visiting_setter_position: Optional[int] = None
    home_setter_id: Optional[str] = None
    visiting_setter_id: Optional[str] = None
    segment_id: int = 0
    _last_match: Optional[str] = None
    _last_set: Optional[int] = None
    plays_since_timeout: int = 999_999
    _last_seen_point: Optional[tuple] = None
    attack_history: Deque[str] = field(default_factory=lambda: deque(maxlen=5))
    prediction_count: int = 0

    def on_set_change(self, match_id: Optional[str], set_number: int) -> None:
        if match_id != self._last_match or set_number != self._last_set:
            self.segment_id += 1
            self._last_match = match_id
            self._last_set = set_number
            self.plays_since_timeout = 999_999
            self.current_set = set_number
            if match_id is not None:
                self.match_id = match_id

    def on_timeout(self) -> None:
        self.plays_since_timeout = 0
        self.segment_id += 1

    def on_point_seen(self, match_id: Optional[str], point_id: Optional[int]) -> None:
        if point_id is None:
            return
        key = (match_id, point_id)
        if key != self._last_seen_point:
            self.plays_since_timeout += 1
            self._last_seen_point = key
            self.current_point = point_id

    @property
    def timeout_active_3(self) -> int:
        return 1 if self.plays_since_timeout <= 3 else 0

    def consecutive_same(self) -> int:
        if not self.attack_history:
            return 0
        latest = self.attack_history[0]
        n = sum(1 for cat in self.attack_history if cat == latest)
        return max(n - 1, 0)

    def prev_n(self, n: int) -> str:
        if n < 1 or n > 5:
            return "None"
        try:
            return self.attack_history[n - 1]
        except IndexError:
            return "None"

    def record_attack(self, category: str) -> None:
        if category and category != "Other":
            self.attack_history.appendleft(category)
