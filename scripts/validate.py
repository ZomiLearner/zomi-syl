#!/usr/bin/env python3
"""Validate TSV format and content."""
import pandas as pd

df = pd.read_csv('data/zomi_syllabified_human.tsv', sep='\t')

# Check columns
assert list(df.columns) == ['word', 'syllables'], "Wrong columns"

# Check no empty values
assert not df['word'].isna().any(), "Empty word found"
assert not df['syllables'].isna().any(), "Empty syllables found"

# Check hyphens removed in word column
assert not df['word'].str.contains('-').any(), "Word column has hyphens"

# Check syllable format
assert df['syllables'].str.contains('-').all(), "Syllables missing hyphens"

print(f"✅ Validated {len(df)} rows")