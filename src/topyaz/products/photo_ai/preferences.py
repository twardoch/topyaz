#!/usr/bin/env python3
# this_file: src/topyaz/products/photo_ai/preferences.py
"""
Photo AI preferences manipulation for topyaz.

This module provides comprehensive control over Topaz Photo AI's autopilot
settings by manipulating the macOS preferences file before CLI execution.
"""

import platform
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger

from topyaz.system.preferences import PreferenceHandler, PreferenceValidationError


@dataclass
class PhotoAIAutopilotSettings:
    """
    Typed configuration for Photo AI autopilot settings.
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
    """

    VALID_FACE_DETECTION = {"auto", "subject", "all"}
    VALID_FACE_PARTS = {"hair", "necks", "eyes", "mouth"}
    VALID_DENOISE_MODELS = {"Auto", "Low Light Beta", "Severe Noise Beta"}
    VALID_DENOISE_LEVELS = {"low", "medium", "high", "severe"}
    VALID_SHARPEN_MODELS = {"Auto", "Sharpen Standard v2", "Lens Blur v2", "Sharpen Natural", "Sharpen Strong"}
    VALID_UPSCALING_MODELS = {"High Fidelity V2", "Standard V2", "Graphics V2"}
    VALID_UPSCALING_TYPES = {"auto", "scale", "width", "height"}

    def __init__(self, preference_file: Path | None = None):
        if preference_file is None:
            preference_file = self._get_default_preference_path()
        super().__init__(preference_file)

    def _get_default_preference_path(self) -> Path:
        if platform.system() == "Darwin":
            return Path.home() / "Library/Preferences/com.topazlabs.Topaz Photo AI.plist"
        if platform.system() == "Windows":
            msg = "Windows preferences manipulation not yet supported"
            raise RuntimeError(msg)
        msg = f"Unsupported platform: {platform.system()}"
        raise RuntimeError(msg)

    def validate_preferences(self, preferences: dict[str, Any]) -> bool:
        try:
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

            face_detection = preferences.get("autopilotFaceDetectOption", "subject")
            if face_detection not in self.VALID_FACE_DETECTION:
                msg = f"Invalid face detection: {face_detection}"
                raise PreferenceValidationError(msg)

            face_strength = preferences.get("autopilotFaceStrength", 0)
            if not (0 <= face_strength <= 100):
                msg = f"Face strength must be 0-100: {face_strength}"
                raise PreferenceValidationError(msg)

            upscaling_factor = preferences.get("autopilotUpscalingFactor", 0)
            if not (1.0 <= upscaling_factor <= 6.0):
                msg = f"Upscaling factor must be 1.0-6.0: {upscaling_factor}"
                raise PreferenceValidationError(msg)

            logger.debug("Preferences validation passed")
            return True
        except Exception as e:
            logger.error(f"Preference validation failed: {e}")
            raise

    def get_default_preferences(self) -> dict[str, Any]:
        return {
            "autopilotFaceDetectOption": "subject",
            "autopilotFaceStrength": 80,
            "faceParts": ["hair", "necks"],
            "autopilotDenoisingModel": "Auto",
            "autopilotDenoiseLevels": ["medium", "high", "severe"],
            "autopilotDenoiseStrength": 3,
            "autopilotDenoisingRawModel": "Auto",
            "autopilotDenoiseRawLevels": ["low", "medium", "high", "severe"],
            "autopilotDenoiseRawStrength": 3,
            "autopilotSharpeningModel": "Auto",
            "autopilotSharpenBlurs": ["medium", "high"],
            "autopilotSharpenStrength": 3,
            "autopilotUpscalingModel": "High Fidelity V2",
            "autopilotUpscalingFactor": 2.0,
            "autopilotUpscalingType": "auto",
            "autopilotUpscalingParam1Strength": 3,
            "autopilotUpscalingParam2Strength": 3,
            "autopilotNonRAWExposureStrength": 25,
            "autopilotRAWExposureStrength": 8,
            "autopilotAdjustColor": False,
            "autopilotTemperatureValue": 50,
            "autopilotOpacityValue": 100,
            "autopilotResolutionUnit": 1,
            "autopilotDefaultResolution": -1.0,
            "saveAllowOverwrite": False,
            "autopilotRecommendFilters": True,
            "saveAppendFilters": False,
        }

    def get_current_autopilot_settings(self) -> PhotoAIAutopilotSettings:
        prefs = self.read_preferences()
        return PhotoAIAutopilotSettings(
            face_strength=prefs.get("autopilotFaceStrength", 80),
            face_detection=prefs.get("autopilotFaceDetectOption", "subject"),
            face_parts=prefs.get("faceParts", ["hair", "necks"]),
            denoise_model=prefs.get("autopilotDenoisingModel", "Auto"),
            denoise_levels=prefs.get("autopilotDenoiseLevels", ["medium", "high", "severe"]),
            denoise_strength=prefs.get("autopilotDenoiseStrength", 3),
            denoise_raw_model=prefs.get("autopilotDenoisingRawModel", "Auto"),
            denoise_raw_levels=prefs.get("autopilotDenoiseRawLevels", ["low", "medium", "high", "severe"]),
            denoise_raw_strength=prefs.get("autopilotDenoiseRawStrength", 3),
            sharpen_model=prefs.get("autopilotSharpeningModel", "Auto"),
            sharpen_levels=prefs.get("autopilotSharpenBlurs", ["medium", "high"]),
            sharpen_strength=prefs.get("autopilotSharpenStrength", 3),
            upscaling_model=prefs.get("autopilotUpscalingModel", "High Fidelity V2"),
            upscaling_factor=prefs.get("autopilotUpscalingFactor", 2.0),
            upscaling_type=prefs.get("autopilotUpscalingType", "auto"),
            deblur_strength=prefs.get("autopilotUpscalingParam1Strength", 3),
            denoise_upscale_strength=prefs.get("autopilotUpscalingParam2Strength", 3),
            lighting_strength=prefs.get("autopilotNonRAWExposureStrength", 25),
            raw_exposure_strength=prefs.get("autopilotRAWExposureStrength", 8),
            adjust_color=prefs.get("autopilotAdjustColor", False),
            temperature_value=prefs.get("autopilotTemperatureValue", 50),
            opacity_value=prefs.get("autopilotOpacityValue", 100),
            resolution_unit=prefs.get("autopilotResolutionUnit", 1),
            default_resolution=prefs.get("autopilotDefaultResolution", -1.0),
            overwrite_files=prefs.get("saveAllowOverwrite", False),
            recurse_directories=prefs.get("saveRecurseDirectories", False),
            append_filters=prefs.get("saveAppendFilters", False),
        )

    def update_autopilot_settings(self, settings: PhotoAIAutopilotSettings) -> None:
        prefs = self.read_preferences()
        prefs.update(
            {
                "autopilotFaceStrength": settings.face_strength or 80,
                "autopilotFaceDetectOption": settings.face_detection or "subject",
                "faceParts": settings.face_parts or ["hair", "necks"],
                "autopilotDenoisingModel": settings.denoise_model or "Auto",
                "autopilotDenoiseLevels": settings.denoise_levels or ["medium", "high", "severe"],
                "autopilotDenoiseStrength": settings.denoise_strength or 3,
                "autopilotDenoisingRawModel": settings.denoise_raw_model or "Auto",
                "autopilotDenoiseRawLevels": settings.denoise_raw_levels or ["low", "medium", "high", "severe"],
                "autopilotDenoiseRawStrength": settings.denoise_raw_strength or 3,
                "autopilotSharpeningModel": settings.sharpen_model or "Auto",
                "autopilotSharpenBlurs": settings.sharpen_levels or ["medium", "high"],
                "autopilotSharpenStrength": settings.sharpen_strength or 3,
                "autopilotUpscalingModel": settings.upscaling_model or "High Fidelity V2",
                "autopilotUpscalingFactor": settings.upscaling_factor or 2.0,
                "autopilotUpscalingType": settings.upscaling_type or "auto",
                "autopilotUpscalingParam1Strength": settings.deblur_strength or 3,
                "autopilotUpscalingParam2Strength": settings.denoise_upscale_strength or 3,
                "autopilotNonRAWExposureStrength": settings.lighting_strength or 25,
                "autopilotRAWExposureStrength": settings.raw_exposure_strength or 8,
                "autopilotAdjustColor": bool(settings.adjust_color) if settings.adjust_color is not None else False,
                "autopilotTemperatureValue": settings.temperature_value or 50,
                "autopilotOpacityValue": settings.opacity_value or 100,
                "autopilotResolutionUnit": settings.resolution_unit or 1,
                "autopilotDefaultResolution": settings.default_resolution or -1.0,
                "saveAllowOverwrite": bool(settings.overwrite_files) if settings.overwrite_files is not None else False,
                "saveAppendFilters": bool(settings.append_filters) if settings.append_filters is not None else False,
            }
        )
        self.write_preferences(prefs)
        logger.info("Updated Photo AI autopilot settings")

    def validate_setting_values(self, **kwargs) -> None:
        if "face_detection" in kwargs and kwargs["face_detection"] not in self.VALID_FACE_DETECTION:
            msg = f"Invalid face_detection: {kwargs['face_detection']}"
            raise PreferenceValidationError(msg)
        if "face_parts" in kwargs and set(kwargs["face_parts"]) - self.VALID_FACE_PARTS:
            msg = f"Invalid face_parts: {set(kwargs['face_parts']) - self.VALID_FACE_PARTS}"
            raise PreferenceValidationError(msg)
        for param in [
            "face_strength",
            "lighting_strength",
            "raw_exposure_strength",
            "temperature_value",
            "opacity_value",
        ]:
            if param in kwargs and not (0 <= kwargs[param] <= 100):
                msg = f"{param} must be 0-100: {kwargs[param]}"
                raise PreferenceValidationError(msg)
        for param in [
            "denoise_strength",
            "denoise_raw_strength",
            "sharpen_strength",
            "deblur_strength",
            "denoise_upscale_strength",
        ]:
            if param in kwargs and not (0 <= kwargs[param] <= 10):
                msg = f"{param} must be 0-10: {kwargs[param]}"
                raise PreferenceValidationError(msg)
        if "upscaling_factor" in kwargs and not (1.0 <= kwargs["upscaling_factor"] <= 6.0):
            msg = f"upscaling_factor must be 1.0-6.0: {kwargs['upscaling_factor']}"
            raise PreferenceValidationError(msg)
        if "denoise_model" in kwargs and kwargs["denoise_model"] not in self.VALID_DENOISE_MODELS:
            msg = f"Invalid denoise_model: {kwargs['denoise_model']}"
            raise PreferenceValidationError(msg)
        if "sharpen_model" in kwargs and kwargs["sharpen_model"] not in self.VALID_SHARPEN_MODELS:
            msg = f"Invalid sharpen_model: {kwargs['sharpen_model']}"
            raise PreferenceValidationError(msg)
        if "upscaling_model" in kwargs and kwargs["upscaling_model"] not in self.VALID_UPSCALING_MODELS:
            msg = f"Invalid upscaling_model: {kwargs['upscaling_model']}"
            raise PreferenceValidationError(msg)
        if "upscaling_type" in kwargs and kwargs["upscaling_type"] not in self.VALID_UPSCALING_TYPES:
            msg = f"Invalid upscaling_type: {kwargs['upscaling_type']}"
            raise PreferenceValidationError(msg)
        if "denoise_levels" in kwargs and set(kwargs["denoise_levels"]) - self.VALID_DENOISE_LEVELS:
            msg = f"Invalid denoise_levels: {set(kwargs['denoise_levels']) - self.VALID_DENOISE_LEVELS}"
            raise PreferenceValidationError(msg)
        if "sharpen_levels" in kwargs and set(kwargs["sharpen_levels"]) - self.VALID_DENOISE_LEVELS:
            msg = f"Invalid sharpen_levels: {set(kwargs['sharpen_levels']) - self.VALID_DENOISE_LEVELS}"
            raise PreferenceValidationError(msg)
        logger.debug("Setting values validation passed")
