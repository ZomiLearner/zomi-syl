"""
zomi-syl
========

A modular, dialect-aware syllabification library for the Zomi language family.

This package exposes a clean public API:

    - syllabify(word, model="auto", dialect="auto")
    - analyze(word, model="auto", dialect="auto")
    - compare_models(word, models=None, dialect="auto")
    - benchmark(models=None, dialect="auto", dataset_version="latest")

Advanced users can access:
    - profiles
    - model registry
    - batch processor
    - evaluation utilities
"""

from .version import __version__

# High-level public API
from .api import (
    syllabify,
    analyze,
    compare_models,
    benchmark,
)

# CLI entry point (optional import)
from .cli import main as cli_main

# Expose profile registry
from .registry.profiles import load_profile, list_profiles

# Expose model registry
from .registry.models import get_model_info, list_models

__all__ = [
    "__version__",
    "syllabify",
    "analyze",
    "compare_models",
    "benchmark",
    "cli_main",
    "load_profile",
    "list_profiles",
    "get_model_info",
    "list_models",
]
