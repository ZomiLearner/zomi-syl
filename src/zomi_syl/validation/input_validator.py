"""
Input validation utilities for zomi-syl.

This module validates all user-provided inputs before they enter the
syllabification pipeline. It ensures:
    - correct types
    - valid word structure
    - safe characters
    - clean batch inputs

All errors are raised with user-friendly messages.
"""

from pathlib import Path
from typing import Iterable, List, Union

from zomi_syl.exceptions import ZomiSylError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ALLOWED_EXTRA_SYMBOLS = {"'", "-", "’"}  # apostrophes + hyphens


def _error(msg: str) -> None:
    """Raise a user-friendly validation error."""
    raise ZomiSylError(msg)


# ---------------------------------------------------------------------------
# Type validation
# ---------------------------------------------------------------------------


def validate_text(obj: Union[str, Path]) -> str:
    """
    Validate that the input is a string or a Path.

    Returns the string value.
    """
    if isinstance(obj, Path):
        return str(obj)

    if not isinstance(obj, str):
        _error(f"Expected string, got {type(obj).__name__}")

    return obj


# ---------------------------------------------------------------------------
# Word validation
# ---------------------------------------------------------------------------


def validate_word(word: str, *, max_length: int = 100) -> str:
    """
    Validate a single word.

    Checks:
        - type
        - non-empty
        - not whitespace-only
        - length limit
        - no control characters
        - no unsupported symbols
    """
    if not isinstance(word, str):
        _error(f"Expected string, got {type(word).__name__}")

    if word == "":
        _error("Input word cannot be empty")

    if word.strip() == "":
        _error("Input word cannot contain only whitespace")

    if len(word) > max_length:
        _error(f"Input word is too long (>{max_length} characters)")

    # Control characters
    for i, ch in enumerate(word):
        if ord(ch) < 32:
            _error(f"Control character U+{ord(ch):04X} at position {i}")

    return word


# ---------------------------------------------------------------------------
# Character inventory validation
# ---------------------------------------------------------------------------


def validate_characters(word: str, allowed_chars: set) -> None:
    """
    Validate that all characters in the word belong to:
        - Latin letters
        - profile-specific symbols
        - tone markers
        - apostrophes
        - hyphens
    """
    for i, ch in enumerate(word):
        if ch in allowed_chars:
            continue
        if ch in _ALLOWED_EXTRA_SYMBOLS:
            continue

        _error(f"Unsupported character {ch!r} at position {i}")


# ---------------------------------------------------------------------------
# Batch validation
# ---------------------------------------------------------------------------


def validate_words(words: Union[List[str], Iterable[str]]) -> List[str]:
    """
    Validate a batch of words.

    Accepts:
        - list[str]
        - generator[str]
        - iterator[str]

    Detects:
        - mixed types
        - nested lists
        - empty datasets
    """
    if isinstance(words, str):
        _error("Expected list of words, got a single string")

    if not isinstance(words, Iterable):
        _error(f"Expected iterable of strings, got {type(words).__name__}")

    validated = []

    for idx, item in enumerate(words):
        if isinstance(item, list):
            _error(f"Nested list detected at index {idx}")

        if not isinstance(item, str):
            _error(f"Expected string at index {idx}, got {type(item).__name__}")

        validated.append(item)

    if len(validated) == 0:
        _error("Input word list cannot be empty")

    return validated
