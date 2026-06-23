# zomi-syl/src/zomi_syl/rule_based/syllabify_v6.py

import re

# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)
import logging

logger = logging.getLogger(__name__)

vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"

patterns = {
    "ccvccc": re.compile(
        rf"^[{consonants}][{consonants}][{vowels}][{consonants}][{consonants}][{consonants}]$"
    ),
    "ccvvc": re.compile(rf"^[{consonants}][{consonants}][{vowels}][{vowels}][{consonants}]$"),
    "cvvvc": re.compile(rf"^[{consonants}][{vowels}][{vowels}][{vowels}][{consonants}]$"),
    "cvvcc": re.compile(rf"^[{consonants}][{vowels}][{vowels}][{consonants}][{consonants}]$"),
    "cvccc": re.compile(rf"^[{consonants}][{vowels}][{consonants}][{consonants}][{consonants}]$"),
    "ccvcc": re.compile(rf"^[{consonants}][{consonants}][{vowels}][{consonants}][{consonants}]$"),
    "cvvc": re.compile(rf"^[{consonants}][{vowels}][{vowels}][{consonants}]$"),
    "cvcc": re.compile(rf"^[{consonants}][{vowels}][{consonants}][{consonants}]$"),
    "ccvc": re.compile(rf"^[{consonants}][{consonants}][{vowels}][{consonants}]$"),
    "cvcv": re.compile(rf"^[{consonants}][{vowels}][{consonants}][{vowels}]$"),
    "cvvv": re.compile(rf"^[{consonants}][{vowels}][{vowels}][{vowels}]$"),
    "ccvv": re.compile(rf"^[{consonants}][{consonants}][{vowels}][{vowels}]$"),
    "cvv": re.compile(rf"^[{consonants}][{vowels}][{vowels}]$"),
    "vccc": re.compile(rf"^[{vowels}][{consonants}][{consonants}][{consonants}]$"),
    "vvcc": re.compile(rf"^[{vowels}][{vowels}][{consonants}][{consonants}]$"),
    "vvc": re.compile(rf"^[{vowels}][{vowels}][{consonants}]$"),
    "vcc": re.compile(rf"^[{vowels}][{consonants}][{consonants}]$"),
    "cvc": re.compile(rf"^[{consonants}][{vowels}][{consonants}]$"),
    "ccv": re.compile(rf"^[{consonants}][{consonants}][{vowels}]$"),
    "cv": re.compile(rf"^[{consonants}][{vowels}]$"),
    "vv": re.compile(rf"^[{vowels}][{vowels}]$"),
    "vc": re.compile(rf"^[{vowels}][{consonants}]$"),
    "v": re.compile(rf"^[{vowels}]$"),
}

pattern_order = list(patterns.keys())  # longest first


def is_reduplicated(word: str) -> str:
    # Split the word into two equal halves
    mid = len(word) // 2
    first, second = word[:mid], word[mid:]

    # Check if both halves are identical
    # if first == second:
    #     return f"{first}-{second}"
    # return word
    reduplicated = first == second
    return reduplicated, [first, second]


def expand_hyphenated(items):
    result = []
    for item in items:
        if item == "-":
            # skip standalone hyphen
            continue
        if "-" in item:
            # split only when there are other characters
            parts = [p for p in item.split("-") if p]  # drop empty pieces
            result.extend(parts)
        else:
            result.append(item)
    return result


def count_illegal_cluster(word):
    # Sort clusters longest → shortest
    clusters = sorted(ILLEGAL_CLUSTERS, key=len, reverse=True)

    count = 0
    i = 0

    while i < len(word):
        matched = False
        for cl in clusters:
            if word.startswith(cl, i):
                count += 1
                i += len(cl)  # skip past the matched cluster
                matched = True
                break
        if not matched:
            i += 1

    return count


def phonotactic_match(word, pattern, vowels="aeiou"):

    word = word.lower()
    pattern = pattern.lower()

    if len(word) != len(pattern):
        return False

    for ch, p in zip(word, pattern):
        if p == "c" and ch in vowels:
            return False
        if p == "v" and ch not in vowels:
            return False

    return True


COMMON_SUFFIXES = [
    "leh",
    "ciang",
    "khat",
    "kha",
    "cih",
    "sak",
    "zia",
    "hi",
    "huai",
    "pah",
    "khin",
    "mah",
    "tah",
    "zah",
    "zin",
    "tun",
    "in",
]

REV_SUFFIXES = sorted([s[::-1] for s in COMMON_SUFFIXES], key=len, reverse=True)

ILLEGAL_CLUSTERS = [
    "ag",  # saguh
    "aia",
    "aka",
    "ama",
    "ana",
    "ann",
    "apa",
    "angi",
    "ec",  # khecin
    "ena",
    "eima",
    "eila",
    "gc",
    "gn",
    "gp",
    "gt",
    "gz",
    "gate",
    "hc",
    "hh",
    "hl",
    "hm",
    "hn",
    "hp",
    "ht",
    "ic",
    "ig",
    "is",
    "ika",
    "iki",
    "ima",
    "ina",
    "ita",
    "kd",
    "kg",
    "kk",
    "kl",
    "km",
    "kn",
    "kp",
    "ks",
    "kt",
    "lc",
    "lg",
    "lk",
    "ll",
    "lp",
    "lm",
    "ln",
    "mb",
    "mc",
    "mg",
    "mh",
    "mk",
    "ml",
    "mm",
    "mn",
    "nk",
    "nl",
    "nm",
    "ns",
    "nt",
    "nate",
    "nga",
    "ngc",
    "ngk",
    "ngg",
    "ngl",
    "ngkh",
    "pl",
    "tl",
    "tn",
    "tm",
    "ts",
    "tale",
    "uc",
    "ug",
    "uma",
    "uta",
    "utun",
]

REV_ILLEGAL = [c[::-1] for c in ILLEGAL_CLUSTERS]

phonos = [
    "cvvccccv",
    "cvcccvc",
    "ccvcccvc",
    "cvvcvvc",
    "cvccvccvcv",
    "cvccvccv",
    "cvcv",
    "ccvccccv",
    "ccvcvc",
    "ccvccvccv",
    "cvvcvc",
    "cvvccvc",
    "ccvvvcvvccv",
    "cvcccvccv",
    "cvvv",
    "cvvccvvc",
    "vccvc",
    "cvccvc",
    "cvvcccvc",
    "vcccvccv",
    "cvcccv",
    "ccvccvc",
    "cvccvcv",
    "vvcv",
    "cvccv",
    "cvccvccvc",
    "cvcvc",
    "cvcvcvc",
    "cvvcv",
    "ccvvv",
    "ccvcccv",
    "ccvcv",
]


def to_cv(word):
    vowels = set("aeiouAEIOU")
    return "".join("v" if ch in vowels else "c" for ch in word)


def split_before_illegal_cluster(word, illegal_clusters, _print=False):
    positions = []
    found_clusters = []
    for cluster in illegal_clusters:

        # check if cluster contains ANY found cluster as substring
        if any(cluster in fc for fc in found_clusters):
            continue
        start = 0

        while True:
            if word.lower()[:3] == "nga" and cluster == "nga":

                break

            pos = word.find(cluster, start)
            if _print:
                print(f"pos: {pos}")
            if pos == -1:
                break

            positions.append(pos)
            # start = pos + 1
            start = pos + len(cluster) - 1

            if _print:
                print(f"len(cluster): {len(cluster)} {cluster}")
            if len(cluster) == 3:

                start = pos + len(cluster) - 2
                positions[-1] = start
                if _print:
                    print(f"3:start: {start}")
                    print(f"3:positions: {positions}")
            if len(cluster) == 4:
                start = pos + len(cluster) - 3
                positions[-1] = start
                if _print:
                    print(f"4:start: {start}")
                    print(f"4:positions: {positions}")

            found_clusters.append(cluster)

    if not positions:
        return [word]

    boundaries = [0] + sorted(set(positions)) + [len(word)]
    if _print:
        print(f"boundaries: {boundaries}")

    result = []
    next_start_index = 0
    for i in range(len(boundaries) - 1):
        # boundaries: [0, 2, 5, 9]
        end_index = boundaries[i + 1] + 1

        part = word[next_start_index:end_index]
        next_start_index = end_index
        if _print:
            print(f"i: {i}; i:i+1:: {part} ")
        if part:
            result.append(part)

    return result


def return_func(ret):
    return expand_hyphenated(ret)


def syllabify_v6(word, all_syllables, _print=False):
    end_syllables = ["ah", "in", "a", "un"]

    syllables = []
    w = word.lower()[::-1]

    redup, ret = is_reduplicated(word)
    if redup:
        return return_func(ret)

    if len(word) == 3 and phonotactic_match(word, "cvc"):  # word[1] in vowels:
        return return_func([word])

    if len(word) == 4 and phonotactic_match(word, "ccvc"):
        return return_func([word])

    if len(word) == 4 and phonotactic_match(word, "cvcv") and word[-3:] == "awi":
        return return_func([word])

    if len(word) == 4 and phonotactic_match(word, "cvcv"):
        return return_func([word[:2], word[2:]])

    if count_illegal_cluster(word) == 1 and any(
        s in word
        for s in [
            "ag",
            "lh",
            "uc",
            "ug",
            "ic",
            "is",
            "ec",
            "ainu",
            "kib",
            "kic",
            "uahu",
            "kiph",
            # "unga",
            "euci",
            "ipin",
        ]
    ):
        # print(f"lenn(rs[0]): {len(rs[0])}; {rs}")
        # if to_cv(word) in phonos:
        return split_before_illegal_cluster(
            word, sorted(ILLEGAL_CLUSTERS, key=lambda x: (-len(x), x))
        )

    if len(word) == 5 and phonotactic_match(word, "vccvc") and word[1:3] in ILLEGAL_CLUSTERS:
        # uklah - kl; umlah - ml; ommun - mm; imlah - ml; iplah - pl;
        return [word[:2], word[2:]]

    if (
        len(word) == 6 and phonotactic_match(word, "cvccvc") and word[2:4] in ILLEGAL_CLUSTERS
    ):  # bukmun - km
        return [word[:3], word[3:]]

    if len(word) == 6 and phonotactic_match(word, "cvcccv") and word[2:4] in ILLEGAL_CLUSTERS:
        # zehphi - hp
        return [word[:3], word[3:]]

    if (
        len(word) == 7 and phonotactic_match(word, "ccvcccv") and word[3:5] in ILLEGAL_CLUSTERS
    ):  # khamkhi - mk
        return [word[:4], word[4:]]

    if len(word) == 7 and phonotactic_match(word, "cvcccvc") and word[2:5] in ILLEGAL_CLUSTERS:
        # nungguh - ngg; nungkin - ngk; kongcin- ngc;
        return [word[:4], word[4:]]

    if len(word) == 7 and phonotactic_match(word, "cvvccvc") and word[3:5] in ILLEGAL_CLUSTERS:
        # muanlah - nl; zuihlah - hl; suahhun - hh; puamcin - mc;
        return [word[:4], word[4:]]

    if len(word) == 7 and phonotactic_match(word, "cvvccvc") and word[2:5] in ILLEGAL_CLUSTERS:
        # puannin - ann
        return [word[:4], word[4:]]

    if len(word) == 7 and phonotactic_match(word, "ccvccvc") and word[3:5] in ILLEGAL_CLUSTERS:
        # khelguh - lg; khukdin - kd; ngahlah - hl; ngaklah - kl; ngamlah- ml
        return [word[:4], word[4:]]

    if (
        len(word) == 8 and phonotactic_match(word, "cvvccccv") and word[-5:-1] in ILLEGAL_CLUSTERS
    ):  # suangkhi - ngkh
        return [word[:-3], word[-3:]]

    if len(word) == 8 and phonotactic_match(word, "cvvccvvc") and word[3:5] in ILLEGAL_CLUSTERS:
        # guahciin - hc
        return [word[:4], word[4:]]

    if len(word) == 8 and phonotactic_match(word, "ccvcccvc") and word[4:6] in ILLEGAL_CLUSTERS:
        # khawlmun - hc
        return [word[:5], word[5:]]

    if len(word) == 8 and phonotactic_match(word, "cvvcccvc") and word[3:6] in ILLEGAL_CLUSTERS:
        # muanglah - ngl;
        return [word[:5], word[5:]]

    if len(word) == 8 and phonotactic_match(word, "ccvccccv") and word[4:6] in ILLEGAL_CLUSTERS:
        # phengphi - gp or ngp;
        return [word[:5], word[5:]]

    if (
        len(word) == 9
        and phonotactic_match(word, "cvccvccvc")
        and word[2:4] in ILLEGAL_CLUSTERS
        and word[5:7] in ILLEGAL_CLUSTERS
    ):  # galpanmun - lp, nm
        return [word[:3], word[3:6], word[6:]]

    if len(word) == 4 and word[1] in vowels and word[2] in vowels:
        return [word]

    while w:
        if _print:
            print(f"w: {w}")
        matched = False
        remaining = len(w[::-1])
        if _print:
            print(f"remaining: {remaining}")

        # 1. Suffix match (longest-first, repeated)
        if remaining > 3:
            suffix_found = True
            while suffix_found:
                suffix_found = False
                for rs in REV_SUFFIXES:
                    if w.startswith(rs):
                        suffix = rs[::-1]
                        if _print:
                            print(f"1: suffix: {suffix}")
                        if suffix in end_syllables and len(w) != len(word):
                            continue
                        if suffix in [
                            "guh",
                            "hah",
                            "hun" "kah",
                            "kun",
                            "lah",
                            "mah",
                            "mun",
                            "nah",
                            "nun",
                            "pun",
                            "tah",
                            "tun",
                        ] and word[-4] in list(vowels) + ["w"]:
                            continue

                        if (
                            len(word) >= 4
                            and suffix in ["ha", "ka", "la", "ma"]
                            and word[-3] in list(vowels) + ["w"]
                            and word[-4] in list(vowels) + ["w"]
                        ):
                            continue
                        syllables.append(suffix)
                        if _print:
                            print(f"1: append(suffix): {suffix}")
                        w = w[len(rs) :]
                        suffix_found = True
                        break
            if suffix_found:
                continue

        # 2. Lexicon match (longest-first)
        for i in range(len(w), 0, -1):
            chunk = w[:i][::-1]
            if _print:
                print(f"2: i: {i}; len(w): {len(w)}; chunk:  {chunk}")
            if chunk in [
                "ngah",
                "ngun",
                "hah",
                "hun",
                "kah",
                "kun",
                "lah",
                "mah",
                "mun",
                "nah",
                "guh",
                "nun",
                "pun",
                "tah",
                "tun",
            ] and len(w) == len(word):
                syllables.append(chunk[-2:])
                w = w[2:]
                matched = True
                break

            if (
                len(word) >= 3
                and chunk in ["ha", "ka", "la", "ma"]
                and len(w) == len(word)
                and word[-3] in list(vowels) + ["w"]
            ):
                syllables.append(chunk[-1])
                w = w[1:]
                matched = True
                break
            if chunk in all_syllables:
                if _print:
                    print(f"2: append(chunk): {chunk}")
                syllables.append(chunk)
                w = w[i:]
                matched = True
                break
        if matched:
            continue

        # 3. Illegal cluster boundary (only if neither side is a known syllable)
        for rc in REV_ILLEGAL:
            if w.startswith(rc):
                left = w[len(rc) :][::-1]
                right = w[: len(rc)][::-1]
                if _print:
                    print(f"3: left: {left}")
                    print(f"3: right: {right}")

                if left not in all_syllables and right not in all_syllables:
                    if left:
                        if _print:
                            print(f"3: append(left): {left}")
                        syllables.append(left)
                        w = w[: len(rc)]
                        matched = True
                        break
        if matched:
            continue

        # 4. Pattern match
        for p in pattern_order:
            for i in range(len(w), 0, -1):
                chunk = w[:i][::-1]
                if _print:
                    print(f"4. chunk: {chunk}")
                if patterns[p].match(chunk):
                    if _print:
                        print(f"4. append(chunk): {chunk}")
                    syllables.append(chunk)
                    w = w[i:]
                    matched = True
                    break
            if matched:
                break
        if matched:
            continue

        # 5. Fallback: take one character
        if not w:
            break

        syllables.append(w[0][::-1])
        w = w[1:]

    rs = syllables[::-1]

    # if count_illegal_cluster(word) == 1 and "ima" in ILLEGAL_CLUSTERS:
    if (
        len(word) >= 3
        and count_illegal_cluster(word) == 1
        and any(
            s in word[-3:]
            for s in [
                "ana",
                "aka",
                "apa",
                "ata",
                "ima",
                "ina",
                "ena",
                "una",
                "upa",
                "uta",
                "ita",
                "eta",
                "unga",
            ]
        )
    ):
        #     # print("asdff")
        #     if to_cv(word) in phonos:
        return split_before_illegal_cluster(
            word, sorted(ILLEGAL_CLUSTERS, key=lambda x: (-len(x), x))
        )

    if len(rs[0]) == 1 or "nga" in word[-3:]:
        # if count_illegal_cluster(word) == 1 or "nga" in word[-3:]: # Not good
        # print(f"lenn(rs[0]): {len(rs[0])}; {rs}")
        if to_cv(word) in phonos:
            return split_before_illegal_cluster(
                word, sorted(ILLEGAL_CLUSTERS, key=lambda x: (-len(x), x))
            )

    # if count_illegal_cluster(word) == 1 and "lh" in word:
    #     # print(f"lenn(rs[0]): {len(rs[0])}; {rs}")
    #     # if to_cv(word) in phonos:
    #         return split_before_illegal_cluster(word, sorted(ILLEGAL_CLUSTERS, key=lambda x: (-len(x), x)))

    # return syllables[::-1]
    if _print:
        print(f"syllables: {syllables}")
    return expand_hyphenated(syllables[::-1])
