"""
Version information for zomi-syl.

This module resolves the installed package version using importlib.metadata.
During development (editable installs or source checkouts), the version falls
back to "0.0.0" to avoid import errors before packaging.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("zomi-syl")
except PackageNotFoundError:
    # Fallback for development environments
    __version__ = "0.0.0"

__all__ = ["__version__"]
