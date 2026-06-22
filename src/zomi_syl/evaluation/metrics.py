"""
Evaluation metrics for zomi-syl.

Provides:
    • syllable accuracy
    • boundary precision/recall/F1
    • character error rate (CER)
"""

from __future__ import annotations
from typing import List, Tuple
from difflib import SequenceMatcher

# ---------------------------------------------------------------------------
# Syllable accuracy
# ---------------------------------------------------------------------------


def syllable_accuracy(gold: List[str], pred: List[str]) -> float:
    if not gold:
        return 0.0
    correct = sum(1 for g, p in zip(gold, pred) if g == p)
    return correct / len(gold)


# ---------------------------------------------------------------------------
# Boundary F1
# ---------------------------------------------------------------------------


def boundary_f1(
    gold_boundaries: List[int], pred_boundaries: List[int]
) -> Tuple[float, float, float]:
    gold_set = set(gold_boundaries)
    pred_set = set(pred_boundaries)

    tp = len(gold_set & pred_set)
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return precision, recall, f1


# ---------------------------------------------------------------------------
# Character Error Rate (CER)
# ---------------------------------------------------------------------------


def cer(gold: str, pred: str) -> float:
    """
    Character error rate using Levenshtein distance.
    """
    if not gold:
        return 0.0
    matcher = SequenceMatcher(None, gold, pred)
    distance = sum(block.size for block in matcher.get_opcodes() if block[0] != "equal")
    return distance / len(gold)
