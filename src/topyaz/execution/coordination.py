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
from topyaz.execution.base import CommandExecutor


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

    def __init__(self, remote_executor: CommandExecutor, base_dir: str = "/tmp/topyaz"):
        """
        Initialize remote file coordinator.

        Args:
            remote_executor: CommandExecutor instance for SSH operations
            base_dir: Base directory on remote server for sessions
        """
        self.executor = remote_executor
        self.base_dir = base_dir
        self.cache_dir = f"{base_dir}/cache"
        self._remote_system_info = None

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

            # 0. Check remote system compatibility and resources
            self._check_remote_compatibility(command)

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
                # Debug: List what's actually in the remote session directory
                self._debug_remote_session_contents(session)
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
                elif prev_arg in ["-i", "--input", "--cli"] or (not prev_arg.startswith("-") and Path(arg).exists()):
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

        # Handle macOS app bundle executables specially
        if self._is_macos_app_executable(local_path):
            return self._upload_macos_app_bundle(local_path, session)

        # Check cache first
        cached_path = self._get_cached_path(local_path)
        if cached_path:
            # Ensure executable permissions for cached executables
            local_file = Path(local_path)
            if local_file.suffix in [".exe", ""] and "bin" in str(local_file):
                self.executor.execute(["chmod", "+x", cached_path])
                logger.debug(f"Ensured execute permissions on cached executable: {cached_path}")
            logger.debug(f"Using cached file: {cached_path}")
            return cached_path

        # Upload to session inputs directory
        remote_path = f"{session.remote_base_dir}/inputs/{local_file.name}"

        logger.debug(f"Uploading {local_path} to {remote_path}")
        self.executor.upload_file(local_path, remote_path)

        # Ensure executable permissions for executables
        if local_file.suffix in [".exe", ""] and "bin" in str(local_file):
            self.executor.execute(["chmod", "+x", remote_path])
            logger.debug(f"Set execute permissions on uploaded executable: {remote_path}")

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

            # Ensure executable permissions for executables
            local_file = Path(local_path)
            if local_file.suffix in [".exe", ""] and "bin" in str(local_file):
                # This looks like an executable, ensure it has execute permissions
                self.executor.execute(["chmod", "+x", cache_path])
                logger.debug(f"Set execute permissions on cached executable: {cache_path}")

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

                # Check if remote path is a file or directory
                file_exit_code, _, _ = self.executor.execute(["test", "-f", remote_path])
                dir_exit_code, _, _ = self.executor.execute(["test", "-d", remote_path])
                
                if file_exit_code == 0:
                    # It's a file, download directly
                    logger.debug(f"Downloading {remote_path} to {local_path}")

                    # Ensure local directory exists
                    local_dir = Path(local_path).parent
                    local_dir.mkdir(parents=True, exist_ok=True)

                    self.executor.download_file(remote_path, local_path)
                elif dir_exit_code == 0:
                    # It's a directory, find files inside and download them
                    logger.debug(f"Remote path is a directory: {remote_path}")
                    self._download_directory_contents(remote_path, local_path, session)
                else:
                    logger.warning(f"Output file/directory not found on remote: {remote_path}")

    def _download_directory_contents(self, remote_dir: str, local_dir: str, session: RemoteSession) -> None:
        """
        Download all files from a remote directory to a local directory.
        
        Args:
            remote_dir: Remote directory path
            local_dir: Local directory path
            session: Remote session
        """
        try:
            # List files in remote directory
            exit_code, stdout, stderr = self.executor.execute(["find", remote_dir, "-type", "f", "-exec", "basename", "{}", ";"])
            
            if exit_code != 0:
                logger.warning(f"Failed to list files in remote directory {remote_dir}: {stderr}")
                return
                
            files = [f.strip() for f in stdout.strip().split('\n') if f.strip()]
            
            if not files:
                logger.warning(f"No files found in remote directory: {remote_dir}")
                return
                
            logger.debug(f"Found {len(files)} files in remote directory: {files}")
            
            # Ensure local directory exists
            local_path = Path(local_dir)
            local_path.mkdir(parents=True, exist_ok=True)
            
            # Download each file
            for filename in files:
                remote_file = f"{remote_dir}/{filename}"
                local_file = str(local_path / filename)
                
                logger.debug(f"Downloading {remote_file} to {local_file}")
                self.executor.download_file(remote_file, local_file)
                
        except Exception as e:
            logger.error(f"Failed to download directory contents from {remote_dir}: {e}")

    def _debug_remote_session_contents(self, session: RemoteSession) -> None:
        """
        Debug method to list all contents of the remote session directory.
        
        Args:
            session: Remote session to debug
        """
        try:
            logger.debug(f"Debugging remote session contents for {session.session_id}")
            
            # List all contents recursively
            exit_code, stdout, stderr = self.executor.execute(["find", session.remote_base_dir, "-type", "f", "-ls"])
            
            if exit_code == 0:
                if stdout.strip():
                    logger.debug(f"Remote session files:\n{stdout}")
                else:
                    logger.debug("No files found in remote session directory")
            else:
                logger.debug(f"Failed to list remote session contents: {stderr}")
                
            # Also check the outputs directory specifically
            outputs_dir = f"{session.remote_base_dir}/outputs"
            exit_code, stdout, stderr = self.executor.execute(["ls", "-la", outputs_dir])
            
            if exit_code == 0:
                logger.debug(f"Outputs directory contents:\n{stdout}")
            else:
                logger.debug(f"Failed to list outputs directory: {stderr}")
                
        except Exception as e:
            logger.debug(f"Failed to debug remote session contents: {e}")

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

    def _is_macos_app_executable(self, local_path: str) -> bool:
        """
        Check if this is a macOS app bundle executable that needs special handling.

        Args:
            local_path: Path to check

        Returns:
            True if this is a macOS app bundle executable
        """
        path = Path(local_path)
        return path.name == "tpai" and "Topaz Photo AI.app" in str(path) and path.exists()

    def _upload_macos_app_bundle(self, local_path: str, session: RemoteSession) -> str:
        """
        Upload macOS app bundle components needed for execution.

        Args:
            local_path: Path to tpai script
            session: Remote session

        Returns:
            Remote path to executable
        """
        local_file = Path(local_path)

        # Check if we have a cached bundle
        bundle_hash = self._calculate_hash(local_path)
        cached_script = f"{self.cache_dir}/{bundle_hash}/tpai"
        cached_main = f"{self.cache_dir}/{bundle_hash}/Topaz Photo AI"

        # Check if bundle is already cached (including Frameworks)
        wrapper_path = f"{self.cache_dir}/{bundle_hash}/tpai_wrapper"
        cached_frameworks = f"{self.cache_dir}/{bundle_hash}/Frameworks"

        try:
            # Check if basic components exist
            exit_code, _, _ = self.executor.execute(["test", "-f", cached_script, "-a", "-f", cached_main])
            if exit_code == 0:
                # Check if Frameworks directory exists (for full bundle)
                exit_code, _, _ = self.executor.execute(["test", "-d", cached_frameworks])
                frameworks_cached = exit_code == 0

                # If this is a fresh install or Frameworks are missing, don't use cache
                app_bundle_path = local_file.parent.parent.parent
                frameworks_dir = app_bundle_path / "Frameworks"
                frameworks_needed = frameworks_dir.exists()

                if frameworks_needed and not frameworks_cached:
                    logger.debug("Frameworks missing from cache, re-uploading bundle")
                    pass  # Continue to re-upload
                else:
                    # Ensure execute permissions
                    self.executor.execute(["chmod", "+x", cached_script, cached_main])

                    # Check if wrapper exists and is current version
                    version_file = f"{self.cache_dir}/{bundle_hash}/wrapper_v2.1"
                    wrapper_exists = self.executor.execute(["test", "-f", wrapper_path])[0] == 0
                    version_current = self.executor.execute(["test", "-f", version_file])[0] == 0
                    
                    if not wrapper_exists or not version_current:
                        logger.debug("Wrapper missing or outdated, regenerating it")
                        self._create_wrapper_script(f"{self.cache_dir}/{bundle_hash}", wrapper_path)
                        # Mark wrapper version
                        self.executor.execute(["touch", version_file])
                    else:
                        self.executor.execute(["chmod", "+x", wrapper_path])

                    logger.debug(f"Using cached Photo AI bundle: {wrapper_path}")
                    return wrapper_path
        except Exception:
            pass

        # Upload the bundle components
        app_bundle_path = local_file.parent.parent.parent  # Go up from bin/tpai to .app
        main_executable = app_bundle_path / "MacOS" / "Topaz Photo AI"
        frameworks_dir = app_bundle_path / "Frameworks"

        if not main_executable.exists():
            logger.error(f"Main Photo AI executable not found at {main_executable}")
            # Fall back to uploading just the script
            return self._upload_simple_file(local_path, session)

        # Create cache directory structure
        cache_base = f"{self.cache_dir}/{bundle_hash}"
        self.executor.execute(["mkdir", "-p", cache_base])

        # Upload bundle components
        logger.debug(f"Uploading Photo AI app bundle to {cache_base}")

        # Upload tpai script
        self.executor.upload_file(str(local_file), cached_script)
        self.executor.execute(["chmod", "+x", cached_script])

        # Upload main executable
        self.executor.upload_file(str(main_executable), cached_main)
        self.executor.execute(["chmod", "+x", cached_main])

        # Upload Frameworks directory if it exists
        if frameworks_dir.exists():
            logger.debug(f"Uploading Frameworks directory from {frameworks_dir}")
            # Create remote Frameworks directory
            remote_frameworks = f"{cache_base}/Frameworks"
            self.executor.execute(["mkdir", "-p", remote_frameworks])

            # Upload all frameworks (this might take a while)
            self._upload_directory_recursive(frameworks_dir, remote_frameworks)
        else:
            logger.warning(f"Frameworks directory not found at {frameworks_dir}")

        # Create wrapper script
        wrapper_path = f"{cache_base}/tpai_wrapper"
        self._create_wrapper_script(cache_base, wrapper_path)
        
        # Mark wrapper version
        version_file = f"{cache_base}/wrapper_v2.1"
        self.executor.execute(["touch", version_file])

        logger.debug(f"Created Photo AI wrapper at {wrapper_path}")
        return wrapper_path

    def _upload_simple_file(self, local_path: str, session: RemoteSession) -> str:
        """
        Upload a single file (fallback method).

        Args:
            local_path: Local file path
            session: Remote session

        Returns:
            Remote file path
        """
        local_file = Path(local_path)
        remote_path = f"{session.remote_base_dir}/inputs/{local_file.name}"

        logger.debug(f"Uploading {local_path} to {remote_path}")
        self.executor.upload_file(local_path, remote_path)

        if local_file.suffix in [".exe", ""] and "bin" in str(local_file):
            self.executor.execute(["chmod", "+x", remote_path])

        return remote_path

    def _create_wrapper_script(self, cache_base: str, wrapper_path: str) -> None:
        """
        Create a wrapper script that sets up the correct directory structure for Photo AI.

        Args:
            cache_base: Base cache directory
            wrapper_path: Path where wrapper should be created
        """
        # Create a wrapper script that tries to run tpai with minimal GUI requirements
        # Version 2.1 - with better error detection
        wrapper_content = f'''#!/bin/bash
cd "{cache_base}"

# Set up headless environment for Photo AI
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:99
export CI=true
export HEADLESS=true
export NO_GUI=true

# Try to run tpai directly first (CLI mode)
if [[ "$@" == *"--cli"* ]]; then
    # CLI mode - try to run tpai binary directly without app bundle
    echo "Running in CLI mode with minimal setup" >&2
    
    # Check if we can even run the binary
    if ! ./tpai --help >/dev/null 2>&1; then
        echo "ERROR: Unable to run tpai binary. This usually means Photo AI requires an active GUI session." >&2
        echo "Photo AI cannot run on remote machines without an active desktop session." >&2
        exit 1
    fi
    
    # Try to run the actual command
    exec ./tpai "$@" 2>&1
else
    # Non-CLI mode - set up full app structure
    echo "Running in GUI mode with full app structure" >&2
    mkdir -p Resources/bin MacOS
    ln -sf "../Topaz Photo AI" MacOS/"Topaz Photo AI"
    cd Resources/bin
    ln -sf ../../tpai .
    exec ./tpai "$@" 2>&1
fi
'''

        # Create wrapper script on remote
        self.executor.execute(["bash", "-c", f"cat > {wrapper_path} << 'WRAPPER_EOF'\n{wrapper_content}WRAPPER_EOF"])
        self.executor.execute(["chmod", "+x", wrapper_path])

    def _upload_directory_recursive(self, local_dir: Path, remote_dir: str) -> None:
        """
        Upload a directory and all its contents recursively.

        Args:
            local_dir: Local directory to upload
            remote_dir: Remote directory path
        """
        try:
            logger.debug(f"Uploading directory {local_dir} to {remote_dir}")

            # Use rsync for efficient directory transfer if available, otherwise fall back to scp
            local_dir_str = str(local_dir).rstrip("/") + "/"
            remote_dir_str = remote_dir.rstrip("/") + "/"

            # Try rsync first (more efficient) - but only if executor has remote_options
            try:
                if hasattr(self.executor, "remote_options"):
                    import subprocess

                    result = subprocess.run(
                        [
                            "rsync",
                            "-avz",
                            "--delete",
                            "-e",
                            f"ssh -p {self.executor.remote_options.ssh_port}",
                            local_dir_str,
                            f"{self.executor.remote_options.user}@{self.executor.remote_options.host}:{remote_dir_str}",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=300,
                        check=False,
                    )

                    if result.returncode == 0:
                        logger.debug(f"Successfully uploaded {local_dir} via rsync")
                        return
                    logger.debug(f"rsync failed, falling back to manual upload: {result.stderr}")
                else:
                    logger.debug("Executor doesn't support rsync, using manual upload")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.debug("rsync not available or timed out, using manual upload")

            # Fallback: manual recursive upload
            self._manual_directory_upload(local_dir, remote_dir)

        except Exception as e:
            logger.error(f"Failed to upload directory {local_dir}: {e}")
            raise

    def _manual_directory_upload(self, local_dir: Path, remote_dir: str) -> None:
        """
        Manually upload directory contents file by file.

        Args:
            local_dir: Local directory to upload
            remote_dir: Remote directory path
        """
        for item in local_dir.rglob("*"):
            if item.is_file():
                # Calculate relative path
                rel_path = item.relative_to(local_dir)
                remote_file = f"{remote_dir}/{rel_path}"

                # Create remote directory if needed
                remote_parent = "/".join(remote_file.split("/")[:-1])
                self.executor.execute(["mkdir", "-p", remote_parent])

                # Upload file
                logger.debug(f"Uploading {item} to {remote_file}")
                self.executor.upload_file(str(item), remote_file)

                # Set execute permissions for executables
                if item.suffix in [".dylib", ".so"] or "bin" in str(item) or item.stat().st_mode & 0o111:
                    self.executor.execute(["chmod", "+x", remote_file])

    def _check_remote_compatibility(self, command: CommandList) -> None:
        """
        Check if the remote system can execute this command.

        Args:
            command: Command to be executed

        Raises:
            RemoteExecutionError: If remote system is incompatible
        """
        # Get remote system info if not cached
        if self._remote_system_info is None:
            self._remote_system_info = self._get_remote_system_info()

        # Check if trying to run macOS app bundle on non-macOS system
        if self._is_macos_app_in_command(command):
            remote_os = self._remote_system_info.get("os", "").lower()
            if "darwin" not in remote_os and "macos" not in remote_os:
                msg = f"Cannot run macOS app bundle on remote {remote_os} system"
                logger.error(msg)
                raise RemoteExecutionError(msg)

        # Check available memory
        remote_memory_gb = self._remote_system_info.get("memory_gb", 0)
        if remote_memory_gb < 8:  # Topaz AI needs substantial memory
            logger.warning(
                f"Remote system has only {remote_memory_gb:.1f}GB memory. Topaz AI processing may fail or be killed."
            )

        if remote_memory_gb < 4:  # Very low memory
            msg = f"Insufficient remote memory: {remote_memory_gb:.1f}GB available, 4GB+ recommended"
            logger.error(msg)
            raise RemoteExecutionError(msg)

    def _get_remote_system_info(self) -> dict[str, Any]:
        """
        Get remote system information for compatibility checking.

        Returns:
            Dictionary with remote system info
        """
        info = {}

        try:
            # Get OS information
            exit_code, stdout, _ = self.executor.execute(["uname", "-s"])
            if exit_code == 0:
                info["os"] = stdout.strip()

            # Get memory information (in MB)
            exit_code, stdout, _ = self.executor.execute(["free", "-m"])
            if exit_code == 0:
                # Parse free output
                lines = stdout.strip().split("\n")
                if len(lines) > 1:
                    # Look for the line with actual memory info
                    mem_line = lines[1]
                    parts = mem_line.split()
                    if len(parts) >= 2:
                        total_mb = int(parts[1])
                        info["memory_gb"] = total_mb / 1024

            # Fallback memory check for macOS
            if "memory_gb" not in info:
                exit_code, stdout, _ = self.executor.execute(["sysctl", "-n", "hw.memsize"])
                if exit_code == 0:
                    try:
                        memory_bytes = int(stdout.strip())
                        info["memory_gb"] = memory_bytes / (1024**3)
                    except ValueError:
                        pass

            # Get available disk space
            exit_code, stdout, _ = self.executor.execute(["df", "-h", "/tmp"])
            if exit_code == 0:
                lines = stdout.strip().split("\n")
                if len(lines) > 1:
                    # Parse df output for available space
                    parts = lines[1].split()
                    if len(parts) >= 4:
                        info["available_space"] = parts[3]

            logger.debug(f"Remote system info: {info}")

        except Exception as e:
            logger.warning(f"Failed to get complete remote system info: {e}")

        return info

    def _is_macos_app_in_command(self, command: CommandList) -> bool:
        """
        Check if the command contains macOS app bundle executables.

        Args:
            command: Command to check

        Returns:
            True if command contains macOS app references
        """
        for arg in command:
            if isinstance(arg, str):
                if ".app" in arg or "tpai" in arg or "Topaz Photo AI" in arg or "Gigapixel" in arg or "Video AI" in arg:
                    return True
        return False
