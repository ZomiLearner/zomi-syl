"""
Core orchestration engine for zomi-syl.

This module:
    • selects the correct backend (rule, CRF, FST, BiLSTM, Transformer)
    • performs fallback routing
    • handles model loading errors
    • validates profiles
    • exposes unified prediction API

Public API:
    get_backend()
    predict()
    predict_batch()
"""

from typing import List

# from zomi_syl.logging_config import get_logger
from zomi_syl.registry.profiles import load_profile
from zomi_syl.registry.models import model_exists
from zomi_syl.models.loader import load_model
from zomi_syl.validation.input_validator import validate_word, validate_characters
from zomi_syl.core.interfaces import Prediction
from zomi_syl.registry.models import list_installed_backends

# logger = get_logger(__name__)

import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Backend selection + fallback
# ---------------------------------------------------------------------------

FALLBACK_ORDER = [
    "transformer",
    "bilstm_crf",
    "bilstm",
    "crf",
    "fst",
    "rule",
]


def get_backend(requested: str) -> str:
    """
    Determine which backend to use, applying fallback logic.

    Example:
        requested="transformer"
        but transformer unavailable → CRF → rule
    """
    if requested == "auto":
        requested = FALLBACK_ORDER[0]

    if model_exists(requested):
        return requested

    logger.warning(f"[engine] Requested backend '{requested}' unavailable. Activating fallback.")

    # Fallback chain
    for backend in FALLBACK_ORDER:
        if model_exists(backend):
            logger.info(f"[engine] Fallback activated → using backend '{backend}'")
            return backend

    raise RuntimeError("No available backends. Installation is corrupted.")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_backend(backend_name: str):
    """
    Load backend model and return a backend instance implementing BaseSyllabifier or BasePredictor.

    In auto mode, failure to load a backend should NOT raise — it should allow fallback.
    Only explicit backend requests should raise.
    """
    try:
        model_obj = load_model(backend_name)
        return model_obj["backend_instance"]

    except Exception as e:
        # Log quietly so normal users never see it
        logger.debug(f"[engine] Backend '{backend_name}' unavailable: {e}")

        # IMPORTANT:
        # Do NOT raise — return None so the caller can continue fallback.
        return None


def _validate_input(word: str, dialect: str) -> None:
    """
    Validate input word and ensure characters are allowed by the profile.
    """
    word = validate_word(word)
    profile = load_profile(dialect)
    allowed_chars = profile.get("allowed_characters", None)

    if allowed_chars:
        validate_characters(word, allowed_chars)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


# def predict(
#     word: str, *, model: str = "auto", dialect: str = "auto", include_metadata: bool = False
# ) -> Prediction:
#     """
#     Predict syllable boundaries for a single word using the selected backend.
#     """
#     if dialect == "auto":
#         dialect = "tedim"

#     _validate_input(word, dialect)

#     logger.info(f"[engine] Predicting word={word!r}, model={model!r}, dialect={dialect!r}")
#     backend_name = get_backend(model)
#     backend = _load_backend(backend_name)

#     logger.info(f"[engine] Predicting with backend='{backend_name}', dialect='{dialect}'")

#     result = backend.predict(word)

#     if include_metadata:
#         meta = backend.get_metadata()
#         result.raw["metadata"] = meta

#     return result


def predict(
    word: str, *, model: str = "auto", dialect: str = "auto", include_metadata: bool = False
) -> Prediction:
    """
    Predict syllable boundaries for a single word using the selected backend.
    """
    if dialect == "auto":
        dialect = "tedim"

    _validate_input(word, dialect)

    logger.debug(f"[engine] Predicting word={word!r}, model={model!r}, dialect={dialect!r}")

    # -----------------------------
    # 1. AUTO MODE
    # -----------------------------
    if model == "auto":

        # Try transformer
        backend = _load_backend("transformer")
        if backend is not None:
            logger.debug("[engine] Using transformer backend")
            return _run_backend(backend, word, include_metadata)

        # Try CRF
        backend = _load_backend("crf")
        if backend is not None:
            logger.debug("[engine] Using CRF backend")
            return _run_backend(backend, word, include_metadata)

        # Fall back to rule
        backend = _load_backend("rule")
        logger.debug("[engine] Using rule backend (fallback)")
        return _run_backend(backend, word, include_metadata)

    # -----------------------------
    # 2. EXPLICIT BACKEND REQUEST
    # -----------------------------
    backend = _load_backend(model)
    if backend is None:

        # s_msg =  f"Requested backend '{model}' is unavailable"
        available = list_installed_backends()
        msg = (
            f"The requested backend '{model}' is not installed.\n"
            f"Available backends: {', '.join(available) if available else 'none'}\n"
            f"Tip: Install the '{model}' model or omit --backend to use automatic fallback."
        )
        raise RuntimeError(msg)

    return _run_backend(backend, word, include_metadata)

def _run_backend(backend, word, include_metadata):
    result = backend.predict(word)
    if include_metadata:
        result.raw["metadata"] = backend.get_metadata()
    return result


def predict_batch(
    words: List[str], *, model: str = "auto", dialect: str = "auto", include_metadata: bool = False
) -> List[Prediction]:
    """
    Batch prediction for multiple words.
    """
    if dialect == "auto":
        dialect = "tedim"

    for w in words:
        _validate_input(w, dialect)

    backend_name = get_backend(model)
    backend = _load_backend(backend_name)

    logger.info(f"[engine] Batch prediction with backend='{backend_name}', dialect='{dialect}'")

    results = backend.predict_batch(words)

    if include_metadata:
        meta = backend.get_metadata()
        for r in results:
            r.raw["metadata"] = meta

    return results


def run_syllabifier(
    word: str, model: str, dialect: str, include_metadata: bool = False
) -> Prediction:
    return predict(word, model=model, dialect=dialect, include_metadata=include_metadata)
