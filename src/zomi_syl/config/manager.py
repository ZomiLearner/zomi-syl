"""
Configuration manager for zomi-syl.

Provides:
    • load_config()
    • save_config()
    • get_config_path()
    • validate_user_config()
"""

from __future__ import annotations
import toml
from pathlib import Path

from zomi_syl.config.loader import load_config_file, validate_config

# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)
import logging

logger = logging.getLogger(__name__)

CONFIG_PATH = Path.home() / ".zomi-syl.toml"


def get_config_path() -> Path:
    return CONFIG_PATH


def load_config() -> dict:
    """
    Load merged config (default + user).
    """
    return load_config_file(CONFIG_PATH)


def save_config(config: dict):
    """
    Save user config to ~/.zomi-syl.toml
    """
    validate_config(config)
    CONFIG_PATH.write_text(toml.dumps(config), encoding="utf-8")
    logger.info(f"[config] Saved configuration to {CONFIG_PATH}")


def validate_user_config() -> bool:
    """
    Validate the user config file.
    """
    cfg = load_config()
    validate_config(cfg)
    return True
