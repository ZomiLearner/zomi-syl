from __future__ import annotations
import json
from pathlib import Path

from zomi_syl.registry.profiles import load_profile


def _flatten_onsets(onsets):
    # profile stores: {"onsets": [ {"grapheme": "..."} ]}
    if isinstance(onsets, dict) and "onsets" in onsets:
        return [o["grapheme"] for o in onsets["onsets"]]
    return onsets


def _flatten_nuclei(nuclei):
    # profile stores: {"vowels": [...]}
    if isinstance(nuclei, dict) and "vowels" in nuclei:
        return nuclei["vowels"]
    return nuclei


def _flatten_codas(codas):
    # profile stores: {"codas": [...]}
    if isinstance(codas, dict) and "codas" in codas:
        return codas["codas"]
    return codas


def generate_ruleset_from_profile(dialect: str, output_path: str):
    profile = load_profile(dialect)

    ruleset = {
        "version": "1.0.0",
        "description": f"Auto-generated rule model for {dialect}",
        "onsets": _flatten_onsets(profile["onsets"]),
        "nuclei": _flatten_nuclei(profile["nuclei"]),
        "codas": _flatten_codas(profile["codas"]),
        "rules": profile["rules"],
    }

    Path(output_path).write_text(
        json.dumps(ruleset, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return ruleset


if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) != 2:
        print("Usage: python -m zomi_syl.models.generate_ruleset <dialect>")
        sys.exit(1)

    dialect = sys.argv[1]
    output_path = Path(__file__).resolve().parent / "bundled" / "rule" / "ruleset.json"

    generate_ruleset_from_profile(dialect, str(output_path))
    print(f"[OK] Generated ruleset.json for dialect '{dialect}' at {output_path}")
