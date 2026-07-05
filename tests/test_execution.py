#!/usr/bin/env python3
# this_file: tests/test_execution.py
"""
Tests for execution backends in topyaz.execution.

These exercise the real ``LocalExecutor`` API, which is constructed from an
``ExecutorContext`` (working dir, env vars, timeout, dry-run) and exposes
``execute(command, input_data=None, timeout=None)`` returning a
``(returncode, stdout, stderr)`` tuple. Failures are surfaced as
``ProcessingError`` rather than the raw subprocess exceptions.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from topyaz.core.errors import ProcessingError
from topyaz.execution.base import ExecutorContext
from topyaz.execution.local import LocalExecutor


class TestLocalExecutor:
    """Test the local execution backend."""

    def test_initialization(self):
        """LocalExecutor stores its context and is always available."""
        context = ExecutorContext(timeout=120, dry_run=False)
        executor = LocalExecutor(context)

        assert executor.context is context
        assert executor.context.timeout == 120
        assert executor.context.dry_run is False
        assert executor.is_available() is True

    def test_initialization_defaults(self):
        """A default context is created when none is supplied."""
        executor = LocalExecutor()

        assert isinstance(executor.context, ExecutorContext)
        assert executor.context.timeout == 3600
        assert executor.context.dry_run is False

    def test_execute_simple_command(self):
        """Executing a simple command returns its stdout."""
        executor = LocalExecutor(ExecutorContext())

        returncode, stdout, stderr = executor.execute(["echo", "hello"])

        assert returncode == 0
        assert "hello" in stdout
        assert stderr == ""

    def test_execute_with_timeout(self):
        """A command that exceeds the timeout raises ProcessingError."""
        executor = LocalExecutor(ExecutorContext(timeout=1))

        with pytest.raises(ProcessingError, match="timed out"):
            executor.execute(["sleep", "5"])

    def test_execute_nonexistent_command(self):
        """A missing executable is wrapped in ProcessingError."""
        executor = LocalExecutor(ExecutorContext())

        with pytest.raises(ProcessingError, match="not found"):
            executor.execute(["nonexistent_command_12345"])

    def test_execute_failing_command(self):
        """A command returning a non-zero exit code is reported, not raised."""
        executor = LocalExecutor(ExecutorContext())

        returncode, _stdout, _stderr = executor.execute(["false"])

        assert returncode != 0

    def test_execute_with_dry_run(self):
        """Dry-run mode short-circuits execution with a marker output."""
        executor = LocalExecutor(ExecutorContext(dry_run=True))

        returncode, stdout, stderr = executor.execute(["echo", "test"])

        assert returncode == 0
        assert stdout == "dry-run-output"
        assert stderr == ""

    def test_execute_with_working_directory(self, tmp_path: Path):
        """The context working directory is honoured by the subprocess."""
        work_dir = tmp_path.resolve()
        executor = LocalExecutor(ExecutorContext(working_dir=str(work_dir)))

        returncode, stdout, _stderr = executor.execute(["pwd"])

        assert returncode == 0
        assert str(work_dir) in stdout

    def test_execute_with_environment_variables(self):
        """Extra environment variables from the context are passed through."""
        executor = LocalExecutor(ExecutorContext(env_vars={"TEST_VAR": "test_value"}))

        returncode, stdout, _stderr = executor.execute(["printenv", "TEST_VAR"])

        assert returncode == 0
        assert "test_value" in stdout

    def test_execute_mocked_success(self):
        """A mocked subprocess success is translated into the result tuple."""
        executor = LocalExecutor(ExecutorContext())

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="mocked output", stderr="")

            returncode, stdout, stderr = executor.execute(["some", "command"])

        assert returncode == 0
        assert stdout == "mocked output"
        assert stderr == ""
        mock_run.assert_called_once()

    def test_execute_mocked_failure(self):
        """A mocked subprocess failure is translated into the result tuple."""
        executor = LocalExecutor(ExecutorContext())

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=1, stdout="", stderr="error message")

            returncode, stdout, stderr = executor.execute(["some", "command"])

        assert returncode == 1
        assert stdout == ""
        assert stderr == "error message"
        mock_run.assert_called_once()

    def test_execute_empty_command_raises(self):
        """An empty command list fails as a ProcessingError."""
        executor = LocalExecutor(ExecutorContext())

        with pytest.raises(ProcessingError):
            executor.execute([])

    def test_execute_none_command_raises(self):
        """A ``None`` command fails as a ProcessingError."""
        executor = LocalExecutor(ExecutorContext())

        with pytest.raises(ProcessingError):
            executor.execute(None)  # type: ignore[arg-type]

    def test_execute_command_with_path_object(self):
        """Commands built from stringified Path objects execute correctly."""
        executor = LocalExecutor(ExecutorContext())
        echo = str(Path("/bin/echo"))

        returncode, stdout, _stderr = executor.execute([echo, "test"])

        assert returncode == 0
        assert "test" in stdout

    def test_execute_output_handling(self):
        """Both stdout and stderr streams are captured independently."""
        executor = LocalExecutor(ExecutorContext())

        returncode, stdout, stderr = executor.execute(["sh", "-c", "echo out && echo err >&2"])

        assert returncode == 0
        assert "out" in stdout
        assert "err" in stderr

    def test_execute_large_output(self):
        """Large stdout is captured in full."""
        executor = LocalExecutor(ExecutorContext())

        returncode, stdout, _stderr = executor.execute(["sh", "-c", "for i in $(seq 1 100); do echo line $i; done"])

        assert returncode == 0
        assert len(stdout.splitlines()) == 100

    def test_execute_unicode_handling(self):
        """Unicode in command output is decoded correctly."""
        executor = LocalExecutor(ExecutorContext())

        returncode, stdout, _stderr = executor.execute(["echo", "Hello 世界 🌍"])

        assert returncode == 0
        assert "Hello" in stdout
        assert "世界" in stdout
        assert "🌍" in stdout

    def test_get_info(self):
        """get_info exposes executor metadata."""
        executor = LocalExecutor(ExecutorContext(timeout=42))

        info = executor.get_info()

        assert info["platform"] == "local"
        assert info["timeout"] == "42"
