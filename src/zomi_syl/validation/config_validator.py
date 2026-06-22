"""
Configuration validation utilities for zomi-syl.

This module validates package configuration before use. It ensures:

    • backend is supported
    • profile exists and is compatible
    • cache and model paths are valid
    • performance settings are safe
    • logging level is valid

All errors are raised with user-friendly messages.
"""

from pathlib import Path
from typing import Dict, Any

from zomi_syl.exceptions import ZomiSylError
from zomi_syl.registry.profiles import profile_exists, load_profile_metadata

# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------


def _fail(message: str) -> None:
    raise ZomiSylError(message)


# ---------------------------------------------------------------------------
# Allowed values
# ---------------------------------------------------------------------------

_ALLOWED_BACKENDS = {
    "rule",
    "crf",
    "fst",
    "bilstm",
    "bilstm_crf",
    "transformer",
}

_ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR"}


# ---------------------------------------------------------------------------
# Backend validation
# ---------------------------------------------------------------------------


def validate_backend(backend: str) -> None:
    """
    Validate that the backend is supported.
    """
    if backend not in _ALLOWED_BACKENDS:
        allowed = ", ".join(sorted(_ALLOWED_BACKENDS))
        _fail(f"Unsupported backend '{backend}'. Allowed: {allowed}")


# ---------------------------------------------------------------------------
# Profile validation
# ---------------------------------------------------------------------------


def _validate_profile_name(profile: str) -> None:
    if not profile_exists(profile):
        _fail(f"Profile '{profile}' does not exist")

    meta = load_profile_metadata(profile)
    version = meta.get("version")

    if version is None:
        _fail(f"Profile '{profile}' missing version field")

    if not version.startswith("1."):
        _fail(f"Profile '{profile}' uses unsupported version: {version}")


# ---------------------------------------------------------------------------
# Path validation
# ---------------------------------------------------------------------------


def _validate_directory(path: Path, label: str) -> None:
    if not path.exists():
        _fail(f"{label} directory does not exist: {path}")

    if not path.is_dir():
        _fail(f"{label} path is not a directory: {path}")

    # Check write permission
    try:
        test_file = path / ".zomi_syl_write_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
    except Exception:
        _fail(f"{label} directory is not writable: {path}")


def validate_paths(config: Dict[str, Any]) -> None:
    """
    Validate model/cache/dataset directories.
    """
    for key in ["models_dir", "cache_dir", "dataset_dir"]:
        if key not in config:
            _fail(f"Missing required path in config: {key}")

        path = Path(config[key])
        _validate_directory(path, key)


# ---------------------------------------------------------------------------
# Performance settings validation
# ---------------------------------------------------------------------------


def _validate_performance(config: Dict[str, Any]) -> None:
    batch_size = config.get("batch_size", 1)
    workers = config.get("workers", 1)
    device = config.get("device", "cpu")

    if not isinstance(batch_size, int) or batch_size <= 0:
        _fail("batch_size must be a positive integer")

    if not isinstance(workers, int) or workers < 0:
        _fail("workers must be a non-negative integer")

    if device not in {"cpu", "cuda"}:
        _fail("device must be 'cpu' or 'cuda'")


# ---------------------------------------------------------------------------
# Logging validation
# ---------------------------------------------------------------------------


def _validate_logging(config: Dict[str, Any]) -> None:
    level = config.get("log_level", "INFO")

    if level not in _ALLOWED_LOG_LEVELS:
        allowed = ", ".join(sorted(_ALLOWED_LOG_LEVELS))
        _fail(f"Invalid log level '{level}'. Allowed: {allowed}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the entire configuration dictionary.

    Expected fields:
        backend
        profile
        models_dir
        cache_dir
        dataset_dir
        batch_size
        workers
        device
        log_level
    """
    # Backend
    if "backend" not in config:
        _fail("Missing required config field: backend")
    validate_backend(config["backend"])

    # Profile
    if "profile" not in config:
        _fail("Missing required config field: profile")
    _validate_profile_name(config["profile"])

    # Paths
    validate_paths(config)

    # Performance
    _validate_performance(config)

    # Logging
    _validate_logging(config)
