#!/usr/bin/env python3
# this_file: tests/test_remote_coordination.py
"""
Tests for remote file coordination functionality.

Tests the RemoteFileCoordinator class and its integration with
the remote execution system.
"""

import tempfile
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from topyaz.core.types import RemoteOptions
from topyaz.execution.coordination import RemoteFileCoordinator, RemoteSession
from topyaz.execution.remote import RemoteExecutor


class TestRemoteFileCoordinator:
    """Test remote file coordination functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock remote executor
        self.mock_executor = MagicMock(spec=RemoteExecutor)
        self.mock_executor.execute.return_value = (0, "success", "")
        self.mock_executor.upload_file.return_value = True
        self.mock_executor.download_file.return_value = True

        # Create coordinator
        self.coordinator = RemoteFileCoordinator(self.mock_executor, "/tmp/test")

    def test_session_creation(self):
        """Test remote session creation."""
        with patch("time.time", return_value=1234567890), patch("uuid.uuid4") as mock_uuid:
            mock_uuid.return_value.hex = "abcd1234" * 4  # 32 chars

            session = self.coordinator._create_session()

            assert session.session_id == "topyaz_1234567890_abcd1234"
            assert session.remote_base_dir == "/tmp/test/sessions/topyaz_1234567890_abcd1234"
            assert session.local_to_remote == {}
            assert session.remote_to_local == {}

            # Verify mkdir was called
            self.mock_executor.execute.assert_called_with(
                [
                    "mkdir",
                    "-p",
                    "/tmp/test/sessions/topyaz_1234567890_abcd1234/inputs",
                    "/tmp/test/sessions/topyaz_1234567890_abcd1234/outputs",
                ]
            )

    def test_file_detection_basic(self):
        """Test basic file detection in commands."""
        command = ["tpai", "input.jpg", "-o", "output.jpg"]

        with patch.object(self.coordinator, "_is_file_path") as mock_is_file:
            mock_is_file.side_effect = lambda x: x.endswith(".jpg")

            with patch("pathlib.Path.exists", return_value=True):
                inputs, outputs = self.coordinator._detect_files(command)

                assert inputs == ["input.jpg"]
                assert outputs == ["output.jpg"]

    def test_file_detection_complex(self):
        """Test file detection with complex command structure."""
        command = ["topazlabs", "--scale", "2", "-i", "photo.png", "--output", "result.png", "--quality", "95"]

        with patch.object(self.coordinator, "_is_file_path") as mock_is_file:
            mock_is_file.side_effect = lambda x: x.endswith(".png")

            with patch("pathlib.Path.exists", return_value=True):
                inputs, outputs = self.coordinator._detect_files(command)

                assert inputs == ["photo.png"]
                assert outputs == ["result.png"]

    def test_is_file_path(self):
        """Test file path detection logic."""
        coordinator = self.coordinator

        # Valid file paths
        with patch("pathlib.Path.exists", return_value=True):
            assert coordinator._is_file_path("image.jpg")
            assert coordinator._is_file_path("/path/to/file.png")
            assert coordinator._is_file_path("./relative/path.mp4")

        # Non-file paths
        assert not coordinator._is_file_path("-o")
        assert not coordinator._is_file_path("--scale")
        assert not coordinator._is_file_path("2")
        assert not coordinator._is_file_path("")

    def test_path_translation(self):
        """Test command path translation."""
        command = ["tpai", "input.jpg", "-o", "output.jpg", "--scale", "2"]
        mapping = {"input.jpg": "/remote/session/inputs/input.jpg", "output.jpg": "/remote/session/outputs/output.jpg"}

        translated = self.coordinator._translate_command(command, mapping)

        expected = [
            "tpai",
            "/remote/session/inputs/input.jpg",
            "-o",
            "/remote/session/outputs/output.jpg",
            "--scale",
            "2",
        ]
        assert translated == expected

    def test_partial_path_translation(self):
        """Test translation of partial paths in arguments."""
        mapping = {"/local/input.jpg": "/remote/input.jpg", "/local/output.jpg": "/remote/output.jpg"}

        # Test complex argument with embedded path
        arg = "--input-file=/local/input.jpg"
        result = self.coordinator._translate_partial_paths(arg, mapping)
        assert result == "--input-file=/remote/input.jpg"

        # Test argument with no paths
        arg = "--scale=2"
        result = self.coordinator._translate_partial_paths(arg, mapping)
        assert result == "--scale=2"

    def test_cleanup_session(self):
        """Test session cleanup."""
        session = RemoteSession(session_id="test_session", remote_base_dir="/tmp/test/sessions/test_session")

        self.coordinator._cleanup_session(session)

        self.mock_executor.execute.assert_called_with(["rm", "-rf", "/tmp/test/sessions/test_session"])

    def test_execute_with_files_success(self):
        """Test successful file coordination workflow."""
        command = ["tpai", "test_input.jpg", "-o", "test_output.jpg"]

        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(b"fake image data")
            test_file_path = temp_file.name

        try:
            # Mock file detection
            with patch.object(self.coordinator, "_detect_files") as mock_detect:
                mock_detect.return_value = ([test_file_path], ["test_output.jpg"])

                # Mock session creation
                with patch.object(self.coordinator, "_create_session") as mock_create:
                    mock_session = RemoteSession(session_id="test", remote_base_dir="/tmp/test/sessions/test")
                    mock_create.return_value = mock_session

                    # Mock file operations
                    with patch.object(self.coordinator, "_upload_input_file") as mock_upload:
                        mock_upload.return_value = "/remote/test_input.jpg"

                        with patch.object(self.coordinator, "_download_output_files") as mock_download:
                            # Execute
                            exit_code, stdout, stderr = self.coordinator.execute_with_files(command)

                            # Verify results
                            assert exit_code == 0
                            assert stdout == "success"
                            assert stderr == ""

                            # Verify upload was called
                            mock_upload.assert_called_once()

                            # Verify download was called (since exit_code == 0)
                            mock_download.assert_called_once()

                            # Verify command was executed with translated paths
                            assert self.mock_executor.execute.called
        finally:
            # Cleanup test file
            Path(test_file_path).unlink(missing_ok=True)

    def test_execute_with_files_failure(self):
        """Test file coordination with command failure."""
        command = ["tpai", "test_input.jpg", "-o", "test_output.jpg"]

        # Mock executor to return failure
        self.mock_executor.execute.return_value = (1, "", "Processing failed")

        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(b"fake image data")
            test_file_path = temp_file.name

        try:
            # Mock file detection
            with patch.object(self.coordinator, "_detect_files") as mock_detect:
                mock_detect.return_value = ([test_file_path], ["test_output.jpg"])

                # Mock session creation
                with patch.object(self.coordinator, "_create_session") as mock_create:
                    mock_session = RemoteSession(session_id="test", remote_base_dir="/tmp/test/sessions/test")
                    mock_create.return_value = mock_session

                    # Mock file operations
                    with patch.object(self.coordinator, "_upload_input_file") as mock_upload:
                        mock_upload.return_value = "/remote/test_input.jpg"

                        with patch.object(self.coordinator, "_download_output_files") as mock_download:
                            # Execute
                            exit_code, stdout, stderr = self.coordinator.execute_with_files(command)

                            # Verify results show failure
                            assert exit_code == 1
                            assert stderr == "Processing failed"

                            # Verify download was NOT called (since exit_code != 0)
                            mock_download.assert_not_called()
        finally:
            # Cleanup test file
            Path(test_file_path).unlink(missing_ok=True)

    def test_caching_functionality(self):
        """Test file caching mechanism."""

        # Create temporary test file for hashing
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_file.write(b"test content for hashing")
            test_file_path = temp_file.name

        try:
            # Test cache miss
            with patch.object(self.coordinator, "_calculate_hash") as mock_hash:
                mock_hash.return_value = "abc123"

                # Mock executor to return file not found for cache check
                self.mock_executor.execute.return_value = (1, "", "")

                result = self.coordinator._get_cached_path(test_file_path)
                assert result is None

                # Test cache hit
                self.mock_executor.execute.return_value = (0, "", "")

                result = self.coordinator._get_cached_path(test_file_path)
                assert result == "/tmp/test/cache/abc123/test_file.jpg"
        finally:
            # Cleanup test file
            Path(test_file_path).unlink(missing_ok=True)

    def test_coordination_test_method(self):
        """Test the built-in coordination test method."""
        # Mock successful operations
        self.mock_executor.execute.side_effect = [
            (0, "", ""),  # mkdir for session creation
            (0, "", ""),  # echo test
            (0, "test", ""),  # cat test
        ]

        with patch.object(self.coordinator, "_create_session") as mock_create:
            mock_session = RemoteSession(session_id="test", remote_base_dir="/tmp/test/sessions/test")
            mock_create.return_value = mock_session

            result = self.coordinator.test_coordination()

            assert result["session_creation"] is True
            assert result["file_upload"] is True
            assert result["command_execution"] is True
            assert result["cleanup"] is True
            assert result["error"] is None


class TestRemoteSession:
    """Test RemoteSession dataclass."""

    def test_session_initialization(self):
        """Test session creation with defaults."""
        session = RemoteSession(session_id="test123", remote_base_dir="/tmp/test")

        assert session.session_id == "test123"
        assert session.remote_base_dir == "/tmp/test"
        assert session.local_to_remote == {}
        assert session.remote_to_local == {}
        assert isinstance(session.created_at, float)

    def test_session_with_mappings(self):
        """Test session with file mappings."""
        local_to_remote = {"local.jpg": "/remote/local.jpg"}
        remote_to_local = {"/remote/local.jpg": "local.jpg"}

        session = RemoteSession(
            session_id="test123",
            remote_base_dir="/tmp/test",
            local_to_remote=local_to_remote,
            remote_to_local=remote_to_local,
        )

        assert session.local_to_remote == local_to_remote
        assert session.remote_to_local == remote_to_local
