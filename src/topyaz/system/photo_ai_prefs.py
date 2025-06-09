#!/usr/bin/env python3
# this_file: src/topyaz/system/photo_ai_prefs.py
"""
Photo AI preferences manipulation for topyaz.

This module provides comprehensive control over Topaz Photo AI's autopilot
settings by manipulating the macOS preferences file before CLI execution.

Used in:
- src/topyaz/products/_photo_ai.py
"""

import platform
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from topyaz.system.preferences import PreferenceHandler, PreferenceValidationError


@dataclass
class PhotoAIAutopilotSettings:
    """
    Typed configuration for Photo AI autopilot settings.

    Maps directly to the autopilot preferences in the Photo AI plist file.
    """

    # Face Recovery
    face_strength: int = 80
    face_detection: str = "subject"  # auto, subject, all
    face_parts: list[str] = field(default_factory=lambda: ["hair", "necks"])

    # Denoise
    denoise_model: str = "Auto"
    denoise_levels: list[str] = field(default_factory=lambda: ["medium", "high", "severe"])
    denoise_strength: int = 3
    denoise_raw_model: str = "Auto"
    denoise_raw_levels: list[str] = field(default_factory=lambda: ["low", "medium", "high", "severe"])
    denoise_raw_strength: int = 3

    # Sharpen
    sharpen_model: str = "Auto"
    sharpen_levels: list[str] = field(default_factory=lambda: ["medium", "high"])
    sharpen_strength: int = 3

    # Upscaling
    upscaling_model: str = "High Fidelity V2"
    upscaling_factor: float = 2.0
    upscaling_type: str = "auto"  # auto, scale, width, height
    deblur_strength: int = 3
    denoise_upscale_strength: int = 3

    # Exposure & Lighting
    lighting_strength: int = 25
    raw_exposure_strength: int = 8
    adjust_color: bool = False

    # White Balance
    temperature_value: int = 50
    opacity_value: int = 100

    # Output
    resolution_unit: int = 1  # 1=inches, 2=cm
    default_resolution: float = -1  # -1=auto

    # Processing
    overwrite_files: bool = False
    recurse_directories: bool = False
    append_filters: bool = False


class PhotoAIPreferences(PreferenceHandler):
    """
    Handler for Topaz Photo AI preferences manipulation.

    Provides safe backup/restore and atomic updates of Photo AI's autopilot
    settings stored in the macOS preferences file.
    """

    # Valid values for validation
    VALID_FACE_DETECTION = {"auto", "subject", "all"}
    VALID_FACE_PARTS = {"hair", "necks", "eyes", "mouth"}
    VALID_DENOISE_MODELS = {"Auto", "Low Light Beta", "Severe Noise Beta"}
    VALID_DENOISE_LEVELS = {"low", "medium", "high", "severe"}
    VALID_SHARPEN_MODELS = {"Auto", "Sharpen Standard v2", "Lens Blur v2", "Sharpen Natural", "Sharpen Strong"}
    VALID_UPSCALING_MODELS = {"High Fidelity V2", "Standard V2", "Graphics V2"}
    VALID_UPSCALING_TYPES = {"auto", "scale", "width", "height"}

    def __init__(self, preference_file: Path | None = None):
        """
        Initialize Photo AI preferences handler.

        Args:
            preference_file: Optional custom path to preferences file.
                           If None, uses default Photo AI preferences location.
        """
        if preference_file is None:
            preference_file = self._get_default_preference_path()

        super().__init__(preference_file)

    def _get_default_preference_path(self) -> Path:
        """
        Get default Photo AI preferences file path for current platform.

        Returns:
            Path to Photo AI preferences file

        Raises:
            RuntimeError: If platform is not supported
        """
        if platform.system() == "Darwin":
            # macOS
            return Path.home() / "Library/Preferences/com.topazlabs.Topaz Photo AI.plist"
        if platform.system() == "Windows":
            # Windows - Photo AI uses registry, but this could be adapted
            msg = "Windows preferences manipulation not yet supported"
            raise RuntimeError(msg)
        msg = f"Unsupported platform: {platform.system()}"
        raise RuntimeError(msg)

    def validate_preferences(self, preferences: dict[str, Any]) -> bool:
        """
        Validate Photo AI preferences structure and values.

        Args:
            preferences: Preference dictionary to validate

        Returns:
            True if preferences are valid

        Raises:
            PreferenceValidationError: If preferences are invalid
        """
        try:
            # Basic structure validation
            required_keys = {
                "autopilotFaceDetectOption",
                "autopilotFaceStrength",
                "autopilotDenoisingModel",
                "autopilotUpscalingModel",
                "autopilotUpscalingFactor",
            }

            missing_keys = required_keys - set(preferences.keys())
            if missing_keys:
                msg = f"Missing required keys: {missing_keys}"
                raise PreferenceValidationError(msg)

            # Value validation
            face_detection = preferences.get("autopilotFaceDetectOption", "subject")
            if face_detection not in self.VALID_FACE_DETECTION:
                msg = f"Invalid face detection: {face_detection}"
                raise PreferenceValidationError(msg)

            face_strength = preferences.get("autopilotFaceStrength", 0)
            if face_strength is not None and not (0 <= face_strength <= 100):
                msg = f"Face strength must be 0-100: {face_strength}"
                raise PreferenceValidationError(msg)

            upscaling_factor = preferences.get("autopilotUpscalingFactor", 0)
            if upscaling_factor is not None and not (1.0 <= upscaling_factor <= 6.0):
                msg = f"Upscaling factor must be 1.0-6.0: {upscaling_factor}"
                raise PreferenceValidationError(msg)

            logger.debug("Preferences validation passed")
            return True

        except Exception as e:
            logger.error(f"Preference validation failed: {e}")
            raise

    def get_default_preferences(self) -> dict[str, Any]:
        """
        Get default Photo AI preferences structure.

        Returns:
            Dictionary with default Photo AI preference values
        """
        return {
            # Face Recovery
            "autopilotFaceDetectOption": "subject",
            "autopilotFaceStrength": 80,
            "faceParts": ["hair", "necks"],
            # Denoise
            "autopilotDenoisingModel": "Auto",
            "autopilotDenoiseLevels": ["medium", "high", "severe"],
            "autopilotDenoiseStrength": 3,
            "autopilotDenoisingRawModel": "Auto",
            "autopilotDenoiseRawLevels": ["low", "medium", "high", "severe"],
            "autopilotDenoiseRawStrength": 3,
            # Sharpen
            "autopilotSharpeningModel": "Auto",
            "autopilotSharpenBlurs": ["medium", "high"],
            "autopilotSharpenStrength": 3,
            # Upscaling
            "autopilotUpscalingModel": "High Fidelity V2",
            "autopilotUpscalingFactor": 2.0,
            "autopilotUpscalingType": "auto",
            "autopilotUpscalingParam1Strength": 3,
            "autopilotUpscalingParam2Strength": 3,
            # Exposure & Color
            "autopilotNonRAWExposureStrength": 25,
            "autopilotRAWExposureStrength": 8,
            "autopilotAdjustColor": False,
            # White Balance
            "autopilotTemperatureValue": 50,
            "autopilotOpacityValue": 100,
            # Output
            "autopilotResolutionUnit": 1,
            "autopilotDefaultResolution": -1.0,
            # Processing
            "saveAllowOverwrite": False,
            "autopilotRecommendFilters": True,
            "saveAppendFilters": False,
        }

    def get_current_autopilot_settings(self) -> PhotoAIAutopilotSettings:
        """
        Get current autopilot settings from preferences.

        Returns:
            Current autopilot settings as typed dataclass
        """
        prefs = self.read_preferences()

        return PhotoAIAutopilotSettings(
            # Face Recovery
            face_strength=prefs.get("autopilotFaceStrength", 80),
            face_detection=prefs.get("autopilotFaceDetectOption", "subject"),
            face_parts=prefs.get("faceParts", ["hair", "necks"]),
            # Denoise
            denoise_model=prefs.get("autopilotDenoisingModel", "Auto"),
            denoise_levels=prefs.get("autopilotDenoiseLevels", ["medium", "high", "severe"]),
            denoise_strength=prefs.get("autopilotDenoiseStrength", 3),
            denoise_raw_model=prefs.get("autopilotDenoisingRawModel", "Auto"),
            denoise_raw_levels=prefs.get("autopilotDenoiseRawLevels", ["low", "medium", "high", "severe"]),
            denoise_raw_strength=prefs.get("autopilotDenoiseRawStrength", 3),
            # Sharpen
            sharpen_model=prefs.get("autopilotSharpeningModel", "Auto"),
            sharpen_levels=prefs.get("autopilotSharpenBlurs", ["medium", "high"]),
            sharpen_strength=prefs.get("autopilotSharpenStrength", 3),
            # Upscaling
            upscaling_model=prefs.get("autopilotUpscalingModel", "High Fidelity V2"),
            upscaling_factor=prefs.get("autopilotUpscalingFactor", 2.0),
            upscaling_type=prefs.get("autopilotUpscalingType", "auto"),
            deblur_strength=prefs.get("autopilotUpscalingParam1Strength", 3),
            denoise_upscale_strength=prefs.get("autopilotUpscalingParam2Strength", 3),
            # Exposure & Color
            lighting_strength=prefs.get("autopilotNonRAWExposureStrength", 25),
            raw_exposure_strength=prefs.get("autopilotRAWExposureStrength", 8),
            adjust_color=prefs.get("autopilotAdjustColor", False),
            # White Balance
            temperature_value=prefs.get("autopilotTemperatureValue", 50),
            opacity_value=prefs.get("autopilotOpacityValue", 100),
            # Output
            resolution_unit=prefs.get("autopilotResolutionUnit", 1),
            default_resolution=prefs.get("autopilotDefaultResolution", -1.0),
            # Processing
            overwrite_files=prefs.get("saveAllowOverwrite", False),
            recurse_directories=prefs.get("saveRecurseDirectories", False),
            append_filters=prefs.get("saveAppendFilters", False),
        )

    def update_autopilot_settings(self, settings: PhotoAIAutopilotSettings) -> None:
        """
        Update autopilot settings in preferences.

        Args:
            settings: New autopilot settings to apply
        """
        # Read current preferences
        prefs = self.read_preferences()

        # Update with new settings
        prefs.update(
            {
                # Face Recovery
                "autopilotFaceStrength": settings.face_strength or 80,
                "autopilotFaceDetectOption": settings.face_detection or "subject",
                "faceParts": settings.face_parts or ["hair", "necks"],
                # Denoise
                "autopilotDenoisingModel": settings.denoise_model or "Auto",
                "autopilotDenoiseLevels": settings.denoise_levels or ["medium", "high", "severe"],
                "autopilotDenoiseStrength": settings.denoise_strength or 3,
                "autopilotDenoisingRawModel": settings.denoise_raw_model or "Auto",
                "autopilotDenoiseRawLevels": settings.denoise_raw_levels or ["low", "medium", "high", "severe"],
                "autopilotDenoiseRawStrength": settings.denoise_raw_strength or 3,
                # Sharpen
                "autopilotSharpeningModel": settings.sharpen_model or "Auto",
                "autopilotSharpenBlurs": settings.sharpen_levels or ["medium", "high"],
                "autopilotSharpenStrength": settings.sharpen_strength or 3,
                # Upscaling
                "autopilotUpscalingModel": settings.upscaling_model or "High Fidelity V2",
                "autopilotUpscalingFactor": settings.upscaling_factor or 2.0,
                "autopilotUpscalingType": settings.upscaling_type or "auto",
                "autopilotUpscalingParam1Strength": settings.deblur_strength or 3,
                "autopilotUpscalingParam2Strength": settings.denoise_upscale_strength or 3,
                # Exposure & Color
                "autopilotNonRAWExposureStrength": settings.lighting_strength or 25,
                "autopilotRAWExposureStrength": settings.raw_exposure_strength or 8,
                "autopilotAdjustColor": bool(settings.adjust_color) if settings.adjust_color is not None else False,
                # White Balance
                "autopilotTemperatureValue": settings.temperature_value or 50,
                "autopilotOpacityValue": settings.opacity_value or 100,
                # Output
                "autopilotResolutionUnit": settings.resolution_unit or 1,
                "autopilotDefaultResolution": settings.default_resolution or -1.0,
                # Processing
                "saveAllowOverwrite": bool(settings.overwrite_files) if settings.overwrite_files is not None else False,
                "saveAppendFilters": bool(settings.append_filters) if settings.append_filters is not None else False,
            }
        )

        # Write updated preferences
        self.write_preferences(prefs)

        logger.info("Updated Photo AI autopilot settings")

    def validate_setting_values(self, **kwargs) -> None:
        """
        Validate individual setting values.

        Args:
            **kwargs: Settings to validate

        Raises:
            PreferenceValidationError: If any setting is invalid
        """
        # Face detection validation
        if "face_detection" in kwargs and kwargs["face_detection"] is not None:
            if kwargs["face_detection"] not in self.VALID_FACE_DETECTION:
                msg = f"Invalid face_detection: {kwargs['face_detection']}"
                raise PreferenceValidationError(msg)

        # Face parts validation
        if "face_parts" in kwargs and kwargs["face_parts"] is not None:
            invalid_parts = set(kwargs["face_parts"]) - self.VALID_FACE_PARTS
            if invalid_parts:
                msg = f"Invalid face_parts: {invalid_parts}"
                raise PreferenceValidationError(msg)

        # Strength validations (0-100)
        for param in [
            "face_strength",
            "lighting_strength",
            "raw_exposure_strength",
            "temperature_value",
            "opacity_value",
        ]:
            if param in kwargs and kwargs[param] is not None:
                value = kwargs[param]
                if not (0 <= value <= 100):
                    msg = f"{param} must be 0-100: {value}"
                    raise PreferenceValidationError(msg)

        # Strength validations (0-10)
        for param in [
            "denoise_strength",
            "denoise_raw_strength",
            "sharpen_strength",
            "deblur_strength",
            "denoise_upscale_strength",
        ]:
            if param in kwargs and kwargs[param] is not None:
                value = kwargs[param]
                if not (0 <= value <= 10):
                    msg = f"{param} must be 0-10: {value}"
                    raise PreferenceValidationError(msg)

        # Upscaling factor validation
        if "upscaling_factor" in kwargs and kwargs["upscaling_factor"] is not None:
            value = kwargs["upscaling_factor"]
            if not (1.0 <= value <= 6.0):
                msg = f"upscaling_factor must be 1.0-6.0: {value}"
                raise PreferenceValidationError(msg)

        # Model validations
        if (
            "denoise_model" in kwargs
            and kwargs["denoise_model"] is not None
            and kwargs["denoise_model"] not in self.VALID_DENOISE_MODELS
        ):
            msg = f"Invalid denoise_model: {kwargs['denoise_model']}"
            raise PreferenceValidationError(msg)

        if (
            "sharpen_model" in kwargs
            and kwargs["sharpen_model"] is not None
            and kwargs["sharpen_model"] not in self.VALID_SHARPEN_MODELS
        ):
            msg = f"Invalid sharpen_model: {kwargs['sharpen_model']}"
            raise PreferenceValidationError(msg)

        if (
            "upscaling_model" in kwargs
            and kwargs["upscaling_model"] is not None
            and kwargs["upscaling_model"] not in self.VALID_UPSCALING_MODELS
        ):
            msg = f"Invalid upscaling_model: {kwargs['upscaling_model']}"
            raise PreferenceValidationError(msg)

        if (
            "upscaling_type" in kwargs
            and kwargs["upscaling_type"] is not None
            and kwargs["upscaling_type"] not in self.VALID_UPSCALING_TYPES
        ):
            msg = f"Invalid upscaling_type: {kwargs['upscaling_type']}"
            raise PreferenceValidationError(msg)

        # Level validations
        if "denoise_levels" in kwargs and kwargs["denoise_levels"] is not None:
            invalid_levels = set(kwargs["denoise_levels"]) - self.VALID_DENOISE_LEVELS
            if invalid_levels:
                msg = f"Invalid denoise_levels: {invalid_levels}"
                raise PreferenceValidationError(msg)

        if "sharpen_levels" in kwargs and kwargs["sharpen_levels"] is not None:
            invalid_levels = set(kwargs["sharpen_levels"]) - self.VALID_DENOISE_LEVELS
            if invalid_levels:
                msg = f"Invalid sharpen_levels: {invalid_levels}"
                raise PreferenceValidationError(msg)

        logger.debug("Setting values validation passed")
