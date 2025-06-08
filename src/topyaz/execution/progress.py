#!/usr/bin/env python3
# this_file: src/topyaz/execution/progress.py
"""
Progress monitoring and callback utilities for topyaz.

This module provides progress tracking capabilities for command execution,
batch processing, and long-running operations.

"""

import re
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from re import Pattern
from typing import Any, Optional

from loguru import logger
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from topyaz.core.types import ProcessingResult


class ProgressCallback(ABC):
    """
    Abstract base class for progress callbacks.

    Provides a standard interface for reporting progress during
    long-running operations.

    """

    @abstractmethod
    def on_start(self, task_name: str, total_steps: int = 100) -> None:
        """
        Called when a task starts.

        Args:
            task_name: Human-readable name of the task
            total_steps: Total number of steps (default 100 for percentage)

        """
        pass

    @abstractmethod
    def on_progress(self, current: int, total: int, message: str | None = None) -> None:
        """
        Called to update progress.

        Args:
            current: Current step number
            total: Total number of steps
            message: Optional progress message

        """
        pass

    @abstractmethod
    def on_complete(self, success: bool, message: str | None = None) -> None:
        """
        Called when a task completes.

        Args:
            success: Whether the task completed successfully
            message: Optional completion message

        """
        pass

    @abstractmethod
    def on_error(self, error: Exception, message: str | None = None) -> None:
        """
        Called when an error occurs.

        Args:
            error: The exception that occurred
            message: Optional error message

        """
        pass


class SilentProgressCallback(ProgressCallback):
    """Silent progress callback that does nothing (for headless operation).

    Used in:
    - topyaz/execution/__init__.py
    """

    def on_start(self, task_name: str, total_steps: int = 100) -> None:
        """No-op start handler."""
        logger.debug(f"Starting task: {task_name} ({total_steps} steps)")

    def on_progress(self, current: int, total: int, message: str | None = None) -> None:
        """No-op progress handler."""
        if message:
            logger.debug(f"Progress {current}/{total}: {message}")

    def on_complete(self, success: bool, message: str | None = None) -> None:
        """No-op completion handler."""
        status = "completed" if success else "failed"
        logger.debug(f"Task {status}: {message or ''}")

    def on_error(self, error: Exception, message: str | None = None) -> None:
        """No-op error handler."""
        logger.error(f"Task error: {error} - {message or ''}")


class ConsoleProgressCallback(ProgressCallback):
    """
    Console-based progress callback using rich progress bars.

    Provides beautiful progress bars for interactive console usage.

    Used in:
    - topyaz/execution/__init__.py
    """

    def __init__(self, console: Console | None = None):
        """
        Initialize console progress callback.

        Args:
            console: Rich console instance (creates new one if None)

        """
        self.console = console or Console()
        self.progress: Progress | None = None
        self.task_id: TaskID | None = None
        self._task_name = ""

    def on_start(self, task_name: str, total_steps: int = 100) -> None:
        """Start progress bar."""
        self._task_name = task_name

        # Create progress bar with custom columns
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=self.console,
            transient=False,
        )

        self.progress.start()
        self.task_id = self.progress.add_task(description=task_name, total=total_steps)

        logger.debug(f"Started progress tracking for: {task_name}")

    def on_progress(self, current: int, total: int, message: str | None = None) -> None:
        """Update progress bar."""
        if self.progress and self.task_id is not None:
            # Update description with message if provided
            description = self._task_name
            if message:
                description = f"{self._task_name}: {message}"

            self.progress.update(self.task_id, completed=current, total=total, description=description)

    def on_complete(self, success: bool, message: str | None = None) -> None:
        """Complete progress bar."""
        if self.progress and self.task_id is not None:
            # Mark as complete
            self.progress.update(self.task_id, completed=self.progress.tasks[self.task_id].total)

            # Update description with final status
            status = "✓ Completed" if success else "✗ Failed"
            final_message = f"{status}: {self._task_name}"
            if message:
                final_message += f" - {message}"

            self.progress.update(self.task_id, description=final_message)

            # Stop progress bar after a brief pause
            time.sleep(0.5)
            self.progress.stop()

            # Print final status
            if success:
                self.console.print(f"✓ {self._task_name} completed successfully", style="green")
            else:
                self.console.print(f"✗ {self._task_name} failed: {message or 'Unknown error'}", style="red")

    def on_error(self, error: Exception, message: str | None = None) -> None:
        """Handle error in progress bar."""
        if self.progress:
            self.progress.stop()

        error_msg = f"Error in {self._task_name}: {error}"
        if message:
            error_msg += f" - {message}"

        self.console.print(error_msg, style="red")
        logger.error(error_msg)


class LoggingProgressCallback(ProgressCallback):
    """Progress callback that outputs to logging system.

    Used in:
    - topyaz/execution/__init__.py
    """

    def __init__(self, log_level: str = "INFO"):
        """
        Initialize logging progress callback.

        Args:
            log_level: Logging level for progress messages

        """
        self.log_level = log_level.upper()
        self._task_name = ""
        self._last_progress = 0
        self._progress_threshold = 5  # Log every 5% progress

    def on_start(self, task_name: str, total_steps: int = 100) -> None:
        """Log task start."""
        self._task_name = task_name
        self._last_progress = 0
        logger.log(self.log_level, f"Started: {task_name} ({total_steps} steps)")

    def on_progress(self, current: int, total: int, message: str | None = None) -> None:
        """Log progress updates (throttled to reduce noise)."""
        if total > 0:
            percentage = (current / total) * 100

            # Only log if we've crossed a threshold
            if percentage - self._last_progress >= self._progress_threshold:
                progress_msg = f"{self._task_name}: {percentage:.1f}% ({current}/{total})"
                if message:
                    progress_msg += f" - {message}"

                logger.log(self.log_level, progress_msg)
                self._last_progress = percentage

    def on_complete(self, success: bool, message: str | None = None) -> None:
        """Log task completion."""
        status = "completed" if success else "failed"
        completion_msg = f"{self._task_name} {status}"
        if message:
            completion_msg += f": {message}"

        level = self.log_level if success else "ERROR"
        logger.log(level, completion_msg)

    def on_error(self, error: Exception, message: str | None = None) -> None:
        """Log task error."""
        error_msg = f"{self._task_name} error: {error}"
        if message:
            error_msg += f" - {message}"

        logger.error(error_msg)


class BatchProgressTracker:
    """
    Tracks progress across multiple batch operations.

    Useful for processing multiple files or running multiple commands
    with unified progress reporting.

    Used in:
    - topyaz/execution/__init__.py
    """

    def __init__(self, callback: ProgressCallback, total_items: int):
        """
        Initialize batch progress tracker.

        Args:
            callback: Progress callback to use
            total_items: Total number of items to process

        """
        self.callback = callback
        self.total_items = total_items
        self.completed_items = 0
        self.failed_items = 0
        self.current_item = ""
        self._lock = threading.Lock()

    def start_batch(self, batch_name: str) -> None:
        """Start batch processing."""
        self.callback.on_start(batch_name, self.total_items)

    def start_item(self, item_name: str) -> None:
        """Start processing an individual item."""
        with self._lock:
            self.current_item = item_name
            self.callback.on_progress(self.completed_items, self.total_items, f"Processing: {item_name}")

    def complete_item(self, success: bool, message: str | None = None) -> None:
        """Mark an item as completed."""
        with self._lock:
            if success:
                self.completed_items += 1
            else:
                self.failed_items += 1

            status = "✓" if success else "✗"
            progress_msg = f"{status} {self.current_item}"
            if message:
                progress_msg += f" - {message}"

            self.callback.on_progress(self.completed_items + self.failed_items, self.total_items, progress_msg)

    def complete_batch(self) -> None:
        """Complete batch processing."""
        total_processed = self.completed_items + self.failed_items
        success = self.failed_items == 0

        message = f"Processed {total_processed}/{self.total_items} items"
        if self.failed_items > 0:
            message += f" ({self.failed_items} failed)"

        self.callback.on_complete(success, message)


class OutputProgressParser:
    """
    Parses progress information from command output.

    Many CLI tools output progress information that can be parsed
    to provide real-time progress updates.

    Used in:
    - topyaz/execution/__init__.py
    """

    def __init__(self, callback: ProgressCallback):
        """
        Initialize output parser.

        Args:
            callback: Progress callback to update

        """
        self.callback = callback
        self.patterns: dict[str, Pattern[str]] = {}
        self._setup_patterns()

    def _setup_patterns(self) -> None:
        """Set up regex patterns for different tools."""
        # Common progress patterns
        self.patterns.update(
            {
                # Percentage: "Progress: 45.2%"
                "percentage": re.compile(r"(?:progress|complete):\s*(\d+(?:\.\d+)?)\s*%", re.IGNORECASE),
                # Fraction: "15/100" or "Processing 15 of 100"
                "fraction": re.compile(r"(?:processing\s+)?(\d+)\s+(?:of|/)\s+(\d+)", re.IGNORECASE),
                # Time remaining: "ETA: 5m 30s"
                "eta": re.compile(r"eta:\s*(\d+[hms]\s*)+", re.IGNORECASE),
                # Frame numbers for video: "frame=1234"
                "frame": re.compile(r"frame\s*=\s*(\d+)", re.IGNORECASE),
                # FFmpeg-style progress: "time=00:01:23.45"
                "time": re.compile(r"time\s*=\s*(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?", re.IGNORECASE),
            }
        )

    def parse_line(self, line: str) -> bool:
        """
        Parse a line of output for progress information.

        Args:
            line: Line of output to parse

        Returns:
            True if progress was found and reported

        """
        line = line.strip()
        if not line:
            return False

        # Try percentage pattern
        if match := self.patterns["percentage"].search(line):
            percentage = float(match.group(1))
            self.callback.on_progress(int(percentage), 100, f"{percentage:.1f}%")
            return True

        # Try fraction pattern
        if match := self.patterns["fraction"].search(line):
            current = int(match.group(1))
            total = int(match.group(2))
            self.callback.on_progress(current, total, f"{current}/{total}")
            return True

        # Try frame pattern (for video processing)
        if match := self.patterns["frame"].search(line):
            frame = int(match.group(1))
            # For frame numbers, we don't know the total, so just report the number
            self.callback.on_progress(frame, frame + 1, f"Frame {frame}")
            return True

        return False

    def add_pattern(self, name: str, pattern: str) -> None:
        """
        Add a custom progress pattern.

        Args:
            name: Name for the pattern
            pattern: Regex pattern string

        """
        self.patterns[name] = re.compile(pattern, re.IGNORECASE)


def create_progress_callback(
    mode: str = "auto", console: Console | None = None, log_level: str = "INFO"
) -> ProgressCallback:
    """
    Create appropriate progress callback based on mode.

    Args:
        mode: Progress mode ("auto", "console", "silent", "logging")
        console: Rich console instance for console mode
        log_level: Log level for logging mode

    Returns:
        Configured progress callback

    Used in:
    - topyaz/execution/__init__.py
    """
    if mode == "auto":
        # Auto-detect based on environment
        try:
            # Try to determine if we're in an interactive terminal
            import sys

            mode = "console" if sys.stdout.isatty() and sys.stderr.isatty() else "logging"
        except Exception:
            mode = "silent"

    if mode == "console":
        return ConsoleProgressCallback(console)
    if mode == "logging":
        return LoggingProgressCallback(log_level)
    if mode == "silent":
        return SilentProgressCallback()
    msg = f"Unknown progress mode: {mode}"
    raise ValueError(msg)


def create_batch_tracker(callback: ProgressCallback, total_items: int) -> BatchProgressTracker:
    """
    Create a batch progress tracker.

    Args:
        callback: Progress callback to use
        total_items: Total number of items to process

    Returns:
        Configured batch tracker

    Used in:
    - topyaz/execution/__init__.py
    """
    return BatchProgressTracker(callback, total_items)


def create_output_parser(callback: ProgressCallback) -> OutputProgressParser:
    """
    Create an output progress parser.

    Args:
        callback: Progress callback to update

    Returns:
        Configured output parser

    Used in:
    - topyaz/execution/__init__.py
    """
    return OutputProgressParser(callback)
