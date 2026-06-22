"""
Full syllabification pipeline for zomi-syl.

Purpose:
    Define the complete workflow:
        Input
        → Validation
        → Normalization
        → Profile Selection
        → Backend Prediction
        → Postprocessing
        → Result Packaging

Features:
    • Pipeline hooks (pre/post processors)
    • Timing collection
    • Unified public API: run_pipeline()
"""

from __future__ import annotations
import time
from typing import Callable, Dict, List, Optional

# from zomi_syl.logging_config import get_logger
from zomi_syl.core.engine import predict
from zomi_syl.registry.profiles import load_profile
from zomi_syl.validation.input_validator import validate_word, validate_characters
from zomi_syl.core.result import SyllabificationResult

# logger = get_logger(__name__)
import logging
logger = logging.getLogger(__name__)



# ---------------------------------------------------------------------------
# Hook types
# ---------------------------------------------------------------------------

PreHook = Callable[[str], str]
PostHook = Callable[[SyllabificationResult], SyllabificationResult]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def run_pipeline(
    word: str,
    *,
    model: str = "auto",
    dialect: str = "auto",
    include_metadata: bool = False,
    pre_hooks: Optional[List[PreHook]] = None,
    post_hooks: Optional[List[PostHook]] = None,
) -> SyllabificationResult:
    """
    Execute the full syllabification pipeline.

    Stages:
        1. Input
        2. Validation
        3. Normalization
        4. Profile Selection
        5. Backend Prediction
        6. Postprocessing
        7. Result Packaging

    Hooks:
        • pre_hooks: functions(word) -> word
        • post_hooks: functions(result) -> result

    Returns:
        SyllabificationResult
    """

    timings: Dict[str, float] = {}

    # --------------------------------------------------------------
    # Stage 1: Input
    # --------------------------------------------------------------
    original_word = word
    logger.debug(f"[pipeline] Input word={word!r}")

    # --------------------------------------------------------------
    # Stage 2: Validation
    # --------------------------------------------------------------
    t1 = time.perf_counter()
    word = validate_word(word)
    timings["validation"] = time.perf_counter() - t1

    # --------------------------------------------------------------
    # Stage 3: Normalization
    # --------------------------------------------------------------
    t2 = time.perf_counter()
    # (Future: Unicode normalization, lowercasing, custom rules)
    normalized = word.strip()
    logger.debug(f"[pipeline] Normalized={normalized!r}")
    timings["normalization"] = time.perf_counter() - t2

    # --------------------------------------------------------------
    # Stage 4: Profile Selection
    # --------------------------------------------------------------
    t3 = time.perf_counter()
    if dialect == "auto":
        dialect = "tedim"

    profile = load_profile(dialect)
    allowed_chars = profile.get("allowed_characters", None)
    if allowed_chars:
        validate_characters(normalized, allowed_chars)

    timings["profile_selection"] = time.perf_counter() - t3

    # --------------------------------------------------------------
    # Stage 5: Pre‑hooks
    # --------------------------------------------------------------
    if pre_hooks:
        for hook in pre_hooks:
            normalized = hook(normalized)
            logger.debug(f"[pipeline] Pre-hook applied → {normalized!r}")

    # --------------------------------------------------------------
    # Stage 6: Backend Prediction
    # --------------------------------------------------------------
    t4 = time.perf_counter()
    prediction = predict(
        normalized,
        model=model,
        dialect=dialect,
        include_metadata=include_metadata,
    )
    timings["prediction"] = time.perf_counter() - t4

    # --------------------------------------------------------------
    # Stage 7: Post‑hooks
    # --------------------------------------------------------------
    if post_hooks:
        for hook in post_hooks:
            prediction = hook(prediction)
            logger.debug("[pipeline] Post-hook applied")

    # logger.info(prediction)
    # --------------------------------------------------------------
    # Stage 8: Result Packaging
    # --------------------------------------------------------------
    t5 = time.perf_counter()
    result = SyllabificationResult(
        word=original_word,
        syllables=prediction.syllables,
        backend=prediction.raw.get("metadata", {}).get("backend_type", model),
        profile=dialect,
        confidence=[c.score for c in prediction.confidence] if prediction.confidence else None,
        metadata=(
            {
                "timings": timings,
                "backend": prediction.raw.get("metadata", {}),
            }
            if include_metadata
            else {}
        ),
    )
    timings["packaging"] = time.perf_counter() - t5

    logger.info(f"[pipeline] Completed in {sum(timings.values()):.4f}s")

    return result
