"""Match-level state tracking and attack-code → category mapping.

Mirrors the bookkeeping in `extract_team_features` (segment_id rolling,
timeout window, point tracking) and `add_memory` (prev_1..prev_5,
consecutive_same), but applied incrementally as Touches arrive instead of
batch-applied to a finished DataFrame.

The predictor is built FROM THE OPPONENT'S PERSPECTIVE — we predict the
visiting team's first-ball side-out attacks. All "their" references below
mean the team configured as the opponent (default: visiting).
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Optional

# ---------------------------------------------------------------------------
# ATTACK_MAPPING — PLACEHOLDER.
#
# The user's training pipeline uses `ATTACK_MAPPING` (not shared in the
# snippet) to project DataVolley attack codes to one of: Front / Middle /
# Back / Pipe / Other. Categories with 'Other' are dropped from training and
# inference. The mapping below is a reasonable starter based on common
# DataVolley conventions. REPLACE WITH THE REAL MAPPING from the notebook
# before going live.
# ---------------------------------------------------------------------------
ATTACK_MAPPING: dict[str, str] = {
    # Outside / left-side attacks
    "V5": "Front", "X5": "Front", "X6": "Front", "V6": "Front",
    # Middle / quick attacks
    "X1": "Middle", "X2": "Middle", "V1": "Middle", "V3": "Middle",
    # Back-row attacks
    "V8": "Back", "X8": "Back",
    # Pipe attacks
    "VP": "Pipe", "XP": "Pipe", "V0": "Pipe",
}

# Reception evaluations that count as "good" — i.e. the FBSO model fires.
GOOD_RECEPTION: frozenset[str] = frozenset({"#", "+"})


def categorize_attack(attack_code: Optional[str]) -> str:
    """Map a DataVolley attack code to a category. Unknown/missing → 'Other'."""
    if not attack_code:
        return "Other"
    return ATTACK_MAPPING.get(attack_code, "Other")


@dataclass
class MatchState:
    """Running state across the file. One instance per ingestor session."""

    # Identity / position
    match_id: Optional[str] = None
    current_set: int = 1
    current_point: Optional[int] = None

    # Scoring (canonical from latest Touch context, if available)
    home_score: int = 0
    visiting_score: int = 0

    # Rotation (must be set manually for now — see manual_rotation_config).
    home_setter_position: Optional[int] = None
    visiting_setter_position: Optional[int] = None
    home_setter_id: Optional[str] = None
    visiting_setter_id: Optional[str] = None

    # Segment tracking — increments on new match/set and on each timeout.
    segment_id: int = 0
    _last_match: Optional[str] = None
    _last_set: Optional[int] = None

    # Timeout tracking — extract_team_features sets timeout_active_3 = 1 if
    # any of the last 3 plays were a timeout.
    plays_since_timeout: int = 999_999
    _last_seen_point: Optional[tuple] = None

    # Rolling attack history for prev_1..prev_5 and consecutive_same.
    # Stores attack categories (Front/Middle/Back/Pipe) in reverse-chronological
    # order: index 0 = most recent attack.
    attack_history: Deque[str] = field(default_factory=lambda: deque(maxlen=5))

    # Increments on each issued PredictionInput.
    prediction_count: int = 0

    def on_set_change(self, match_id: Optional[str], set_number: int) -> None:
        """Mirror extract_team_features: bump segment_id on new match/set."""
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
        """Increment the timeout window counter when a new point begins."""
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
        """Streak of the most-recent attack category in attack_history.

        Mirrors add_memory's `consecutive_same` — count consecutive prior
        plays whose target matched the latest one. Returns 0 if no history.
        """
        if not self.attack_history:
            return 0
        latest = self.attack_history[0]
        n = 0
        for cat in self.attack_history:
            if cat == latest:
                n += 1
            else:
                break
        # add_memory shifts by 1 — the streak that was running *before* current.
        # In our rolling-window terms: count of prev plays matching prev_1.
        return max(n - 1, 0)

    def prev_n(self, n: int) -> str:
        """Return prev_n category, or 'None' if history doesn't reach back that far."""
        if n < 1 or n > 5:
            return "None"
        try:
            return self.attack_history[n - 1]
        except IndexError:
            return "None"

    def record_attack(self, category: str) -> None:
        """Push an attack category onto the rolling window (appendleft)."""
        if category and category != "Other":
            self.attack_history.appendleft(category)
