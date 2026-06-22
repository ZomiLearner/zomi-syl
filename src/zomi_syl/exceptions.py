"""
Custom exception hierarchy for the zomi-syl package.

These exceptions provide clear, structured, and user-friendly error messages
across all subsystems: profiles, models, datasets, validation, and the
syllabification engine.
"""

# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------


class ZomiSylError(Exception):
    """Base class for all zomi-syl exceptions."""

    pass


# ---------------------------------------------------------------------------
# Profile / Dialect errors
# ---------------------------------------------------------------------------


class ProfileNotFoundError(ZomiSylError):
    """Raised when a requested dialect/profile does not exist."""

    def __init__(self, profile: str):
        super().__init__(
            f"Profile '{profile}' not found. " f"Use list_profiles() to see available profiles."
        )


class ProfileValidationError(ZomiSylError):
    """Raised when a profile's JSON files fail validation."""

    pass


class ProfileLoadError(ZomiSylError):
    """Raised when a profile cannot be loaded due to missing or invalid files."""

    pass


# ---------------------------------------------------------------------------
# Model errors
# ---------------------------------------------------------------------------


class ModelNotFoundError(ZomiSylError):
    """Raised when a requested model is not registered."""

    def __init__(self, model: str):
        super().__init__(
            f"Model '{model}' is not registered. " f"Use list_models() to see available models."
        )


class ModelLoadError(ZomiSylError):
    """Raised when a model cannot be loaded (HF, local cache, or bundled)."""

    pass


class ModelDownloadError(ZomiSylError):
    """Raised when a Hugging Face model fails to download."""

    pass


class UnsupportedModelBackendError(ZomiSylError):
    """Raised when a backend type is not supported (e.g., unknown architecture)."""

    pass


# ---------------------------------------------------------------------------
# Dataset errors
# ---------------------------------------------------------------------------


class DatasetNotFoundError(ZomiSylError):
    """Raised when a requested dataset or dataset version is missing."""

    pass


class DatasetLoadError(ZomiSylError):
    """Raised when a dataset cannot be loaded from Hugging Face or local cache."""

    pass


class DatasetValidationError(ZomiSylError):
    """Raised when dataset structure or fields are invalid."""

    pass


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------


class InputValidationError(ZomiSylError):
    """Raised when user input fails validation (empty string, invalid chars, etc.)."""

    pass


class ConfigurationError(ZomiSylError):
    """Raised when configuration files or values are invalid."""

    pass


# ---------------------------------------------------------------------------
# Engine / Pipeline errors
# ---------------------------------------------------------------------------


class SyllabificationError(ZomiSylError):
    """Raised when the engine fails to syllabify a word."""

    pass


class PipelineError(ZomiSylError):
    """Raised when the processing pipeline encounters an unrecoverable error."""

    pass


class BackendExecutionError(ZomiSylError):
    """Raised when a backend (rule, CRF, FST, ML) fails during execution."""

    pass


# ---------------------------------------------------------------------------
# Utility errors
# ---------------------------------------------------------------------------


class NormalizationError(ZomiSylError):
    """Raised when Unicode or text normalization fails."""

    pass


class LoanwordDetectionError(ZomiSylError):
    """Raised when loanword detection logic encounters invalid state."""

    pass


class ResourceNotFoundError(ZomiSylError):
    """Raised when a required JSON resource is missing."""

    pass


class ResourceLoadError(ZomiSylError):
    """Raised when a required JSON resource cannot be loaded."""

    pass
