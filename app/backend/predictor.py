"""Predictor — loads a trained FSBO model bundle or falls back to a uniform stub.

Model bundles are produced by Section 8 of fsbo_final_model.py and saved as:
    {MODEL_DIR}/{team_id}_bundle.pkl

Environment variables
---------------------
MODEL_DIR   Path to directory containing *_bundle.pkl files.
TEAM_ID     team_id whose bundle to load (matches the CSV team_id column).

If either variable is unset or the file is missing the stub fires instead,
returning a uniform distribution — all SSE / UI plumbing still works fine.

Bundle schema (written by fsbo_final_model.py)
----------------------------------------------
{
    "team_id":         str,
    "gb":              GradientBoostingClassifier,
    "mlp_state_dict":  OrderedDict  (optional — falls back to GBM-only if absent),
    "scaler":          StandardScaler,
    "feature_encoders": dict[str, LabelEncoder],
    "target_le":       LabelEncoder,
    "n_features":      int,
    "n_classes":       int,
}
"""
from __future__ import annotations

import logging
import os
import pickle
from pathlib import Path
from typing import Optional

import numpy as np

from .schemas import Prediction, PredictionInput

log = logging.getLogger(__name__)

_NUMERIC_COLS  = ["score_diff", "setter_position", "consecutive_same", "set_number", "timeout_active_3"]
_CATEGORICAL_COLS = ["prev_1", "prev_2", "prev_3", "prev_4", "prev_5", "setter_id", "reception_quality"]
_STUB_CATEGORIES = ("Front", "Middle", "Back", "Pipe")


# ── Bundle wrapper ─────────────────────────────────────────────────────────────

class _Bundle:
    def __init__(self, raw: dict) -> None:
        self.gb     = raw["gb"]
        self.scaler = raw["scaler"]
        self.encoders: dict = raw["feature_encoders"]
        self.target_le      = raw["target_le"]
        self.classes: list[str] = list(self.target_le.classes_)
        self.team_id: str   = str(raw.get("team_id", "unknown"))

        # Optional MLP (requires torch)
        self.mlp = None
        if "mlp_state_dict" in raw:
            try:
                import torch
                from .mlp import MLP
                mlp = MLP(raw["n_features"], raw["n_classes"])
                mlp.load_state_dict(raw["mlp_state_dict"])
                mlp.eval()
                self.mlp = mlp
                log.info("predictor: MLP loaded for team %s", self.team_id)
            except Exception:
                log.warning("predictor: torch not available or MLP load failed — GBM-only mode")

    def predict_proba(self, features: PredictionInput) -> list[tuple[str, float]]:
        feat = features.model_dump()
        row: list[float] = []

        for col in _NUMERIC_COLS:
            val = feat.get(col)
            row.append(float(val) if val is not None else 0.0)

        for col in _CATEGORICAL_COLS:
            val = str(feat.get(col) or "None")
            le  = self.encoders.get(col)
            if le is not None and val in le.classes_:
                row.append(float(le.transform([val])[0]))
            else:
                row.append(0.0)

        X = np.array(row).reshape(1, -1)
        gb_p = self.gb.predict_proba(X)

        if self.mlp is not None:
            try:
                import torch
                X_s = self.scaler.transform(X)
                with torch.no_grad():
                    mlp_p = torch.softmax(
                        self.mlp(torch.FloatTensor(X_s)), dim=1
                    ).numpy()
                if gb_p.shape[1] == mlp_p.shape[1]:
                    probs = (0.4 * gb_p + 0.6 * mlp_p)[0]
                else:
                    probs = gb_p[0]
            except Exception:
                probs = gb_p[0]
        else:
            probs = gb_p[0]

        pairs = [(cls, float(probs[i])) for i, cls in enumerate(self.classes) if i < len(probs)]
        return sorted(pairs, key=lambda x: x[1], reverse=True)


# ── Loading ────────────────────────────────────────────────────────────────────

_bundle: Optional[_Bundle] = None
_bundle_loaded = False   # track whether we've attempted a load already


def _load() -> Optional[_Bundle]:
    model_dir = os.environ.get("MODEL_DIR", "").strip()
    team_id   = os.environ.get("TEAM_ID",   "").strip()

    if not model_dir or not team_id:
        log.info("predictor: MODEL_DIR/TEAM_ID not configured — stub mode")
        return None

    path = Path(model_dir) / f"{team_id}_bundle.pkl"
    if not path.exists():
        log.warning("predictor: bundle not found at %s — stub mode", path)
        return None

    try:
        with open(path, "rb") as fh:
            raw = pickle.load(fh)
        b = _Bundle(raw)
        log.info("predictor: loaded bundle for team %s (%d classes)", b.team_id, len(b.classes))
        return b
    except Exception:
        log.exception("predictor: failed to load bundle — stub mode")
        return None


def _get() -> Optional[_Bundle]:
    global _bundle, _bundle_loaded
    if not _bundle_loaded:
        _bundle = _load()
        _bundle_loaded = True
    return _bundle


# ── Public API ─────────────────────────────────────────────────────────────────

def predict(features: PredictionInput, *, prediction_count: int) -> Prediction:
    bundle = _get()

    if bundle is None:
        prob = 1.0 / len(_STUB_CATEGORIES)
        return Prediction(
            prediction_count=prediction_count,
            top_k=[(c, prob) for c in _STUB_CATEGORIES],
            note="stub-predictor",
        )

    try:
        top_k = bundle.predict_proba(features)
        mode  = "gbm+mlp" if bundle.mlp else "gbm-only"
        return Prediction(
            prediction_count=prediction_count,
            top_k=top_k,
            note=f"{mode}-team-{bundle.team_id}",
        )
    except Exception:
        log.exception("predictor: inference error — falling back to stub")
        prob = 1.0 / len(_STUB_CATEGORIES)
        return Prediction(
            prediction_count=prediction_count,
            top_k=[(c, prob) for c in _STUB_CATEGORIES],
            note="stub-predictor (error fallback)",
        )
