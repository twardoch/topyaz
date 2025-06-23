#!/usr/bin/env python3
# this_file: src/topyaz/execution/local.py
"""
Local command execution for topyaz.

This module provides local command execution capabilities with timeout
handling and error recovery.

"""

import subprocess
import time

from loguru import logger

from topyaz.core.errors import ProcessingError
from topyaz.core.types import CommandList
from topyaz.execution.base import CommandExecutor, ExecutorContext

OUTPUT_PREVIEW_LENGTH = 500


class LocalExecutor(CommandExecutor):
    """
    Executes commands locally on the current machine.

    Used in:
    - topyaz/cli.py
    - topyaz/execution/__init__.py
    """

    def __init__(self, context: ExecutorContext | None = None):
        """
        Initialize local _executor.

        Args:
            context: Execution context with environment and settings

        """
        self.context = context or ExecutorContext()

    def is_available(self) -> bool:
        """Local execution is always available."""
        return True

    def execute(
        self,
        command: CommandList,
        input_data: str | None = None,
        timeout: int | None = None,
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
                "env": self.context.get_env(),
            }

            if self.context.working_dir:
                kwargs["cwd"] = self.context.working_dir

            # Execute command
            start_time = time.time()
            # S603: `command` is a list of arguments. `shell=False` is implicitly used via `kwargs` not setting it.
            # Inputs to `command` are expected to be validated by upstream callers (e.g., parameter handlers).
            result = subprocess.run(command, **kwargs, check=False)  # noqa: S603
            execution_time = time.time() - start_time

            logger.debug(f"Command completed in {execution_time:.2f}s with return code: {result.returncode}")

            if result.stdout:
                stdout_preview = result.stdout[:OUTPUT_PREVIEW_LENGTH]
                if len(result.stdout) > OUTPUT_PREVIEW_LENGTH:
                    stdout_preview += "..."
                logger.debug(f"STDOUT: {stdout_preview}")
            if result.stderr:
                stderr_preview = result.stderr[:OUTPUT_PREVIEW_LENGTH]
                if len(result.stderr) > OUTPUT_PREVIEW_LENGTH:
                    stderr_preview += "..."
                logger.debug(f"STDERR: {stderr_preview}")

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired as e:
            msg = f"Command timed out after {actual_timeout} seconds"
            logger.error(msg)
            raise ProcessingError(msg) from e

        except FileNotFoundError as e:
            msg = f"Command not found: {command[0]}"
            logger.error(msg)
            raise ProcessingError(msg) from e

        except Exception as e:
            msg = f"Command execution failed: {e}"
            logger.error(msg)
            raise ProcessingError(msg) from e

    def get_info(self) -> dict[str, str]:
        """Get information about this _executor.

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
