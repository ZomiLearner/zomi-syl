import csv
from pathlib import Path

import pytest

from zomi_syl.backends.crf_backend import CRFBackend

# @pytest.fixture(scope="session")
# def crf_backend():
#     model_dir = Path("src/zomi_syl/models/crf")
#     return CRFBackend(str(model_dir))

# @pytest.fixture
# def crf_backend():
#     from zomi_syl.backends.crf_backend import CRFBackend
#     model_dir = Path("src/zomi_syl/models/crf")
#     return CRFBackend(str(model_dir), prefer_package_model=True)


@pytest.fixture(scope="session")
def crf_backend():
    return CRFBackend()


@pytest.fixture(scope="session")
def golden_entries():
    # golden_path = Path("tests/golden/crf_golden.tsv")
    golden_path = Path("training/data/crf_golden.tsv")
    entries = []
    with open(golden_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            entries.append(
                {
                    "word": row["word"],
                    "expected": row["expected_syllables"],
                }
            )
    return entries


def test_crf_golden_regression(crf_backend, golden_entries):
    """
    CRF predictions must match frozen golden outputs.
    """
    for entry in golden_entries:
        word = entry["word"]
        expected = entry["expected"]

        pred = crf_backend.predict(word)
        actual = "-".join(pred.syllables)

        assert actual == expected, (
            f"\nGolden regression mismatch for word={word}\n"
            f"Expected: {expected}\n"
            f"Actual:   {actual}\n"
        )


def test_crf_batch_matches_single(crf_backend, golden_entries):
    """
    Batch predictions must equal single predictions.
    """
    words = [e["word"] for e in golden_entries]
    batch_preds = crf_backend.predict_batch(words)

    for entry, batch_pred in zip(golden_entries, batch_preds):
        word = entry["word"]
        single_pred = crf_backend.predict(word)

        assert (
            batch_pred.syllables == single_pred.syllables
        ), f"Batch vs single syllables mismatch for word={word}"

        assert [b.index for b in batch_pred.boundaries] == [
            b.index for b in single_pred.boundaries
        ], f"Batch vs single boundaries mismatch for word={word}"
