"""Pydantic schemas for the live prediction pipeline.

These types are the contract between the parser, the ingestor, the feature
builder (later), the predictor (later), and the frontend. Field names mirror
the Volleymetrics CSV export columns where possible so that training-time and
inference-time features stay in sync.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

# DataVolley skill codes: Serve, Reception, Attack, Block, Dig, sEt, Freeball
Skill = Literal["S", "R", "A", "B", "D", "E", "F"]
TeamSide = Literal["home", "visiting"]


class Play(BaseModel):
    """One coded touch from the live scout feed.

    `raw` keeps the original DataVolley scout-code line so downstream consumers
    can re-derive fields we haven't surfaced yet without re-tailing the file.
    """

    sequence: int = Field(description="Monotonic id assigned by the ingestor in file order")
    team_side: TeamSide
    player_number: Optional[int] = None
    skill: Skill
    evaluation_code: str = Field(description="DataVolley evaluation: # + ! - / =")
    attack_code: Optional[str] = None
    set_code: Optional[str] = None
    start_zone: Optional[int] = None
    end_zone: Optional[int] = None
    set_number: int = 1
    home_score: int = 0
    visiting_score: int = 0
    home_setter_position: Optional[int] = None
    visiting_setter_position: Optional[int] = None
    raw: str


class Prediction(BaseModel):
    """Output of the predictor stub (and, later, the real model).

    `top_k` is ordered most-likely-first. `note` is a placeholder while the
    real model isn't wired in — once it is, replace the stub's note with the
    model identifier.
    """

    play_count: int = Field(description="Number of plays consumed up to this prediction")
    last_play: Optional[Play] = None
    top_k: list[tuple[str, float]] = Field(
        default_factory=list,
        description="Ordered (attack_category, probability) pairs, most likely first",
    )
    note: str = "stub-predictor"
