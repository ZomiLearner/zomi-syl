#!/usr/bin/env python3
"""
Evaluate CRF syllabifier on a TSV dataset.
Computes accuracy, precision, recall, F1.

Usage:
    python scripts/evaluate_crf.py
"""

import csv
import joblib
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

# Unified feature extractor
from .features import strip_and_flags, sent2features, labels_to_syllables


def load_data(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append((row["word"].strip(), row["syllables"].strip()))
    return rows


def flatten_labels(label_lists):
    return [lab for seq in label_lists for lab in seq]


def main():
    model = joblib.load("training/model/crf/crf_syllabifier.joblib")
    data = load_data("training/data/zomi_only.tsv")

    gold_all = []
    pred_all = []

    for word, gold_syll in data:
        clean_chars, flags = strip_and_flags(word)
        X = sent2features(clean_chars, flags)

        pred_labels = model.predict_single(X)

        # Convert gold syllables to BIO labels
        gold_labels = []
        for part in gold_syll.split("-"):
            gold_labels.append("B")
            gold_labels.extend(["I"] * (len(part) - 1))

        gold_all.extend(gold_labels)
        pred_all.extend(pred_labels)

    print("Accuracy:", accuracy_score(gold_all, pred_all))
    print("Precision:", precision_score(gold_all, pred_all, average="macro"))
    print("Recall:", recall_score(gold_all, pred_all, average="macro"))
    print("F1:", f1_score(gold_all, pred_all, average="macro"))


if __name__ == "__main__":
    main()
