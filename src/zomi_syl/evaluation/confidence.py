"""
Confidence scoring utilities.

Provides:
    • average confidence
    • min/max confidence
    • calibration error (ECE)
"""

from __future__ import annotations
from typing import List


def average_confidence(scores: List[float]) -> float:
    return sum(scores) / len(scores) if scores else 0.0


def min_confidence(scores: List[float]) -> float:
    return min(scores) if scores else 0.0


def max_confidence(scores: List[float]) -> float:
    return max(scores) if scores else 0.0


# ---------------------------------------------------------------------------
# Expected Calibration Error (ECE)
# ---------------------------------------------------------------------------


def expected_calibration_error(scores: List[float], correct: List[bool], bins: int = 10) -> float:
    """
    Compute ECE for confidence calibration.
    """
    if not scores:
        return 0.0

    bucket_size = 1.0 / bins
    ece = 0.0

    for i in range(bins):
        lo = i * bucket_size
        hi = lo + bucket_size

        bucket = [(s, c) for s, c in zip(scores, correct) if lo <= s < hi]
        if not bucket:
            continue

        avg_conf = sum(s for s, _ in bucket) / len(bucket)
        avg_acc = sum(1 for _, c in bucket if c) / len(bucket)

        ece += (len(bucket) / len(scores)) * abs(avg_conf - avg_acc)

    return ece
