"""
Batch syllabification processor for zomi-syl.

This module provides:
    • file-based batch processing
    • parallel workers
    • progress bar support
    • multiple output formats (text, csv, jsonl)
    • robust error handling per line

Used by:
    • CLI: zomi-syl batch
    • CI pipelines
    • corpus builders
    • HF Spaces
"""

from __future__ import annotations
import csv
import json
from pathlib import Path
from typing import List, Optional

from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

from zomi_syl.core.pipeline import run_pipeline

# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Worker function
# ---------------------------------------------------------------------------


def _process_word(word: str, model: str, dialect: str) -> dict:
    """
    Process a single word using the full pipeline.
    Returns a dict suitable for JSONL/CSV/text formatting.
    """
    try:
        result = run_pipeline(
            word,
            model=model,
            dialect=dialect,
            include_metadata=False,
        )
        return {
            "word": word,
            "syllables": result.syllables,
            "joined": result.joined,
            "error": None,
        }
    except Exception as e:
        return {
            "word": word,
            "syllables": [],
            "joined": "",
            "error": str(e),
        }


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def _write_text(results: List[dict], output: Optional[str]):
    """
    Default text output:
        word<TAB>syllables
    """
    lines = []
    for r in results:
        if r["error"]:
            lines.append(f"{r['word']}\tERROR: {r['error']}")
        else:
            lines.append(f"{r['word']}\t{r['joined'].replace('-', '.')}")
    text = "\n".join(lines)

    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text)


def _write_jsonl(results: List[dict], output: Optional[str]):
    """
    JSONL output: one JSON object per line.
    """
    lines = [json.dumps(r, ensure_ascii=False) for r in results]
    text = "\n".join(lines)

    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text)


def _write_csv(results: List[dict], output: Optional[str]):
    """
    CSV output: word, syllables, error
    """
    if not output:
        raise ValueError("CSV output requires --output <file.csv>")

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "syllables", "error"])
        for r in results:
            writer.writerow(
                [
                    r["word"],
                    r["joined"],
                    r["error"],
                ]
            )


# ---------------------------------------------------------------------------
# Main batch processor
# ---------------------------------------------------------------------------


def run_batch(
    file_path: str,
    *,
    output: Optional[str] = None,
    fmt: str = "text",
    workers: int = 1,
    show_progress: bool = False,
    model: str = "auto",
    dialect: str = "auto",
):
    """
    Run batch syllabification on a file of words.

    Parameters:
        file_path: input file with one word per line
        output: optional output file
        fmt: "text", "jsonl", "csv"
        workers: number of parallel processes
        show_progress: show tqdm progress bar
        model: backend model
        dialect: profile/dialect
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    words = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    logger.info(f"[batch] Loaded {len(words)} words from {file_path}")
    logger.info(f"[batch] Using backend={model}, dialect={dialect}, workers={workers}")

    results: List[dict] = []

    # Parallel processing
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_process_word, w, model, dialect): w for w in words}

            iterator = as_completed(futures)
            if show_progress:
                iterator = tqdm(iterator, total=len(words), desc="Processing")

            for fut in iterator:
                results.append(fut.result())

    else:
        iterator = words
        if show_progress:
            iterator = tqdm(words, desc="Processing")

        for w in iterator:
            results.append(_process_word(w, model, dialect))

    # Output formatting
    if fmt == "text":
        _write_text(results, output)
    elif fmt == "jsonl":
        _write_jsonl(results, output)
    elif fmt == "csv":
        _write_csv(results, output)
    else:
        raise ValueError(f"Unknown format: {fmt}")

    logger.info("[batch] Completed batch processing")
