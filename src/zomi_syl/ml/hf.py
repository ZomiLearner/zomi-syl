"""
Low-level HuggingFace Hub communication layer for zomi-syl.

This module provides:
    • repository validation
    • metadata retrieval
    • revision listing
    • authentication support (public/private repos)

Public API:
    get_repo_info()
    get_model_info()
    get_dataset_info()
"""

from typing import Dict, Any, Optional, List

from huggingface_hub import HfApi, HfHubHTTPError, RepositoryNotFoundError

from zomi_syl.exceptions import ZomiSylError
# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)
import logging
logger = logging.getLogger(__name__)



# ---------------------------------------------------------------------------
# HF API client
# ---------------------------------------------------------------------------


def _api(token: Optional[str] = None) -> HfApi:
    """Return an HF API client with optional authentication."""
    return HfApi(token=token)


# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------


def _fail(msg: str) -> None:
    raise ZomiSylError(msg)


# ---------------------------------------------------------------------------
# Repository validation
# ---------------------------------------------------------------------------


def _validate_repo(repo_id: str, token: Optional[str]) -> None:
    """
    Ensure a repo exists and is accessible.
    """
    try:
        _api(token).repo_info(repo_id)
    except RepositoryNotFoundError:
        _fail(f"HF repository not found: {repo_id}")
    except HfHubHTTPError as e:
        _fail(f"Cannot access HF repository '{repo_id}': {e}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_repo_info(repo_id: str, *, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Return general metadata for any HF repo (model or dataset).
    """
    try:
        info = _api(token).repo_info(repo_id)
        return info.__dict__
    except RepositoryNotFoundError:
        _fail(f"HF repository not found: {repo_id}")
    except HfHubHTTPError as e:
        _fail(f"Failed to fetch repo info for '{repo_id}': {e}")


def get_model_info(repo_id: str, *, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Return metadata for a model repository.

    Includes:
        • model card metadata
        • tags
        • siblings (files)
        • last modified
    """
    _validate_repo(repo_id, token)

    try:
        info = _api(token).model_info(repo_id)
        return info.__dict__
    except HfHubHTTPError as e:
        _fail(f"Failed to fetch model info for '{repo_id}': {e}")


def get_dataset_info(repo_id: str, *, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Return metadata for a dataset repository.

    Includes:
        • dataset card metadata
        • tags
        • siblings (files)
        • last modified
    """
    _validate_repo(repo_id, token)

    try:
        info = _api(token).dataset_info(repo_id)
        return info.__dict__
    except HfHubHTTPError as e:
        _fail(f"Failed to fetch dataset info for '{repo_id}': {e}")


def list_revisions(repo_id: str, *, token: Optional[str] = None) -> List[str]:
    """
    List all revisions (branches + tags) for a repo.
    """
    _validate_repo(repo_id, token)

    try:
        refs = _api(token).list_repo_refs(repo_id)
        branches = [b.name for b in refs.branches]
        tags = [t.name for t in refs.tags]
        return branches + tags
    except HfHubHTTPError as e:
        _fail(f"Failed to list revisions for '{repo_id}': {e}")
