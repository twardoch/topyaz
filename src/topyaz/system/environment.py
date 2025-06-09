#!/usr/bin/env python3
# this_file: src/topyaz/system/environment.py
"""
Environment validation for topyaz.

This module validates system environment requirements including OS version,
available memory, disk space, and other system prerequisites.

"""

import platform
import shutil
from pathlib import Path
from typing import Any

import psutil
from loguru import logger

from topyaz.core.errors import EnvironmentError
from topyaz.core.types import SystemRequirements


class EnvironmentValidator:
    """
    Validates system environment and requirements.

    Performs checks for:
    - Operating system compatibility
    - Memory availability
    - Disk space requirements
    - Required executables
    - System dependencies

    Used in:
    - topyaz/cli.py
    - topyaz/system/__init__.py
    """

    def __init__(self, requirements: SystemRequirements | None = None):
        """
        Initialize environment validator.

        Args:
            requirements: System requirements to validate against.
                         Uses defaults if not provided.

        """
        self.requirements = requirements or SystemRequirements()
        self._validation_results = {}

    def validate_all(self, raise_on_error: bool = True) -> dict[str, bool]:
        """
        Perform all environment validations.

        Args:
            raise_on_error: Raise exception on validation failure

        Returns:
            Dictionary of validation results

        Raises:
            EnvironmentError: If validation fails and raise_on_error is True

        Used in:
        - topyaz/cli.py
        """
        self._validation_results = {
            "os_version": self.validate_os_version(raise_on_error=False),
            "memory": self.validate_memory(raise_on_error=False),
            "disk_space": self.validate_disk_space(raise_on_error=False),
            "gpu": self.validate_gpu_availability(raise_on_error=False),
        }

        all_valid = all(self._validation_results.values())

        if not all_valid and raise_on_error:
            failed = [k for k, v in self._validation_results.items() if not v]
            msg = f"Environment validation failed: {', '.join(failed)}"
            raise OSError(msg)

        return self._validation_results

    def validate_os_version(self, raise_on_error: bool = True) -> bool:
        """
        Validate operating system version.

        Args:
            raise_on_error: Raise exception on validation failure

        Returns:
            True if OS version is compatible

        Raises:
            EnvironmentError: If OS version is incompatible and raise_on_error is True

        """
        system = platform.system()

        if system == "Darwin":  # macOS
            return self._validate_macos_version(raise_on_error)
        if system == "Windows":
            return self._validate_windows_version(raise_on_error)
        if raise_on_error:
            msg = f"Unsupported operating system: {system}"
            raise OSError(msg)
        logger.warning(f"Unsupported operating system: {system}")
        return False

    def _validate_macos_version(self, raise_on_error: bool) -> bool:
        """Validate macOS version."""
        try:
            version_str = platform.mac_ver()[0]
            if not version_str:
                logger.warning("Could not determine macOS version")
                return True  # Assume compatible if can't determine

            # Parse version
            parts = version_str.split(".")
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0

            min_major, min_minor = self.requirements.min_macos_version

            if major < min_major or (major == min_major and minor < min_minor):
                msg = f"macOS {min_major}.{min_minor}+ required, found {major}.{minor}"
                if raise_on_error:
                    raise OSError(msg)
                logger.warning(msg)
                return False

            logger.debug(f"macOS version {major}.{minor} is compatible")
            return True

        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse macOS version: {e}")
            return True  # Assume compatible if can't parse

    def _validate_windows_version(self, raise_on_error: bool) -> bool:
        """Validate Windows version."""
        # Windows 10+ is generally compatible
        version = platform.version()
        logger.debug(f"Windows version: {version}")

        # Basic check for Windows 10+
        try:
            # Windows version format_output: "10.0.19041"
            major = int(version.split(".")[0])
            if major < 10:
                msg = "Windows 10 or later required"
                if raise_on_error:
                    raise OSError(msg)
                logger.warning(msg)
                return False
        except (ValueError, IndexError):
            logger.warning("Could not parse Windows version")

        return True

    def validate_memory(self, required_gb: int | None = None, raise_on_error: bool = True) -> bool:
        """
        Validate available system memory.

        Args:
            required_gb: Required memory in GB (uses default if None)
            raise_on_error: Raise exception on validation failure

        Returns:
            True if sufficient memory is available

        Raises:
            EnvironmentError: If insufficient memory and raise_on_error is True

        """
        required_gb = required_gb or self.requirements.min_memory_gb
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)

        logger.debug(f"Memory: {total_gb:.1f}GB total, {available_gb:.1f}GB available, {memory.percent:.1f}% used")

        if total_gb < required_gb:
            msg = f"Insufficient memory: {required_gb}GB required, {total_gb:.1f}GB total"
            if raise_on_error:
                raise OSError(msg)
            logger.warning(msg)
            return False

        if available_gb < 2:  # Warn if less than 2GB available
            logger.warning(f"Low available memory: {available_gb:.1f}GB. Consider closing other applications.")

        return True

    def validate_disk_space(
        self, required_gb: int | None = None, path: Path | None = None, raise_on_error: bool = True
    ) -> bool:
        """
        Validate available disk space.

        Args:
            required_gb: Required space in GB (uses default if None)
            path: Path to check space for (uses home directory if None)
            raise_on_error: Raise exception on validation failure

        Returns:
            True if sufficient disk space is available

        Raises:
            EnvironmentError: If insufficient space and raise_on_error is True

        """
        required_gb = required_gb or self.requirements.min_disk_space_gb
        check_path = path or Path.home()

        try:
            disk_usage = psutil.disk_usage(str(check_path))
            free_gb = disk_usage.free / (1024**3)
            total_gb = disk_usage.total / (1024**3)

            logger.debug(
                f"Disk space at {check_path}: {free_gb:.1f}GB free "
                f"of {total_gb:.1f}GB total ({disk_usage.percent:.1f}% used)"
            )

            if free_gb < required_gb:
                msg = f"Insufficient disk space: {required_gb}GB required, {free_gb:.1f}GB available at {check_path}"
                if raise_on_error:
                    raise OSError(msg)
                logger.warning(msg)
                return False

            if free_gb < required_gb * 1.5:  # Warn if less than 150% of required
                logger.warning(
                    f"Low disk space: {free_gb:.1f}GB available. Recommend at least {required_gb * 1.5:.1f}GB free."
                )

            return True

        except Exception as e:
            logger.error(f"Failed to check disk space: {e}")
            if raise_on_error:
                msg = f"Disk space check failed: {e}"
                raise OSError(msg)
            return False

    def validate_gpu_availability(self, raise_on_error: bool = True) -> bool:
        """
        Validate GPU availability (basic check).

        Args:
            raise_on_error: Raise exception on validation failure

        Returns:
            True if GPU is available or not required

        Raises:
            EnvironmentError: If GPU required but not available and raise_on_error is True

        """
        if not self.requirements.required_gpu:
            return True

        # Basic GPU checks
        gpu_available = False

        # Check for common GPU utilities
        if platform.system() == "Darwin":
            # macOS always has Metal support on modern systems
            gpu_available = True
            logger.debug("macOS Metal GPU support available")
        elif shutil.which("nvidia-smi"):
            gpu_available = True
            logger.debug("NVIDIA GPU detected")
        elif shutil.which("rocm-smi"):
            gpu_available = True
            logger.debug("AMD GPU detected")

        if not gpu_available and self.requirements.required_gpu:
            msg = "No compatible GPU detected. GPU acceleration may not be available."
            if raise_on_error:
                raise OSError(msg)
            logger.warning(msg)
            return False

        return True

    def check_executable(self, name: str, paths: list[str]) -> Path | None:
        """
        Check if an executable exists at any of the given paths.

        Args:
            name: Executable name for logging
            paths: List of paths to check

        Returns:
            Path to executable if found, None otherwise

        """
        for path_str in paths:
            path = Path(path_str)
            if path.exists() and path.is_file():
                logger.debug(f"Found {name} at: {path}")
                return path

        logger.debug(f"{name} not found in: {paths}")
        return None

    def get_system_info(self) -> dict[str, Any]:
        """
        Get comprehensive system information.

        Returns:
            Dictionary containing system information

        Used in:
        - topyaz/cli.py
        """
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(Path.home())

        info = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent_used": memory.percent,
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent_used": disk.percent,
            },
            "cpu": {
                "count": psutil.cpu_count(),
                "count_physical": psutil.cpu_count(logical=False),
            },
        }

        # Add macOS specific info
        if platform.system() == "Darwin":
            info["macos_version"] = platform.mac_ver()[0]

        return info
