"""
Configuration loader for zomi-syl.

Loads:
    • default config
    • user config (if exists)
Validates:
    • structure using schema.json
"""

from __future__ import annotations
import json
import toml
from pathlib import Path
from jsonschema import validate, ValidationError

# from zomi_syl.logging_config import get_logger

# logger = get_logger(__name__)
import logging
logger = logging.getLogger(__name__)


CONFIG_DIR = Path(__file__).parent
DEFAULT_CONFIG = CONFIG_DIR / "default.toml"
SCHEMA_FILE = CONFIG_DIR / "schema.json"


def load_schema() -> dict:
    return json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))


def load_default_config() -> dict:
    return toml.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))


def load_user_config(path: Path) -> dict:
    if not path.exists():
        return {}
    return toml.loads(path.read_text(encoding="utf-8"))


def merge_configs(default: dict, user: dict) -> dict:
    """
    Shallow merge: user config overrides defaults.
    """
    merged = default.copy()
    for key, value in user.items():
        if isinstance(value, dict) and key in merged:
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


def validate_config(config: dict):
    schema = load_schema()
    try:
        validate(instance=config, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Invalid configuration: {e.message}") from e


def load_config_file(path: Path) -> dict:
    default = load_default_config()
    user = load_user_config(path)
    merged = merge_configs(default, user)
    validate_config(merged)
    return merged
