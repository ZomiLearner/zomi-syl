#!/usr/bin/env python3

# zomi_syl/utils/features.py
# Shared Zomi-aware feature extractor for CRF training + inference

from typing import List, Dict, Any, Tuple

# -----------------------------
# Zomi linguistic constants
# -----------------------------

ZOMI_ONSETS = {
    "k",
    "kh",
    "g",
    "ng",
    "t",
    "th",
    "d",
    "n",
    "p",
    "ph",
    "b",
    "m",
    "s",
    "z",
    "c",
    "ch",
    "j",
    "l",
    "r",
    "h",
}

CODA_CLUSTERS = {"ng"}

ZOMI_CODAS = {"k", "ng", "m", "n", "p", "t", "h"}

VOWELS = {"a", "e", "i", "o", "u"}
LONG_VOWELS = {"aa", "ee", "ii", "oo", "uu"}

PREFIXES = {"a", "ka", "na", "ta", "pa", "in", "hun", "thu"}


# -----------------------------
# Hyphen stripping (shared)
# -----------------------------


def strip_and_flags(word: str) -> Tuple[List[str], List[bool]]:
    chars = []
    flags = []
    last = False

    for ch in word:
        if ch == "-":
            last = True
            continue
        chars.append(ch)
        flags.append(last)
        last = False

    return chars, flags


# -----------------------------
# Zomi-aware feature extractor
# -----------------------------


def char_features(chars: List[str], prev_hyphen_flags: List[bool], i: int) -> Dict[str, Any]:
    ch = chars[i]
    features: Dict[str, Any] = {
        "bias": 1.0,
        "char": ch,
        "char.lower": ch.lower(),
        "is_digit": ch.isdigit(),
        "is_alpha": ch.isalpha(),
        "is_upper": ch.isupper(),
        "is_lower": ch.islower(),
        "pos": i,
        "pos_from_end": len(chars) - i - 1,
        "prev_hyphen": prev_hyphen_flags[i],
    }

    # -------------------------
    # A. Context characters
    # -------------------------
    if i > 0:
        prev = chars[i - 1]
        features.update(
            {
                "prev.char": prev,
                "prev.char.lower": prev.lower(),
                "prev.prev_hyphen": prev_hyphen_flags[i - 1],
            }
        )
    else:
        features["BOS"] = True

    if i < len(chars) - 1:
        nxt = chars[i + 1]
        features.update(
            {
                "next.char": nxt,
                "next.char.lower": nxt.lower(),
                "next_prev_hyphen": prev_hyphen_flags[i + 1],
            }
        )
    else:
        features["EOS"] = True

    # -------------------------
    # B. Zomi onset features
    # -------------------------
    bigram = "".join(chars[i : i + 2])
    trigram = "".join(chars[i : i + 3])

    features["is_onset_bigram"] = bigram in ZOMI_ONSETS
    features["is_onset_trigram"] = trigram in ZOMI_ONSETS

    # # Detect coda clusters like "ng"
    # if i > 0:
    #     pair = chars[i-1] + chars[i]
    #     if pair in CODA_CLUSTERS:
    #         features["is_coda"] = True

    if i > 0:
        prev_bigram = "".join(chars[i - 1 : i + 1])
        features["prev_is_onset"] = prev_bigram in ZOMI_ONSETS

    if i < len(chars) - 1:
        next_bigram = "".join(chars[i : i + 2])
        features["next_is_onset"] = next_bigram in ZOMI_ONSETS

    # -------------------------
    # C. Coda features
    # -------------------------
    # features["is_coda"] = ch in ZOMI_CODAS
    # Start with simple coda consonants
    is_coda = ch in ZOMI_CODAS

    # Add coda clusters like "ng"
    if i > 0:
        pair = chars[i - 1] + chars[i]
        if pair in CODA_CLUSTERS:
            is_coda = True

    features["is_coda"] = is_coda

    if i > 0:
        features["prev_is_coda"] = chars[i - 1] in ZOMI_CODAS

    if i < len(chars) - 1:
        features["next_is_coda"] = chars[i + 1] in ZOMI_CODAS

    # -------------------------
    # D. Vowel features
    # -------------------------
    features["is_vowel"] = ch.lower() in VOWELS

    if i < len(chars) - 1:
        digraph = ch.lower() + chars[i + 1].lower()
        features["is_long_vowel"] = digraph in LONG_VOWELS
    else:
        features["is_long_vowel"] = False

    features["vowel_class"] = ch.lower() if ch.lower() in VOWELS else "C"

    # -------------------------
    # E. Reverse-rule features
    # -------------------------
    features["suffix_2"] = "".join(chars[i : i + 2])
    features["suffix_3"] = "".join(chars[i : i + 3])
    features["suffix_4"] = "".join(chars[i : i + 4])

    features["prefix_2"] = "".join(chars[0:2])
    features["prefix_3"] = "".join(chars[0:3])

    # -------------------------
    # F. Morphological prefix features
    # -------------------------
    prefix = "".join(chars[0:i])
    features["is_prefix"] = prefix in PREFIXES

    for p in PREFIXES:
        if prefix == p:
            features["prefix_class"] = p
            break
    else:
        features["prefix_class"] = "none"

    # -------------------------
    # G. Syllable-shape features
    # -------------------------
    features["char_type"] = "V" if ch.lower() in VOWELS else "C"

    if i > 0:
        features["prev_char_type"] = "V" if chars[i - 1].lower() in VOWELS else "C"
    if i < len(chars) - 1:
        features["next_char_type"] = "V" if chars[i + 1].lower() in VOWELS else "C"

    window = "".join(["V" if c.lower() in VOWELS else "C" for c in chars[max(0, i - 1) : i + 2]])
    features["cvc_pattern_window"] = window

    return features


def sent2features(chars: List[str], flags: List[bool]):
    return [char_features(chars, flags, i) for i in range(len(chars))]


# -----------------------------
# Decoding labels → syllables
# -----------------------------


def labels_to_syllables(chars: List[str], labels: List[str]) -> str:
    """
    Convert BIO labels back into a hyphen-separated syllable string.
    """
    syllables = []
    current = []

    for ch, lab in zip(chars, labels):
        if lab == "B":
            if current:
                syllables.append("".join(current))
            current = [ch]
        else:
            current.append(ch)

    if current:
        syllables.append("".join(current))

    return "-".join(syllables)


extract_features = char_features
