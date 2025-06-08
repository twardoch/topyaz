#!/usr/bin/env python3
# this_file: src/topyaz/__main__.py
"""
Main entry point for the topyaz CLI.

This module provides the CLI interface using Python Fire for automatic command generation.
"""

import fire
from loguru import logger

from topyaz.cli import topyazWrapper


def main() -> None:
    """Main entry point for the topyaz CLI."""
    try:
        # Use Python Fire to automatically generate CLI from the topyazWrapper class
        fire.Fire(topyazWrapper)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
