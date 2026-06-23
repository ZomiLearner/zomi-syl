"""
Model registry for zomi-syl.

This module provides a central catalog of every model known to the system.
It supports:

    • model metadata (name, version, backend_type, author, license)
    • storage information (local path, HF repo, download URL, cache)
    • capability information (supported profiles, GPU/CPU, batch mode)
    • version management (latest version, compatibility)

Public API:
    list_models()
    get_model_info()
    get_supported_profiles()
"""

import importlib
from pathlib import Path
from typing import Dict, Any, List

from zomi_syl.exceptions import ZomiSylError
from zomi_syl.utils.model_paths import resolve_model_path

# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)

import logging

logger = logging.getLogger(__name__)

BACKENDS = {
    "rule": "zomi_syl.backends.rule_backend.RuleBackend",
    "crf": "zomi_syl.backends.crf_backend.CRFBackend",
}

# ---------------------------------------------------------------------------
# Base directory
# ---------------------------------------------------------------------------

def _import_backend(path: str):
    module_name, class_name = path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

def _models_root() -> Path:
    """Return the root directory containing all local models."""
    return Path(__file__).resolve().parent.parent / "models"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fail(msg: str) -> None:
    raise ZomiSylError(msg)


def _load_json(path: Path) -> Dict[str, Any]:
    import json

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        _fail(f"Failed to load JSON file {path}: {e}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_backend(name: str):
    name = name.lower()

    if name not in BACKENDS:
        raise ZomiSylError(f"Unknown backend: {name}")

    # try:
    #     if name == "rule":
    #         # packaged rule model directory
    #         # model_dir = importlib.resources.files("zomi_syl.models.rule")
    #         model_dir = importlib.resources.files("zomi_syl") / "models" / "rule"
    #         return RuleBackend(str(model_dir))

    #     if name == "crf":
    #         # CRF resolves its own model_dir internally
    #         return CRFBackend()

    # except Exception as e:
    #     raise ZomiSylError(f"Failed to load backend '{name}': {e}")
    backend_path = BACKENDS[name]
    backend_cls = _import_backend(backend_path)

    try:
        # Try passing model_dir first
        model_dir = resolve_model_path(name)
        return backend_cls(str(model_dir))
    except TypeError:
        # Backends like CRFBackend that don't accept model_dir
        return backend_cls()
    except Exception as e:
        raise ZomiSylError(f"Failed to load backend '{name}': {e}")

def list_models() -> List[str]:
    """
    Return a list of all available model names.

    Includes:
        • rule (built-in)
        • crf (synthetic metadata)
        • all local models with model.json
    """
    root = _models_root()
    local = []
    logger.info(f"[models] Scanning for local models in {root}")
    if root.exists():
        for p in root.iterdir():
            logger.info(f"[models] Scanning {p}")
            if p.is_dir() and (p / "model.json").exists():
                local.append(p.name)

    # Built-in + synthetic models
    models = ["rule", "crf"]

    # Add local models
    models.extend(sorted(local))
    return models
    # return ["rule"] + sorted(local)


def list_installed_backends() -> list[str]:
    """
    Return a list of installed backend names (e.g., ['rule', 'crf']).
    """
    return list_models()
    # backends = []
    # for name in list_models():  # the existing registry function
    #     try:
    #         load_model(name)
    #         backends.append(name)
    #     except Exception:
    #         pass
    # return backends


def model_exists(name: str) -> bool:
    return name in list_models()


def get_model_path(name: str) -> Path:
    """
    Return the directory path of a model.

    Rule-based model has no directory.
    """
    if name == "rule":
        _fail("Rule-based model has no model directory")

    path = _models_root() / name
    if not path.exists():
        _fail(f"Model '{name}' does not exist")

    return path

# def resolve_model_path(backend_name: str) -> Path:
#     """
#     Unified model directory resolver for all backends.
#     Always loads packaged models, never source-tree paths.
#     """
#     backend_name = backend_name.lower()

#     # All packaged models live under: zomi_syl/models/<backend_name>/
#     base = importlib.resources.files("zomi_syl") / "models" / backend_name

#     if not base.exists():
#         raise FileNotFoundError(f"Model directory not found for backend '{backend_name}': {base}")

#     return Path(base)

def _load_metadata(name: str) -> Dict[str, Any]:
    """
    Load model.json metadata.

    For rule-based model, return synthetic metadata.
    """
    logger.info(f"[models] Loading metadata for model '{name}'")
    if name == "rule":
        return {
            "name": "rule",
            "version": "1.0.0",
            "backend_type": "rule",
            "author": "Zomi NLP Project",
            "license": "MIT",
            "rule": {"path": "src/zomi_syl/models/bundled/rule"},
            "storage": {
                "local_path": "src/zomi_syl/models/bundled/rule",
                "hf_repo": None,
                "download_url": None,
                "cache_path": None,
            },
            "capabilities": {
                "supported_profiles": ["tedim", "zolai_standard", "myanmar_zomi"],
                "supports_confidence": False,
                "supports_batch": True,
                "supports_gpu": False,
                "supports_cpu": True,
            },
            "compatibility": {
                "latest_version": "1.0.0",
                "min_package_version": "0.1.0",
                "compatible_profile_versions": ["1.x"],
            },
        }
    elif name == "crf":
        return {
            "name": "crf",
            "version": "1.0.0",
            "backend_type": "crf",
            "author": "Zomi NLP Project",
            "license": "MIT",
            "crf": {"path": "src/zomi_syl/models/crf"},
            "storage": {
                "local_path": "src/zomi_syl/models/crf",
                "hf_repo": None,
                "download_url": None,
                "cache_path": None,
            },
            "capabilities": {
                "supported_profiles": ["tedim", "zolai_standard", "myanmar_zomi"],
                "supports_confidence": True,
                "supports_batch": True,
                "supports_gpu": False,
                "supports_cpu": True,
            },
            "compatibility": {
                "latest_version": "1.0.0",
                "min_package_version": "0.1.0",
                "compatible_profile_versions": ["1.x"],
            },
        }
    path = get_model_path(name) / "model.json"
    return _load_json(path)


def get_model_info(name: str) -> Dict[str, Any]:
    """
    Return full model information including:

        • metadata
        • resolved paths
        • capability flags
        • version compatibility
    """
    if not model_exists(name):
        _fail(f"Model '{name}' does not exist")

    meta = _load_metadata(name)

    # Resolve storage paths
    if name != "rule":
        root = get_model_path(name)
        logger.info(f"[models] Resolving storage paths for model '{name}' ({root})")
        storage = meta.get("storage", {})

        if "local_path" in storage and storage["local_path"]:
            storage["local_path"] = str(root / storage["local_path"])

        if "cache_path" in storage and storage["cache_path"]:
            storage["cache_path"] = str(root / storage["cache_path"])

        meta["storage"] = storage

    return meta


def get_supported_profiles(name: str) -> List[str]:
    """
    Return the list of dialect profiles supported by a model.
    """
    info = get_model_info(name)
    caps = info.get("capabilities", {})

    profiles = caps.get("supported_profiles")
    if not profiles:
        return []

    return profiles
