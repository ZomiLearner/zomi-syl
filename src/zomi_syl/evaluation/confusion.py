"""
Confusion analysis for zomi-syl.

Provides:
    • boundary confusion matrix
    • error breakdown
"""

from __future__ import annotations
from typing import List, Dict


def boundary_confusion(gold: List[int], pred: List[int]) -> Dict[str, int]:
    gold_set = set(gold)
    pred_set = set(pred)

    return {
        "tp": len(gold_set & pred_set),
        "fp": len(pred_set - gold_set),
        "fn": len(gold_set - pred_set),
    }


def error_breakdown(gold: List[int], pred: List[int]) -> Dict[str, List[int]]:
    gold_set = set(gold)
    pred_set = set(pred)

    return {
        "missed": sorted(list(gold_set - pred_set)),
        "spurious": sorted(list(pred_set - gold_set)),
    }
