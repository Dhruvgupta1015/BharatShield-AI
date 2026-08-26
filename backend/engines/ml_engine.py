"""
BharatShield AI — ML Inference Engine
Loads the serialized TF-IDF + LogReg phishing classifier and provides
inference for the live analysis pipeline.

Design:
- Lazy-loads model on first use
- Graceful fallback if artifacts are missing
- Isolated from rule-based detection logic
"""

import json
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Resolve artifact path relative to this file
# File location: backend/engines/ml_engine.py
# Artifacts:     ml/artifacts/ (from project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ARTIFACTS_DIR = _PROJECT_ROOT / "ml" / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "phishing_classifier.joblib"
METADATA_PATH = ARTIFACTS_DIR / "model_metadata.json"

# Module-level state (loaded once)
_pipeline = None
_metadata = None
_is_loaded = False
_load_error = None


def _load_model():
    """Attempt to load the serialized ML model. Called once on first use."""
    global _pipeline, _metadata, _is_loaded, _load_error

    if _is_loaded:
        return

    try:
        import joblib

        if not MODEL_PATH.exists():
            _load_error = f"Model artifact not found at {MODEL_PATH}"
            logger.warning(
                f"ML model not available: {_load_error}. "
                "Run `python ml/train_and_export.py` to generate artifacts."
            )
            _is_loaded = True
            return

        _pipeline = joblib.load(MODEL_PATH)
        logger.info(f"ML model loaded successfully from {MODEL_PATH}")

        if METADATA_PATH.exists():
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                _metadata = json.load(f)
            logger.info(
                f"Model metadata loaded: {_metadata.get('model_name')} "
                f"{_metadata.get('model_version', 'unknown')}"
            )

        _is_loaded = True

    except Exception as e:
        _load_error = str(e)
        logger.error(f"Failed to load ML model: {e}")
        _is_loaded = True


def is_available() -> bool:
    """Check if the ML model is loaded and ready for inference."""
    _load_model()
    return _pipeline is not None


def get_model_version() -> Optional[str]:
    """Return the model version string, or None if unavailable."""
    _load_model()
    if _metadata:
        return _metadata.get("model_version")
    return None


def predict(text: str) -> Tuple[Optional[str], Optional[float]]:
    """
    Run ML inference on a single text input.

    Returns:
        (prediction, confidence) where:
        - prediction: "phishing" or "benign" (None if model unavailable)
        - confidence: probability of the predicted class (None if unavailable)
    """
    _load_model()

    if _pipeline is None:
        return None, None

    try:
        pred = _pipeline.predict([text])[0]
        proba = _pipeline.predict_proba([text])[0]
        phishing_prob = float(proba[1])

        prediction = "phishing" if pred == 1 else "benign"
        confidence = phishing_prob if pred == 1 else (1.0 - phishing_prob)

        return prediction, round(confidence, 4)

    except Exception as e:
        logger.error(f"ML inference failed: {e}")
        return None, None


def get_phishing_probability(text: str) -> Optional[float]:
    """
    Return the raw phishing probability (0.0–1.0) for use in risk fusion.
    Returns None if the model is unavailable.
    """
    _load_model()

    if _pipeline is None:
        return None

    try:
        proba = _pipeline.predict_proba([text])[0]
        return round(float(proba[1]), 4)
    except Exception as e:
        logger.error(f"ML probability estimation failed: {e}")
        return None
