"""Predictor: loads BiLSTM_CNN or MLP bundle, falls back to stub.

Auto-detects models/ directory relative to repo root if MODEL_DIR not set.
Defaults TEAM_ID to 1378 (UC San Diego) if not set.
"""
from __future__ import annotations
import logging, os, pickle, warnings
from pathlib import Path
from typing import Optional
import numpy as np
from .schemas import Prediction, PredictionInput

log = logging.getLogger(__name__)

_NUMERIC_COLS    = ["score_diff","setter_position","consecutive_same","set_number","timeout_active_3"]
_CATEGORICAL_COLS = ["prev_1","prev_2","prev_3","prev_4","prev_5","setter_id","reception_quality"]
_STUB_CATS = ("Front","Middle","Back","Pipe")

_REPO_ROOT = Path(__file__).resolve().parents[2]


class _Bundle:
    def __init__(self, raw: dict) -> None:
        self.gb         = raw["gb"]
        self.scaler     = raw["scaler"]
        self.encoders   = raw["feature_encoders"]
        self.target_le  = raw["target_le"]
        self.classes    = list(self.target_le.classes_)
        self.team_id    = str(raw.get("team_id","unknown"))
        self.model_type = raw.get("model_type","mlp")
        self.gb_w       = float(raw.get("gb_weight", 0.4))
        self.nn_w       = float(raw.get("bilstm_weight", raw.get("mlp_weight", 0.6)))
        self.nn_model   = None
        n_feat = raw["n_features"]; n_cls = raw["n_classes"]
        try:
            import torch
            if self.model_type == "bilstm_cnn" and "bilstm_state_dict" in raw:
                from .bilstm_cnn import BiLSTM_CNN
                m = BiLSTM_CNN(n_feat, n_cls); m.load_state_dict(raw["bilstm_state_dict"]); m.eval()
                self.nn_model = m
                log.info("predictor: BiLSTM_CNN loaded for team %s", self.team_id)
            elif "mlp_state_dict" in raw:
                from .mlp import MLP
                m = MLP(n_feat, n_cls); m.load_state_dict(raw["mlp_state_dict"]); m.eval()
                self.nn_model = m
                log.info("predictor: MLP loaded for team %s", self.team_id)
        except Exception:
            log.warning("predictor: neural net load failed for team %s — GBM-only", self.team_id)

    def _encode(self, features: PredictionInput) -> "np.ndarray":
        feat = features.model_dump(); row: list[float] = []
        for col in _NUMERIC_COLS:
            v = feat.get(col); row.append(float(v) if v is not None else 0.0)
        for col in _CATEGORICAL_COLS:
            val = str(feat.get(col) or "None"); le = self.encoders.get(col)
            row.append(float(le.transform([val])[0]) if le is not None and val in le.classes_ else 0.0)
        return np.array(row).reshape(1,-1)

    def predict_proba(self, features: PredictionInput) -> list[tuple[str,float]]:
        X = self._encode(features)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            gb_p = self.gb.predict_proba(X)
        if self.nn_model is not None:
            try:
                import torch
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    X_s = self.scaler.transform(X)
                with torch.no_grad():
                    nn_p = torch.softmax(self.nn_model(torch.FloatTensor(X_s)),dim=1).numpy()
                probs = (self.gb_w*gb_p + self.nn_w*nn_p)[0] if gb_p.shape[1]==nn_p.shape[1] else gb_p[0]
            except Exception:
                probs = gb_p[0]
        else:
            probs = gb_p[0]
        return sorted([(cls,float(probs[i])) for i,cls in enumerate(self.classes) if i<len(probs)],
                      key=lambda x:x[1], reverse=True)


_bundle: Optional[_Bundle] = None
_loaded = False


def _load() -> Optional[_Bundle]:
    # MODEL_DIR: env var, else auto-detect repo models/ dir
    model_dir = os.environ.get("MODEL_DIR","").strip()
    if not model_dir:
        candidate = _REPO_ROOT / "models"
        if candidate.exists():
            model_dir = str(candidate)
            log.info("predictor: MODEL_DIR not set, using %s", model_dir)
        else:
            log.warning("predictor: MODEL_DIR not set and no models/ dir found — stub")
            return None

    # TEAM_ID: env var, else default to 1378 (UC San Diego)
    team_id = os.environ.get("TEAM_ID","1378").strip()

    path = Path(model_dir) / f"{team_id}_bundle.pkl"
    if not path.exists():
        # Try float-suffixed filename e.g. 1378.0_bundle.pkl
        alt = Path(model_dir) / f"{team_id}.0_bundle.pkl"
        if alt.exists():
            path = alt
        else:
            log.warning("predictor: bundle not found at %s — stub", path)
            return None
    try:
        with open(path,"rb") as fh: raw = pickle.load(fh)
        b = _Bundle(raw)
        log.info("predictor: loaded %s bundle (%d classes, model=%s)", b.team_id, len(b.classes), b.model_type)
        return b
    except Exception:
        log.exception("predictor: load failed — stub"); return None


def _get() -> Optional[_Bundle]:
    global _bundle, _loaded
    if not _loaded: _bundle = _load(); _loaded = True
    return _bundle


def predict(features: PredictionInput, *, prediction_count: int) -> Prediction:
    bundle = _get()
    if bundle is None:
        p = 1.0/len(_STUB_CATS)
        return Prediction(prediction_count=prediction_count,
                          top_k=[(c,p) for c in _STUB_CATS], note="stub")
    try:
        top_k = bundle.predict_proba(features)
        mode  = bundle.model_type if bundle.nn_model else "gbm-only"
        return Prediction(prediction_count=prediction_count, top_k=top_k,
                          note=f"{mode}-team-{bundle.team_id}")
    except Exception:
        log.exception("predictor: inference error")
        p = 1.0/len(_STUB_CATS)
        return Prediction(prediction_count=prediction_count,
                          top_k=[(c,p) for c in _STUB_CATS], note="stub-error-fallback")
