from __future__ import annotations
from typing import List, Dict, Any
import torch

from transformers import AutoTokenizer, AutoModelForTokenClassification

from zomi_syl.core.interfaces import (
    BasePredictor,
    Prediction,
    Boundary,
    ConfidenceScore,
)
from zomi_syl.models.utils import logits_to_tags, tags_to_boundaries


class TransformerBackend(BasePredictor):

    def __init__(self, model_name: str, device: str = "cpu"):
        self.model_name = model_name
        self.device = device

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.model.to(device)
        self.model.eval()

    def predict(self, word: str) -> Prediction:
        inputs = self.tokenizer(list(word), return_tensors="pt", is_split_into_words=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits.squeeze(0)

        tags = logits_to_tags(logits)
        boundaries = tags_to_boundaries(word, tags)
        conf = self.predict_proba(word)

        return Prediction(
            syllables="-".join(_split(word, boundaries)),
            boundaries=boundaries,
            confidence=conf,
            raw={"logits": logits.cpu().tolist(), "tags": tags},
        )

    def predict_batch(self, words: List[str]) -> List[Prediction]:
        return [self.predict(w) for w in words]

    def predict_proba(self, word: str) -> List[ConfidenceScore]:
        inputs = self.tokenizer(list(word), return_tensors="pt", is_split_into_words=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits.squeeze(0)

        probs = torch.softmax(logits, dim=-1)
        idx_B = self.model.config.label2id.get("B", 1)

        return [ConfidenceScore(index=i, score=float(probs[i][idx_B])) for i in range(len(word))]

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "backend_type": "transformer",
            "version": "1.0.0",
            "capabilities": {
                "supports_confidence": True,
                "supports_batch": False,
                "supports_gpu": self.device != "cpu",
            },
            "model_name": self.model_name,
        }


def _split(word: str, boundaries: List[Boundary]) -> List[str]:
    idxs = [b.index for b in boundaries]
    parts = []
    prev = 0
    for i in idxs:
        parts.append(word[prev:i])
        prev = i
    parts.append(word[prev:])
    return parts
