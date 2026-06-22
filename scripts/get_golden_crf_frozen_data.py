#!/usr/bin/env python3
"""
Download golden_crf_word from Google Sheet and freeze it into tests/golden/crf_golden.tsv.

Usage:
    python scripts/get_golden_crf_freeze.py --url "<sheet-url>" [--sheet "Sheet1"]
"""

import argparse
import pandas as pd
from pathlib import Path

from google_sheet_reader import read_google_sheet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Direct Google Sheet URL")
    parser.add_argument("--sheet", default=None, help="Optional sheet/tab name")
    parser.add_argument(
        "--output",
        default="training/data/crf_golden.tsv",
        help="Output freeze file",
    )
    args = parser.parse_args()

    print("🔄 Reading Google Sheet...")
    df = read_google_sheet(args.url, args.sheet)

    if df is None:
        print("✗ Failed to load sheet")
        return

    required_cols = ["word", "syllables"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    print("🔍 Filtering non-Zomi rows...")
    df = df[df["is_zomi"].isna() | (df["is_zomi"].astype(str).str.strip() == "")]

    print("✨ Fetching golden_crf_word...")
    freeze_df = df[["word", "syllables"]].copy()
    freeze_df = freeze_df.rename(columns={"syllables": "expected_syllables"})
    freeze_df = freeze_df.sort_values("word")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    freeze_df.to_csv(output_path, sep="\t", index=False)
    print(f"✓ Golden CRF word and syllables written to: {output_path}")


if __name__ == "__main__":
    main()
