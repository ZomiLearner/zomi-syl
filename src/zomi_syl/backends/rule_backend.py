# # from __future__ import annotations
# # from typing import List, Dict, Any

# # from zomi_syl.core.interfaces import (
# #     BaseSyllabifier,
# #     Prediction,
# #     Boundary,
# #     ConfidenceScore,
# # )
# # from zomi_syl.rule_based.syllabifier import syllabify_rule_based
# # from zomi_syl.registry.profiles import load_profile


# # class RuleBackend2(BaseSyllabifier):

# #     def __init__(self, dialect: str = "tedim"):
# #         self.dialect = dialect
# #         self.profile = load_profile(dialect)

# #     def predict(self, word: str) -> Prediction:
# #         sylls = syllabify_rule_based(
# #             word=word,
# #             profile={
# #                 "onsets": self.profile["onsets"],
# #                 "nuclei": self.profile["nuclei"],
# #                 "codas": self.profile["codas"],
# #             },
# #             rules=self.profile["rules"],
# #         )

# #         boundaries = []
# #         idx = 0
# #         for syl in sylls[:-1]:
# #             idx += len(syl)
# #             boundaries.append(Boundary(index=idx, is_boundary=True))

# #         conf = [ConfidenceScore(index=b.index, score=1.0) for b in boundaries]

# #         return Prediction(
# #             syllables="-".join(sylls),
# #             boundaries=boundaries,
# #             confidence=conf,
# #             raw={"backend": "rule"},
# #         )

# #     def predict_batch(self, words: List[str]) -> List[Prediction]:
# #         return [self.predict(w) for w in words]

# #     def get_metadata(self) -> Dict[str, Any]:
# #         return {
# #             "backend_type": "rule",
# #             "version": "1.0.0",
# #             "capabilities": {
# #                 "supports_confidence": True,
# #                 "supports_batch": True,
# #                 "supports_gpu": False,
# #             },
# #             "dialect": self.dialect,
# #         }


#################################

# from __future__ import annotations
# from typing import List, Dict, Any
# import json
# from pathlib import Path
# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)

# from zomi_syl.core.interfaces import (
#     BaseSyllabifier,
#     Prediction,
#     Boundary,
#     ConfidenceScore,
# )
# from zomi_syl.rule_based.syllabifier import syllabify_rule_based
# from zomi_syl.backends.rule_backend_reverse import reverse_syllabify
# import json


# class RuleBackend(BaseSyllabifier):

#     def __init__(self, model_dir: str, use_reverse: bool = False):
#         """
#         Parameters:
#             model_dir: path to bundled rule model directory
#             use_reverse: if True, use reverse syllabifier instead of forward
#         """
#         self.model_dir = Path(model_dir)
#         self.use_reverse = use_reverse

#         ruleset_path = self.model_dir / "ruleset.json"
#         if not ruleset_path.exists():
#             raise FileNotFoundError(f"ruleset.json not found in {self.model_dir}")

#         self.ruleset = json.loads(ruleset_path.read_text(encoding="utf-8"))

#         self.onsets = self.ruleset["onsets"]
#         self.nuclei = self.ruleset["nuclei"]
#         self.codas = self.ruleset["codas"]
#         self.rules = self.ruleset["rules"]

#     # ------------------------------------------------------------------
#     # Core prediction
#     # ------------------------------------------------------------------

#     def predict(self, word: str) -> Prediction:
#         """
#         Predict syllables using either:
#             - forward rule-based syllabifier
#             - reverse syllabifier (suffix-first)
#         """

#         # -------------------------------
#         # 1. Choose algorithm
#         # -------------------------------
#         if self.use_reverse:
#             sylls = reverse_syllabify(word, {
#                 "onsets": self.onsets,
#                 "nuclei": self.nuclei,
#                 "codas": self.codas,
#             })
#         else:
#             sylls = syllabify_rule_based(
#                 word=word,
#                 profile={
#                     "onsets": self.onsets,
#                     "nuclei": self.nuclei,
#                     "codas": self.codas,
#                 },
#                 rules=self.rules,
#             )

#         # -------------------------------
#         # 2. Build boundaries
#         # -------------------------------
#         boundaries = []
#         idx = 0
#         for syl in sylls[:-1]:
#             idx += len(syl)
#             boundaries.append(Boundary(index=idx, is_boundary=True))

#         # -------------------------------
#         # 3. Confidence (rule-based = 1.0)
#         # -------------------------------
#         conf = [ConfidenceScore(index=b.index, score=1.0) for b in boundaries]

#         # -------------------------------
#         # 4. Wrap in Prediction object
#         # -------------------------------
#         return Prediction(
#             syllables=sylls,                # LIST[str]
#             boundaries=boundaries,
#             confidence=conf,
#             raw={
#                 "backend": "rule-reverse" if self.use_reverse else "rule",
#                 "ruleset": self.ruleset,
#             },
#         )

#     # ------------------------------------------------------------------
#     # Batch prediction
#     # ------------------------------------------------------------------

#     def predict_batch(self, words: List[str]) -> List[Prediction]:
#         return [self.predict(w) for w in words]

#     # ------------------------------------------------------------------
#     # Metadata
#     # ------------------------------------------------------------------

#     def get_metadata(self) -> Dict[str, Any]:
#         return {
#             "backend_type": "rule-reverse" if self.use_reverse else "rule",
#             "version": "1.0.0",
#             "capabilities": {
#                 "supports_confidence": True,
#                 "supports_batch": True,
#                 "supports_gpu": False,
#             },
#             "model_dir": str(self.model_dir),
#         }

############################


# from __future__ import annotations
# from typing import List, Dict, Any
# from pathlib import Path
# import json

# from zomi_syl.core.interfaces import (
#     BaseSyllabifier,
#     Prediction,
#     Boundary,
#     ConfidenceScore,
# )

# from zomi_syl.rule_based.syllabifier import syllabify_rule_based
# from zomi_syl.backends.rule_backend_reverse import reverse_syllabify


# class RuleBackend(BaseSyllabifier):

#     def __init__(self, model_dir: str, use_reverse: bool = False):
#         """
#         RuleBackend supporting both forward and reverse syllabification.

#         Args:
#             model_dir: path to bundled rule model directory
#             use_reverse: if True, use reverse syllabifier
#         """
#         self.model_dir = Path(model_dir)
#         self.use_reverse = use_reverse

#         ruleset_path = self.model_dir / "ruleset.json"
#         if not ruleset_path.exists():
#             raise FileNotFoundError(f"ruleset.json not found in {self.model_dir}")

#         self.ruleset = json.loads(ruleset_path.read_text(encoding="utf-8"))

#         self.onsets = self.ruleset["onsets"]
#         self.nuclei = self.ruleset["nuclei"]
#         self.codas = self.ruleset["codas"]
#         self.rules = self.ruleset["rules"]

#     # ------------------------------------------------------------------
#     # Core prediction
#     # ------------------------------------------------------------------

#     def predict(self, word: str) -> Prediction:
#         """
#         Predict syllables using either:
#             - forward rule-based syllabifier
#             - reverse syllabifier (suffix-first)
#         """

#         # 1. Choose algorithm
#         if self.use_reverse:
#             sylls = reverse_syllabify(word, {
#                 "onsets": self.onsets,
#                 "nuclei": self.nuclei,
#                 "codas": self.codas,
#             })
#             backend_name = "rule-reverse"
#         else:
#             sylls = syllabify_rule_based(
#                 word=word,
#                 profile={
#                     "onsets": self.onsets,
#                     "nuclei": self.nuclei,
#                     "codas": self.codas,
#                 },
#                 rules=self.rules,
#             )
#             backend_name = "rule"

#         # 2. Build boundaries
#         boundaries = []
#         idx = 0
#         for syl in sylls[:-1]:
#             idx += len(syl)
#             boundaries.append(Boundary(index=idx, is_boundary=True))

#         # 3. Confidence (rule-based = 1.0)
#         conf = [ConfidenceScore(index=b.index, score=1.0) for b in boundaries]

#         # 4. Wrap in Prediction object
#         return Prediction(
#             syllables=sylls,  # LIST[str]
#             boundaries=boundaries,
#             confidence=conf,
#             raw={
#                 "backend": backend_name,
#                 "ruleset": self.ruleset,
#             },
#         )

#     # ------------------------------------------------------------------
#     # Batch prediction
#     # ------------------------------------------------------------------

#     def predict_batch(self, words: List[str]) -> List[Prediction]:
#         return [self.predict(w) for w in words]

#     # ------------------------------------------------------------------
#     # Metadata
#     # ------------------------------------------------------------------

#     def get_metadata(self) -> Dict[str, Any]:
#         return {
#             "backend_type": "rule-reverse" if self.use_reverse else "rule",
#             "version": "1.0.0",
#             "capabilities": {
#                 "supports_confidence": True,
#                 "supports_batch": True,
#                 "supports_gpu": False,
#             },
#             "model_dir": str(self.model_dir),
#         }

##############################


# from __future__ import annotations
# from typing import List, Dict, Any
# from pathlib import Path
# import json

# from zomi_syl.core.interfaces import (
#     BaseSyllabifier,
#     Prediction,
#     Boundary,
#     ConfidenceScore,
# )

# from zomi_syl.rule_based.syllabifier import syllabify_rule_based
# from zomi_syl.backends.rule_backend_reverse import reverse_syllabify


# class RuleBackend(BaseSyllabifier):

#     def __init__(self, model_dir: str):
#         self.model_dir = Path(model_dir)

#         ruleset_path = self.model_dir / "ruleset.json"
#         if not ruleset_path.exists():
#             raise FileNotFoundError(f"ruleset.json not found in {self.model_dir}")

#         self.ruleset = json.loads(ruleset_path.read_text(encoding="utf-8"))

#         self.onsets = self.ruleset["onsets"]
#         self.nuclei = self.ruleset["nuclei"]
#         self.codas = self.ruleset["codas"]
#         self.rules = self.ruleset["rules"]

#     # --------------------------------------------------------------
#     # Hybrid syllabification
#     # --------------------------------------------------------------

#     def _valid_syllable(self, syl: str) -> bool:
#         """
#         Very strict Zomi phonotactic validator.
#         Rejects impossible syllables like 'i', 'tna', 'lphu', etc.
#         """
#         # nucleus must exist
#         if not any(n in syl for n in self.nuclei):
#             return False

#         # no illegal onset clusters
#         for onset in ["lp", "rp", "rt", "tn", "tl", "lph", "tph"]:
#             if syl.startswith(onset):
#                 return False

#         # no illegal coda clusters
#         for bad in ["lp", "rp", "rt", "tn", "tl"]:
#             if syl.endswith(bad):
#                 return False

#         return True

#     def _valid_sequence(self, sylls: List[str]) -> bool:
#         """Reject sequences with illegal syllables."""
#         return all(self._valid_syllable(s) for s in sylls)

#     # --------------------------------------------------------------
#     # Core prediction
#     # --------------------------------------------------------------

#     def predict(self, word: str) -> Prediction:
#         """
#         Hybrid syllabification:
#             1. Try reverse syllabifier
#             2. Validate
#             3. If invalid → try forward
#             4. Validate
#             5. If both fail → fallback to safest segmentation
#         """

#         # 1. Reverse attempt
#         try:
#             rev = reverse_syllabify(word, {
#                 "onsets": self.onsets,
#                 "nuclei": self.nuclei,
#                 "codas": self.codas,
#             })
#             if self._valid_sequence(rev):
#                 sylls = rev
#                 backend_name = "rule-reverse"
#             else:
#                 raise ValueError("Reverse invalid")
#         except Exception:
#             # 2. Forward attempt
#             print(f"asdfdfdsf")
#             fwd = syllabify_rule_based(
#                 word=word,
#                 profile={
#                     "onsets": self.onsets,
#                     "nuclei": self.nuclei,
#                     "codas": self.codas,
#                 },
#                 rules=self.rules,
#             )
#             if self._valid_sequence(fwd):
#                 sylls = fwd
#                 backend_name = "rule"
#             else:
#                 # 3. Final fallback: split on nuclei
#                 fallback = []
#                 buf = ""
#                 for ch in word:
#                     buf += ch
#                     if any(n in buf for n in self.nuclei):
#                         fallback.append(buf)
#                         buf = ""
#                 if buf:
#                     fallback.append(buf)
#                 sylls = fallback
#                 backend_name = "rule-fallback"

#         # Build boundaries
#         boundaries = []
#         idx = 0
#         for syl in sylls[:-1]:
#             idx += len(syl)
#             boundaries.append(Boundary(index=idx, is_boundary=True))

#         conf = [ConfidenceScore(index=b.index, score=1.0) for b in boundaries]

#         return Prediction(
#             syllables=sylls,
#             boundaries=boundaries,
#             confidence=conf,
#             raw={
#                 "backend": backend_name,
#                 "ruleset": self.ruleset,
#             },
#         )

#     def predict_batch(self, words: List[str]) -> List[Prediction]:
#         return [self.predict(w) for w in words]

#     # ------------------------------------------------------------------
#     # Metadata
#     # ------------------------------------------------------------------

#     def get_metadata(self) -> Dict[str, Any]:
#         return {
#             "backend_type": "rule-reverse" if self.use_reverse else "rule",
#             "version": "1.0.0",
#             "capabilities": {
#                 "supports_confidence": True,
#                 "supports_batch": True,
#                 "supports_gpu": False,
#             },
#             "model_dir": str(self.model_dir),
#         }


from __future__ import annotations
from typing import List, Dict, Any
from pathlib import Path
import json

from zomi_syl.core.interfaces import (
    BaseSyllabifier,
    Prediction,
    Boundary,
    ConfidenceScore,
)

# Use your v6 engine
from zomi_syl.rule_based.syllabify_v6 import syllabify_v6


class RuleBackend(BaseSyllabifier):

    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)

        ruleset_path = self.model_dir / "ruleset.json"
        if not ruleset_path.exists():
            raise FileNotFoundError(f"ruleset.json not found in {self.model_dir}")

        self.ruleset = json.loads(ruleset_path.read_text(encoding="utf-8"))

        # REQUIRED: ruleset.json must contain "all_syllables"
        self.all_syllables = self.ruleset["all_syllables"]

    # --------------------------------------------------------------
    # Core prediction (v6 only)
    # --------------------------------------------------------------

    def predict(self, word: str) -> Prediction:
        sylls = syllabify_v6(word, self.all_syllables)

        # Build boundaries
        boundaries = []
        idx = 0
        for syl in sylls[:-1]:
            idx += len(syl)
            boundaries.append(Boundary(index=idx, is_boundary=True))

        conf = [ConfidenceScore(index=b.index, score=1.0) for b in boundaries]

        return Prediction(
            syllables=sylls,
            boundaries=boundaries,
            confidence=conf,
            raw={
                "backend": "rule-v6",
                "ruleset": self.ruleset,
            },
        )

    def predict_batch(self, words: List[str]) -> List[Prediction]:
        return [self.predict(w) for w in words]

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "backend_type": "rule-reverse" if self.use_reverse else "rule",
            "version": "1.0.0",
            "capabilities": {
                "supports_confidence": True,
                "supports_batch": True,
                "supports_gpu": False,
            },
            "model_dir": str(self.model_dir),
        }
