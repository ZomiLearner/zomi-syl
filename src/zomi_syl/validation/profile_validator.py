"""
Profile validation utilities for zomi-syl.

This module validates profile directories and resources before they are
loaded into the syllabification pipeline. It ensures:

    • required files exist
    • JSON structure is valid
    • inventories are consistent
    • rules reference valid symbols
    • versions are compatible

All errors are raised with user-friendly messages.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from zomi_syl.exceptions import ZomiSylError

# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------


def _fail(message: str) -> None:
    raise ZomiSylError(message)


# ---------------------------------------------------------------------------
# Required profile files
# ---------------------------------------------------------------------------

_REQUIRED_FILES = {
    "profile.json",
    "vowels.json",
    "onsets.json",
    "codas.json",
    "nuclei.json",
    "rules.json",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_profile_directory(path: Path) -> None:
    """
    Ensure the profile directory contains all required files.
    """
    if not path.exists():
        _fail(f"Profile directory does not exist: {path}")

    if not path.is_dir():
        _fail(f"Expected profile directory, got file: {path}")

    files = {p.name for p in path.iterdir() if p.is_file()}

    missing = _REQUIRED_FILES - files
    if missing:
        missing_list = ", ".join(sorted(missing))
        _fail(f"Profile is missing required files: {missing_list}")


def validate_profile_resources(resources: Dict[str, Any]) -> None:
    """
    Validate the structure and content of loaded profile resources.
    """
    # Required keys
    for key in ["vowels", "onsets", "codas", "nuclei", "rules"]:
        if key not in resources:
            _fail(f"Profile missing required resource: {key}")

    # Validate inventories
    _validate_inventory("vowels", resources["vowels"])
    _validate_inventory("nuclei", resources["nuclei"])
    _validate_inventory("onsets", resources["onsets"])
    _validate_inventory("codas", resources["codas"])

    # Cross-inventory consistency
    _validate_inventory_consistency(resources)

    # Validate rules
    _validate_rules(resources["rules"], resources)

    # Version validation
    if "profile" in resources:
        validate_profile_version(resources["profile"])


def validate_profile_version(profile_json: Dict[str, Any]) -> None:
    """
    Validate profile version compatibility.
    """
    version = profile_json.get("version")
    if version is None:
        _fail("profile.json missing required field: version")

    # For now, only version 1.x.x is supported
    if not version.startswith("1."):
        _fail(f"Unsupported profile version: {version}")


def validate_profile(path: Path) -> Dict[str, Any]:
    """
    Validate a profile directory and return loaded resources.
    """
    validate_profile_directory(path)

    # Load JSON files
    resources = {}
    for fname in _REQUIRED_FILES:
        fpath = path / fname
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                resources[fname.replace(".json", "")] = json.load(f)
        except json.JSONDecodeError as e:
            _fail(f"Invalid JSON in {fname}: {e}")

    # Validate structure + content
    validate_profile_resources(resources)

    return resources


# ---------------------------------------------------------------------------
# Inventory validation
# ---------------------------------------------------------------------------


def _extract_graphemes(items: List[Any]) -> List[str]:
    """
    Extract graphemes from inventory items.

    Supports:
        • ["a", "aa"]
        • [{"grapheme": "kh", "description": "..."}]
    """
    graphemes = []
    for item in items:
        if isinstance(item, str):
            graphemes.append(item)
        elif isinstance(item, dict) and "grapheme" in item:
            graphemes.append(item["grapheme"])
        else:
            _fail(f"Invalid inventory entry: {item!r}")
    return graphemes


def _validate_inventory(name: str, items: List[Any]) -> None:
    """
    Validate a single inventory (vowels, onsets, codas, nuclei).
    """
    graphemes = _extract_graphemes(items)

    # Duplicates
    seen = set()
    duplicates = []
    for g in graphemes:
        if g in seen:
            duplicates.append(g)
        seen.add(g)

    if duplicates:
        dup_list = ", ".join(duplicates)
        _fail(f"Duplicate entries in {name}: {dup_list}")


def _validate_inventory_consistency(resources: Dict[str, Any]) -> None:
    """
    Detect overlapping or illegal definitions across inventories.
    """
    vowels = set(_extract_graphemes(resources["vowels"]))
    nuclei = set(_extract_graphemes(resources["nuclei"]))
    onsets = set(_extract_graphemes(resources["onsets"]))
    codas = set(_extract_graphemes(resources["codas"]))

    # Nuclei must be subset of vowels
    missing = nuclei - vowels
    if missing:
        missing_list = ", ".join(sorted(missing))
        _fail(f"Nuclei contain symbols not in vowels: {missing_list}")

    # Onset/coda overlap is usually illegal
    overlap = onsets & codas
    if overlap:
        overlap_list = ", ".join(sorted(overlap))
        _fail(f"Symbols appear in both onsets and codas: {overlap_list}")


# ---------------------------------------------------------------------------
# Rule validation
# ---------------------------------------------------------------------------


def _validate_rules(rules: Dict[str, Any], resources: Dict[str, Any]) -> None:
    """
    Validate rule definitions and cross-resource references.
    """
    # Basic structure
    if not isinstance(rules, dict):
        _fail("rules.json must contain a JSON object")

    # Example: ensure rule IDs unique (if present)
    if "rules" in rules and isinstance(rules["rules"], list):
        ids = [r.get("id") for r in rules["rules"] if isinstance(r, dict)]
        if len(ids) != len(set(ids)):
            _fail("Duplicate rule IDs detected in rules.json")

    # Cross-resource references
    all_symbols = (
        set(_extract_graphemes(resources["vowels"]))
        | set(_extract_graphemes(resources["onsets"]))
        | set(_extract_graphemes(resources["codas"]))
    )

    # Example: check rule references
    for key, value in rules.items():
        if isinstance(value, str) and value not in all_symbols:
            # Only treat as symbol reference if it looks like a grapheme
            if len(value) <= 4:
                _fail(f"Rule references unknown symbol: {value!r}")
