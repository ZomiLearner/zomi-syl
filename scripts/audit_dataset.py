# !/usr/bin/env python3

""" 
usage:
    python3 scripts/audit_dataset.py

"""

import csv
from collections import defaultdict, Counter
from train_crf import (
    strip_hyphens_with_flags,
    syllables_to_labels,
)

# -----------------------------
# Zomi onset clusters
# -----------------------------
VALID_ONSETS = {
    "t","th","k","kh","p","ph","ng","n","m","s","z","v","h","l","r",
    "g","b","d","j","ch","sh","tl","kl","pl","gl","br","dr","gr",
    "kr","pr","tr","thr","phr","khr"
}

def is_valid_onset(s):
    return any(s.startswith(o) for o in VALID_ONSETS)


# -----------------------------
# 1. Inconsistent segmentation
# -----------------------------
def find_inconsistent_segmentations(rows):
    groups = defaultdict(set)
    for w, s in rows:
        groups[w].add(s)
    return {w: segs for w, segs in groups.items() if len(segs) > 1}


# -----------------------------
# 2. Illegal onset splits
# -----------------------------
def find_illegal_onset_splits(rows):
    bad = []
    for w, s in rows:
        parts = s.split("-")
        for p in parts:
            if not is_valid_onset(p):
                bad.append((w, s, p))
                break
    return bad


# -----------------------------
# 3. Reverse-rule violations
# -----------------------------
def find_reverse_rule_violations(rows):
    violations = []
    for w, s in rows:
        parts = s.split("-")
        if len(parts) < 2:
            continue

        prefix = parts[0]
        final = parts[-1]

        if not is_valid_onset(prefix):
            violations.append((w, s, "Invalid prefix onset"))

        if len(final) == 0:
            violations.append((w, s, "Empty final syllable"))

    return violations


# -----------------------------
# 4. Alignment errors (CRF BIO)
# -----------------------------
def find_alignment_errors(rows):
    errors = []
    for w, s in rows:
        clean, flags = strip_hyphens_with_flags(w)
        try:
            _ = syllables_to_labels(clean, s)
        except Exception as e:
            errors.append((w, s, str(e)))
    return errors


# -----------------------------
# 5. Syllable frequency table
# -----------------------------
def syllable_frequency(rows):
    counter = Counter()
    for _, s in rows:
        for syl in s.split("-"):
            counter[syl] += 1
    return counter


# -----------------------------
# Main audit function
# -----------------------------
def audit(path="data/zomi_syllabified_human.tsv"):
    rows = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            rows.append((row["word"].strip(), row["syllables"].strip()))

    print("\n=== DATASET AUDIT REPORT ===\n")

    # 1. Inconsistent segmentations
    inconsistent = find_inconsistent_segmentations(rows)
    print("1. Inconsistent segmentations:")
    for w, segs in inconsistent.items():
        print("  ", w, "→", segs)
    print(f"Total inconsistent words: {len(inconsistent)}\n")

    # 2. Illegal onset splits
    illegal = find_illegal_onset_splits(rows)
    print("2. Illegal onset splits:")
    for w, s, bad in illegal[:50]:
        print("  ", w, "|", s, "| illegal onset:", bad)
    print(f"Total illegal onset splits: {len(illegal)}\n")

    # 3. Reverse-rule violations
    reverse = find_reverse_rule_violations(rows)
    print("3. Reverse-rule violations:")
    for w, s, reason in reverse[:50]:
        print("  ", w, "|", s, "|", reason)
    print(f"Total reverse-rule violations: {len(reverse)}\n")

    # 4. Alignment errors
    alignment = find_alignment_errors(rows)
    print("4. Alignment errors:")
    for w, s, err in alignment[:50]:
        print("  ", w, "|", s, "|", err)
    print(f"Total alignment errors: {len(alignment)}\n")

    # 5. Syllable frequency
    freq = syllable_frequency(rows)
    print("5. Top 30 syllables:")
    for syl, count in freq.most_common(30):
        print(f"  {count:5d}  {syl}")

    print("\n=== END OF REPORT ===\n")


if __name__ == "__main__":
    audit()
