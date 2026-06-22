"""
Core backend interfaces for zomi-syl.

Purpose:
    Define the contracts every backend must satisfy.
    This file acts as the "language" spoken by all backends:
        • rule-based
        • CRF
        • FST
        • BiLSTM
        • Transformer

Contains:
    • Abstract base classes
    • Required methods
    • Type definitions
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Type definitions
# ---------------------------------------------------------------------------


@dataclass
class Boundary:
    """
    Represents a predicted syllable boundary at a character index.

    Example:
        Boundary(index=3, is_boundary=True)
    """

    index: int
    is_boundary: bool


@dataclass
class ConfidenceScore:
    """
    Represents a confidence score for a boundary prediction.

    Example:
        ConfidenceScore(index=3, score=0.87)
    """

    index: int
    score: float


@dataclass
class Prediction:
    """
    Unified prediction output for all backends.

    Fields:
        syllables: "thu-gen-na"
        syllables: ["thu", "gen", "na"]
        boundaries: list[Boundary]
        confidence: list[ConfidenceScore] (optional)
        raw: backend-specific raw output (tags, logits, marginals, etc.)
    """

    syllables: List[str]
    boundaries: List[Boundary]
    confidence: List[ConfidenceScore]
    raw: Dict[str, Any]


# ---------------------------------------------------------------------------
# Abstract base classes
# ---------------------------------------------------------------------------


class BaseSyllabifier(ABC):
    """
    Abstract interface for all syllabification backends.

    Required methods:
        • predict()
        • predict_batch()
        • get_metadata()
    """

    @abstractmethod
    def predict(self, word: str) -> Prediction:
        """
        Predict syllable boundaries for a single word.
        Must return a Prediction object.
        """
        raise NotImplementedError

    @abstractmethod
    def predict_batch(self, words: List[str]) -> List[Prediction]:
        """
        Predict syllable boundaries for multiple words.
        Must return a list of Prediction objects.
        """
        raise NotImplementedError

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return backend metadata:
            • backend_type
            • version
            • capabilities
        """
        raise NotImplementedError


class BasePredictor(ABC):
    """
    Abstract interface for ML-based predictors (CRF, BiLSTM, Transformer).

    Required methods:
        • predict()
        • predict_batch()
        • predict_proba()
        • get_metadata()
    """

    @abstractmethod
    def predict(self, word: str) -> Prediction:
        """
        Predict syllable boundaries for a single word.
        """
        raise NotImplementedError

    @abstractmethod
    def predict_batch(self, words: List[str]) -> List[Prediction]:
        """
        Predict syllable boundaries for multiple words.
        """
        raise NotImplementedError

    @abstractmethod
    def predict_proba(self, word: str) -> List[ConfidenceScore]:
        """
        Return confidence scores for each boundary position.
        """
        raise NotImplementedError

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return backend metadata.
        """
        raise NotImplementedError
