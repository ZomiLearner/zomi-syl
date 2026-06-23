from __future__ import annotations

import importlib.resources
from pathlib import Path
from typing import List, Dict, Any
import joblib

from zomi_syl.core.interfaces import (
    BaseSyllabifier,
    Prediction,
    Boundary,
    ConfidenceScore,
)

from zomi_syl.utils.features import strip_and_flags, sent2features
from zomi_syl.utils.model_paths import resolve_model_path


class CRFBackend(BaseSyllabifier):
    """
    CRF-based syllabifier backend.

    - Uses the same feature pipeline as training:
        strip_and_flags() → sent2features()
    - Predicts BIO tags and converts them to syllables + boundaries.
    """
    backend_name: str = "crf"
    backend_version: str = "1.0.0"
    backend_type: str = "statistical"

    def __init__(self, model_dir: str | None = None):
        self.backend_name = self.backend_name
        if model_dir is None:
            model_dir = resolve_model_path("crf")
        # 1. Resolve model directory
        if model_dir is not None:
            self.model_dir = Path(model_dir)
        else:
            self.model_dir = self._resolve_model_path()

        # 2. Resolve model path
        self.model_path = self.model_dir / "crf_syllabifier.joblib"

        if not self.model_path.exists():
            raise FileNotFoundError(f"CRF model not found: {self.model_path}")

        # 3. Load model
        self.model = joblib.load(self.model_path)
        
        # 4. Get/Define CRF tagset
        self.tagset = getattr(self.model, "tagset", ["B", "I"])
        
        # 5. Get/Define feature templates (must match training)
        self.feature_templates = getattr(self.model, "feature_templates", [])

    # def __init__(self, model_dir: str | None = None):
    #     self.model_dir = Path(model_dir)
    #     if model_dir is not None:
    #         # Explicit path provided
    #         self.model_dir = Path(model_dir)
    #     else:
    #         # Auto‑resolve packaged model
    #         self.model_dir = self._resolve_model_path()

    # if prefer_package_model:
    #     # Always load the packaged model
    #     self.model_dir = importlib.resources.files("zomi_syl.models.crf")
    # else:
    #     # Normal behavior (repo model if exists, else package model)
    #     self.model_dir = self._resolve_model_path()

    # self.model_path = self.model_dir / "crf_syllabifier.joblib"

    # if not self.model_path.exists():
    #     raise FileNotFoundError(f"CRF model not found: {self.model_path}")

    # self.model = joblib.load(self.model_path)

    def _resolve_model_path(self):
        return importlib.resources.files("zomi_syl.models.crf")

    # def _resolve_model_path(self):
    #     """
    #     Prefer local model folder if it exists (dev mode),
    #     otherwise load packaged model.
    #     """
    #     local_path = Path(__file__).parent.parent / "models" / "crf"
    #     if local_path.exists():
    #         return local_path

    #     import importlib.resources
    #     return importlib.resources.files("zomi_syl.models.crf")

    # --------------------------------------------------------------
    # BIO → syllables (on hyphen-stripped chars)
    # --------------------------------------------------------------

    def _bio_to_syllables(self, chars: List[str], tags: List[str]) -> List[str]:
        """
        Convert BIO tags over hyphen-stripped characters into syllables.
        """
        sylls: List[str] = []
        buf: List[str] = []

        for ch, tag in zip(chars, tags):
            if tag == "B":
                if buf:
                    sylls.append("".join(buf))
                buf = [ch]
            else:  # "I"
                buf.append(ch)

        if buf:
            sylls.append("".join(buf))

        return sylls

    # --------------------------------------------------------------
    # Core prediction
    # --------------------------------------------------------------

    def predict(self, word: str) -> Prediction:
        """
        Predict syllable boundaries for a single word.
        Hyphens in the input are ignored for feature extraction.
        """
        # 1. Strip hyphens → chars + flags
        chars, flags = strip_and_flags(word)

        # 2. Features (must match training)
        X = sent2features(chars, flags)

        # 3. Predict BIO tags
        tags = self.model.predict_single(X)

        # 4. BIO → syllables (on stripped chars)
        sylls = self._bio_to_syllables(chars, tags)

        # 5. Boundaries (indices in stripped string)
        boundaries: List[Boundary] = []
        idx = 0
        for syl in sylls[:-1]:
            idx += len(syl)
            boundaries.append(Boundary(index=idx, is_boundary=True))

        # 6. Confidence scores
        conf: List[ConfidenceScore] = []
        if hasattr(self.model, "predict_marginals_single"):
            marginals = self.model.predict_marginals_single(X)
            for b in boundaries:
                score = marginals[b.index - 1].get("B", 1.0)
                conf.append(ConfidenceScore(index=b.index, score=score))
        else:
            conf = [ConfidenceScore(index=b.index, score=1.0) for b in boundaries]

        # 7. Unified prediction
        return Prediction(
            syllables=sylls,
            boundaries=boundaries,
            confidence=conf,
            raw={
                "backend": "crf",
                "tags": tags,
            },
        )

    # --------------------------------------------------------------
    # Batch prediction
    # --------------------------------------------------------------

    def predict_batch(self, words: List[str]) -> List[Prediction]:
        """
        Batch prediction: guarantees equivalence with per-word predict().
        """
        return [self.predict(w) for w in words]

    # --------------------------------------------------------------
    # Metadata
    # --------------------------------------------------------------
    # Model specific features
    def _feature_metadata(self):
        return {
            "tagset": self.tagset,
            "num_features": len(self.feature_templates),
            "feature_templates": self.feature_templates,
            "model_path": str(self.model_path),
        }

    def get_metadata(self, include_ruleset=False) -> Dict[str, Any]:
        return {
            "backend_type": "crf",
            "version": self.backend_version,
            "capabilities": {
                "supports_confidence": True,
                "supports_batch": True,
                "supports_gpu": False,
                "supports_cpu": True,
            },
            "ums": self._base_ums(),
        }

    # --------------------------------------------------------------
    # API
    # --------------------------------------------------------------

    def __call__(self, word: str) -> Prediction:
        return self.predict(word)
