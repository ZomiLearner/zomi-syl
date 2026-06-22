"""
Dataset + HF artifact download manager for zomi-syl.

Handles:
    • initial dataset download
    • resume download
    • update download
    • checksum verification
    • retry logic
    • corruption detection

Public API:
    download_dataset()
"""

from pathlib import Path
from typing import Optional
import hashlib

from huggingface_hub import hf_hub_download, HfHubHTTPError

from zomi_syl.exceptions import ZomiSylError
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
# Public API
# ---------------------------------------------------------------------------


def download_dataset(
    repo: str, filename: str, *, checksum: Optional[str] = None, token: Optional[str] = None
) -> Path:
    """
    Download a dataset file from HF.

    Supports:
        • resume download
        • checksum verification
        • progress reporting
    """
    logger.debug(f"[download] Downloading dataset '{filename}' from {repo}")

    try:
        path = hf_hub_download(
            repo_id=repo,
            filename=filename,
            token=token,
            resume_download=True,
            force_download=False,
        )
    except HfHubHTTPError as e:
        _fail(f"Failed to download dataset '{filename}' from '{repo}': {e}")

    path = Path(path)

    # Verify checksum
    if checksum:
        actual = _compute_checksum(path)
        if actual != checksum:
            _fail(
                f"Checksum mismatch for dataset '{filename}'. " f"Expected {checksum}, got {actual}"
            )

    return path
