#!/usr/bin/env python3
# this_file: src/topyaz/execution/fabric_remote.py
"""
Enhanced Fabric-based remote command execution with virtual display support.

This module provides SSH-based remote command execution capabilities with
automatic virtual display setup for GUI applications like Topaz products.
"""

import time
from pathlib import Path
from typing import List, Optional

from fabric import Connection, Result
from loguru import logger

from topyaz.core.errors import (
    AuthenticationError,
    RemoteExecutionError,
)
from topyaz.core.types import CommandList, RemoteOptions
from topyaz.execution.base import CommandExecutor, ExecutorContext


class EnhancedRemoteOptions(RemoteOptions):
    """Enhanced remote options with virtual display support."""

    def __init__(self, *args, **kwargs):
        # Extract virtual display options
        self.enable_virtual_display: bool = kwargs.pop("enable_virtual_display", True)
        self.virtual_display_strategy: str = kwargs.pop("virtual_display_strategy", "auto")
        self.xvfb_screen_size: str = kwargs.pop("xvfb_screen_size", "1024x768x24")
        self.force_display_setup: bool = kwargs.pop("force_display_setup", False)

        super().__init__(*args, **kwargs)


class VirtualDisplayManager:
    """Manages virtual display setup for remote GUI applications."""

    # GUI applications that need virtual display
    GUI_APPLICATIONS = {
        "topaz_photo_ai": ["/Applications/Topaz Photo AI.app", "tpai", "Topaz Photo AI"],
        "topaz_gigapixel": ["/Applications/Topaz Gigapixel AI.app", "gigapixel", "Topaz Gigapixel AI"],
        "topaz_video_ai": ["/Applications/Topaz Video AI.app", "Video AI"],
    }

    def __init__(self, connection: Connection, options: EnhancedRemoteOptions):
        self.connection = connection
        self.options = options
        self._remote_platform = None
        self._display_capabilities = None

    def is_gui_application(self, command: CommandList) -> bool:
        """
        Check if the command contains a GUI application.

        Args:
            command: Command to check

        Returns:
            True if command contains GUI application
        """
        command_str = " ".join(command)

        for app_type, patterns in self.GUI_APPLICATIONS.items():
            for pattern in patterns:
                if pattern in command_str:
                    logger.debug(f"Detected GUI application ({app_type}): {pattern}")
                    return True

        return False

    def get_remote_platform(self) -> str:
        """Get the remote platform (darwin, linux, etc.)."""
        if self._remote_platform is None:
            try:
                result = self.connection.run("uname -s", hide=True, timeout=10)
                if result.ok:
                    self._remote_platform = result.stdout.strip().lower()
                else:
                    self._remote_platform = "unknown"
            except Exception as e:
                logger.debug(f"Failed to detect remote platform: {e}")
                self._remote_platform = "unknown"

        return self._remote_platform

    def check_display_capabilities(self) -> dict:
        """Check what display technologies are available on the remote system."""
        if self._display_capabilities is not None:
            return self._display_capabilities

        capabilities = {
            "has_xvfb": False,
            "has_xquartz": False,
            "has_display": False,
            "has_launchctl": False,
            "display_var": None,
        }

        # Check for Xvfb
        try:
            result = self.connection.run("which xvfb-run", hide=True, timeout=5)
            capabilities["has_xvfb"] = result.ok
        except:
            pass

        # Check for XQuartz on macOS
        try:
            result = self.connection.run("ls /Applications/Utilities/XQuartz.app", hide=True, timeout=5)
            capabilities["has_xquartz"] = result.ok
        except:
            pass

        # Check for existing DISPLAY
        try:
            result = self.connection.run("echo $DISPLAY", hide=True, timeout=5)
            if result.ok and result.stdout.strip():
                capabilities["has_display"] = True
                capabilities["display_var"] = result.stdout.strip()
        except:
            pass

        # Check for launchctl (macOS)
        try:
            result = self.connection.run("which launchctl", hide=True, timeout=5)
            capabilities["has_launchctl"] = result.ok
        except:
            pass

        self._display_capabilities = capabilities
        logger.debug(f"Remote display capabilities: {capabilities}")
        return capabilities

    def setup_virtual_display_command(self, command: CommandList) -> CommandList:
        """
        Wrap command with virtual display setup.

        Args:
            command: Original command

        Returns:
            Modified command with virtual display setup
        """
        if not self.options.enable_virtual_display:
            return command

        if not self.is_gui_application(command):
            if not self.options.force_display_setup:
                return command

        platform = self.get_remote_platform()
        capabilities = self.check_display_capabilities()

        strategy = self.options.virtual_display_strategy
        if strategy == "auto":
            strategy = self._choose_best_strategy(platform, capabilities)

        logger.info(f"Setting up virtual display using strategy: {strategy}")

        if strategy == "xvfb":
            return self._setup_xvfb(command, capabilities)
        if strategy == "macos_launchctl":
            return self._setup_macos_launchctl(command)
        if strategy == "macos_env":
            return self._setup_macos_environment(command)
        if strategy == "xquartz":
            return self._setup_xquartz(command)
        logger.warning(f"Unknown virtual display strategy: {strategy}, using original command")
        return command

    def _choose_best_strategy(self, platform: str, capabilities: dict) -> str:
        """Choose the best virtual display strategy for the platform."""
        if platform == "darwin":  # macOS
            if capabilities["has_launchctl"]:
                return "macos_launchctl"
            if capabilities["has_xquartz"]:
                return "xquartz"
            return "macos_env"
        if platform == "linux":
            if capabilities["has_xvfb"]:
                return "xvfb"
            return "linux_env"
        return "fallback"

    def _setup_xvfb(self, command: CommandList, capabilities: dict) -> CommandList:
        """Set up Xvfb virtual framebuffer."""
        if not capabilities["has_xvfb"]:
            logger.warning("xvfb-run not available, falling back to environment setup")
            return self._setup_environment_fallback(command)

        screen_size = self.options.xvfb_screen_size

        # Use xvfb-run with automatic display selection
        xvfb_command = [
            "xvfb-run",
            "-a",  # Automatically choose display number
            "-s",
            f'"-screen 0 {screen_size}"',
            "--",
        ]

        return xvfb_command + command

    def _setup_macos_launchctl(self, command: CommandList) -> CommandList:
        """Set up macOS GUI context with direct execution and error capture."""
        # Simpler approach - run directly with environment but capture errors
        
        # Quote the command properly to handle spaces in paths
        quoted_command = []
        for arg in command:
            if " " in arg or "'" in arg or '"' in arg:
                # Escape quotes and wrap in single quotes
                escaped = arg.replace("'", "'\"'\"'")
                quoted_command.append(f"'{escaped}'")
            else:
                quoted_command.append(arg)
        
        # Build command with environment and error handling
        env_setup = [
            "export DISPLAY=:99",
            "export QT_QPA_PLATFORM=offscreen",
            "export NSUnbufferedIO=YES",
            "export CI=true",
            "export HEADLESS=true", 
            "export NO_GUI=true",
            "export TERM=xterm-256color",
            "export DYLD_LIBRARY_PATH=/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/CoreGraphics.framework/Versions/A:$DYLD_LIBRARY_PATH",
            # macOS specific - try to disable UI interactions
            "export NSUIElement=1",
            "export LSUIElement=1",
        ]
        
        # Run command directly - let Fabric handle timeouts
        # Add error handling to see what's happening
        
        return [
            "bash",
            "-c", 
            f"{'; '.join(env_setup)}; {' '.join(quoted_command)} 2>&1 || echo 'Command failed with exit code: '$?"
        ]

    def _setup_macos_environment(self, command: CommandList) -> CommandList:
        """Set up macOS environment variables for GUI access."""
        # Try setting environment variables that might help
        return [
            "bash",
            "-c",
            f"export DISPLAY=:0; export DYLD_LIBRARY_PATH=/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/CoreGraphics.framework/Versions/A:$DYLD_LIBRARY_PATH; {' '.join(command)}",
        ]

    def _setup_xquartz(self, command: CommandList) -> CommandList:
        """Set up XQuartz for macOS."""
        # Start XQuartz and set DISPLAY
        return [
            "bash",
            "-c",
            f"/Applications/Utilities/XQuartz.app/Contents/MacOS/X11.bin :99 & export DISPLAY=:99; sleep 2; {' '.join(command)}",
        ]

    def _setup_environment_fallback(self, command: CommandList) -> CommandList:
        """Fallback environment setup."""
        # Basic environment variable setup
        env_vars = [
            "export DISPLAY=${DISPLAY:-:0}",
            "export QT_QPA_PLATFORM=${QT_QPA_PLATFORM:-offscreen}",
            "export QT_ASSUME_NO_WINDOWS_WM=1",
        ]

        return ["bash", "-c", f"{'; '.join(env_vars)}; {' '.join(command)}"]


class EnhancedFabricRemoteExecutor(CommandExecutor):
    """
    Enhanced Fabric remote executor with virtual display support.
    """

    def __init__(self, remote_options: EnhancedRemoteOptions, context: ExecutorContext | None = None):
        """
        Initialize enhanced fabric remote executor.

        Args:
            remote_options: Enhanced remote connection configuration
            context: Execution context
        """
        if not remote_options.host:
            msg = "Remote host is required"
            raise RemoteExecutionError(msg)
        if not remote_options.user:
            msg = "Remote user is required"
            raise RemoteExecutionError(msg)

        self.remote_options = remote_options
        self.context = context or ExecutorContext()
        self._connection: Connection | None = None
        self._display_manager: VirtualDisplayManager | None = None

    def is_available(self) -> bool:
        """Check if remote execution is available."""
        try:
            conn = self._create_connection()
            result = conn.run('echo "test"', hide=True, timeout=10)
            conn.close()
            return result.ok
        except Exception as e:
            logger.debug(f"Remote execution not available: {e}")
            return False

    def execute(
        self,
        command: CommandList,
        input_data: str | None = None,
        timeout: int | None = None,
    ) -> tuple[int, str, str]:
        """
        Execute command on remote host with virtual display support.

        Args:
            command: Command and arguments to execute
            input_data: Optional input data to pass to command
            timeout: Optional timeout override

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        actual_timeout = timeout or self.context.timeout

        if self.context.dry_run:
            logger.info(f"DRY RUN (enhanced fabric): {' '.join(command)} on {self.remote_options.host}")
            return 0, "dry-run-output", ""

        try:
            conn = self._get_connection()

            # Set up virtual display manager if not already done
            if self._display_manager is None:
                self._display_manager = VirtualDisplayManager(conn, self.remote_options)

            # Wrap command with virtual display setup if needed
            enhanced_command = self._display_manager.setup_virtual_display_command(command)

            # Build command string
            command_str = self._build_command_string(enhanced_command)
            logger.debug(f"Executing remotely via Enhanced Fabric: {command_str}")

            start_time = time.time()

            # Execute command with Fabric
            result: Result = conn.run(
                command_str,
                hide=True,
                warn=True,
                timeout=actual_timeout,
                in_stream=input_data.encode() if input_data else None,
            )

            execution_time = time.time() - start_time
            logger.debug(f"Remote command completed in {execution_time:.2f}s with exit status: {result.exited}")

            # Log output previews
            if result.stdout:
                stdout_preview = result.stdout[:500]
                if len(result.stdout) > 500:
                    stdout_preview += "..."
                logger.debug(f"Remote STDOUT: {stdout_preview}")

            if result.stderr:
                stderr_preview = result.stderr[:500]
                if len(result.stderr) > 500:
                    stderr_preview += "..."
                logger.debug(f"Remote STDERR: {stderr_preview}")

            return result.exited, result.stdout, result.stderr

        except Exception as e:
            if "authentication" in str(e).lower() or "auth" in str(e).lower():
                msg = f"SSH authentication failed for {self.remote_options.user}@{self.remote_options.host}: {e}"
                logger.error(msg)
                raise AuthenticationError(msg)

            msg = f"Remote command execution failed: {e}"
            logger.error(msg)
            raise RemoteExecutionError(msg)

    def _get_connection(self) -> Connection:
        """Get or create Fabric connection."""
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection

    def _create_connection(self) -> Connection:
        """Create Fabric SSH connection to remote host."""
        try:
            connect_kwargs = {}

            if self.remote_options.ssh_key:
                connect_kwargs["key_filename"] = str(self.remote_options.ssh_key)

            host_string = f"{self.remote_options.user}@{self.remote_options.host}:{self.remote_options.ssh_port}"
            logger.debug(f"Creating Enhanced Fabric connection to {host_string}")

            connection = Connection(
                host=self.remote_options.host,
                user=self.remote_options.user,
                port=self.remote_options.ssh_port,
                connect_timeout=self.remote_options.connection_timeout,
                connect_kwargs=connect_kwargs,
            )

            connection.open()
            logger.debug("Enhanced Fabric SSH connection established")

            return connection

        except Exception as e:
            if "authentication" in str(e).lower():
                msg = f"SSH authentication failed: {e}"
                logger.error(msg)
                raise AuthenticationError(msg)

            msg = f"SSH connection failed: {e}"
            logger.error(msg)
            raise RemoteExecutionError(msg)

    def _build_command_string(self, command: CommandList) -> str:
        """Build properly escaped command string for remote execution."""
        import shlex

        escaped_args = [shlex.quote(arg) for arg in command]
        command_str = " ".join(escaped_args)

        if self.context.env_vars:
            env_prefix = " ".join(f"{key}={shlex.quote(value)}" for key, value in self.context.env_vars.items())
            command_str = f"env {env_prefix} {command_str}"

        if self.context.working_dir:
            command_str = f"cd {shlex.quote(self.context.working_dir)} && {command_str}"

        return command_str

    def test_virtual_display(self) -> dict:
        """Test virtual display setup on remote system."""
        if self._display_manager is None:
            conn = self._get_connection()
            self._display_manager = VirtualDisplayManager(conn, self.remote_options)

        capabilities = self._display_manager.check_display_capabilities()
        platform = self._display_manager.get_remote_platform()

        # Test a simple GUI command
        test_command = ["echo", "Virtual display test"]
        enhanced_command = self._display_manager.setup_virtual_display_command(test_command)

        return {
            "platform": platform,
            "capabilities": capabilities,
            "original_command": test_command,
            "enhanced_command": enhanced_command,
            "strategy": self._display_manager._choose_best_strategy(platform, capabilities),
        }

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """
        Upload file to remote host using Fabric.

        Args:
            local_path: Local file path
            remote_path: Remote file path

        Returns:
            True if successful

        Raises:
            RemoteExecutionError: If upload fails
        """
        try:
            conn = self._get_connection()

            logger.debug(f"Uploading {local_path} to {remote_path}")

            # Ensure remote directory exists
            remote_dir = str(Path(remote_path).parent)
            conn.run(f"mkdir -p {remote_dir}", hide=True)

            # Upload file using Fabric's put method
            result = conn.put(local_path, remote_path)

            logger.debug(f"File upload completed: {result.local} -> {result.remote}")
            return True

        except Exception as e:
            msg = f"File upload failed: {e}"
            logger.error(msg)
            raise RemoteExecutionError(msg)

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Download file from remote host using Fabric.

        Args:
            remote_path: Remote file path
            local_path: Local file path

        Returns:
            True if successful

        Raises:
            RemoteExecutionError: If download fails
        """
        try:
            conn = self._get_connection()

            logger.debug(f"Downloading {remote_path} to {local_path}")

            # Ensure local directory exists
            local_dir = Path(local_path).parent
            local_dir.mkdir(parents=True, exist_ok=True)

            # Download file using Fabric's get method
            result = conn.get(remote_path, local_path)

            logger.debug(f"File download completed: {result.remote} -> {result.local}")
            return True

        except Exception as e:
            msg = f"File download failed: {e}"
            logger.error(msg)
            raise RemoteExecutionError(msg)

    def close(self) -> None:
        """Close the SSH connection."""
        if self._connection:
            try:
                self._connection.close()
                logger.debug("Enhanced Fabric SSH connection closed")
            except Exception as e:
                logger.debug(f"Error closing Enhanced Fabric connection: {e}")
            finally:
                self._connection = None
                self._display_manager = None

    def get_info(self) -> dict[str, str]:
        """Get information about this executor."""
        return {
            "platform": "enhanced-fabric-remote",
            "host": self.remote_options.host,
            "port": str(self.remote_options.ssh_port),
            "user": self.remote_options.user,
            "connected": str(self._connection is not None),
            "ssh_key": str(self.remote_options.ssh_key) if self.remote_options.ssh_key else "password",
            "virtual_display": str(self.remote_options.enable_virtual_display),
            "display_strategy": self.remote_options.virtual_display_strategy,
        }


# Keep the original FabricRemoteExecutor for backward compatibility
class FabricRemoteExecutor(CommandExecutor):
    """
    Executes commands on remote machines via SSH using Fabric.

    Provides secure remote execution with simplified API,
    automatic connection management, and better error handling
    compared to raw paramiko.

    Used in:
    - topyaz/cli.py (as alternative to RemoteExecutor)
    - topyaz/execution/__init__.py
    """

    def __init__(self, remote_options: RemoteOptions, context: ExecutorContext | None = None):
        """
        Initialize fabric remote executor.

        Args:
            remote_options: Remote connection configuration
            context: Execution context

        Raises:
            RemoteExecutionError: If remote options are invalid
        """
        if not remote_options.host:
            msg = "Remote host is required"
            raise RemoteExecutionError(msg)
        if not remote_options.user:
            msg = "Remote user is required"
            raise RemoteExecutionError(msg)

        self.remote_options = remote_options
        self.context = context or ExecutorContext()
        self._connection: Connection | None = None

    def is_available(self) -> bool:
        """Check if remote execution is available."""
        try:
            # Test connection without keeping it open
            conn = self._create_connection()
            result = conn.run('echo "test"', hide=True, timeout=10)
            conn.close()
            return result.ok
        except Exception as e:
            logger.debug(f"Remote execution not available: {e}")
            return False

    def execute(
        self,
        command: CommandList,
        input_data: str | None = None,
        timeout: int | None = None,
    ) -> tuple[int, str, str]:
        """
        Execute command on remote host using Fabric.

        Args:
            command: Command and arguments to execute
            input_data: Optional input data to pass to command
            timeout: Optional timeout override

        Returns:
            Tuple of (return_code, stdout, stderr)

        Raises:
            RemoteExecutionError: If remote execution fails
        """
        actual_timeout = timeout or self.context.timeout

        if self.context.dry_run:
            logger.info(f"DRY RUN (fabric): {' '.join(command)} on {self.remote_options.host}")
            return 0, "dry-run-output", ""

        try:
            conn = self._get_connection()

            # Build command string
            command_str = self._build_command_string(command)
            logger.debug(f"Executing remotely via Fabric: {command_str}")

            start_time = time.time()

            # Execute command with Fabric
            result: Result = conn.run(
                command_str,
                hide=True,  # Don't print output during execution
                warn=True,  # Don't raise on non-zero exit
                timeout=actual_timeout,
                in_stream=input_data.encode() if input_data else None,
            )

            execution_time = time.time() - start_time

            logger.debug(f"Remote command completed in {execution_time:.2f}s with exit status: {result.exited}")

            # Log output previews
            if result.stdout:
                stdout_preview = result.stdout[:500]
                if len(result.stdout) > 500:
                    stdout_preview += "..."
                logger.debug(f"Remote STDOUT: {stdout_preview}")

            if result.stderr:
                stderr_preview = result.stderr[:500]
                if len(result.stderr) > 500:
                    stderr_preview += "..."
                logger.debug(f"Remote STDERR: {stderr_preview}")

            return result.exited, result.stdout, result.stderr

        except Exception as e:
            # Fabric wraps various exceptions, check for authentication issues
            if "authentication" in str(e).lower() or "auth" in str(e).lower():
                msg = f"SSH authentication failed for {self.remote_options.user}@{self.remote_options.host}: {e}"
                logger.error(msg)
                raise AuthenticationError(msg)

            msg = f"Remote command execution failed: {e}"
            logger.error(msg)
            raise RemoteExecutionError(msg)

    def _get_connection(self) -> Connection:
        """Get or create Fabric connection."""
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection

    def _create_connection(self) -> Connection:
        """Create Fabric SSH connection to remote host."""
        try:
            # Build connection arguments
            connect_kwargs = {}

            if self.remote_options.ssh_key:
                connect_kwargs["key_filename"] = str(self.remote_options.ssh_key)

            # Create connection
            host_string = f"{self.remote_options.user}@{self.remote_options.host}:{self.remote_options.ssh_port}"

            logger.debug(f"Creating Fabric connection to {host_string}")

            connection = Connection(
                host=self.remote_options.host,
                user=self.remote_options.user,
                port=self.remote_options.ssh_port,
                connect_timeout=self.remote_options.connection_timeout,
                connect_kwargs=connect_kwargs,
            )

            # Test the connection
            connection.open()
            logger.debug("Fabric SSH connection established")

            return connection

        except Exception as e:
            if "authentication" in str(e).lower():
                msg = f"SSH authentication failed: {e}"
                logger.error(msg)
                raise AuthenticationError(msg)

            msg = f"SSH connection failed: {e}"
            logger.error(msg)
            raise RemoteExecutionError(msg)

    def _build_command_string(self, command: CommandList) -> str:
        """
        Build properly escaped command string for remote execution.

        Args:
            command: Command and arguments

        Returns:
            Escaped command string
        """
        import shlex

        # Use shlex to properly escape arguments
        escaped_args = [shlex.quote(arg) for arg in command]
        command_str = " ".join(escaped_args)

        # Add environment variables if any
        if self.context.env_vars:
            env_prefix = " ".join(f"{key}={shlex.quote(value)}" for key, value in self.context.env_vars.items())
            command_str = f"env {env_prefix} {command_str}"

        # Add working directory if specified
        if self.context.working_dir:
            command_str = f"cd {shlex.quote(self.context.working_dir)} && {command_str}"

        return command_str

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """
        Upload file to remote host using Fabric.

        Args:
            local_path: Local file path
            remote_path: Remote file path

        Returns:
            True if successful

        Raises:
            RemoteExecutionError: If upload fails
        """
        try:
            conn = self._get_connection()

            logger.debug(f"Uploading {local_path} to {remote_path}")

            # Ensure remote directory exists
            remote_dir = str(Path(remote_path).parent)
            conn.run(f"mkdir -p {remote_dir}", hide=True)

            # Upload file using Fabric's put method
            result = conn.put(local_path, remote_path)

            logger.debug(f"File upload completed: {result.local} -> {result.remote}")
            return True

        except Exception as e:
            msg = f"File upload failed: {e}"
            logger.error(msg)
            raise RemoteExecutionError(msg)

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Download file from remote host using Fabric.

        Args:
            remote_path: Remote file path
            local_path: Local file path

        Returns:
            True if successful

        Raises:
            RemoteExecutionError: If download fails
        """
        try:
            conn = self._get_connection()

            logger.debug(f"Downloading {remote_path} to {local_path}")

            # Ensure local directory exists
            local_dir = Path(local_path).parent
            local_dir.mkdir(parents=True, exist_ok=True)

            # Download file using Fabric's get method
            result = conn.get(remote_path, local_path)

            logger.debug(f"File download completed: {result.remote} -> {result.local}")
            return True

        except Exception as e:
            msg = f"File download failed: {e}"
            logger.error(msg)
            raise RemoteExecutionError(msg)

    def test_connection(self) -> dict[str, any]:
        """
        Test remote connection and return diagnostics.

        Returns:
            Dictionary with connection test results
        """
        result = {
            "host": self.remote_options.host,
            "port": self.remote_options.ssh_port,
            "user": self.remote_options.user,
            "connected": False,
            "error": None,
            "latency_ms": None,
            "server_info": {},
        }

        try:
            start_time = time.time()
            conn = self._create_connection()
            connect_time = (time.time() - start_time) * 1000

            result["connected"] = True
            result["latency_ms"] = round(connect_time, 2)

            # Get server information using Fabric
            try:
                uname_result = conn.run("uname -a", hide=True, timeout=10)
                if uname_result.ok:
                    result["server_info"]["uname"] = uname_result.stdout.strip()

                whoami_result = conn.run("whoami", hide=True, timeout=10)
                if whoami_result.ok:
                    result["server_info"]["user"] = whoami_result.stdout.strip()

                pwd_result = conn.run("pwd", hide=True, timeout=10)
                if pwd_result.ok:
                    result["server_info"]["home"] = pwd_result.stdout.strip()

            except Exception as e:
                logger.debug(f"Failed to get server info: {e}")

            conn.close()

        except Exception as e:
            result["error"] = str(e)
            logger.debug(f"Connection test failed: {e}")

        return result

    def get_info(self) -> dict[str, str]:
        """Get information about this executor."""
        return {
            "platform": "fabric-remote",
            "host": self.remote_options.host,
            "port": str(self.remote_options.ssh_port),
            "user": self.remote_options.user,
            "connected": str(self._connection is not None),
            "ssh_key": str(self.remote_options.ssh_key) if self.remote_options.ssh_key else "password",
        }

    def close(self) -> None:
        """Close the SSH connection."""
        if self._connection:
            try:
                self._connection.close()
                logger.debug("Fabric SSH connection closed")
            except Exception as e:
                logger.debug(f"Error closing Fabric connection: {e}")
            finally:
                self._connection = None

    def __del__(self):
        """Cleanup SSH connection on object destruction."""
        self.close()
