"""
Text normalization utilities for zomi-syl.

Normalization is intentionally lightweight at this stage. It performs:
    - Unicode NFC normalization
    - Whitespace cleanup
    - Basic punctuation normalization
    - Optional profile-specific normalization hooks

Dialect/profile-specific normalization rules can be added later without
changing the public API.
"""

import unicodedata
from typing import Optional

# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)
import logging
logger = logging.getLogger(__name__)



# ---------------------------------------------------------------------------
# Core normalization steps
# ---------------------------------------------------------------------------


def _unicode_normalize(text: str) -> str:
    """Apply Unicode NFC normalization."""
    return unicodedata.normalize("NFC", text)


def _clean_whitespace(text: str) -> str:
    """Collapse repeated whitespace and trim edges."""
    return " ".join(text.split())


def _normalize_punctuation(text: str) -> str:
    """Basic punctuation normalization (extendable)."""
    # Example: convert fancy quotes to ASCII quotes
    replacements = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
    }
    for src, tgt in replacements.items():
        text = text.replace(src, tgt)
    return text


# ---------------------------------------------------------------------------
# Profile-specific normalization (placeholder)
# ---------------------------------------------------------------------------


def _apply_profile_rules(text: str, profile: str) -> str:
    """
    Placeholder for dialect/profile-specific normalization.

    Profiles may eventually define:
        - vowel harmonization
        - tone mark normalization
        - stylized spelling cleanup
        - Myanmar Zomi orthographic variants
        - India Zomi ASCII variants

    For now, this is a no-op.
    """
    # Future: load rules from profiles/<profile>/normalization.json
    return text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def normalize(text: str, profile: Optional[str] = None) -> str:
    """
    Normalize input text before syllabification.

    Parameters
    ----------
    text : str
        Raw input text.
    profile : str, optional
        Dialect/profile name. If provided, profile-specific normalization
        rules may be applied.

    Returns
    -------
    str
        Normalized text.
    """
    if not isinstance(text, str):
        raise TypeError("normalize() expects a string input.")

    logger.debug(f"Normalizing text: {text!r}")

    # Step 1: Unicode normalization
    text = _unicode_normalize(text)

    # Step 2: Whitespace cleanup
    text = _clean_whitespace(text)

    # Step 3: Punctuation normalization
    text = _normalize_punctuation(text)

    # Step 4: Profile-specific rules (future)
    if profile:
        text = _apply_profile_rules(text, profile)

    logger.debug(f"Normalized text: {text!r}")
    return text
