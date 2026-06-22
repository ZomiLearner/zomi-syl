"""
Utility functions for model backends:
    • tags → boundaries
    • logits → tags
"""

from __future__ import annotations
from typing import List
import torch

from zomi_syl.core.interfaces import Boundary

# ---------------------------------------------------------------------------
# CRF + Transformer: tags → boundaries
# ---------------------------------------------------------------------------


def tags_to_boundaries(word: str, tags: List[str]) -> List[Boundary]:
    boundaries = []
    for i, tag in enumerate(tags):
        if tag == "B":  # boundary tag
            boundaries.append(Boundary(index=i, is_boundary=True))
    return boundaries


# ---------------------------------------------------------------------------
# Transformer: logits → tags
# ---------------------------------------------------------------------------


def logits_to_tags(logits: torch.Tensor) -> List[str]:
    """
    logits: [seq_len, num_labels]
    """
    ids = torch.argmax(logits, dim=-1).tolist()
    # Assume label mapping: 0 = O, 1 = B
    return ["B" if i == 1 else "O" for i in ids]
