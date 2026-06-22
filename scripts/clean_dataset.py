import csv
import os

INPUT = "training/data/zomi_syllabified_human.tsv"
ZOMI_OUT = "training/data/zomi_only.tsv"
NON_ZOMI_OUT = "training/data/non_zomi.tsv"
MIXED_OUT = "training/data/mixed_unsure.tsv"   # optional

print("📁 Ensuring training directory exists...")
os.makedirs("training/data", exist_ok=True)

def is_blank(value):
    return value is None or value.strip() == ""

def clean_dataset():
    zomi_rows = []
    non_zomi_rows = []
    mixed_rows = []

    with open(INPUT, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            word = row["word"].strip()
            syll = row["syllables"].strip()
            flag = row.get("is_zomi", "").strip().lower()

            # Case 1: Zomi (blank flag)
            if is_blank(flag):
                zomi_rows.append(row)
                continue

            # Case 2: Explicit Non‑Zomi
            # if flag in {"yes", "Non-Zomi", "nonzomi", "foreign"}:
            if flag in {"yes"}:
                non_zomi_rows.append(row)
                continue

            # Case 3: Ambiguous / Zomilified / unclear
            mixed_rows.append(row)

    # Write outputs
    def write_tsv(path, rows):
        if not rows:
            return
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys(), delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)

    write_tsv(ZOMI_OUT, zomi_rows)
    write_tsv(NON_ZOMI_OUT, non_zomi_rows)
    write_tsv(MIXED_OUT, mixed_rows)

    print("=== CLEANING COMPLETE ===")
    print(f"Zomi words:      {len(zomi_rows)}  → {ZOMI_OUT}")
    print(f"Non‑Zomi words:  {len(non_zomi_rows)}  → {NON_ZOMI_OUT}")
    print(f"Mixed/unsure:    {len(mixed_rows)}  → {MIXED_OUT}")

if __name__ == "__main__":
    clean_dataset()
