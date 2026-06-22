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
    parser.add_argument("--sheet", default="zomi_syllabified_human", help="Optional sheet/tab name")
    parser.add_argument(
        "--output",
        default="training/data/zomi_syllabified_human.tsv",
        help="Output file containing Zomi words syllabified by human",
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

    # print("🔍 Filtering non-Zomi rows...")
    # df = df[df["non_zomi"].astype(str).str.strip() == ""]

    print("✨ Fetching zomi_syllabified_human sheet...")
    filtered_df = df[["word", "syllables", "is_zomi"]].copy()
    # df_zomi = df.loc[df["is_zomi"].isna() | (df["is_zomi"].str.strip() == ""), ["word", "syllables"]]

    filtered_df = filtered_df.sort_values("word")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    filtered_df.to_csv(output_path, sep="\t", index=False)
    print(f"✓ Zomi syllabified words written to: {output_path}")
    print(f"✓ Total words: {len(filtered_df)}")
    print(f"✓ Unique words: {filtered_df['word'].nunique()}")
    print(f"✓ Avg syllables per word: {filtered_df['syllables'].str.count('-').mean() + 1:.2f}")
    print(f"✓ Max syllables: {filtered_df['syllables'].str.count('-').max() + 1}")
    print(f"Execute:\n""\tmake clean-dataset\nto generate training data: zomi_only.tsv, non_zomi.tsv, mixed_unsure.tsv")


if __name__ == "__main__":
    main()
