#!/usr/bin/env python3
# this_file: src/topyaz/core/_config.py
"""
Configuration management for topyaz.

This module handles loading, parsing, and accessing configuration from YAML files
and environment variables. It provides a centralized configuration management system
with support for nested keys and default values.

"""

import os
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from topyaz.core.types import ConfigDict


class Config:
    """
    Manages topyaz configuration from files and environment.

    Configuration is loaded from:
    1. Default values (hardcoded)
    2. System _config file (~/.topyaz/_config.yaml)
    3. User-specified _config file
    4. Environment variables (TOPYAZ_* prefix)

    Configuration keys can be accessed using dot notation:
        _config.get("video.default_model")
        _config.get("defaults.output_dir", "~/processed")

    Used in:
    - topyaz/cli.py
    - topyaz/core/__init__.py
    """

    DEFAULT_CONFIG: ConfigDict = {
        "defaults": {
            "output_dir": "~/processed",
            "preserve_structure": True,
            "backup_originals": False,
            "log_level": "INFO",
            "timeout": 3600,
            "parallel_jobs": 1,
        },
        "video": {
            "default_model": "amq-13",
            "default_codec": "hevc_videotoolbox",
            "default_quality": 18,
            "device": 0,
        },
        "_gigapixel": {
            "default_model": "std",
            "default_format": "preserve",
            "default_scale": 2,
            "parallel_read": 4,
            "quality_output": 95,
        },
        "photo": {
            "default_format": "preserve",
            "default_quality": 95,
            "autopilot_preset": "default",
            "bit_depth": 16,
        },
        "paths": {
            "_gigapixel": {
                "macos": [
                    "/Applications/Topaz Gigapixel AI.app/Contents/Resources/bin/_gigapixel",
                    "/Applications/Topaz Gigapixel AI.app/Contents/MacOS/Topaz Gigapixel AI",
                ],
                "windows": [
                    "C:\\Program Files\\Topaz Labs LLC\\Topaz Gigapixel AI\\bin\\_gigapixel.exe",
                ],
            },
            "_video_ai": {
                "macos": [
                    "/Applications/Topaz Video AI.app/Contents/MacOS/ffmpeg",
                ],
                "windows": [
                    "C:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\ffmpeg.exe",
                ],
            },
            "_photo_ai": {
                "macos": [
                    "/Applications/Topaz Photo AI.app/Contents/Resources/bin/tpai",
                    "/Applications/Topaz Photo AI.app/Contents/MacOS/Topaz Photo AI",
                ],
                "windows": [
                    "C:\\Program Files\\Topaz Labs LLC\\Topaz Photo AI\\tpai.exe",
                ],
            },
        },
    }

    def __init__(self, config_file: Path | None = None):
        """
        Initialize configuration manager.

        Args:
            config_file: Optional path to configuration file.
                        If not provided, uses ~/.topyaz/_config.yaml

        """
        self.config_file = config_file or Path.home() / ".topyaz" / "_config.yaml"
        self.config = self._load_config()
        self._load_env_vars()

    def _load_config(self) -> ConfigDict:
        """
        Load configuration from YAML file.

        Returns:
            Merged configuration dictionary

        """
        # Start with default _config
        config = self._deep_copy_dict(self.DEFAULT_CONFIG)

        # Load from _config file if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    user_config = yaml.safe_load(f) or {}

                # Merge user _config into defaults
                config = self._merge_configs(config, user_config)
                logger.debug(f"Loaded configuration from {self.config_file}")

            except yaml.YAMLError as e:
                logger.warning(f"Failed to parse _config file {self.config_file}: {e}")
            except Exception as e:
                logger.warning(f"Failed to load _config from {self.config_file}: {e}")
        else:
            logger.debug(f"Config file not found: {self.config_file}")

        return config

    def _load_env_vars(self) -> None:
        """
        Load configuration from environment variables.

        Environment variables should be prefixed with TOPYAZ_ and use
        double underscores for nested keys:
            TOPYAZ_VIDEO__DEFAULT_MODEL=amq-13
            TOPYAZ_DEFAULTS__LOG_LEVEL=DEBUG

        """
        prefix = "TOPYAZ_"

        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue

            # Remove prefix and convert to lowercase
            config_key = key[len(prefix) :].lower()

            # Convert double underscores to dots for nested keys
            config_key = config_key.replace("__", ".")

            # Try to parse value as appropriate type
            parsed_value = self._parse_env_value(value)

            # Set the configuration value
            self._set_nested(config_key, parsed_value)
            logger.debug(f"Set _config from env: {config_key} = {parsed_value}")

    def _parse_env_value(self, value: str) -> Any:
        """
        Parse environment variable value to appropriate type.

        Args:
            value: String value from environment

        Returns:
            Parsed value (bool, int, float, or str)

        """
        # Try to parse as boolean
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        if value.lower() in ("false", "no", "0", "off"):
            return False

        # Try to parse as integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try to parse as float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _merge_configs(self, base: ConfigDict, update: ConfigDict) -> ConfigDict:
        """
        Recursively merge two configuration dictionaries.

        Args:
            base: Base configuration
            update: Configuration to merge in

        Returns:
            Merged configuration

        """
        result = base.copy()

        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursive merge for nested dicts
                result[key] = self._merge_configs(result[key], value)
            else:
                # Direct assignment for other types
                result[key] = value

        return result

    def _deep_copy_dict(self, d: ConfigDict) -> ConfigDict:
        """
        Create a deep copy of a dictionary.

        Args:
            d: Dictionary to copy

        Returns:
            Deep copy of the dictionary

        """
        if not isinstance(d, dict):
            return d

        return {key: self._deep_copy_dict(value) if isinstance(value, dict) else value for key, value in d.items()}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with dot notation support.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found

        Returns:
            Configuration value or default

        Examples:
            _config.get("video.default_model")  # "amq-13"
            _config.get("missing.key", "default")  # "default"

        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def _set_nested(self, key: str, value: Any) -> None:
        """
        Set a nested configuration value using dot notation.

        Args:
            key: Configuration key with dot notation
            value: Value to set

        """
        keys = key.split(".")
        target = self.config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        # Set the final value
        if keys:
            target[keys[-1]] = value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set

        """
        self._set_nested(key, value)
        logger.debug(f"Set _config: {key} = {value}")

    def save(self, path: Path | None = None) -> None:
        """
        Save current configuration to file.

        Args:
            path: Path to save to (defaults to original _config file)

        """
        save_path = path or self.config_file
        save_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(save_path, "w") as f:
                yaml.safe_dump(self.config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Saved configuration to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def get_product_paths(self, product: str, platform: str | None = None) -> list[str]:
        """
        Get executable paths for a specific product.

        Args:
            product: Product name (_gigapixel, _video_ai, _photo_ai)
            platform: Platform name (macos, windows). Auto-detected if None.

        Returns:
            List of possible executable paths

        """
        if platform is None:
            import platform as plat

            system = plat.system()
            platform = "macos" if system == "Darwin" else "windows"

        paths = self.get(f"paths.{product}.{platform}", [])
        return paths if isinstance(paths, list) else []

    def to_dict(self) -> ConfigDict:
        """
        Get full configuration as dictionary.

        Returns:
            Complete configuration dictionary

        """
        return self._deep_copy_dict(self.config)
