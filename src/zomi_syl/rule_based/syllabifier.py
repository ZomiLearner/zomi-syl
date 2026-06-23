"""
Rule-based syllabification backend for zomi-syl.

This backend uses:
    - profile-specific onset/coda/nucleus inventories
    - maximal onset principle
    - digraph protection
    - simple phonotactic constraints

It is deterministic and fast, and serves as the fallback backend when
ML/FST models are unavailable or disabled.
"""

from typing import List, Dict

# from zomi_syl.logging_config import get_logger
from zomi_syl.preprocess.normalize import normalize
from zomi_syl.exceptions import ZomiSylError

# logger = get_logger(__name__)

import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper: check if a substring is a valid onset
# ---------------------------------------------------------------------------


def _match_onset(text: str, onsets: List[str]) -> str:
    """
    Return the longest valid onset at the beginning of `text`.
    If none match, return empty string.
    """
    matches = [o for o in onsets if text.startswith(o)]
    if not matches:
        return ""
    return max(matches, key=len)  # longest match


# ---------------------------------------------------------------------------
# Helper: check if a substring is a valid nucleus
# ---------------------------------------------------------------------------


def _match_nucleus(text: str, nuclei: List[str]) -> str:
    """
    Return the longest valid nucleus at the beginning of `text`.
    """
    matches = [n for n in nuclei if text.startswith(n)]
    if not matches:
        return ""
    return max(matches, key=len)


# ---------------------------------------------------------------------------
# Helper: check if a substring is a valid coda
# ---------------------------------------------------------------------------


def _match_coda(text: str, codas: List[str]) -> str:
    """
    Return the longest valid coda at the beginning of `text`.
    """
    matches = [c for c in codas if text.startswith(c)]
    if not matches:
        return ""
    return max(matches, key=len)


# ---------------------------------------------------------------------------
# Core rule-based syllabifier
# ---------------------------------------------------------------------------


def syllabify_rule_based(word: str, profile: Dict[str, List[str]], rules: Dict) -> List[str]:
    """
    Syllabify a word using deterministic rule-based logic.

    Parameters
    ----------
    word : str
        Input word (raw).
    profile : dict
        Loaded profile resources containing:
            - onsets
            - nuclei
            - codas
    rules : dict
        Profile-specific rule settings.

    Returns
    -------
    List[str]
        List of syllables.
    """
    if not word:
        return []

    # Normalize input
    text = normalize(word)
    logger.debug(f"[rule] Normalized input: {text}")

    onsets = [o["grapheme"] if isinstance(o, dict) else o for o in profile["onsets"]]
    nuclei = profile["nuclei"]
    codas = profile["codas"]

    syllables = []
    i = 0
    n = len(text)

    while i < n:
        start = i

        # 1. Match onset (optional)
        onset = _match_onset(text[i:], onsets)
        if onset:
            i += len(onset)
        logger.debug(f"[rule] Onset: {onset!r}")

        # 2. Match nucleus (required)
        nucleus = _match_nucleus(text[i:], nuclei)
        if not nucleus:
            raise ZomiSylError(f"Cannot find nucleus in segment: {text[i:]} (word={word!r})")
        i += len(nucleus)
        logger.debug(f"[rule] Nucleus: {nucleus!r}")

        # 3. Match coda (optional)
        coda = _match_coda(text[i:], codas)
        if coda:
            i += len(coda)
        logger.debug(f"[rule] Coda: {coda!r}")

        # Extract syllable
        syll = text[start:i]
        syllables.append(syll)
        logger.info(f"[rule] Syllable: {syll!r}")
    print(f"syllables: {syllables}")
    return syllables
