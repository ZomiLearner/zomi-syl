# src/zomi_syl/backends/crf_backend.py
# from __future__ import annotations

# import importlib.resources
# import json
# from pathlib import Path
# from typing import List, Dict, Any
# import joblib
# import traceback
# from zomi_syl.exceptions import ZomiSylError

# from zomi_syl.core.interfaces import (
#     BaseSyllabifier,
#     Prediction,
#     Boundary,
#     ConfidenceScore,
# )

# from zomi_syl.utils.features import strip_and_flags, sent2features
# from zomi_syl.utils.model_paths import resolve_model_path


# class CRFBackend(BaseSyllabifier):
#     """
#     CRF-based syllabifier backend.

#     - Uses the same feature pipeline as training:
#         strip_and_flags() → sent2features()
#     - Predicts BIO tags and converts them to syllables + boundaries.
#     """
#     backend_name: str = "crf"
#     backend_version: str = "1.0.0"
#     backend_type: str = "statistical"

#     def __init__(self, model_dir: str | None = None):
#         self.backend_name = self.backend_name
#         if model_dir is None:
#             model_dir = resolve_model_path("crf")
#         # 1. Resolve model directory
#         if model_dir is not None:
#             self.model_dir = Path(model_dir)
#         else:
#             self.model_dir = self._resolve_model_path()

#         # 2. Resolve model path
#         # self.model_path = self.model_dir / "crf_syllabifier.joblib"
#         self.model_path = self.model_dir / "crf_syllabifier.crfsuite"

#         if not self.model_path.exists():
#             raise FileNotFoundError(f"CRF model not found: {self.model_path}")

#         # # 3. Load model
#         # self.model = joblib.load(self.model_path)
#         try:
#             # self.model = joblib.load(self.model_path)
#             self.model = json.load(self.model_path)
#         except Exception as e:
#             tb = traceback.format_exc()
#             raise ZomiSylError(
#                 f"CRF model failed to load from {self.model_path}: {e}\n\n{tb}"
#             )
        
#         # 4. Get/Define CRF tagset
#         self.tagset = getattr(self.model, "tagset", ["B", "I"])
        
#         # 5. Get/Define feature templates (must match training)
#         self.feature_templates = getattr(self.model, "feature_templates", [])

#     # def __init__(self, model_dir: str | None = None):
#     #     self.model_dir = Path(model_dir)
#     #     if model_dir is not None:
#     #         # Explicit path provided
#     #         self.model_dir = Path(model_dir)
#     #     else:
#     #         # Auto‑resolve packaged model
#     #         self.model_dir = self._resolve_model_path()

#     # if prefer_package_model:
#     #     # Always load the packaged model
#     #     self.model_dir = importlib.resources.files("zomi_syl.models.crf")
#     # else:
#     #     # Normal behavior (repo model if exists, else package model)
#     #     self.model_dir = self._resolve_model_path()

#     # self.model_path = self.model_dir / "crf_syllabifier.joblib"

#     # if not self.model_path.exists():
#     #     raise FileNotFoundError(f"CRF model not found: {self.model_path}")

#     # self.model = joblib.load(self.model_path)

#     def _resolve_model_path(self):
#         return importlib.resources.files("zomi_syl.models.crf")

#     # def _resolve_model_path(self):
#     #     """
#     #     Prefer local model folder if it exists (dev mode),
#     #     otherwise load packaged model.
#     #     """
#     #     local_path = Path(__file__).parent.parent / "models" / "crf"
#     #     if local_path.exists():
#     #         return local_path

#     #     import importlib.resources
#     #     return importlib.resources.files("zomi_syl.models.crf")

#     # --------------------------------------------------------------
#     # BIO → syllables (on hyphen-stripped chars)
#     # --------------------------------------------------------------

#     def _bio_to_syllables(self, chars: List[str], tags: List[str]) -> List[str]:
#         """
#         Convert BIO tags over hyphen-stripped characters into syllables.
#         """
#         sylls: List[str] = []
#         buf: List[str] = []

#         for ch, tag in zip(chars, tags):
#             if tag == "B":
#                 if buf:
#                     sylls.append("".join(buf))
#                 buf = [ch]
#             else:  # "I"
#                 buf.append(ch)

#         if buf:
#             sylls.append("".join(buf))

#         return sylls

#     # --------------------------------------------------------------
#     # Core prediction
#     # --------------------------------------------------------------

#     def predict(self, word: str) -> Prediction:
#         """
#         Predict syllable boundaries for a single word.
#         Hyphens in the input are ignored for feature extraction.
#         """
#         # 1. Strip hyphens → chars + flags
#         chars, flags = strip_and_flags(word)

#         # 2. Features (must match training)
#         X = sent2features(chars, flags)

#         # 3. Predict BIO tags
#         tags = self.model.predict_single(X)

#         # 4. BIO → syllables (on stripped chars)
#         sylls = self._bio_to_syllables(chars, tags)

#         # 5. Boundaries (indices in stripped string)
#         boundaries: List[Boundary] = []
#         idx = 0
#         for syl in sylls[:-1]:
#             idx += len(syl)
#             boundaries.append(Boundary(index=idx, is_boundary=True))

#         # 6. Confidence scores
#         conf: List[ConfidenceScore] = []
#         if hasattr(self.model, "predict_marginals_single"):
#             marginals = self.model.predict_marginals_single(X)
#             for b in boundaries:
#                 score = marginals[b.index - 1].get("B", 1.0)
#                 conf.append(ConfidenceScore(index=b.index, score=score))
#         else:
#             conf = [ConfidenceScore(index=b.index, score=1.0) for b in boundaries]

#         # 7. Unified prediction
#         return Prediction(
#             syllables=sylls,
#             boundaries=boundaries,
#             confidence=conf,
#             raw={
#                 "backend": "crf",
#                 "tags": tags,
#             },
#         )

#     # --------------------------------------------------------------
#     # Batch prediction
#     # --------------------------------------------------------------

#     def predict_batch(self, words: List[str]) -> List[Prediction]:
#         """
#         Batch prediction: guarantees equivalence with per-word predict().
#         """
#         return [self.predict(w) for w in words]

#     # --------------------------------------------------------------
#     # Metadata
#     # --------------------------------------------------------------
#     # Model specific features
#     def _feature_metadata(self):
#         return {
#             "tagset": self.tagset,
#             "num_features": len(self.feature_templates),
#             "feature_templates": self.feature_templates,
#             "model_path": str(self.model_path),
#         }

#     def get_metadata(self, include_ruleset=False) -> Dict[str, Any]:
#         return {
#             "backend_type": "crf",
#             "version": self.backend_version,
#             "capabilities": {
#                 "supports_confidence": True,
#                 "supports_batch": True,
#                 "supports_gpu": False,
#                 "supports_cpu": True,
#             },
#             "ums": self._base_ums(),
#         }

#     # --------------------------------------------------------------
#     # API
#     # --------------------------------------------------------------

#     def __call__(self, word: str) -> Prediction:
#         return self.predict(word)

from __future__ import annotations

import importlib.resources
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import joblib
import traceback
from zomi_syl.exceptions import ZomiSylError

import logging

logger = logging.getLogger(__name__)

from zomi_syl.core.interfaces import (
    BaseSyllabifier,
    Prediction,
    Boundary,
    ConfidenceScore,
)

from zomi_syl.utils.features import strip_and_flags, sent2features
from zomi_syl.utils.model_paths import resolve_model_path

# Graceful import of pycrfsuite
try:
    import pycrfsuite
    PYCRFSUITE_AVAILABLE = True
except ImportError:
    PYCRFSUITE_AVAILABLE = False
    pycrfsuite = None

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
    
    # Add this class-level constant for easy checking
    AVAILABLE: bool = PYCRFSUITE_AVAILABLE

    def __init__(self, model_dir: str | None = None):
        # Check if pycrfsuite is available
        if not PYCRFSUITE_AVAILABLE:
            raise ZomiSylError(
                "CRF backend requires 'python-crfsuite' package.\n"
                "Install it with: pip install python-crfsuite"
            )

        self.backend_name = self.backend_name
        if model_dir is None:
            model_dir = resolve_model_path("crf")
        # 1. Resolve model directory
        if model_dir is not None:
            self.model_dir = Path(model_dir)
        else:
            self.model_dir = self._resolve_model_path()

        # 2. Find model file (try multiple extensions)
        self.model_path = self._find_model_file()
        
        if self.model_path is None:
            raise FileNotFoundError(
                f"No CRF model found in {self.model_dir}. "
                f"Available files: {self._list_model_files()}"
            )

        # 3. Load model using pycrfsuite
        try:
            self.model = pycrfsuite.Tagger()
            self.model.open(str(self.model_path))
            logger.info(f"[CRFBackend] Model loaded successfully from {str(self.model_path)}")
        except Exception as e:
            tb = traceback.format_exc()
            raise ZomiSylError(
                f"CRF model failed to load from {self.model_path}: {e}\n\n{tb}"
            )
        
        # 4. Get/Define CRF tagset
        # pycrfsuite doesn't store tagset directly, but we can infer it
        # or store it as metadata separately
        self.tagset = ["B", "I"]  # Default BIO tags
        
        # 5. Get/Define feature templates (must match training)
        # pycrfsuite doesn't store feature templates directly
        # You might want to store these separately or hardcode them
        self.feature_templates = []

    def _resolve_model_path(self):
        """Resolve the path to the packaged CRF model."""
        try:
            import importlib.resources
            model_dir = importlib.resources.files("zomi_syl.models.crf")
            return Path(str(model_dir))
        except Exception as e:
            raise ZomiSylError(f"Could not resolve model path: {e}")

    def _find_model_file(self) -> Optional[Path]:
        """Find the model file, trying multiple possible names/extensions."""
        possible_names = [
            "crf_syllabifier.crfsuite",
            "crf_syllabifier.joblib",
            "crf_syllabifier.pkl",
            "model.crfsuite",
            "model.joblib",
            "crf_model.crfsuite",
            "crf_model.joblib",
        ]
        
        for name in possible_names:
            candidate = self.model_dir / name
            if candidate.exists() and candidate.is_file():
                return candidate
        return None

    def _list_model_files(self) -> List[str]:
        """List all files in the model directory."""
        try:
            if self.model_dir.exists() and self.model_dir.is_dir():
                return [f.name for f in self.model_dir.iterdir() if f.is_file()]
            return []
        except Exception:
            return []

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

    def predict_single(self, xseq):
        """
        Predict tags for a single feature sequence.
        
        Args:
            xseq: List of feature dictionaries for each position
            
        Returns:
            List of predicted tags (B/I)
        """
        if self.model_path is None:
            raise RuntimeError("Model not trained or loaded")
        
        # Use the already loaded tagger
        return self.model.tag(xseq)
    
    def predict(self, word: str) -> Prediction:
        """
        Predict syllable boundaries for a single word.
        Hyphens in the input are ignored for feature extraction.
        """
        if not PYCRFSUITE_AVAILABLE:
            raise ZomiSylError(
                "CRF backend requires 'python-crfsuite' package.\n"
                "Install it with: pip install python-crfsuite"
            )

        # 1. Strip hyphens → chars + flags
        chars, flags = strip_and_flags(word)

        # 2. Features (must match training)
        X = sent2features(chars, flags)

        # 3. Predict BIO tags using pycrfsuite
        # 3. Predict BIO tags using predict_single method
        try:
            # tags = self.model.tag(X)
            tags = self.predict_single(X)
        except Exception as e:
            raise ZomiSylError(f"CRF prediction failed: {e}")

        # 4. BIO → syllables (on stripped chars)
        sylls = self._bio_to_syllables(chars, tags)

        # 5. Boundaries (indices in stripped string)
        boundaries: List[Boundary] = []
        idx = 0
        for syl in sylls[:-1]:
            idx += len(syl)
            boundaries.append(Boundary(index=idx, is_boundary=True))

        # 6. Confidence scores (pycrfsuite doesn't support marginals directly)
        conf: List[ConfidenceScore] = []
        for b in boundaries:
            # Try to get actual confidence if available
            try:
                # Some pycrfsuite versions support marginals
                marginals = self.model.marginals(X)
                if marginals and b.index - 1 < len(marginals):
                    score = marginals[b.index - 1].get("B", 0.5)
                else:
                    score = 0.5
            except (AttributeError, Exception):
                score = 0.5
            conf.append(ConfidenceScore(index=b.index, score=score))

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
            "model_type": "pycrfsuite",
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
            "feature_metadata": self._feature_metadata(),
        }

    # --------------------------------------------------------------
    # API
    # --------------------------------------------------------------

    def __call__(self, word: str) -> Prediction:
        return self.predict(word)