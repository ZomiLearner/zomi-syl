"""
Structured result objects for zomi-syl.

SyllabificationResult is the final packaged output returned by the pipeline.
It wraps the backend Prediction object into a stable, JSON-serializable
structure for API, CLI, batch processing, and evaluation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json

from zomi_syl.core.interfaces import Boundary


@dataclass
class SyllabificationResult:
    """
    Final packaged syllabification output.

    Fields:
        word: original input word
        syllables: list of syllables
        backend: backend used ("rule", "crf", "fst", "bilstm", "transformer")
        profile: dialect/profile used
        boundaries: list[Boundary]
        confidence: list[float] or None
        raw: backend-specific raw output (tags, logits, marginals, etc.)
        metadata: timing, debug info, backend metadata, etc.
    """

    word: str
    syllables: List[str]
    backend: str
    profile: str

    boundaries: List[Boundary] = field(default_factory=list)
    confidence: Optional[List[float]] = None

    raw: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def joined(self) -> str:
        """Return syllables joined with hyphens."""
        return "-".join(self.syllables)

    @property
    def count(self) -> int:
        """Number of syllables."""
        return len(self.syllables)

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to a JSON-serializable dictionary."""
        return {
            "word": self.word,
            "syllables": self.syllables,
            "backend": self.backend,
            "profile": self.profile,
            "boundaries": [
                {"index": b.index, "is_boundary": b.is_boundary} for b in self.boundaries
            ],
            "confidence": self.confidence,
            "raw": self.raw,
            "metadata": self.metadata,
        }

    def to_json(self, indent: Optional[int] = None) -> str:
        """Serialize result to JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    # ------------------------------------------------------------------
    # Pretty printing
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Human-readable representation."""
        conf = ""
        if self.confidence:
            avg = sum(self.confidence) / len(self.confidence)
            conf = f" (avg_conf={avg:.3f})"
        return f"{self.word} → {self.joined} [{self.backend}/{self.profile}]{conf}"

    def __repr__(self) -> str:
        return (
            f"SyllabificationResult("
            f"word={self.word!r}, "
            f"syllables={self.syllables!r}, "
            f"backend={self.backend!r}, "
            f"profile={self.profile!r}, "
            f"boundaries={self.boundaries!r}, "
            f"confidence={self.confidence!r}, "
            f"raw={self.raw!r}, "
            f"metadata={self.metadata!r})"
        )

    def __eq__(self, other) -> bool:
        return self.to_dict() == other.to_dict()
