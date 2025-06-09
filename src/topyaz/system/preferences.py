#!/usr/bin/env python3
# this_file: src/topyaz/system/preferences.py
"""
Base preferences handling system for topyaz.

This module provides base classes and utilities for handling macOS
preference files and other configuration systems across different platforms.

Used in:
- src/topyaz/system/photo_ai_prefs.py
- src/topyaz/products/photo_ai.py
"""

import plistlib
import tempfile
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from loguru import logger


class PreferenceError(Exception):
    """Base exception for preference-related errors."""

    pass


class PreferenceBackupError(PreferenceError):
    """Errors related to preference backup operations."""

    pass


class PreferenceRestoreError(PreferenceError):
    """Errors related to preference restore operations."""

    pass


class PreferenceValidationError(PreferenceError):
    """Errors related to preference validation."""

    pass


class PreferenceHandler(ABC):
    """
    Abstract base class for handling application preferences.

    Provides a framework for safely backing up, modifying, and restoring
    application preference files with atomic operations and error handling.
    """

    def __init__(self, preference_file: Path):
        """
        Initialize preference handler.

        Args:
            preference_file: Path to the preference file to manage
        """
        self.preference_file = Path(preference_file)
        self._backups: dict[str, Path] = {}

    @abstractmethod
    def validate_preferences(self, preferences: dict[str, Any]) -> bool:
        """
        Validate preference structure and values.

        Args:
            preferences: Preference dictionary to validate

        Returns:
            True if preferences are valid

        Raises:
            PreferenceValidationError: If preferences are invalid
        """
        pass

    @abstractmethod
    def get_default_preferences(self) -> dict[str, Any]:
        """
        Get default preferences structure.

        Returns:
            Dictionary with default preference values
        """
        pass

    def read_preferences(self) -> dict[str, Any]:
        """
        Read preferences from file.

        Returns:
            Dictionary with current preferences

        Raises:
            PreferenceError: If preferences cannot be read
        """
        try:
            if not self.preference_file.exists():
                logger.warning(f"Preference file not found: {self.preference_file}")
                return self.get_default_preferences()

            with open(self.preference_file, "rb") as f:
                preferences = plistlib.load(f)

            logger.debug(f"Successfully read preferences from {self.preference_file}")
            return preferences

        except Exception as e:
            error_msg = f"Failed to read preferences from {self.preference_file}: {e}"
            logger.error(error_msg)
            raise PreferenceError(error_msg) from e

    def write_preferences(self, preferences: dict[str, Any]) -> None:
        """
        Write preferences to file atomically.

        Args:
            preferences: Preference dictionary to write

        Raises:
            PreferenceError: If preferences cannot be written
        """
        try:
            # Validate preferences before writing
            self.validate_preferences(preferences)

            # Ensure parent directory exists
            self.preference_file.parent.mkdir(parents=True, exist_ok=True)

            # Write to temporary file first for atomic operation
            temp_file = self.preference_file.with_suffix(".tmp")

            with open(temp_file, "wb") as f:
                plistlib.dump(preferences, f)

            # Atomic move
            temp_file.replace(self.preference_file)

            logger.debug(f"Successfully wrote preferences to {self.preference_file}")

        except Exception as e:
            # Clean up temp file if it exists
            temp_file = self.preference_file.with_suffix(".tmp")
            if temp_file.exists():
                temp_file.unlink()

            error_msg = f"Failed to write preferences to {self.preference_file}: {e}"
            logger.error(error_msg)
            raise PreferenceError(error_msg) from e

    def backup(self) -> str:
        """
        Create a backup of current preferences.

        Returns:
            Backup ID for later restoration

        Raises:
            PreferenceBackupError: If backup cannot be created
        """
        try:
            backup_id = str(uuid.uuid4())

            if not self.preference_file.exists():
                logger.info(f"No preference file to backup: {self.preference_file}")
                # Store empty backup to indicate file didn't exist
                self._backups[backup_id] = None
                return backup_id

            # Create backup in temp directory
            backup_dir = Path(tempfile.gettempdir()) / "topyaz_backups"
            backup_dir.mkdir(exist_ok=True)

            backup_file = backup_dir / f"{self.preference_file.name}_{backup_id}.bak"

            # Copy current preferences to backup
            with open(self.preference_file, "rb") as src, open(backup_file, "wb") as dst:
                dst.write(src.read())

            self._backups[backup_id] = backup_file

            logger.info(f"Created preference backup: {backup_id}")
            return backup_id

        except Exception as e:
            error_msg = f"Failed to create backup: {e}"
            logger.error(error_msg)
            raise PreferenceBackupError(error_msg) from e

    def restore(self, backup_id: str) -> None:
        """
        Restore preferences from backup.

        Args:
            backup_id: Backup ID returned from backup()

        Raises:
            PreferenceRestoreError: If backup cannot be restored
        """
        try:
            if backup_id not in self._backups:
                msg = f"Unknown backup ID: {backup_id}"
                raise PreferenceRestoreError(msg)

            backup_file = self._backups[backup_id]

            if backup_file is None:
                # Original file didn't exist, remove current file
                if self.preference_file.exists():
                    self.preference_file.unlink()
                    logger.info(f"Removed preference file (original didn't exist): {self.preference_file}")
            else:
                # Restore from backup file
                if not backup_file.exists():
                    msg = f"Backup file not found: {backup_file}"
                    raise PreferenceRestoreError(msg)

                with open(backup_file, "rb") as src, open(self.preference_file, "wb") as dst:
                    dst.write(src.read())

                logger.info(f"Restored preferences from backup: {backup_id}")

            # Clean up backup
            self._cleanup_backup(backup_id)

        except Exception as e:
            error_msg = f"Failed to restore backup {backup_id}: {e}"
            logger.error(error_msg)
            raise PreferenceRestoreError(error_msg) from e

    def _cleanup_backup(self, backup_id: str) -> None:
        """
        Clean up backup file.

        Args:
            backup_id: Backup ID to clean up
        """
        try:
            if backup_id in self._backups:
                backup_file = self._backups[backup_id]
                if backup_file and backup_file.exists():
                    backup_file.unlink()
                    logger.debug(f"Cleaned up backup file: {backup_file}")
                del self._backups[backup_id]
        except Exception as e:
            logger.warning(f"Failed to clean up backup {backup_id}: {e}")

    def cleanup_all_backups(self) -> None:
        """Clean up all backup files."""
        for backup_id in list(self._backups.keys()):
            self._cleanup_backup(backup_id)

    def __enter__(self):
        """Context manager entry - create backup."""
        self._backup_id_for_context = self.backup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - restore from backup."""
        if hasattr(self, "_backup_id_for_context"):
            self.restore(self._backup_id_for_context)
        self.cleanup_all_backups()
