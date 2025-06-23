#!/usr/bin/env python3
# this_file: src/topyaz/products/photo_ai/api.py
"""
Topaz Photo AI implementation for topyaz.

This module provides the Photo AI product implementation with support
for automatic and manual photo enhancement.
"""

import contextlib
import platform
from pathlib import Path
from typing import Any

from loguru import logger

from topyaz.core.errors import ProcessingError

# PhotoAIParams removed from here
from topyaz.core.types import CommandList, ProcessingOptions, ProcessingResult, Product
from topyaz.execution.base import CommandExecutor
from topyaz.products.base import MacOSTopazProduct
from topyaz.products.photo_ai.batch import PhotoAIBatch
from topyaz.products.photo_ai.params import PhotoAIParams  # Kept this direct import
from topyaz.products.photo_ai.preferences import PhotoAIAutopilotSettings, PhotoAIPreferences


class PhotoAI(MacOSTopazProduct):
    """
    Topaz Photo AI implementation.
    """

    def __init__(self, executor: CommandExecutor, options: ProcessingOptions):
        super().__init__(executor, options, Product.PHOTO_AI)
        self.batch_handler = PhotoAIBatch(self)
        self.param_handler = PhotoAIParams()

    @property
    def product_name(self) -> str:
        return "Topaz Photo AI"

    @property
    def executable_name(self) -> str:
        return "tpai"

    @property
    def app_name(self) -> str:
        return "Topaz Photo AI.app"

    @property
    def app_executable_path(self) -> str:
        return "Contents/Resources/bin/tpai"

    @property
    def supported_formats(self) -> list[str]:
        return ["jpg", "jpeg", "png", "tiff", "tif", "bmp", "webp", "dng", "raw", "cr2", "nef", "arw", "orf", "rw2"]

    def get_search_paths(self) -> list[Path]:
        if platform.system() == "Darwin":
            return [
                Path("/Applications/Topaz Photo AI.app/Contents/Resources/bin/tpai"),
                Path("/Applications/Topaz Photo AI.app/Contents/MacOS/Topaz Photo AI"),
                Path.home() / "Applications/Topaz Photo AI.app/Contents/Resources/bin/tpai",
            ]
        if platform.system() == "Windows":
            return [
                Path("C:/Program Files/Topaz Labs LLC/Topaz Photo AI/tpai.exe"),
                Path("C:/Program Files (x86)/Topaz Labs LLC/Topaz Photo AI/tpai.exe"),
            ]
        return [Path("/usr/local/bin/tpai"), Path("/opt/photo-ai/bin/tpai")]

    def validate_params(self, **kwargs) -> None:
        self.param_handler.validate_params(**kwargs)

    def build_command(self, input_path: Path, output_path: Path, **kwargs) -> CommandList:
        executable = self.get_executable_path()
        return self.param_handler.build_command(
            executable, input_path, output_path, verbose=self.options.verbose, **kwargs
        )

    def parse_output(self, stdout: str, stderr: str) -> dict[str, Any]:
        info = {}
        if stdout:
            lines = stdout.split("\n")
            for raw_line in lines:
                line = raw_line.strip()
                if "images processed" in line.lower():
                    with contextlib.suppress(ValueError, IndexError):
                        info["images_processed"] = int(line.split()[0])
                if "autopilot:" in line.lower():
                    info["autopilot_preset"] = line.split(":")[-1].strip()
                if "enhancements applied:" in line.lower():
                    info["enhancements_applied"] = line.split(":")[-1].strip().split(", ")
        if stderr:
            error_lines = [line.strip() for line in stderr.split("\n") if line.strip()]
            if error_lines:
                info["errors"] = error_lines
        return info

    def process_batch_directory(self, input_dir: Path, output_dir: Path, **kwargs) -> list[dict[str, Any]]:
        return self.batch_handler.process_batch_directory(input_dir, output_dir, **kwargs)

    def _find_output_file(self, temp_dir: Path, input_path: Path) -> Path:
        stem = input_path.stem
        ext = input_path.suffix
        exact_file = temp_dir / input_path.name
        if exact_file.exists():
            return exact_file
        pattern = f"{stem}*{ext}"
        matching_files = list(temp_dir.glob(pattern))
        if matching_files:
            return max(matching_files, key=lambda f: f.stat().st_mtime)
        msg = f"No output files found in temporary directory {temp_dir}"
        raise ProcessingError(msg)

    def get_default_params(self) -> PhotoAIParams:
        return PhotoAIParams()

    def process(self, input_path: Path | str, output_path: Path | str | None = None, **kwargs) -> ProcessingResult:
        autopilot_params = {k: v for k, v in kwargs.items() if self.param_handler._is_autopilot_param(k)}
        if autopilot_params:
            return self._process_with_preferences(input_path, output_path, **kwargs)
        return super().process(input_path, output_path, **kwargs)

    def _process_with_preferences(
        self, input_path: Path | str, output_path: Path | str | None, **kwargs
    ) -> ProcessingResult:
        try:
            autopilot_settings = self._build_autopilot_settings(**kwargs)
            with PhotoAIPreferences() as prefs:
                backup_id = prefs.backup()
                try:
                    prefs.update_autopilot_settings(autopilot_settings)
                    logger.info("Applied enhanced autopilot settings to Photo AI preferences")
                    return super().process(input_path, output_path, **kwargs)
                finally:
                    prefs.restore(backup_id)
                    logger.info("Restored original Photo AI preferences")
        except ImportError:
            logger.warning("Preferences system not available - falling back to standard processing")
            return super().process(input_path, output_path, **kwargs)
        except Exception as e:
            logger.error(f"Error in preferences manipulation: {e}")
            return super().process(input_path, output_path, **kwargs)

    def _build_autopilot_settings(self, **kwargs):
        return PhotoAIAutopilotSettings(
            face_strength=kwargs.get("face_strength", 80),
            face_detection=kwargs.get("face_detection", "subject"),
            face_parts=kwargs.get("face_parts", ["hair", "necks"]),
            denoise_model=kwargs.get("denoise_model", "Auto"),
            denoise_levels=kwargs.get("denoise_levels", ["medium", "high", "severe"]),
            denoise_strength=kwargs.get("denoise_strength", 3),
            denoise_raw_model=kwargs.get("denoise_raw_model", "Auto"),
            denoise_raw_levels=kwargs.get("denoise_raw_levels", ["low", "medium", "high", "severe"]),
            denoise_raw_strength=kwargs.get("denoise_raw_strength", 3),
            sharpen_model=kwargs.get("sharpen_model", "Auto"),
            sharpen_levels=kwargs.get("sharpen_levels", ["medium", "high"]),
            sharpen_strength=kwargs.get("sharpen_strength", 3),
            upscaling_model=kwargs.get("upscaling_model", "High Fidelity V2"),
            upscaling_factor=kwargs.get("upscaling_factor", 2.0),
            upscaling_type=kwargs.get("upscaling_type", "auto"),
            deblur_strength=kwargs.get("deblur_strength", 3),
            denoise_upscale_strength=kwargs.get("denoise_upscale_strength", 3),
            lighting_strength=kwargs.get("lighting_strength", 25),
            raw_exposure_strength=kwargs.get("raw_exposure_strength", 8),
            adjust_color=kwargs.get("adjust_color", False),
            temperature_value=kwargs.get("temperature_value", 50),
            opacity_value=kwargs.get("opacity_value", 100),
            resolution_unit=kwargs.get("resolution_unit", 1),
            default_resolution=kwargs.get("default_resolution", -1.0),
            overwrite_files=kwargs.get("overwrite_files", False),
            recurse_directories=kwargs.get("recurse_directories", False),
            append_filters=kwargs.get("append_filters", False),
        )
