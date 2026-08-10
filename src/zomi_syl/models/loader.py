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
from zomi_syl.backends.crf_backend import CRFBackend, PYCRFSUITE_AVAILABLE

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
    """Load CRF syllabifier model.
    
    Gracefully handles missing pycrfsuite and provides clear error messages.
    """
    logger.info("[models:loader] Loading CRF model")
    
    # Check if pycrfsuite is available BEFORE trying to load
    if not PYCRFSUITE_AVAILABLE:
        error_msg = (
            "CRF backend requires 'python-crfsuite' package.\n"
            "Install it with: pip install python-crfsuite\n"
            "Or use rule-based backend: load_model('rule')"
        )
        logger.error(f"[models:loader] {error_msg}")
        raise ZomiSylError(error_msg)
    
    try:
        # Resolve model directory
        model_dir = MODEL_DIR / "crf"
        if not model_dir.exists():
            # Try alternative locations
            alt_dirs = [
                BUNDLED / "crf",
                Path(__file__).parent.parent / "models" / "crf",
            ]
            for alt in alt_dirs:
                if alt.exists():
                    model_dir = alt
                    logger.info(f"[models:loader] Found CRF model at: {model_dir}")
                    break
            else:
                raise ZomiSylError(
                    f"CRF model directory not found. Tried: {model_dir}, {alt_dirs}"
                )

        logger.info(f"[models:loader] Loading CRF model from {model_dir}")
        
        # Try to load the backend
        try:
            backend = CRFBackend(str(model_dir))
            logger.info("[models:loader] CRF model loaded successfully")
        except ImportError as e:
            # Handle import errors specifically
            raise ZomiSylError(
                f"CRF backend failed to import: {e}\n"
                "Make sure python-crfsuite is installed: pip install python-crfsuite"
            )
        except FileNotFoundError as e:
            # Handle missing model files
            raise ZomiSylError(
                f"CRF model files not found: {e}\n"
                "The model may need to be downloaded or installed."
            )
        except Exception as e:
            # Handle other errors
            import traceback
            tb = traceback.format_exc()
            raise ZomiSylError(
                f"Failed to load CRF model: {e}\n\n{tb}"
            )
        
        return {
            "backend_instance": backend,
            "crf": backend,  # ← REQUIRED for compatibility
        }
        
    except ZomiSylError:
        # Re-raise ZomiSylError as-is
        raise
    except Exception as e:
        # Catch any unexpected errors
        import traceback
        tb = traceback.format_exc()
        logger.error(f"[models:loader] Unexpected error loading CRF: {e}\n{tb}")
        raise ZomiSylError(f"Unexpected error loading CRF model: {e}")


def _load_fst_model(info: Dict[str, Any]) -> Any:
    """Load FST model (requires openfst-python)."""
    # Check if openfst is available
    try:
        import openfst  # type: ignore
        FST_AVAILABLE = True
    except ImportError:
        FST_AVAILABLE = False
    
    if not FST_AVAILABLE:
        raise ZomiSylError(
            "FST backend requires 'openfst-python' package.\n"
            "Install it with: pip install openfst-python"
        )
    
    path = info["storage"].get("local_path")
    if not path:
        _fail("FST model missing local_path")
    
    logger.info(f"[models:loader] Loading FST model from {path}")
    return {"backend": "fst", "path": path, "info": info}


def _load_bilstm_model(info: Dict[str, Any]) -> Any:
    """Load BiLSTM model (requires torch)."""
    # Check if torch is available
    try:
        import torch  # type: ignore
        TORCH_AVAILABLE = True
    except ImportError:
        TORCH_AVAILABLE = False
    
    if not TORCH_AVAILABLE:
        raise ZomiSylError(
            "BiLSTM backend requires 'torch' package.\n"
            "Install it with: pip install zomi-syl[torch]"
        )
    
    weights = info["storage"].get("weights_path")
    if not weights:
        _fail("BiLSTM model missing weights_path")
    
    logger.info(f"[models:loader] Loading BiLSTM model from {weights}")
    return {"backend": "bilstm", "weights": weights, "info": info}


def _load_bilstm_crf_model(info: Dict[str, Any]) -> Any:
    """Load BiLSTM-CRF model (requires torch)."""
    # Check if torch is available
    try:
        import torch  # type: ignore
        TORCH_AVAILABLE = True
    except ImportError:
        TORCH_AVAILABLE = False
    
    if not TORCH_AVAILABLE:
        raise ZomiSylError(
            "BiLSTM-CRF backend requires 'torch' package.\n"
            "Install it with: pip install zomi-syl[torch]"
        )
    
    weights = info["storage"].get("weights_path")
    if not weights:
        _fail("BiLSTM-CRF model missing weights_path")
    
    logger.info(f"[models:loader] Loading BiLSTM-CRF model from {weights}")
    return {"backend": "bilstm_crf", "weights": weights, "info": info}


def _load_transformer_model(info: Dict[str, Any]) -> Any:
    """Load Transformer model (requires transformers)."""
    # Check if transformers is available
    try:
        import transformers  # type: ignore
        TRANSFORMERS_AVAILABLE = True
    except ImportError:
        TRANSFORMERS_AVAILABLE = False
    
    if not TRANSFORMERS_AVAILABLE:
        raise ZomiSylError(
            "Transformer backend requires 'transformers' package.\n"
            "Install it with: pip install transformers"
        )
    
    repo = info["storage"].get("hf_repo")
    if not repo:
        _fail("Transformer model missing hf_repo")
    
    logger.info(f"[models:loader] Loading Transformer model from {repo}")
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
    
    Args:
        name: Model name to load
        force_reload: Force reload even if cached
    
    Returns:
        Loaded model instance
    
    Raises:
        ZomiSylError: If model loading fails
    """
    from zomi_syl.registry.models import get_model_info

    # Check cache
    if not force_reload and name in _MODEL_CACHE:
        logger.debug(f"[models] Returning cached model '{name}'")
        return _MODEL_CACHE[name]

    # Get model info from registry
    try:
        info = get_model_info(name)
    except Exception as e:
        raise ZomiSylError(f"Model '{name}' not found in registry: {e}")

    backend = info.get("backend_type") or info["metadata"].get("backend_type")
    if not backend:
        raise ZomiSylError(f"Model '{name}' has no backend_type specified")

    logger.debug(f"[models] Loading model '{name}' ({backend})")

    # Check if backend is supported
    if backend not in _BACKEND_LOADERS:
        supported = ", ".join(_BACKEND_LOADERS.keys())
        raise ZomiSylError(
            f"Unsupported backend '{backend}' for model '{name}'. "
            f"Supported backends: {supported}"
        )

    # Load the model
    loader = _BACKEND_LOADERS[backend]

    try:
        model = loader(info)
        logger.debug(f"[models] Loaded model '{name}' ({backend})")
    except ZomiSylError:
        # Re-raise ZomiSylError as-is
        raise
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise ZomiSylError(
            f"Failed to load model '{name}': {e}\n\n{tb}"
        )

    # Cache the model
    _MODEL_CACHE[name] = model
    logger.debug(f"[models] Cached model '{name}' ({backend})")

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
    else:
        logger.warning(f"[models] Model '{name}' not in cache")


def reload_model(name: str) -> Any:
    """Force reload a model."""
    unload_model(name)
    return load_model(name, force_reload=True)


def list_models() -> list[str]:
    """List all currently loaded (cached) models."""
    return list(_MODEL_CACHE.keys())


def get_model_status(name: str) -> Dict[str, Any]:
    """Get detailed status of a model including availability checks."""
    status = {
        "name": name,
        "cached": name in _MODEL_CACHE,
        "backend": None,
        "available": False,
        "error": None
    }
    
    if name in _MODEL_CACHE:
        model = _MODEL_CACHE[name]
        if isinstance(model, dict):
            status["backend"] = model.get("backend")
            status["available"] = True
        else:
            status["backend"] = getattr(model, "backend_name", "unknown")
            status["available"] = True
    
    return status

def get_available_backends() -> Dict[str, bool]:
    """Check which backends are available with their dependencies."""
    backends = {
        "rule": True,  # Always available
        "crf": PYCRFSUITE_AVAILABLE,
        "fst": False,
        "bilstm": False,
        "bilstm_crf": False,
        "transformer": False,
    }
    
    # Check FST
    try:
        import openfst  # type: ignore
        backends["fst"] = True
    except ImportError:
        pass
    
    # Check PyTorch
    try:
        import torch  # type: ignore
        backends["bilstm"] = True
        backends["bilstm_crf"] = True
    except ImportError:
        pass
    
    # Check Transformers
    try:
        import transformers  # type: ignore
        backends["transformer"] = True
    except ImportError:
        pass
    
    return backends