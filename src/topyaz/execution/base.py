#!/usr/bin/env python3
# this_file: src/topyaz/execution/base.py
"""
Base classes for command execution in topyaz.

This module defines abstract interfaces for command execution that can be
implemented for local and remote execution environments.

"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple

from topyaz.core.types import CommandList


class CommandExecutor(ABC):
    """
    Abstract base class for command execution.

    Defines the interface for executing commands in different environments
    (local, remote, containerized, etc.).

    Used in:
    - topyaz/execution/__init__.py
    - topyaz/execution/local.py
    - topyaz/execution/remote.py
    - topyaz/products/base.py
    - topyaz/products/gigapixel.py
    - topyaz/products/photo_ai.py
    - topyaz/products/video_ai.py
    """

    @abstractmethod
    def execute(
        self, command: CommandList, input_data: str | None = None, timeout: int | None = None
    ) -> tuple[int, str, str]:
        """
        Execute a command and return the result.

        Args:
            command: Command and arguments to execute
            input_data: Optional input data to pass to command
            timeout: Optional timeout in seconds

        Returns:
            Tuple of (return_code, stdout, stderr)

        Raises:
            ProcessingError: If command execution fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this executor is available for use.

        Returns:
            True if executor can be used, False otherwise
        """
        pass

    def supports_progress(self) -> bool:
        """
        Check if this executor supports progress monitoring.

        Returns:
            True if progress monitoring is supported

        """
        return False

    def get_info(self) -> dict[str, str]:
        """
        Get information about this executor.

        Returns:
            Dictionary with executor information

        Used in:
        - topyaz/execution/local.py
        - topyaz/execution/remote.py
        """
        return {
            "type": self.__class__.__name__,
            "available": str(self.is_available()),
            "supports_progress": str(self.supports_progress()),
        }


class ProgressCallback(ABC):
    """
    Abstract base class for progress callbacks.

    Used to monitor command execution progress.

    Used in:
    - topyaz/execution/__init__.py
    - topyaz/execution/local.py
    - topyaz/execution/remote.py
    """

    @abstractmethod
    def on_output(self, line: str, is_stderr: bool = False) -> None:
        """
        Called when command produces output.

        Args:
            line: Output line
            is_stderr: True if from stderr, False if from stdout
        """
        pass

    @abstractmethod
    def on_progress(self, current: int, total: int | None = None) -> None:
        """
        Called when progress can be determined.

        Args:
            current: Current progress value
            total: Total value (None if unknown)
        """
        pass

    @abstractmethod
    def on_complete(self, success: bool, message: str = "") -> None:
        """
        Called when command completes.

        Args:
            success: Whether command succeeded
            message: Optional completion message
        """
        pass


class ProgressAwareExecutor(CommandExecutor):
    """
    Extended executor interface that supports progress monitoring.

    This is a specialized interface for executors that can provide
    real-time progress feedback during command execution.

    Used in:
    - topyaz/execution/__init__.py
    - topyaz/execution/local.py
    - topyaz/execution/remote.py
    """

    @abstractmethod
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
            timeout: Optional timeout in seconds

        Returns:
            Tuple of (return_code, stdout, stderr)

        Raises:
            ProcessingError: If command execution fails
        """
        pass

    def supports_progress(self) -> bool:
        """Progress monitoring is supported by default."""
        return True


class ExecutorContext:
    """
    Context information for command execution.

    Provides environment variables, working directory, and other
    context needed for command execution.

    Used in:
    - topyaz/execution/__init__.py
    - topyaz/execution/local.py
    - topyaz/execution/remote.py
    """

    def __init__(
        self,
        working_dir: str | None = None,
        env_vars: dict[str, str] | None = None,
        timeout: int = 3600,
        dry_run: bool = False,
    ):
        """
        Initialize execution context.

        Args:
            working_dir: Working directory for command execution
            env_vars: Additional environment variables
            timeout: Default timeout in seconds
            dry_run: If True, don't actually execute commands

        """
        self.working_dir = working_dir
        self.env_vars = env_vars or {}
        self.timeout = timeout
        self.dry_run = dry_run

    def get_env(self) -> dict[str, str]:
        """
        Get complete environment variables.

        Returns:
            Dictionary of environment variables

        Used in:
        - topyaz/execution/local.py
        """
        import os

        env = os.environ.copy()
        env.update(self.env_vars)
        return env

    def add_env_var(self, key: str, value: str) -> None:
        """
        Add an environment variable.

        Args:
            key: Variable name
            value: Variable value

        """
        self.env_vars[key] = value

    def remove_env_var(self, key: str) -> None:
        """
        Remove an environment variable.

        Args:
            key: Variable name to remove

        """
        self.env_vars.pop(key, None)
