"""
Unified ML prediction interface for zomi-syl.

Purpose:
    Provide a single, backend-agnostic prediction API for all ML backends:
        • CRF
        • BiLSTM
        • Transformer

Features:
    • Prediction abstraction (hide backend differences)
    • Batch prediction
    • Confidence extraction
    • Post-processing: tags → boundaries → syllables

Public API:
    predict()
    predict_batch()
    predict_proba()
"""

from typing import Any, Dict, List

from zomi_syl.exceptions import ZomiSylError

# from zomi_syl.logging_config import get_logger
from zomi_syl.models.loader import load_model
from zomi_syl.features import strip_and_flags, sent2features, labels_to_syllables

# logger = get_logger(__name__)
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------


def _fail(msg: str) -> None:
    raise ZomiSylError(msg)


# ---------------------------------------------------------------------------
# Backend-specific prediction
# ---------------------------------------------------------------------------


def _predict_crf(model_obj: Any, word: str) -> Dict[str, Any]:
    """
    CRF backend: predict labels and syllables for a single word.
    """
    chars, flags = strip_and_flags(word)
    feats = sent2features(chars, flags)
    labels = model_obj.predict_single(feats)
    syllables = labels_to_syllables(chars, labels)
    return {"labels": labels, "syllables": syllables}


def _predict_crf_proba(model_obj: Any, word: str) -> List[float]:
    """
    CRF backend: return per-character confidence scores (marginals).
    """
    chars, flags = strip_and_flags(word)
    feats = sent2features(chars, flags)
    marginals = model_obj.predict_marginals_single(feats)
    # Convert dict-of-label-probs to a single confidence per position
    # (e.g. probability of boundary label "B")
    scores: List[float] = []
    for pos_probs in marginals:
        scores.append(pos_probs.get("B", 0.0))
    return scores


def _predict_bilstm(model_obj: Any, word: str) -> Dict[str, Any]:
    """
    BiLSTM backend: placeholder for actual PyTorch inference.
    """
    raise NotImplementedError("BiLSTM backend prediction not implemented yet")


def _predict_bilstm_proba(model_obj: Any, word: str) -> List[float]:
    """
    BiLSTM backend: placeholder for confidence extraction.
    """
    raise NotImplementedError("BiLSTM backend probability not implemented yet")


def _predict_transformer(model_obj: Any, word: str) -> Dict[str, Any]:
    """
    Transformer backend: placeholder for actual HF inference.
    """
    raise NotImplementedError("Transformer backend prediction not implemented yet")


def _predict_transformer_proba(model_obj: Any, word: str) -> List[float]:
    """
    Transformer backend: placeholder for confidence extraction.
    """
    raise NotImplementedError("Transformer backend probability not implemented yet")


_BACKEND_PREDICT = {
    "crf": _predict_crf,
    "bilstm": _predict_bilstm,
    "bilstm_crf": _predict_bilstm,  # can share logic later
    "transformer": _predict_transformer,
}

_BACKEND_PROBA = {
    "crf": _predict_crf_proba,
    "bilstm": _predict_bilstm_proba,
    "bilstm_crf": _predict_bilstm_proba,
    "transformer": _predict_transformer_proba,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def predict(word: str, model_name: str) -> str:
    """
    Predict syllable boundaries for a single word.

    Returns:
        syllabified string, e.g. "thu-gen-na"
    """
    model = load_model(model_name)
    backend = model.get("backend")
    model_obj = model.get("model")

    if backend not in _BACKEND_PREDICT:
        _fail(f"Backend '{backend}' does not support prediction")

    result = _BACKEND_PREDICT[backend](model_obj, word)
    return result["syllables"]


def predict_proba(word: str, model_name: str) -> List[float]:
    """
    Return confidence scores for each character boundary in a word.

    Returns:
        list[float] aligned with characters in the input word.
    """
    model = load_model(model_name)
    backend = model.get("backend")
    model_obj = model.get("model")

    if backend not in _BACKEND_PROBA:
        _fail(f"Backend '{backend}' does not support probability extraction")

    return _BACKEND_PROBA[backend](model_obj, word)


def predict_batch(words: List[str], model_name: str) -> List[str]:
    """
    Batch prediction for multiple words.

    Returns:
        list of syllabified strings.
    """
    model = load_model(model_name)
    backend = model.get("backend")
    model_obj = model.get("model")

    if backend not in _BACKEND_PREDICT:
        _fail(f"Backend '{backend}' does not support prediction")

    fn = _BACKEND_PREDICT[backend]
    outputs: List[str] = []
    for w in words:
        result = fn(model_obj, w)
        outputs.append(result["syllables"])
    return outputs
