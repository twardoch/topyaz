#!/usr/bin/env python3
# this_file: src/topyaz/utils/logging.py
"""
Simplified logging setup for topyaz.
"""

import sys

from loguru import logger


def setup_logging(*, verbose: bool = True) -> None:  # Added *
    """
    Configure logging for topyaz.

    Args:
        verbose: If True, use DEBUG level, otherwise INFO
    """
    logger.remove()
    log_level = "DEBUG" if verbose else "INFO"
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>"
    )
    logger.add(sys.stderr, format=log_format, level=log_level, colorize=True)
    logger.info(f"Logging configured at {log_level} level.")


# Re-export logger for convenience
__all__ = ["logger", "setup_logging"]
