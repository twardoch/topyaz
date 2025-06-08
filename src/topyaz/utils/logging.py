#!/usr/bin/env python3
# this_file: src/topyaz/utils/logging.py
"""
Logging configuration and utilities for topyaz.

This module provides centralized logging setup using loguru, with support for
console and file output, structured logging, and various formatting options.

"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from topyaz.core.types import LogLevel


class LoggingManager:
    """
    Manages logging configuration for topyaz.

    Provides methods to configure console and file logging with
    appropriate formatting and rotation policies.

    Used in:
    - topyaz/cli.py
    - topyaz/utils/__init__.py
    """

    # Default log format for console output
    CONSOLE_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Simplified format for file output (no color codes)
    FILE_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"

    # Minimal format for non-verbose mode
    SIMPLE_FORMAT = "<level>{level: <8}</level> | <level>{message}</level>"

    def __init__(self):
        """Initialize logging manager."""
        self._configured = False
        self._log_file: Path | None = None

    def setup(
        self,
        log_level: str | LogLevel = "INFO",
        verbose: bool = True,
        log_file: Path | None = None,
        log_to_file: bool = True,
        rotation: str = "10 MB",
        retention: str = "1 week",
        colorize: bool = True,
    ) -> None:
        """
        Configure logging for topyaz.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            verbose: Enable verbose output with detailed formatting
            log_file: Path to log file (auto-generated if None)
            log_to_file: Enable file logging
            rotation: Log rotation size/time (e.g., "10 MB", "1 day")
            retention: Log retention period (e.g., "1 week", "30 days")
            colorize: Enable colored console output

        """
        # Remove existing handlers to avoid duplicates
        logger.remove()

        # Convert log level to string if enum
        if isinstance(log_level, LogLevel):
            log_level = log_level.value

        # Configure console logging
        console_format = self.CONSOLE_FORMAT if verbose else self.SIMPLE_FORMAT
        logger.add(
            sys.stderr,
            format=console_format,
            level=log_level,
            colorize=colorize,
            filter=self._console_filter,
        )

        # Configure file logging if enabled
        if log_to_file:
            if log_file is None:
                log_dir = Path.home() / ".topyaz" / "logs"
                log_dir.mkdir(parents=True, exist_ok=True)
                log_file = log_dir / "topyaz.log"

            self._log_file = log_file

            logger.add(
                log_file,
                format=self.FILE_FORMAT,
                level="DEBUG",  # Always log debug to file
                rotation=rotation,
                retention=retention,
                compression="zip",
                encoding="utf-8",
                filter=self._file_filter,
            )

        self._configured = True
        logger.debug(f"Logging configured: level={log_level}, verbose={verbose}")

    def _console_filter(self, record: dict) -> bool:
        """
        Filter for console output.

        Args:
            record: Log record dictionary

        Returns:
            True to include the record, False to exclude

        """
        # Filter out some noisy debug messages from console
        if record["level"].name == "DEBUG":
            # Skip paramiko debug messages
            if record["name"].startswith("paramiko"):
                return False
            # Skip urllib3 debug messages
            if record["name"].startswith("urllib3"):
                return False

        return True

    def _file_filter(self, record: dict) -> bool:
        """
        Filter for file output.

        Args:
            record: Log record dictionary

        Returns:
            True to include the record, False to exclude

        """
        # Include all messages in file (can add filtering later if needed)
        return True

    def add_context(self, **kwargs) -> None:
        """
        Add context variables to all log messages.

        Args:
            **kwargs: Context variables to add

        Example:
            logging_manager.add_context(product="gigapixel", operation="upscale")

        """
        logger.configure(extra=kwargs)

    def get_log_file(self) -> Path | None:
        """
        Get current log file path.

        Returns:
            Path to log file or None if file logging disabled

        """
        return self._log_file

    @staticmethod
    def create_progress_logger(name: str) -> "ProgressLogger":
        """
        Create a progress-aware logger for long operations.

        Args:
            name: Logger name/operation description

        Returns:
            ProgressLogger instance
        """
        return ProgressLogger(name)


class ProgressLogger:
    """
    Logger for tracking progress of long-running operations.

    Provides methods to log progress updates without cluttering the output.

    Used in:
    - topyaz/utils/__init__.py
    """

    def __init__(self, name: str):
        """
        Initialize progress logger.

        Args:
            name: Operation name/description

        """
        self.name = name
        self._last_percent = -1

    def update(self, current: int, total: int, message: str = "") -> None:
        """
        Log progress update.

        Args:
            current: Current item/step
            total: Total items/steps
            message: Optional progress message

        """
        if total == 0:
            return

        percent = int((current / total) * 100)

        # Only log at 10% intervals to reduce noise
        if percent >= self._last_percent + 10 or percent == 100:
            self._last_percent = percent

            msg = f"{self.name}: {percent}% ({current}/{total})"
            if message:
                msg += f" - {message}"

            logger.info(msg)

    def complete(self, message: str = "Complete") -> None:
        """
        Log operation completion.

        Args:
            message: Completion message

        """
        logger.success(f"{self.name}: {message}")

    def error(self, message: str) -> None:
        """
        Log operation error.

        Args:
            message: Error message

        """
        logger.error(f"{self.name}: {message}")


# Global logging manager instance
logging_manager = LoggingManager()


def setup_logging(
    log_level: str | LogLevel = "INFO", verbose: bool = True, log_file: Path | None = None, **kwargs
) -> None:
    """
    Convenience function to set up logging.

    Args:
        log_level: Logging level
        verbose: Enable verbose output
        log_file: Optional log file path
        **kwargs: Additional arguments for LoggingManager.setup()

    Used in:
    - topyaz/utils/__init__.py
    """
    logging_manager.setup(log_level=log_level, verbose=verbose, log_file=log_file, **kwargs)


def get_logger(name: str | None = None) -> logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (uses caller's module if None)

    Returns:
        Logger instance

    Used in:
    - topyaz/utils/__init__.py
    """
    if name:
        return logger.bind(name=name)
    return logger


# Re-export logger for convenience
__all__ = [
    "LoggingManager",
    "ProgressLogger",
    "get_logger",
    "logger",
    "logging_manager",
    "setup_logging",
]
