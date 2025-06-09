#!/usr/bin/env python3
"""
Demonstration of remote coordination functionality.

This script shows how the RemoteFileCoordinator works to enable
transparent remote processing with automatic file coordination.
"""

from pathlib import Path
from unittest.mock import MagicMock

from src.topyaz.core.types import RemoteOptions
from src.topyaz.execution.coordination import RemoteFileCoordinator
from src.topyaz.execution.remote import RemoteExecutor


def demo_file_detection():
    """Demonstrate file detection in commands."""

    # Create a mock executor
    mock_executor = MagicMock(spec=RemoteExecutor)
    coordinator = RemoteFileCoordinator(mock_executor, "/tmp/topyaz")

    # Test various command patterns
    test_commands = [
        ["tpai", "input.jpg", "-o", "output.jpg"],
        ["gigapixel", "--scale", "4", "/path/to/image.png", "--output", "/path/to/result.png"],
        ["video_ai", "movie.mp4", "--scale", "2", "-o", "enhanced_movie.mp4"],
    ]

    for command in test_commands:
        # Mock file path detection
        def mock_is_file_path(arg):
            return any(ext in arg for ext in [".jpg", ".png", ".mp4"])

        coordinator._is_file_path = mock_is_file_path

        # Mock Path.exists for input detection
        import unittest.mock

        with unittest.mock.patch("pathlib.Path.exists", return_value=True):
            inputs, outputs = coordinator._detect_files(command)


def demo_path_translation():
    """Demonstrate path translation."""

    mock_executor = MagicMock(spec=RemoteExecutor)
    coordinator = RemoteFileCoordinator(mock_executor, "/tmp/topyaz")

    # Example command with local paths
    command = ["tpai", "/Users/john/vacation.jpg", "-o", "/Users/john/enhanced.jpg", "--scale", "2"]

    # Example path mapping (what would be created during coordination)
    path_mapping = {
        "/Users/john/vacation.jpg": "/tmp/topyaz/sessions/session123/inputs/vacation.jpg",
        "/Users/john/enhanced.jpg": "/tmp/topyaz/sessions/session123/outputs/enhanced.jpg",
    }

    coordinator._translate_command(command, path_mapping)

    for _local, _remote in path_mapping.items():
        pass


def demo_workflow():
    """Demonstrate the complete workflow."""

    # Create mock executor with realistic responses
    mock_executor = MagicMock(spec=RemoteExecutor)
    mock_executor.execute.return_value = (0, "Processing complete", "")
    mock_executor.upload_file.return_value = True
    mock_executor.download_file.return_value = True

    coordinator = RemoteFileCoordinator(mock_executor, "/tmp/topyaz")

    # Simulate the actual workflow
    command = ["tpai", "/local/input.jpg", "-o", "/local/output.jpg"]

    # Mock the internal methods to show the flow
    def mock_detect_files(cmd):
        return (["/local/input.jpg"], ["/local/output.jpg"])

    def mock_create_session():
        from src.topyaz.execution.coordination import RemoteSession

        return RemoteSession(session_id="demo_session_123", remote_base_dir="/tmp/topyaz/sessions/demo_session_123")

    coordinator._detect_files = mock_detect_files
    coordinator._create_session = mock_create_session

    session = coordinator._create_session()

    inputs, outputs = coordinator._detect_files(command)

    # Simulate path mapping
    path_mapping = {}
    for inp in inputs:
        remote_path = f"{session.remote_base_dir}/inputs/{Path(inp).name}"
        path_mapping[inp] = remote_path

    for out in outputs:
        remote_path = f"{session.remote_base_dir}/outputs/{Path(out).name}"
        path_mapping[out] = remote_path

    coordinator._translate_command(command, path_mapping)


def demo_caching():
    """Demonstrate file caching functionality."""

    mock_executor = MagicMock(spec=RemoteExecutor)
    coordinator = RemoteFileCoordinator(mock_executor, "/tmp/topyaz")

    # Mock hash calculation
    def mock_calculate_hash(path):
        return "abc123def456"  # Mock hash

    coordinator._calculate_hash = mock_calculate_hash

    file_path = "/local/frequently_used.jpg"
    file_hash = coordinator._calculate_hash(file_path)
    f"{coordinator.cache_dir}/{file_hash}/{Path(file_path).name}"

    # First run - cache miss
    mock_executor.execute.return_value = (1, "", "File not found")  # Cache miss
    coordinator._get_cached_path(file_path)

    # Second run - cache hit
    mock_executor.execute.return_value = (0, "", "")  # Cache hit
    coordinator._get_cached_path(file_path)


if __name__ == "__main__":
    demo_file_detection()
    demo_path_translation()
    demo_workflow()
    demo_caching()
