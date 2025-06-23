#!/usr/bin/env python3
# this_file: src/topyaz/execution/base.py
"""
Base classes for command execution in topyaz.

This module defines abstract interfaces for command execution that can be
implemented for local and remote execution environments.

"""

import os  # Moved from ExecutorContext.get_env
from abc import ABC, abstractmethod

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
    - topyaz/products/_gigapixel.py
    - topyaz/products/_photo_ai.py
    - topyaz/products/_video_ai.py
    """

    @abstractmethod
    def execute(
        self,
        command: CommandList,
        input_data: str | None = None,
        timeout: int | None = None,
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
        Check if this _executor is available for use.

        Returns:
            True if _executor can be used, False otherwise
        """
        pass

    def get_info(self) -> dict[str, str]:
        """
        Get information about this _executor.

        Returns:
            Dictionary with _executor information

        Used in:
        - topyaz/execution/local.py
        - topyaz/execution/remote.py
        """
        return {
            "type": self.__class__.__name__,
            "available": str(self.is_available()),
        }


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
        *,  # Make dry_run keyword-only
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
        # import os # Moved to top
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
