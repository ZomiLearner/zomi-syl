from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ReverseRuleset:
    onsets: List[str]
    nuclei: List[str]
    codas: List[str]
    # Optional: suffixes/prefixes if one wants to exploit morphology later
    suffixes: Optional[List[str]] = None
    prefixes: Optional[List[str]] = None


def normalize_input(word: str) -> str:
    """Basic normalization + treat hyphen as explicit syllable boundary."""
    # Strip whitespace
    w = word.strip()
    # Normalize hyphen as explicit boundary marker
    # We keep it, but the core algorithm will treat it as a hard boundary.
    return w


def is_onset(seg: str, rules: ReverseRuleset) -> bool:
    return seg in rules.onsets


def is_nucleus(seg: str, rules: ReverseRuleset) -> bool:
    return seg in rules.nuclei


def is_coda(seg: str, rules: ReverseRuleset) -> bool:
    return seg in rules.codas


def segment_graphemes(word: str) -> List[str]:
    """
    Segment into graphemes (digraph‑aware).
    Assumes digraphs are two‑char onsets like 'kh', 'ng', 'ph', etc.
    It can adapt this to use the existing grapheme segmenter.
    """
    digraphs = {"kh", "ng", "ch", "ph", "ts", "ny"}
    i = 0
    out: List[str] = []
    while i < len(word):
        # Hyphen is treated as its own token
        if word[i] == "-":
            out.append("-")
            i += 1
            continue
        if i + 1 < len(word) and word[i : i + 2] in digraphs:
            out.append(word[i : i + 2])
            i += 2
        else:
            out.append(word[i])
            i += 1
    return out


def reverse_syllabify_segment(graphemes: List[str], rules: ReverseRuleset) -> List[str]:
    """
    Reverse syllabification on a single segment (no hyphens inside).
    Returns a list of syllables (each syllable is a string).
    """
    syllables_rev: List[str] = []
    i = len(graphemes) - 1

    while i >= 0:
        # 1. Find nucleus going left
        nucleus_start = nucleus_end = None
        j = i
        while j >= 0:
            # Try longest possible nucleus (e.g. 'aaw', 'iai', etc.)
            # Here we just check single grapheme nuclei; adapt if the nuclei are multi‑grapheme.
            if is_nucleus(graphemes[j], rules):
                nucleus_start = nucleus_end = j
                break
            j -= 1

        if nucleus_start is None:
            # No nucleus found → invalid segment
            raise ValueError(f"Cannot find nucleus in segment: {''.join(graphemes)}")

        # 2. Collect coda to the right of nucleus (if any)
        coda_start = nucleus_end + 1
        coda_end = i
        coda: List[str] = []
        if coda_start <= coda_end:
            # All graphemes to the right are candidate coda
            coda = graphemes[coda_start : coda_end + 1]
            # Enforce simple codas only (no complex codas)
            # If last grapheme is not a valid coda, push it back to next syllable (onset)
            while coda and not is_coda(coda[-1], rules):
                # Move last coda element back to next syllable (onset of previous syllable)
                i -= 1
                coda.pop()
            # If coda is empty after pruning, that's fine (open syllable)

        # 3. Collect onset to the left of nucleus
        onset_end = nucleus_start - 1
        onset_start = onset_end
        onset: List[str] = []
        while onset_start >= 0:
            candidate = graphemes[onset_start]
            if is_onset(candidate, rules):
                onset.insert(0, candidate)
                onset_start -= 1
            else:
                break

        # 4. Build syllable
        syll = "".join(onset + graphemes[nucleus_start : nucleus_end + 1] + coda)
        syllables_rev.append(syll)

        # 5. Move index to the left of this syllable
        i = onset_start

    # Reverse back to normal order
    syllables_rev.reverse()
    return syllables_rev


def reverse_syllabify(word: str, rules_dict: Dict[str, Any]) -> List[str]:
    """
    Public API: reverse syllabify a Zomi word using a ruleset dict
    compatible with the existing ruleset.json structure.
    """
    rules = ReverseRuleset(
        onsets=rules_dict["onsets"],
        nuclei=rules_dict["nuclei"],
        codas=rules_dict["codas"],
    )

    w = normalize_input(word)
    graphemes = segment_graphemes(w)

    # Split on hyphen as explicit pre‑syllable boundary
    segments: List[List[str]] = []
    current: List[str] = []
    for g in graphemes:
        if g == "-":
            if current:
                segments.append(current)
                current = []
        else:
            current.append(g)
    if current:
        segments.append(current)

    syllables: List[str] = []
    for seg in segments:
        if not seg:
            continue
        seg_sylls = reverse_syllabify_segment(seg, rules)
        syllables.extend(seg_sylls)

    return syllables
