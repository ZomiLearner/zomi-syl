#!/usr/bin/env python3
"""Print dataset statistics."""
import pandas as pd

df = pd.read_csv('data/zomi_syllabified_human.tsv', sep='\t')

print(f"Total words: {len(df)}")
print(f"Unique words: {df['word'].nunique()}")
print(f"Avg syllables per word: {df['syllables'].str.count('-').mean() + 1:.2f}")
print(f"Max syllables: {df['syllables'].str.count('-').max() + 1}")