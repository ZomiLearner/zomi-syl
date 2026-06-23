"""
Benchmark execution framework for zomi-syl.

Loads:
    • dataset
Runs:
    • backend predictions
Computes:
    • accuracy
    • boundary F1
Generates:
    • optional HTML/Markdown report
"""

from __future__ import annotations
from typing import List, Optional

from zomi_syl.core.pipeline import run_pipeline
from zomi_syl.evaluation.metrics import syllable_accuracy, boundary_f1
from zomi_syl.evaluation.reports import generate_markdown_report, generate_html_report

# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)

import logging

logger = logging.getLogger(__name__)


def run_benchmark(
    models: Optional[List[str]] = None,
    backend: str = "auto",
    dialect: str = "auto",
    dataset: str = "auto",
    dataset_version: str = "latest",
    report_path: str | None = None,
) -> str:
    """
    Run benchmark on a dataset.

    dataset format:
        list of {"word": "...", "syllables": ["..."], "boundaries": [..]}
    """
    # Placeholder dataset loader
    # Replace with real dataset manager
    data = _load_dummy_dataset()

    results = {}

    logger.info(f"[benchmark] Running backend={backend}")

    gold_syllables = [item["syllables"] for item in data]
    gold_boundaries = [item["boundaries"] for item in data]

    pred_syllables = []
    pred_boundaries = []

    for item in data:
        pred = run_pipeline(
            item["word"],
            model=backend,
            dialect="tedim",
            include_metadata=False,
        )
        pred_syllables.append(pred.syllables)
        pred_boundaries.append([b.index for b in pred.boundaries])

    # Compute metrics
    acc = sum(syllable_accuracy(g, p) for g, p in zip(gold_syllables, pred_syllables)) / len(data)

    f1 = sum(boundary_f1(g, p)[2] for g, p in zip(gold_boundaries, pred_boundaries)) / len(data)

    results[backend] = {
        "accuracy": acc,
        "boundary_f1": f1,
    }

    # Generate report
    if report_path:
        if report_path.endswith(".html"):
            html = generate_html_report(results)
            open(report_path, "w", encoding="utf-8").write(html)
        else:
            md = generate_markdown_report(results)
            open(report_path, "w", encoding="utf-8").write(md)

    # return generate_markdown_report(results)
    # Return raw results (dict), not Markdown
    # return results
    # Return structured dict (not markdown)
    # return {
    #     "model": backend,
    #     "dialect": dialect,
    #     "dataset_version": dataset_version,
    #     "results": results,
    # }
    return {
        "model": backend,
        "dialect": dialect,
        "dataset_version": dataset_version,

        # REQUIRED BY TEST SUITE
        "accuracy": acc,
        "boundary_f1": f1,

        # full per-model results
        "results": results,
    }




def _load_dummy_dataset():
    """
    Temporary dataset for development.
    Replace with real dataset loader.
    """
    return [
        {"word": "thugenna", "syllables": ["thu", "gen", "na"], "boundaries": [3, 6]},
        {"word": "khaile", "syllables": ["khai", "le"], "boundaries": [4]},
    ]
