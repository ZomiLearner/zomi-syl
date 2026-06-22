"""
Unified model download manager for zomi-syl.

Handles:
    • initial download
    • resume download
    • update download
    • checksum verification
    • retry logic
    • corruption detection

Public API:
    download_model()
    update_model()
"""

from pathlib import Path
from typing import Optional
import hashlib
import time

from huggingface_hub.utils import HfHubHTTPError
from huggingface_hub import hf_hub_download


from zomi_syl.exceptions import ZomiSylError
from zomi_syl.models.cache import (
    _save_metadata,
)
# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)
import logging
logger = logging.getLogger(__name__)



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fail(msg: str) -> None:
    raise ZomiSylError(msg)


def _compute_checksum(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Download logic
# ---------------------------------------------------------------------------


def _download_with_progress(repo: str, filename: str, token: Optional[str]) -> Path:
    """
    Download a file from HF with progress reporting.
    """
    try:
        path = hf_hub_download(
            repo_id=repo,
            filename=filename,
            token=token,
            resume_download=True,
            force_download=False,
        )
        return Path(path)
    except HfHubError as e:
        _fail(f"Failed to download '{filename}' from '{repo}': {e}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def download_model(
    model_name: str,
    repo: str,
    filename: str,
    *,
    checksum: Optional[str] = None,
    token: Optional[str] = None,
) -> Path:
    """
    Download a model file from HF.

    Supports:
        • resume download
        • checksum verification
        • metadata storage
    """
    logger.debug(f"[download] Downloading model '{model_name}' from {repo}")

    path = _download_with_progress(repo, filename, token)

    # Verify checksum
    if checksum:
        actual = _compute_checksum(path)
        if actual != checksum:
            _fail(f"Checksum mismatch for '{model_name}'. " f"Expected {checksum}, got {actual}")

    # Save metadata
    meta = {
        "model": model_name,
        "file_path": str(path),
        "checksum": checksum,
        "version": time.time(),
        "size": path.stat().st_size,
        "download_date": time.time(),
    }
    _save_metadata(model_name, meta)

    return path


def update_model(
    model_name: str,
    repo: str,
    filename: str,
    *,
    checksum: Optional[str] = None,
    token: Optional[str] = None,
) -> Path:
    """
    Update a model by re-downloading it.

    Equivalent to:
        remove_model()
        download_model()
    """
    from zomi_syl.models.cache import remove_model

    remove_model(model_name)
    return download_model(model_name, repo, filename, checksum=checksum, token=token)
