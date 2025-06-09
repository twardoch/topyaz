#!/usr/bin/env python3
# this_file: src/topyaz/execution/remote.py
"""
Remote command execution for topyaz via SSH.

This module provides SSH-based remote command execution capabilities with
support for authentication, file transfer, and connection management.

"""

import time

import paramiko
from loguru import logger

from topyaz.core.errors import (
    AuthenticationError,
    RemoteExecutionError,
)
from topyaz.core.types import CommandList, RemoteOptions
from topyaz.execution.base import CommandExecutor, ExecutorContext


class RemoteExecutor(CommandExecutor):
    """
    Executes commands on remote machines via SSH.

    Provides secure remote execution with authentication,
    connection management, and error handling.

    Used in:
    - topyaz/cli.py
    - topyaz/execution/__init__.py
    """

    def __init__(self, remote_options: RemoteOptions, context: ExecutorContext | None = None):
        """
        Initialize remote _executor.

        Args:
            remote_options: Remote connection configuration
            context: Execution context

        Raises:
            RemoteExecutionError: If remote _options are invalid

        """
        if not remote_options.host:
            msg = "Remote host is required"
            raise RemoteExecutionError(msg)
        if not remote_options.user:
            msg = "Remote user is required"
            raise RemoteExecutionError(msg)

        self.remote_options = remote_options
        self.context = context or ExecutorContext()
        self._ssh_client: paramiko.SSHClient | None = None
        self._connected = False

    def is_available(self) -> bool:
        """Check if remote execution is available."""
        try:
            # Test connection without keeping it open
            self._create_connection()
            self._close_connection()
            return True
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
        Execute command on remote host.

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
            logger.info(f"DRY RUN (remote): {' '.join(command)} on {self.remote_options.host}")
            return 0, "dry-run-output", ""

        try:
            self._ensure_connection()

            # Build command string with proper escaping
            command_str = self._build_command_string(command)
            logger.debug(f"Executing remotely: {command_str}")

            # Execute command
            start_time = time.time()
            stdin, stdout, stderr = self._ssh_client.exec_command(command_str, timeout=actual_timeout)

            # Send input if provided
            if input_data:
                try:
                    stdin.write(input_data)
                    stdin.flush()
                except Exception as e:
                    logger.debug(f"Failed to send input: {e}")

            stdin.close()

            # Get results
            exit_status = stdout.channel.recv_exit_status()
            stdout_data = stdout.read().decode("utf-8", errors="ignore")
            stderr_data = stderr.read().decode("utf-8", errors="ignore")

            execution_time = time.time() - start_time

            logger.debug(f"Remote command completed in {execution_time:.2f}s with exit status: {exit_status}")

            if stdout_data:
                stdout_preview = stdout_data[:500]
                if len(stdout_data) > 500:
                    stdout_preview += "..."
                logger.debug(f"Remote STDOUT: {stdout_preview}")
            if stderr_data:
                stderr_preview = stderr_data[:500]
                if len(stderr_data) > 500:
                    stderr_preview += "..."
                logger.debug(f"Remote STDERR: {stderr_preview}")

            return exit_status, stdout_data, stderr_data

        except paramiko.AuthenticationException as e:
            msg = f"SSH authentication failed for {self.remote_options.user}@{self.remote_options.host}: {e}"
            logger.error(msg)
            raise AuthenticationError(msg)

        except paramiko.SSHException as e:
            msg = f"SSH connection error: {e}"
            logger.error(msg)
            raise RemoteExecutionError(msg)

        except Exception as e:
            msg = f"Remote command execution failed: {e}"
            logger.error(msg)
            raise RemoteExecutionError(msg)

    def _ensure_connection(self) -> None:
        """Ensure SSH connection is established."""
        if not self._connected or self._ssh_client is None:
            self._create_connection()

    def _create_connection(self) -> None:
        """Create SSH connection to remote host."""
        try:
            # Create SSH client
            self._ssh_client = paramiko.SSHClient()
            self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Prepare connection arguments
            connect_kwargs = {
                "hostname": self.remote_options.host,
                "username": self.remote_options.user,
                "port": self.remote_options.ssh_port,
                "timeout": self.remote_options.connection_timeout,
            }

            # Add authentication
            if self.remote_options.ssh_key:
                connect_kwargs["key_filename"] = str(self.remote_options.ssh_key)

            logger.debug(
                f"Connecting to {self.remote_options.user}@{self.remote_options.host}:{self.remote_options.ssh_port}"
            )

            # Connect
            self._ssh_client.connect(**connect_kwargs)
            self._connected = True

            logger.debug("SSH connection established")

        except paramiko.AuthenticationException as e:
            msg = f"SSH authentication failed: {e}"
            logger.error(msg)
            raise AuthenticationError(msg)

        except Exception as e:
            msg = f"SSH connection failed: {e}"
            logger.error(msg)
            raise RemoteExecutionError(msg)

    def _close_connection(self) -> None:
        """Close SSH connection."""
        if self._ssh_client:
            try:
                self._ssh_client.close()
                logger.debug("SSH connection closed")
            except Exception as e:
                logger.debug(f"Error closing SSH connection: {e}")
            finally:
                self._ssh_client = None
                self._connected = False

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

        # Join with spaces
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
        Upload file to remote host.

        Args:
            local_path: Local file path
            remote_path: Remote file path

        Returns:
            True if successful

        Raises:
            RemoteExecutionError: If upload fails

        """
        try:
            self._ensure_connection()

            # Use SFTP for file transfer
            sftp = self._ssh_client.open_sftp()

            logger.debug(f"Uploading {local_path} to {remote_path}")
            sftp.put(local_path, remote_path)
            sftp.close()

            logger.debug("File upload completed")
            return True

        except Exception as e:
            msg = f"File upload failed: {e}"
            logger.error(msg)
            raise RemoteExecutionError(msg)

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Download file from remote host.

        Args:
            remote_path: Remote file path
            local_path: Local file path

        Returns:
            True if successful

        Raises:
            RemoteExecutionError: If download fails

        """
        try:
            self._ensure_connection()

            # Use SFTP for file transfer
            sftp = self._ssh_client.open_sftp()

            logger.debug(f"Downloading {remote_path} to {local_path}")
            sftp.get(remote_path, local_path)
            sftp.close()

            logger.debug("File download completed")
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
            self._create_connection()
            connect_time = (time.time() - start_time) * 1000

            result["connected"] = True
            result["latency_ms"] = round(connect_time, 2)

            # Get server information
            try:
                _, stdout, _ = self._ssh_client.exec_command("uname -a", timeout=10)
                result["server_info"]["uname"] = stdout.read().decode().strip()

                _, stdout, _ = self._ssh_client.exec_command("whoami", timeout=10)
                result["server_info"]["user"] = stdout.read().decode().strip()

                _, stdout, _ = self._ssh_client.exec_command("pwd", timeout=10)
                result["server_info"]["home"] = stdout.read().decode().strip()

            except Exception as e:
                logger.debug(f"Failed to get server info: {e}")

            self._close_connection()

        except Exception as e:
            result["error"] = str(e)
            logger.debug(f"Connection test failed: {e}")

        return result

    def get_info(self) -> dict[str, str]:
        """Get information about this _executor.

        Used in:
        - topyaz/cli.py
        - topyaz/execution/local.py
        """
        info = super().get_info()
        info.update(
            {
                "platform": "remote",
                "host": self.remote_options.host,
                "port": str(self.remote_options.ssh_port),
                "user": self.remote_options.user,
                "connected": str(self._connected),
                "ssh_key": str(self.remote_options.ssh_key) if self.remote_options.ssh_key else "password",
            }
        )
        return info

    def __del__(self):
        """Cleanup SSH connection on object destruction."""
        if hasattr(self, "_ssh_client"):
            self._close_connection()


class RemoteConnectionPool:
    """
    Manages a pool of SSH connections for reuse.

    This can improve performance when executing multiple commands
    on the same remote host.

    Used in:
    - topyaz/execution/__init__.py
    """

    def __init__(self, max_connections: int = 5):
        """
        Initialize connection pool.

        Args:
            max_connections: Maximum number of connections to maintain

        """
        self.max_connections = max_connections
        self._connections: dict[str, list[RemoteExecutor]] = {}
        self._in_use: set[RemoteExecutor] = set()

    def get_executor(self, remote_options: RemoteOptions) -> RemoteExecutor:
        """
        Get an _executor from the pool or create a new one.

        Args:
            remote_options: Remote connection _options

        Returns:
            RemoteExecutor instance

        """
        key = self._get_connection_key(remote_options)

        # Try to get from pool
        if self._connections.get(key):
            executor = self._connections[key].pop()
            self._in_use.add(executor)
            return executor

        # Create new _executor
        executor = RemoteExecutor(remote_options)
        self._in_use.add(executor)
        return executor

    def return_executor(self, executor: RemoteExecutor) -> None:
        """
        Return an _executor to the pool.

        Args:
            executor: Executor to return

        """
        if executor not in self._in_use:
            return

        self._in_use.remove(executor)

        key = self._get_connection_key(executor.remote_options)

        if key not in self._connections:
            self._connections[key] = []

        # Only keep if under limit
        if len(self._connections[key]) < self.max_connections:
            self._connections[key].append(executor)
        else:
            # Close excess connections
            executor._close_connection()

    def _get_connection_key(self, remote_options: RemoteOptions) -> str:
        """Get unique key for connection."""
        return f"{remote_options.user}@{remote_options.host}:{remote_options.ssh_port}"

    def close_all(self) -> None:
        """Close all connections in the pool."""
        for executors in self._connections.values():
            for executor in executors:
                executor._close_connection()

        for executor in self._in_use:
            executor._close_connection()

        self._connections.clear()
        self._in_use.clear()


# Global connection pool instance
_connection_pool = RemoteConnectionPool()


def get_remote_executor(remote_options: RemoteOptions) -> RemoteExecutor:
    """
    Get a remote _executor from the global connection pool.

    Args:
        remote_options: Remote connection _options

    Returns:
        RemoteExecutor instance

    Used in:
    - topyaz/execution/__init__.py
    """
    return _connection_pool.get_executor(remote_options)


def return_remote_executor(executor: RemoteExecutor) -> None:
    """
    Return a remote _executor to the global connection pool.

    Args:
        executor: Executor to return

    Used in:
    - topyaz/execution/__init__.py
    """
    _connection_pool.return_executor(executor)
