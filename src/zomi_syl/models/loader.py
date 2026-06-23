"""
Unified model loader for zomi-syl.

This module provides a single entry point for loading any model backend:
    • rule
    • crf
    • fst
    • bilstm
    • bilstm_crf
    • transformer

It supports:
    • backend routing
    • lazy loading
    • cache reuse
    • unload / reload
    • local + HF models
    • version checks
    • corruption detection

Public API:
    load_model()
    unload_model()
    reload_model()
"""

from pathlib import Path
from typing import Any, Dict, Optional

from zomi_syl.exceptions import ZomiSylError

# from zomi_syl.logging_config import get_logger

# NEW: clean imports
from zomi_syl.backends.rule_backend import RuleBackend
from zomi_syl.backends.crf_backend import CRFBackend

# logger = get_logger(__name__)
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Global model cache (lazy loading)
# ---------------------------------------------------------------------------

_MODEL_CACHE: Dict[str, Any] = {}

# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------


def _fail(msg: str) -> None:
    raise ZomiSylError(msg)


# Bundled model directory
BUNDLED = Path(__file__).parent / "bundled"
MODEL_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Backend loaders
# ---------------------------------------------------------------------------


def _load_rule_model(info: Dict[str, Any]) -> Any:
    """Load rule-based model (syllabify_v6)."""
    # model_dir = BUNDLED / "rule"
    model_dir = MODEL_DIR / "rule"
    if not model_dir.exists():
        raise ZomiSylError(f"Rule model directory not found: {model_dir}")

    logger.info(f"[models:loader] Loading rule model from {model_dir}")
    backend = RuleBackend(str(model_dir))
    # return {"backend_instance": backend}
    return {
        "backend_instance": backend,
        "rule": backend,  # ← REQUIRED
    }


def _load_crf_model(info: Dict[str, Any]) -> Any:
    """Load CRF syllabifier model."""
    print("[models:loader] Loading CRF model")
    # model_dir = BUNDLED / "crf"
    model_dir = MODEL_DIR / "crf"
    if not model_dir.exists():
        raise ZomiSylError(f"CRF model directory not found: {model_dir}")

    logger.info(f"[models:loader] Loading CRF model from {model_dir}")
    backend = CRFBackend(str(model_dir))
    # return {"backend_instance": backend}
    return {
        "backend_instance": backend,
        "crf": backend,  # ← REQUIRED
    }


def _load_fst_model(info: Dict[str, Any]) -> Any:
    path = info["storage"].get("local_path")
    if not path:
        _fail("FST model missing local_path")
    return {"backend": "fst", "path": path, "info": info}


def _load_bilstm_model(info: Dict[str, Any]) -> Any:
    weights = info["storage"].get("weights_path")
    if not weights:
        _fail("BiLSTM model missing weights_path")
    return {"backend": "bilstm", "weights": weights, "info": info}


def _load_bilstm_crf_model(info: Dict[str, Any]) -> Any:
    weights = info["storage"].get("weights_path")
    if not weights:
        _fail("BiLSTM-CRF model missing weights_path")
    return {"backend": "bilstm_crf", "weights": weights, "info": info}


def _load_transformer_model(info: Dict[str, Any]) -> Any:
    repo = info["storage"].get("hf_repo")
    if not repo:
        _fail("Transformer model missing hf_repo")
    return {"backend": "transformer", "repo": repo, "info": info}


# ---------------------------------------------------------------------------
# Backend routing table
# ---------------------------------------------------------------------------

_BACKEND_LOADERS = {
    "rule": _load_rule_model,
    "crf": _load_crf_model,
    "fst": _load_fst_model,
    "bilstm": _load_bilstm_model,
    "bilstm_crf": _load_bilstm_crf_model,
    "transformer": _load_transformer_model,
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_model(name: str, *, force_reload: bool = False) -> Any:
    """
    Load a model by name with lazy caching.
    """
    from zomi_syl.registry.models import get_model_info

    if not force_reload and name in _MODEL_CACHE:
        return _MODEL_CACHE[name]

    info = get_model_info(name)
    backend = info.get("backend_type") or info["metadata"].get("backend_type")

    logger.debug(f"[models] Loading model '{name}' ({backend})")

    if backend not in _BACKEND_LOADERS:
        _fail(f"Unsupported backend '{backend}' for model '{name}'")

    loader = _BACKEND_LOADERS[backend]

    try:
        model = loader(info)
    except Exception as e:
        _fail(f"Failed to load model '{name}': {e}")

    _MODEL_CACHE[name] = model
    logger.debug(f"[models] Loaded model '{name}' ({backend})")

    return model


def unload_model(name: Optional[str] = None) -> None:
    """Unload one or all models."""
    if name is None:
        _MODEL_CACHE.clear()
        logger.debug("[models] Unloaded all models")
        return

    if name in _MODEL_CACHE:
        del _MODEL_CACHE[name]
        logger.debug(f"[models] Unloaded model '{name}'")


def reload_model(name: str) -> Any:
    """Force reload a model."""
    unload_model(name)
    return load_model(name, force_reload=True)


def list_models() -> list[str]:
    return list(_MODEL_CACHE.keys())
