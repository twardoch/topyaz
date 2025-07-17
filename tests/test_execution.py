#!/usr/bin/env python3
# this_file: tests/test_execution.py
"""
Tests for execution backends in topyaz.execution.
"""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from topyaz.core.types import ProcessingOptions
from topyaz.execution.local import LocalExecutor


class TestLocalExecutor:
    """Test local execution backend."""

    def test_initialization(self):
        """Test LocalExecutor initialization."""
        options = ProcessingOptions(verbose=True, dry_run=False)
        executor = LocalExecutor(options)
        
        assert executor.options == options
        assert executor.options.verbose is True
        assert executor.options.dry_run is False

    def test_execute_simple_command(self):
        """Test executing a simple command."""
        options = ProcessingOptions()
        executor = LocalExecutor(options)
        
        # Test with a simple command that should succeed
        returncode, stdout, stderr = executor.execute(["echo", "hello"])
        
        assert returncode == 0
        assert "hello" in stdout
        assert stderr == ""

    def test_execute_with_timeout(self):
        """Test command execution with timeout."""
        options = ProcessingOptions(timeout=1)
        executor = LocalExecutor(options)
        
        # Test with a command that should timeout
        with pytest.raises(subprocess.TimeoutExpired):
            executor.execute(["sleep", "5"])

    def test_execute_nonexistent_command(self):
        """Test executing a non-existent command."""
        options = ProcessingOptions()
        executor = LocalExecutor(options)
        
        # Should raise FileNotFoundError or similar
        with pytest.raises((FileNotFoundError, OSError)):
            executor.execute(["nonexistent_command_12345"])

    def test_execute_failing_command(self):
        """Test executing a command that fails."""
        options = ProcessingOptions()
        executor = LocalExecutor(options)
        
        # Test with a command that should fail
        returncode, stdout, stderr = executor.execute(["false"])
        
        assert returncode != 0

    def test_execute_with_verbose(self):
        """Test command execution with verbose output."""
        options = ProcessingOptions(verbose=True)
        executor = LocalExecutor(options)
        
        # Should execute successfully and potentially log more
        returncode, stdout, stderr = executor.execute(["echo", "test"])
        
        assert returncode == 0
        assert "test" in stdout

    def test_execute_with_dry_run(self):
        """Test command execution in dry run mode."""
        options = ProcessingOptions(dry_run=True)
        executor = LocalExecutor(options)
        
        # In dry run, should not execute but return success
        returncode, stdout, stderr = executor.execute(["echo", "test"])
        
        # Implementation may vary, but should handle dry run gracefully
        assert returncode == 0
        assert "DRY RUN" in stdout or "dry run" in stdout.lower()

    def test_execute_with_working_directory(self):
        """Test command execution with working directory."""
        options = ProcessingOptions()
        executor = LocalExecutor(options)
        
        # Test with pwd command to verify working directory
        returncode, stdout, stderr = executor.execute(["pwd"], cwd="/tmp")
        
        assert returncode == 0
        assert "/tmp" in stdout

    def test_execute_with_environment_variables(self):
        """Test command execution with environment variables."""
        options = ProcessingOptions()
        executor = LocalExecutor(options)
        
        # Test with environment variable
        env = {"TEST_VAR": "test_value"}
        returncode, stdout, stderr = executor.execute(["printenv", "TEST_VAR"], env=env)
        
        assert returncode == 0
        assert "test_value" in stdout

    @patch('subprocess.run')
    def test_execute_mocked_success(self, mock_run):
        """Test command execution with mocked subprocess."""
        options = ProcessingOptions()
        executor = LocalExecutor(options)
        
        # Mock successful execution
        mock_run.return_value = Mock(
            returncode=0,
            stdout="mocked output",
            stderr=""
        )
        
        returncode, stdout, stderr = executor.execute(["test", "command"])
        
        assert returncode == 0
        assert stdout == "mocked output"
        assert stderr == ""
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_execute_mocked_failure(self, mock_run):
        """Test command execution with mocked subprocess failure."""
        options = ProcessingOptions()
        executor = LocalExecutor(options)
        
        # Mock failed execution
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="error message"
        )
        
        returncode, stdout, stderr = executor.execute(["test", "command"])
        
        assert returncode == 1
        assert stdout == ""
        assert stderr == "error message"
        mock_run.assert_called_once()

    def test_execute_command_list_validation(self):
        """Test that command list is properly validated."""
        options = ProcessingOptions()
        executor = LocalExecutor(options)
        
        # Test with empty command list
        with pytest.raises((ValueError, TypeError)):
            executor.execute([])
        
        # Test with None command
        with pytest.raises((ValueError, TypeError)):
            executor.execute(None)

    def test_execute_command_string_conversion(self):
        """Test that command strings are properly handled."""
        options = ProcessingOptions()
        executor = LocalExecutor(options)
        
        # Test with Path objects in command
        path_obj = Path("/bin/echo")
        returncode, stdout, stderr = executor.execute([str(path_obj), "test"])
        
        # Should work if echo is available
        if returncode == 0:
            assert "test" in stdout

    def test_execute_output_handling(self):
        """Test proper handling of command output."""
        options = ProcessingOptions()
        executor = LocalExecutor(options)
        
        # Test with command that produces both stdout and stderr
        returncode, stdout, stderr = executor.execute(["sh", "-c", "echo 'out' && echo 'err' >&2"])
        
        assert returncode == 0
        assert "out" in stdout
        assert "err" in stderr

    def test_execute_large_output(self):
        """Test handling of large command output."""
        options = ProcessingOptions()
        executor = LocalExecutor(options)
        
        # Test with command that produces large output
        returncode, stdout, stderr = executor.execute(["sh", "-c", "for i in {1..100}; do echo 'line $i'; done"])
        
        assert returncode == 0
        assert len(stdout.splitlines()) == 100

    def test_execute_unicode_handling(self):
        """Test proper handling of unicode in command output."""
        options = ProcessingOptions()
        executor = LocalExecutor(options)
        
        # Test with unicode characters
        returncode, stdout, stderr = executor.execute(["echo", "Hello 世界 🌍"])
        
        assert returncode == 0
        assert "Hello" in stdout
        assert "世界" in stdout
        assert "🌍" in stdout