#!/usr/bin/env python3
# this_file: src/topyaz/execution/coordination.py
"""
Remote file coordination for topyaz.

This module provides transparent file coordination for remote execution,
handling upload, path translation, execution, and download automatically.
"""

import hashlib
import shlex
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger

from topyaz.core.errors import RemoteExecutionError
from topyaz.core.types import CommandList
from topyaz.execution.remote import RemoteExecutor


@dataclass
class RemoteSession:
    """Represents a remote processing session with file mappings."""

    session_id: str
    remote_base_dir: str
    local_to_remote: dict[str, str] = field(default_factory=dict)  # Local path → Remote path
    remote_to_local: dict[str, str] = field(default_factory=dict)  # Remote path → Local path
    created_at: float = field(default_factory=time.time)


class RemoteFileCoordinator:
    """
    Coordinates file transfers and path translation for remote execution.

    Provides transparent file coordination that handles:
    - Uploading input files to remote server
    - Translating local paths to remote paths in commands
    - Executing commands on remote server
    - Downloading output files back to local system
    - Cleaning up remote session files

    Used in:
    - topyaz/products/base.py
    """

    def __init__(self, remote_executor: RemoteExecutor, base_dir: str = "/tmp/topyaz"):
        """
        Initialize remote file coordinator.

        Args:
            remote_executor: RemoteExecutor instance for SSH operations
            base_dir: Base directory on remote server for sessions
        """
        self.executor = remote_executor
        self.base_dir = base_dir
        self.cache_dir = f"{base_dir}/cache"

    def execute_with_files(self, command: CommandList) -> tuple[int, str, str]:
        """
        Execute command with automatic file coordination.

        Args:
            command: Command and arguments to execute

        Returns:
            Tuple of (return_code, stdout, stderr)

        Raises:
            RemoteExecutionError: If coordination fails
        """
        session = self._create_session()
        try:
            logger.debug(f"Starting remote session {session.session_id}")

            # 1. Detect files in command
            input_files, output_files = self._detect_files(command)
            logger.debug(f"Detected {len(input_files)} input files, {len(output_files)} output files")

            # 2. Upload input files with caching
            for local_path in input_files:
                remote_path = self._upload_input_file(local_path, session)
                session.local_to_remote[local_path] = remote_path
                session.remote_to_local[remote_path] = local_path

            # 3. Map output files (no upload needed)
            for local_path in output_files:
                remote_path = f"{session.remote_base_dir}/outputs/{Path(local_path).name}"
                session.local_to_remote[local_path] = remote_path
                session.remote_to_local[remote_path] = local_path

            # 4. Translate command paths
            translated_command = self._translate_command(command, session.local_to_remote)
            logger.debug(f"Translated command: {' '.join(translated_command)}")

            # 5. Execute on remote
            exit_code, stdout, stderr = self.executor.execute(translated_command)
            logger.debug(f"Remote execution completed with exit code: {exit_code}")

            # 6. Download output files if successful
            if exit_code == 0:
                self._download_output_files(output_files, session)
            else:
                logger.warning("Remote execution failed, skipping output download")

            return exit_code, stdout, stderr

        except Exception as e:
            logger.error(f"Remote coordination failed: {e}")
            msg = f"Remote coordination failed: {e}"
            raise RemoteExecutionError(msg)
        finally:
            self._cleanup_session(session)

    def _create_session(self) -> RemoteSession:
        """Create unique remote session directory."""
        session_id = f"topyaz_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        remote_dir = f"{self.base_dir}/sessions/{session_id}"

        # Create session directory structure on remote
        self.executor.execute(["mkdir", "-p", f"{remote_dir}/inputs", f"{remote_dir}/outputs"])

        logger.debug(f"Created remote session directory: {remote_dir}")

        return RemoteSession(
            session_id=session_id,
            remote_base_dir=remote_dir,
        )

    def _detect_files(self, command: CommandList) -> tuple[list[str], list[str]]:
        """
        Detect input and output files in command arguments.

        Args:
            command: Command and arguments

        Returns:
            Tuple of (input_files, output_files)
        """
        input_files = []
        output_files = []

        for i, arg in enumerate(command):
            if self._is_file_path(arg):
                prev_arg = command[i - 1] if i > 0 else ""

                # Output file detection
                if prev_arg in ["-o", "--output"]:
                    output_files.append(arg)
                # Input file detection (positional or after input flags)
                elif prev_arg in ["-i", "--input"] or (not prev_arg.startswith("-") and Path(arg).exists()):
                    input_files.append(arg)

        return input_files, output_files

    def _is_file_path(self, arg: str) -> bool:
        """
        Check if argument looks like a file path.

        Args:
            arg: Command argument to check

        Returns:
            True if argument appears to be a file path
        """
        # Skip obvious non-paths
        if arg.startswith("-") or len(arg) < 2:
            return False

        # Check if it's a valid path format
        try:
            path = Path(arg)
            # Must have extension or exist as path
            return bool(path.suffix) or path.exists()
        except (OSError, ValueError):
            return False

    def _upload_input_file(self, local_path: str, session: RemoteSession) -> str:
        """
        Upload input file to remote session, with caching support.

        Args:
            local_path: Local file path
            session: Remote session

        Returns:
            Remote file path
        """
        local_file = Path(local_path)

        # Check cache first
        cached_path = self._get_cached_path(local_path)
        if cached_path:
            logger.debug(f"Using cached file: {cached_path}")
            return cached_path

        # Upload to session inputs directory
        remote_path = f"{session.remote_base_dir}/inputs/{local_file.name}"

        logger.debug(f"Uploading {local_path} to {remote_path}")
        self.executor.upload_file(local_path, remote_path)

        # Cache file for future use
        self._cache_file(local_path, remote_path)

        return remote_path

    def _get_cached_path(self, local_path: str) -> str | None:
        """
        Check if file already exists in cache.

        Args:
            local_path: Local file path

        Returns:
            Cached remote path if available, None otherwise
        """
        try:
            file_hash = self._calculate_hash(local_path)
            cached_path = f"{self.cache_dir}/{file_hash}/{Path(local_path).name}"

            # Check if cached file exists on remote
            exit_code, _, _ = self.executor.execute(["test", "-f", cached_path])
            return cached_path if exit_code == 0 else None

        except Exception as e:
            logger.debug(f"Cache check failed for {local_path}: {e}")
            return None

    def _cache_file(self, local_path: str, remote_path: str) -> None:
        """
        Cache uploaded file for future use.

        Args:
            local_path: Local file path
            remote_path: Remote file path
        """
        try:
            file_hash = self._calculate_hash(local_path)
            cache_path = f"{self.cache_dir}/{file_hash}/{Path(local_path).name}"

            # Create cache directory and copy file
            self.executor.execute(["mkdir", "-p", f"{self.cache_dir}/{file_hash}"])
            self.executor.execute(["cp", remote_path, cache_path])

            logger.debug(f"Cached file at {cache_path}")

        except Exception as e:
            logger.debug(f"Failed to cache file {local_path}: {e}")

    def _calculate_hash(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file for caching.

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash string
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def _translate_command(self, command: CommandList, path_mapping: dict[str, str]) -> CommandList:
        """
        Replace local paths with remote equivalents in command.

        Args:
            command: Original command with local paths
            path_mapping: Mapping from local to remote paths

        Returns:
            Command with translated paths
        """
        translated = []

        for arg in command:
            # Check if argument is a path that needs translation
            if arg in path_mapping:
                translated.append(path_mapping[arg])
            else:
                # Handle partial path matches for complex arguments
                translated_arg = self._translate_partial_paths(arg, path_mapping)
                translated.append(translated_arg)

        return translated

    def _translate_partial_paths(self, arg: str, mapping: dict[str, str]) -> str:
        """
        Handle arguments that contain paths as substrings.

        Args:
            arg: Command argument
            mapping: Path mapping dictionary

        Returns:
            Argument with translated paths
        """
        result = arg

        # Sort by path length (longest first) to avoid partial replacements
        for local_path, remote_path in sorted(mapping.items(), key=lambda x: len(str(x[0])), reverse=True):
            result = result.replace(str(local_path), str(remote_path))

        return result

    def _download_output_files(self, output_files: list[str], session: RemoteSession) -> None:
        """
        Download output files from remote session to local paths.

        Args:
            output_files: List of local output file paths
            session: Remote session
        """
        for local_path in output_files:
            if local_path in session.local_to_remote:
                remote_path = session.local_to_remote[local_path]

                # Check if remote file exists before downloading
                exit_code, _, _ = self.executor.execute(["test", "-f", remote_path])
                if exit_code == 0:
                    logger.debug(f"Downloading {remote_path} to {local_path}")

                    # Ensure local directory exists
                    local_dir = Path(local_path).parent
                    local_dir.mkdir(parents=True, exist_ok=True)

                    self.executor.download_file(remote_path, local_path)
                else:
                    logger.warning(f"Output file not found on remote: {remote_path}")

    def _cleanup_session(self, session: RemoteSession) -> None:
        """
        Clean up remote session files.

        Args:
            session: Remote session to cleanup
        """
        try:
            logger.debug(f"Cleaning up remote session {session.session_id}")
            self.executor.execute(["rm", "-rf", session.remote_base_dir])
        except Exception as e:
            logger.warning(f"Failed to cleanup session {session.session_id}: {e}")

    def test_coordination(self) -> dict[str, Any]:
        """
        Test remote coordination capabilities.

        Returns:
            Dictionary with test results
        """
        result = {
            "session_creation": False,
            "file_upload": False,
            "command_execution": False,
            "cleanup": False,
            "error": None,
        }

        try:
            # Test session creation
            session = self._create_session()
            result["session_creation"] = True

            # Test basic file operations
            exit_code, _, _ = self.executor.execute(["echo", "test", ">", f"{session.remote_base_dir}/test.txt"])
            result["file_upload"] = exit_code == 0

            # Test command execution
            exit_code, _, _ = self.executor.execute(["cat", f"{session.remote_base_dir}/test.txt"])
            result["command_execution"] = exit_code == 0

            # Test cleanup
            self._cleanup_session(session)
            result["cleanup"] = True

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Coordination test failed: {e}")

        return result
