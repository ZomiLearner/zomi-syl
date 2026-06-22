"""
Profile registry for zomi-syl.

This module provides:
    • listing available profiles
    • checking profile existence
    • loading profile metadata
    • loading full profile resources
    • resolving profile paths

It integrates with the profile validator to ensure all profiles are safe
before use.
"""

from pathlib import Path
from typing import Dict, Any, List

from zomi_syl.exceptions import ZomiSylError
from zomi_syl.validation.profile_validator import validate_profile
# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)
import logging
logger = logging.getLogger(__name__)



# ---------------------------------------------------------------------------
# Base directory
# ---------------------------------------------------------------------------


def _profiles_root() -> Path:
    """Return the root directory containing all profiles."""
    return Path(__file__).resolve().parent.parent / "profiles"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def list_profiles() -> List[str]:
    """
    Return a list of available profile names.

    Example:
        ["tedim", "zolai_standard", "myanmar_zomi"]
    """
    root = _profiles_root()
    if not root.exists():
        return []

    profiles = [p.name for p in root.iterdir() if p.is_dir() and (p / "profile.json").exists()]

    return sorted(profiles)


def profile_exists(name: str) -> bool:
    """
    Check whether a profile exists.
    """
    return name in list_profiles()


def get_profile_path(name: str) -> Path:
    """
    Return the directory path of a profile.

    Raises a user-friendly error if the profile does not exist.
    """
    root = _profiles_root()
    path = root / name

    if not path.exists():
        raise ZomiSylError(f"Profile '{name}' does not exist")

    return path


def load_profile_metadata(name: str) -> Dict[str, Any]:
    """
    Load only profile.json (metadata), without loading inventories.

    Useful for:
        • version checks
        • listing profiles
        • config validation
    """
    path = get_profile_path(name) / "profile.json"

    try:
        import json

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise ZomiSylError(f"Failed to load metadata for profile '{name}': {e}")


def load_profile(name: str) -> Dict[str, Any]:
    """
    Load and validate a full profile.

    Returns a dictionary containing:
        • profile (metadata)
        • vowels
        • onsets
        • codas
        • nuclei
        • rules
    """
    logger.debug(f"[profiles] Loading profile '{name}'")

    path = get_profile_path(name)

    # Validate + load all resources
    resources = validate_profile(path)

    logger.debug(f"[profiles] Loaded profile '{name}' successfully")
    return resources
