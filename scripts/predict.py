#!/usr/bin/env python3
"""
CRF syllabifier inference script for Zomi.

Usage:
    python scripts/predict.py "thungetna-ah"
"""

import argparse
import joblib

# Unified feature extractor
from .features import strip_and_flags, sent2features, labels_to_syllables
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Predict syllables for a Zomi word.")
    parser.add_argument("--model_dir", type=str, required=True, help="Directory containing CRF model")
    parser.add_argument("--word", type=str, required=True, help="Word to syllabify")
    return parser.parse_args()

# -----------------------------
# Inference
# -----------------------------

def predict_syllables(word: str, model_path: str = "training/model/crf/crf_syllabifier.joblib") -> str:
    """Predict syllable boundaries for a single word."""
    crf = joblib.load(model_path)

    clean_chars, flags = strip_and_flags(word)
    X = sent2features(clean_chars, flags)
    labels = crf.predict_single(X)

    return labels_to_syllables(clean_chars, labels)


# -----------------------------
# CLI
# -----------------------------

def main():
    args = parse_args()

    model_path = Path(args.model_dir) / "crf_syllabifier.joblib"
    model = joblib.load(model_path)

    chars, flags = strip_and_flags(args.word)
    feats = sent2features(chars, flags)
    labels = model.predict_single(feats)

    print(labels_to_syllables(chars, labels))


if __name__ == "__main__":
    main()
