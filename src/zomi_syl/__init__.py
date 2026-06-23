# zomi-syl/src/zomi_syl/__init__.py
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

# from .core.engine import _load_backend
from .registry.models import load_backend as _load_backend

def load_backend(name: str):
    """
    Public API: load a backend by name ('rule', 'crf', etc.)
    Returns the backend instance directly.
    
    This should not be part of .api, because .api is for high‑level user functions.
    It is a developer‑level function, and is not part of the public API.
    """
    return _load_backend(name)

__all__ = [
    "__version__",
    "syllabify",
    "analyze",
    "compare_models",
    "benchmark",
    "cli_main",
    "load_profile",
    "load_backend",
    "list_profiles",
    "get_model_info",
    "list_models",
]
