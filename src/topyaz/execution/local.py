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
                stdout_preview = result.stdout[:500]
                if len(result.stdout) > 500:
                    stdout_preview += "..."
                logger.debug(f"STDOUT: {stdout_preview}")
            if result.stderr:
                stderr_preview = result.stderr[:500]
                if len(result.stderr) > 500:
                    stderr_preview += "..."
                logger.debug(f"STDERR: {stderr_preview}")

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
