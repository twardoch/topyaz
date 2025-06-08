#!/usr/bin/env python3
# this_file: src/topyaz/execution/local.py
"""
Local command execution for topyaz.

This module provides local command execution capabilities with support for
progress monitoring, timeout handling, and error recovery.

"""

import subprocess
import threading
import time
from typing import Optional, Tuple

from loguru import logger

from topyaz.core.errors import ProcessingError
from topyaz.core.types import CommandList
from topyaz.execution.base import CommandExecutor, ExecutorContext, ProgressAwareExecutor, ProgressCallback


class LocalExecutor(ProgressAwareExecutor):
    """
    Executes commands locally on the current machine.

    Provides both simple execution and progress-aware execution
    with real-time output monitoring.

    Used in:
    - topyaz/cli.py
    - topyaz/execution/__init__.py
    """

    def __init__(self, context: ExecutorContext | None = None):
        """
        Initialize local executor.

        Args:
            context: Execution context with environment and settings

        """
        self.context = context or ExecutorContext()

    def is_available(self) -> bool:
        """Local execution is always available."""
        return True

    def execute(
        self, command: CommandList, input_data: str | None = None, timeout: int | None = None
    ) -> tuple[int, str, str]:
        """
        Execute command locally.

        Args:
            command: Command and arguments to execute
            input_data: Optional input data to pass to command
            timeout: Optional timeout override

        Returns:
            Tuple of (return_code, stdout, stderr)

        Raises:
            ProcessingError: If command execution fails

        """
        actual_timeout = timeout or self.context.timeout

        if self.context.dry_run:
            logger.info(f"DRY RUN: {' '.join(command)}")
            return 0, "dry-run-output", ""

        try:
            logger.debug(f"Executing locally: {' '.join(command)}")

            # Prepare subprocess arguments
            kwargs = {
                "input": input_data,
                "capture_output": True,
                "text": True,
                "timeout": actual_timeout,
                "encoding": "utf-8",
                "errors": "ignore",
                "check": False,
                "env": self.context.get_env(),
            }

            if self.context.working_dir:
                kwargs["cwd"] = self.context.working_dir

            # Execute command
            start_time = time.time()
            result = subprocess.run(command, **kwargs, check=False)
            execution_time = time.time() - start_time

            logger.debug(f"Command completed in {execution_time:.2f}s with return code: {result.returncode}")

            if result.stdout:
                logger.debug(f"STDOUT: {result.stdout[:500]}{'...' if len(result.stdout) > 500 else ''}")
            if result.stderr:
                logger.debug(f"STDERR: {result.stderr[:500]}{'...' if len(result.stderr) > 500 else ''}")

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            msg = f"Command timed out after {actual_timeout} seconds"
            logger.error(msg)
            raise ProcessingError(msg)

        except FileNotFoundError:
            msg = f"Command not found: {command[0]}"
            logger.error(msg)
            raise ProcessingError(msg)

        except Exception as e:
            msg = f"Command execution failed: {e}"
            logger.error(msg)
            raise ProcessingError(msg)

    def execute_with_progress(
        self,
        command: CommandList,
        callback: ProgressCallback,
        input_data: str | None = None,
        timeout: int | None = None,
    ) -> tuple[int, str, str]:
        """
        Execute command with progress monitoring.

        Args:
            command: Command and arguments to execute
            callback: Progress callback handler
            input_data: Optional input data
            timeout: Optional timeout override

        Returns:
            Tuple of (return_code, stdout, stderr)

        Raises:
            ProcessingError: If command execution fails

        """
        actual_timeout = timeout or self.context.timeout

        if self.context.dry_run:
            logger.info(f"DRY RUN (with progress): {' '.join(command)}")
            callback.on_progress(1, 1)
            callback.on_complete(True, "Dry run completed")
            return 0, "dry-run-output", ""

        try:
            logger.debug(f"Executing locally with progress: {' '.join(command)}")

            # Start process
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE if input_data else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="ignore",
                env=self.context.get_env(),
                cwd=self.context.working_dir,
            )

            # Collect output
            stdout_lines = []
            stderr_lines = []

            # Output reading threads
            def read_stdout():
                try:
                    for line in iter(process.stdout.readline, ""):
                        stdout_lines.append(line)
                        callback.on_output(line.rstrip(), is_stderr=False)
                        self._extract_progress(line, callback)
                finally:
                    process.stdout.close()

            def read_stderr():
                try:
                    for line in iter(process.stderr.readline, ""):
                        stderr_lines.append(line)
                        callback.on_output(line.rstrip(), is_stderr=True)
                        self._extract_progress(line, callback)
                finally:
                    process.stderr.close()

            # Start output threads
            stdout_thread = threading.Thread(target=read_stdout)
            stderr_thread = threading.Thread(target=read_stderr)

            stdout_thread.start()
            stderr_thread.start()

            # Send input if provided
            if input_data:
                try:
                    process.stdin.write(input_data)
                    process.stdin.close()
                except Exception as e:
                    logger.debug(f"Failed to send input: {e}")

            # Wait for process with timeout
            try:
                exit_code = process.wait(timeout=actual_timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                callback.on_complete(False, f"Command timed out after {actual_timeout} seconds")
                msg = f"Command timed out after {actual_timeout} seconds"
                raise ProcessingError(msg)

            # Wait for output threads
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)

            # Combine output
            stdout_text = "".join(stdout_lines)
            stderr_text = "".join(stderr_lines)

            # Report completion
            success = exit_code == 0
            callback.on_complete(success, f"Command completed with exit code {exit_code}")

            logger.debug(f"Command completed with return code: {exit_code}")

            return exit_code, stdout_text, stderr_text

        except ProcessingError:
            raise
        except Exception as e:
            callback.on_complete(False, str(e))
            msg = f"Command execution failed: {e}"
            logger.error(msg)
            raise ProcessingError(msg)

    def _extract_progress(self, line: str, callback: ProgressCallback) -> None:
        """
        Extract progress information from command output.

        Args:
            line: Output line to analyze
            callback: Progress callback to notify

        """
        line_lower = line.lower()

        # Look for common progress patterns
        import re

        # FFmpeg progress (Video AI)
        ffmpeg_match = re.search(r"frame=\s*(\d+)", line)
        if ffmpeg_match:
            frame_num = int(ffmpeg_match.group(1))
            callback.on_progress(frame_num)
            return

        # Percentage progress
        percent_match = re.search(r"(\d+)%", line)
        if percent_match:
            percent = int(percent_match.group(1))
            callback.on_progress(percent, 100)
            return

        # Processing indicators
        if any(keyword in line_lower for keyword in ["processing", "analyzing", "enhancing"]):
            # Simple progress indication without specific numbers
            callback.on_progress(1)  # Indicates activity

    def get_info(self) -> dict[str, str]:
        """Get information about this executor.

        Used in:
        - topyaz/cli.py
        - topyaz/execution/remote.py
        """
        info = super().get_info()
        info.update(
            {
                "platform": "local",
                "working_dir": self.context.working_dir or "current",
                "timeout": str(self.context.timeout),
                "dry_run": str(self.context.dry_run),
            }
        )
        return info


class SimpleProgressCallback(ProgressCallback):
    """
    Simple progress callback that logs progress updates.

    This is a basic implementation that can be used when no custom
    progress handling is needed.

    """

    def __init__(self, task_name: str = "Processing"):
        """
        Initialize simple progress callback.

        Args:
            task_name: Name of the task for logging

        """
        self.task_name = task_name
        self._last_percent = -1

    def on_output(self, line: str, is_stderr: bool = False) -> None:
        """Log output line at debug level."""
        logger.debug(f"{'STDERR' if is_stderr else 'STDOUT'}: {line}")

    def on_progress(self, current: int, total: int | None = None) -> None:
        """Log progress updates."""
        if total:
            percent = int((current / total) * 100)
            if percent >= self._last_percent + 10:  # Log every 10%
                self._last_percent = percent
                logger.info(f"{self.task_name}: {percent}% ({current}/{total})")
        # Indeterminate progress
        elif current % 10 == 0:  # Log every 10th update
            logger.info(f"{self.task_name}: Working... ({current})")

    def on_complete(self, success: bool, message: str = "") -> None:
        """Log completion."""
        if success:
            logger.success(f"{self.task_name}: {message or 'Completed successfully'}")
        else:
            logger.error(f"{self.task_name}: {message or 'Failed'}")


class QuietProgressCallback(ProgressCallback):
    """
    Progress callback that doesn't log anything.

    Useful when you want progress monitoring internally but
    don't want console output.

    """

    def __init__(self):
        """Initialize quiet progress callback."""
        self.current = 0
        self.total = None
        self.success = None
        self.message = ""

    def on_output(self, line: str, is_stderr: bool = False) -> None:
        """Silently ignore output."""
        pass

    def on_progress(self, current: int, total: int | None = None) -> None:
        """Store progress internally."""
        self.current = current
        if total is not None:
            self.total = total

    def on_complete(self, success: bool, message: str = "") -> None:
        """Store completion status."""
        self.success = success
        self.message = message

    def get_progress_percent(self) -> float | None:
        """Get current progress as percentage."""
        if self.total and self.total > 0:
            return (self.current / self.total) * 100
        return None
