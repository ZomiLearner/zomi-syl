#!/usr/bin/env python3
"""
Validate syllable boundaries between:
  - word (orthographic, may contain hyphens)
  - syllables (explicit hyphen-separated syllables)

This script checks:
  1. Hyphens in the word are treated as syllable boundaries.
  2. Syllables column aligns with the hyphen-stripped word.
  3. No mismatches in character sequences.
  4. Distinctions like 'naah' vs 'na-ah' are preserved.

Usage:
    python scripts/test_syllable_boundaries.py data/zomi_syllabified_human.tsv
"""

import sys
import csv
from typing import List, Tuple


def strip_and_flags(word: str) -> Tuple[List[str], List[bool]]:
    """
    Remove hyphens from the orthographic word, but record whether each
    character was preceded by a hyphen.

    Example:
        "na-ah" -> chars = ["n","a","a","h"]
                  flags = [False, False, True, False]
    """
    chars = []
    flags = []
    last_was_hyphen = False

    for ch in word:
        if ch == "-":
            last_was_hyphen = True
            continue
        chars.append(ch)
        flags.append(last_was_hyphen)
        last_was_hyphen = False

    return chars, flags


def check_alignment(word: str, syllables: str) -> Tuple[bool, str]:
    """
    Validate that the syllables string aligns with the hyphen-stripped word.
    Returns (ok, message).
    """
    clean_chars, flags = strip_and_flags(word)
    parts = syllables.split("-")

    # Flatten syllables into characters
    flat = "".join(parts)

    if len(flat) != len(clean_chars):
        return False, (
            f"Length mismatch: clean='{ ''.join(clean_chars) }' "
            f"({len(clean_chars)} chars) vs syllables='{flat}' ({len(flat)} chars)"
        )

    # Character-by-character check
    for i, (c1, c2) in enumerate(zip(clean_chars, flat)):
        if c1 != c2:
            return False, (
                f"Char mismatch at index {i}: "
                f"clean='{c1}' vs syllables='{c2}' "
                f"(word='{word}', syllables='{syllables}')"
            )

    # Optional: check that hyphens in word correspond to syllable boundaries
    # If a hyphen was before clean_chars[i], then syllables should start a new part at that char.
    syll_index = 0
    char_count = 0
    for part in parts:
        for _ in part:
            if char_count < len(flags) and flags[char_count] and syll_index == 0:
                # Hyphen in word but syllable didn't start here
                return False, (
                    f"Word has hyphen before char {char_count}, "
                    f"but syllables do not start a new syllable here. "
                    f"(word='{word}', syllables='{syllables}')"
                )
            char_count += 1
        syll_index += 1

    return True, "OK"


def main():
    if len(sys.argv) != 2:
        print("Usage: python test_syllable_boundaries.py <file.tsv>")
        sys.exit(1)

    path = sys.argv[1]

    total = 0
    passed = 0
    failed = 0

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            total += 1
            word = row["word"].strip()
            syll = row["syllables"].strip()

            ok, msg = check_alignment(word, syll)
            if ok:
                passed += 1
            else:
                failed += 1
                print(f"[FAIL] {word} | {syll} → {msg}")

    print("\n=== SUMMARY ===")
    print(f"Total rows:   {total}")
    print(f"Passed:       {passed}")
    print(f"Failed:       {failed}")
    print("================")


if __name__ == "__main__":
    main()
