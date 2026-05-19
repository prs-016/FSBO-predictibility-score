"""Pydantic schemas for the live prediction pipeline.

Three nested concepts to keep straight:

* **Touch** — one scouted action in the .dvw file (one serve, one reception,
  one set, one attack, etc.). The ingestor emits one Touch per file line.

* **PredictionInput** — one row matching the *training* schema in
  `extract_team_features` + `add_memory`. Built by the feature builder when
  the opponent makes a `#`/`+` reception (the FBSO trigger). One Touch may
  produce zero or one PredictionInput.

* **Prediction** — model output (top-K attack categories with probabilities).
  One per PredictionInput.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

# DataVolley skill codes: Serve, Reception, Attack, Block, Dig, sEt, Freeball
Skill = Literal["S", "R", "A", "B", "D", "E", "F"]
TeamSide = Literal["home", "visiting"]
# Attack categories the model predicts. Match the training ATTACK_MAPPING values.
AttackCategory = Literal["Front", "Middle", "Back", "Pipe"]


class Touch(BaseModel):
    """One scouted action from the .dvw stream."""

    sequence: int = Field(description="Monotonic id assigned in file order")
    team_side: TeamSide
    player_number: Optional[int] = None
    skill: Skill
    evaluation_code: str = Field(description="DataVolley evaluation: # + ! - / =")
    attack_code: Optional[str] = None
    set_code: Optional[str] = None
    start_zone: Optional[int] = None
    end_zone: Optional[int] = None

    # Match-level context (filled by parser from trailing JSON in replay,
    # or in production from extra DVW positions). May be None if unknown.
    match_id: Optional[str] = None
    set_number: Optional[int] = None
    point_id: Optional[int] = None
    home_score: Optional[int] = None
    visiting_score: Optional[int] = None
    home_setter_position: Optional[int] = None
    visiting_setter_position: Optional[int] = None
    phase: Optional[str] = Field(default=None, description="Serve / Reception / Transition")
    set_player_id: Optional[str] = None
    point_differential: Optional[int] = None
    is_timeout: bool = False

    raw: str


class PredictionInput(BaseModel):
    """Feature row matching the training schema (`t_fbso`).

    Built by the feature builder when an opponent reception with eval `#`/`+`
    is observed. Mirrors `extract_team_features` + `add_memory` outputs so the
    training-time and inference-time feature contracts are byte-identical.
    """

    # Identifiers / context
    match_id: Optional[str] = None
    segment_id: int = 0
    set_number: int = 1
    point_id: Optional[int] = None

    # Numeric features (training: numeric_cols)
    score_diff: int = 0
    setter_position: Optional[int] = None
    consecutive_same: int = 0
    timeout_active_3: int = 0

    # Categorical features (training: categorical_cols)
    prev_1: str = "None"
    prev_2: str = "None"
    prev_3: str = "None"
    prev_4: str = "None"
    prev_5: str = "None"
    setter_id: Optional[str] = None
    reception_quality: str = Field(description="DataVolley eval code: # or +")


class Prediction(BaseModel):
    """Output of the predictor (stub or real)."""

    prediction_count: int = Field(description="Number of predictions issued this session")
    top_k: list[tuple[str, float]] = Field(
        default_factory=list,
        description="Ordered (attack_category, probability) pairs, most likely first",
    )
    note: str = "stub-predictor"
