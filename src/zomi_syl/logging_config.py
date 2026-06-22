"""
Logging configuration for Zomi-Syl.

This module provides a single function, `configure_logging()`, which is
called only by the CLI entrypoint. Library code never configures logging
and never attaches handlers.

Default behavior:
- End users see no INFO/DEBUG logs (level = WARNING)
- Developers can enable verbose logs via:
      export ZOMI_SYL_LOG=info
      export ZOMI_SYL_LOG=debug
"""

import logging
import os


def configure_logging() -> None:
    """
    Configure global logging for the Zomi-Syl CLI.

    The log level is controlled by the environment variable ZOMI_SYL_LOG.
    Valid values: debug, info, warning, error, critical.

    Library modules should use:
        logger = logging.getLogger(__name__)
    and never call basicConfig() or attach handlers.
    """
    level_name = os.getenv("ZOMI_SYL_LOG", "warning").lower()

    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    logging.basicConfig(
        level=level_map.get(level_name, logging.WARNING),
        format="%(levelname)s: %(message)s",
    )
