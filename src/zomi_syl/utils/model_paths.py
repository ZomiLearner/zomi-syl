# zomi_syl/utils/model_paths.py

import importlib.resources
from pathlib import Path

def resolve_model_path(backend_name: str) -> Path:
    """
    Unified model directory resolver for all backends.
    Always loads packaged models, never source-tree paths.
    """
    backend_name = backend_name.lower()
    base = importlib.resources.files("zomi_syl") / "models" / backend_name

    if not base.exists():
        raise FileNotFoundError(
            f"Model directory not found for backend '{backend_name}': {base}"
        )

    return Path(base)
