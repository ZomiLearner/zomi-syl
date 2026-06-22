#!/usr/bin/env python3
"""
Train a CRF-based Zomi syllabifier from a TSV file with syllable-level alignment.
"""

import argparse
import os
import csv
from typing import List, Dict

import joblib
import sklearn_crfsuite

# Unified feature extractor
from .features import strip_and_flags, sent2features


# -----------------------------
# Data loading
# -----------------------------

def read_tsv(path: str) -> List[Dict[str, str]]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            w = (row.get("word") or "").strip()
            s = (row.get("syllables") or "").strip()

            if w and s:
                rows.append({"word": w, "syllables": s})
    return rows


# -----------------------------
# Convert gold syllables → BIO labels
# -----------------------------

def syllables_to_labels(clean_chars: List[str], syllables: str) -> List[str]:
    parts = syllables.split("-")
    labels = []
    idx = 0

    for part in parts:
        for j, ch in enumerate(part):
            if idx >= len(clean_chars):
                raise ValueError("Length mismatch")
            if clean_chars[idx] != ch:
                raise ValueError("Character mismatch")
            labels.append("B" if j == 0 else "I")
            idx += 1

    if idx != len(clean_chars):
        raise ValueError("Final length mismatch")

    return labels


# -----------------------------
# Train CRF
# -----------------------------

def train_crf(X_train, y_train):
    crf = sklearn_crfsuite.CRF(
        algorithm="lbfgs",
        c1=0.1,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True,
    )
    crf.fit(X_train, y_train)
    return crf

def save_model(crf, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(crf, os.path.join(output_dir, "crf_syllabifier.joblib"))

    import json
    with open(os.path.join(output_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump({"model_type": "CRF", "task": "zomi_syllabification"}, f, indent=2)


# -----------------------------
# Main
# -----------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = read_tsv(args.input)
    if not rows:
        raise SystemExit("No valid rows found")

    X_train = []
    y_train = []
    skipped = 0

    for row in rows:
        word = row["word"]
        syll = row["syllables"]

        clean_chars, flags = strip_and_flags(word)

        try:
            labels = syllables_to_labels(clean_chars, syll)
        except Exception as e:
            print("Alignment error:", word, "|", syll, "|", e)
            skipped += 1
            continue

        if len(clean_chars) != len(labels):
            print("Skipping row (length mismatch):", word, "|", syll)
            skipped += 1
            continue

        # NEW unified feature extractor
        X_train.append(sent2features(clean_chars, flags))
        y_train.append(labels)

    print(f"Training on {len(X_train)} words (skipped {skipped})...")
    crf = train_crf(X_train, y_train)
    save_model(crf, args.output)


if __name__ == "__main__":
    main()
