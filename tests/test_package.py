"""Test suite for topyaz."""

from unittest.mock import patch


def test_version():
    """Verify package exposes version."""
    import topyaz

    assert topyaz.__version__


def test_imports():
    """Test that all expected classes and functions can be imported."""
    from topyaz import (
        AuthenticationError,
        ProcessingError,
        TopazError,
        topyazWrapper,
    )
    from topyaz.topyaz import EnvironmentError as TopyazEnvironmentError

    # Check classes exist
    assert topyazWrapper
    assert TopazError
    assert AuthenticationError
    assert TopyazEnvironmentError
    assert ProcessingError

    # Check inheritance
    assert issubclass(AuthenticationError, TopazError)
    assert issubclass(TopyazEnvironmentError, TopazError)
    assert issubclass(ProcessingError, TopazError)


def test_wrapper_initialization():
    """Test topyazWrapper can be initialized with basic parameters."""
    from topyaz import topyazWrapper

    with patch("topyaz.topyaz.logger"):
        wrapper = topyazWrapper(verbose=False, dry_run=True, log_level="ERROR")

        assert wrapper.verbose is False
        assert wrapper.dry_run is True
        assert wrapper.timeout == 3600


def test_version_command():
    """Test version command returns version string."""
    from topyaz import topyazWrapper

    with patch("topyaz.topyaz.logger"):
        wrapper = topyazWrapper(verbose=False)
        version_str = wrapper.version()
        assert "topyaz v" in version_str


def test_executable_finding():
    """Test executable finding logic."""
    from topyaz import topyazWrapper

    with patch("topyaz.topyaz.logger"):
        wrapper = topyazWrapper(verbose=False)

        # Test with mock paths
        with patch("topyaz.topyaz.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            result = wrapper._find_executable("gigapixel")
            assert result is None


def test_dry_run_mode():
    """Test dry run mode doesn't execute actual commands."""
    from topyaz import topyazWrapper

    with patch("topyaz.topyaz.logger"):
        wrapper = topyazWrapper(dry_run=True, verbose=False)

        # Test command execution in dry run mode
        result = wrapper._execute_command(["echo", "test"])
        assert result == (0, "dry-run-output", "")
