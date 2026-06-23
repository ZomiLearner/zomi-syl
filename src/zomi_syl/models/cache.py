"""
Model cache manager for zomi-syl.

This module manages local model storage under:
    ~/.cache/zomi-syl

It supports:
    • cache discovery
    • cache metadata
    • integrity verification
    • cache maintenance (clear, remove, purge old versions)

Public API:
    get_cache_dir()
    model_cached()
    verify_model()
    clear_cache()
    remove_model()
    purge_old_versions()
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

from zomi_syl.exceptions import ZomiSylError

# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Cache directory
# ---------------------------------------------------------------------------


def get_cache_dir() -> Path:
    """
    Return the cache directory path, creating it if needed.

    Default:
        ~/.cache/zomi-syl
    """
    root = Path.home() / ".cache" / "zomi-syl"
    root.mkdir(parents=True, exist_ok=True)
    return root


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------


def _metadata_path(model_name: str) -> Path:
    return get_cache_dir() / f"{model_name}.meta.json"


def _load_metadata(model_name: str) -> Optional[Dict[str, Any]]:
    path = _metadata_path(model_name)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _save_metadata(model_name: str, meta: Dict[str, Any]) -> None:
    path = _metadata_path(model_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Cache status
# ---------------------------------------------------------------------------


def model_cached(model_name: str) -> bool:
    """
    Return True if the model exists in cache and metadata is present.
    """
    meta = _load_metadata(model_name)
    if not meta:
        return False

    file_path = meta.get("file_path")
    if not file_path:
        return False

    return Path(file_path).exists()


# ---------------------------------------------------------------------------
# Integrity verification
# ---------------------------------------------------------------------------


def _compute_checksum(path: Path) -> str:
    """Compute SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_model(model_name: str) -> None:
    """
    Verify that a cached model is valid.

    Checks:
        • file exists
        • checksum matches
        • metadata fields present

    Raises user-friendly errors on failure.
    """
    meta = _load_metadata(model_name)
    if not meta:
        raise ZomiSylError(f"No cached metadata for model '{model_name}'")

    file_path = meta.get("file_path")
    checksum = meta.get("checksum")

    if not file_path or not checksum:
        raise ZomiSylError(f"Metadata incomplete for model '{model_name}'")

    path = Path(file_path)
    if not path.exists():
        raise ZomiSylError(f"Cached model file missing: {path}")

    actual = _compute_checksum(path)
    if actual != checksum:
        raise ZomiSylError(
            f"Checksum mismatch for model '{model_name}'. " f"Expected {checksum}, got {actual}"
        )

    logger.debug(f"[cache] Model '{model_name}' verified successfully")


# ---------------------------------------------------------------------------
# Cache maintenance
# ---------------------------------------------------------------------------


def clear_cache() -> None:
    """
    Remove all cached models and metadata.
    """
    root = get_cache_dir()
    for p in root.iterdir():
        try:
            p.unlink()
        except Exception:
            pass
    logger.debug("[cache] Cleared all cached models")


def remove_model(model_name: str) -> None:
    """
    Remove a single model from cache.
    """
    meta = _load_metadata(model_name)
    if not meta:
        return

    file_path = meta.get("file_path")
    if file_path:
        try:
            Path(file_path).unlink()
        except Exception:
            pass

    try:
        _metadata_path(model_name).unlink()
    except Exception:
        pass

    logger.debug(f"[cache] Removed cached model '{model_name}'")


def purge_old_versions(model_name: str, keep_version: str) -> None:
    """
    Remove cached versions of a model except the specified version.
    """
    meta = _load_metadata(model_name)
    if not meta:
        return

    if meta.get("version") != keep_version:
        remove_model(model_name)
