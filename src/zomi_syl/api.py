"""
Public API for zomi-syl.

This module provides the high-level functions used by end users:
    - syllabify()
    - analyze()
    - compare_models()
    - benchmark()

These functions wrap the core engine and return structured result objects.
"""

from typing import List, Optional, Dict, Any

from zomi_syl.core.engine import run_syllabifier
from zomi_syl.core.result import SyllabificationResult
from zomi_syl.registry.models import list_models
from zomi_syl.evaluation.benchmark import run_benchmark

# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)

import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# syllabify()
# ---------------------------------------------------------------------------


# def syllabify(
#     word: str, model: str = "auto", dialect: str = "auto", return_metadata: bool = False
# ) -> SyllabificationResult:
#     """
#     Syllabify a single word using the selected backend and dialect profile.

#     Parameters
#     ----------
#     word : str
#         Input word.
#     model : str, default "auto"
#         Backend to use ("rule", "crf", "fst", "bilstm", "bilstm_crf", "transformer").
#         "auto" selects the recommended default model.
#     dialect : str, default "auto"
#         Dialect/profile to use ("tedim", "zolai_standard", etc.).
#         "auto" selects the default profile.
#     return_metadata : bool, default False
#         If True, include backend-specific metadata in the result.

#     Returns
#     -------
#     SyllabificationResult
#     """
#     logger.debug(f"API syllabify(word={word!r}, model={model!r}, dialect={dialect!r})")

#     # result = run_syllabifier(
#     #     word=word, model=model, dialect=dialect, include_metadata=return_metadata
#     # )

#     # return result
#     def syllabify(word, model="auto", dialect="auto", return_metadata=False):
#         if isinstance(word, list):
#             return [
#                 syllabify(
#                     w,
#                     model=model,
#                     dialect=dialect,
#                     return_metadata=return_metadata,
#                 )
#                 for w in word
#             ]

#         return run_syllabifier(
#             word,
#             model=model,
#             dialect=dialect,
#             include_metadata=return_metadata,
#         )
def syllabify(word, model="auto", dialect="auto", return_metadata=False):
    """
    Public API: syllabify a word or list of words.
    """

    # Batch mode
    if isinstance(word, list):
        return [
            syllabify(
                w,
                model=model,
                dialect=dialect,
                return_metadata=return_metadata,
            )
            for w in word
        ]

    # Single word mode
    return run_syllabifier(
        word,
        model=model,
        dialect=dialect,
        include_metadata=return_metadata,
    )



# ---------------------------------------------------------------------------
# analyze()
# ---------------------------------------------------------------------------


def analyze(word: str, model: str = "auto", dialect: str = "auto") -> Dict[str, Any]:
    """
    Return a detailed analysis of the syllabification process.

    This is similar to syllabify(), but returns a richer dictionary
    including:
        - syllables
        - backend used
        - profile used
        - confidence (if ML)
        - metadata (timing, alignment, debug info)

    Parameters
    ----------
    word : str
        Input word.
    model : str, default "auto"
        Backend to use.
    dialect : str, default "auto"
        Dialect/profile to use.

    Returns
    -------
    dict
        Detailed analysis dictionary.
    """
    # result = syllabify(word, model=model, dialect=dialect, return_metadata=True)
    # return result.to_dict()
    pred = syllabify(word, model=model, dialect=dialect, return_metadata=True)

    return {
        "input": word,
        "model": model,
        "dialect": dialect,
        "syllables": pred.syllables,
        "prediction": pred,
        "metadata": pred.raw.get("metadata", {}),
        "backend": pred.raw.get("backend"),
        "confidence": [
            {"index": c.index, "score": c.score}
            for c in pred.confidence
        ],
    }

# ---------------------------------------------------------------------------
# compare_models()
# ---------------------------------------------------------------------------


def compare_models(
    word: str, models: Optional[List[str]] = None, dialect: str = "auto"
) -> Dict[str, SyllabificationResult]:
    """
    Run multiple backends on the same word and compare outputs.

    Parameters
    ----------
    word : str
        Input word.
    models : list[str], optional
        List of model names. If None, all registered models are used.
    dialect : str, default "auto"
        Dialect/profile to use.

    Returns
    -------
    dict[str, SyllabificationResult]
        Mapping from model name → result.
    """
    if models is None:
        models = list_models()

    logger.debug(f"API compare_models(word={word!r}, models={models}, dialect={dialect!r})")

    results = {}
    for m in models:
        results[m] = syllabify(word, model=m, dialect=dialect, return_metadata=True)

    return results


# ---------------------------------------------------------------------------
# benchmark()
# ---------------------------------------------------------------------------


def benchmark(
    models: Optional[List[str]] = None, dialect: str = "auto", dataset_version: str = "latest"
) -> Dict[str, Any]:
    """
    Run a benchmark suite across one or more models.

    Parameters
    ----------
    models : list[str], optional
        Models to benchmark. If None, benchmark all registered models.
    dialect : str, default "auto"
        Dialect/profile to use.
    dataset_version : str, default "latest"
        Version of the HF dataset to use.

    Returns
    -------
    dict
        Benchmark results including accuracy, F1, speed, etc.
    """
    if models is None:
        models = list_models()

    logger.debug(
        f"API benchmark(models={models}, dialect={dialect!r}, dataset={dataset_version!r})"
    )

    return run_benchmark(models=models, dialect=dialect, dataset_version=dataset_version)
