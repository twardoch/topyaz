#!/usr/bin/env python3
# this_file: src/topyaz/products/_gigapixel.py
"""
Topaz Gigapixel AI implementation for topyaz.

This module provides the Gigapixel AI product implementation with support
for upscaling, denoising, and enhancement of images.

"""

import contextlib
import platform
from pathlib import Path
from typing import Any

# from loguru import logger # F401: Unused import
from topyaz.core.errors import ProcessingError, ValidationError
from topyaz.core.types import CommandList, GigapixelParams, ProcessingOptions, Product
from topyaz.execution.base import CommandExecutor
from topyaz.products.base import MacOSTopazProduct

# Constants for Gigapixel AI parameter validation
GIGA_MAX_SCALE = 6
GIGA_MAX_EFFECT_STRENGTH = 100  # For denoise, sharpen, etc.
GIGA_MAX_CREATIVITY_TEXTURE = 6
GIGA_MAX_QUALITY = 100
GIGA_MAX_PARALLEL_READ = 10


class GigapixelAI(MacOSTopazProduct):
    """
    Topaz Gigapixel AI implementation.

    Provides image upscaling and enhancement capabilities using Gigapixel AI's
    various models and processing _options.

    Used in:
    - topyaz/cli.py
    - topyaz/products/__init__.py
    - topyaz/products/base.py
    """

    def __init__(self, executor: CommandExecutor, options: ProcessingOptions):
        """
        Initialize Gigapixel AI instance.

        Args:
            executor: Command _executor for running operations
            options: Processing _options and configuration

        """
        super().__init__(executor, options, Product.GIGAPIXEL)

    @property
    def product_name(self) -> str:
        """Human-readable product name."""
        return "Topaz Gigapixel AI"

    @property
    def executable_name(self) -> str:
        """Name of the executable file."""
        return "gigapixel"

    @property
    def app_name(self) -> str:
        """Name of the macOS application."""
        return "Topaz Gigapixel AI.app"

    @property
    def app_executable_path(self) -> str:
        """Relative path to executable within app bundle."""
        return "Contents/Resources/bin/gigapixel"

    @property
    def supported_formats(self) -> list[str]:
        """List of supported file formats."""
        return ["jpg", "jpeg", "png", "tiff", "tif", "bmp", "webp"]

    def get_search_paths(self) -> list[Path]:
        """Get platform-specific search paths for Gigapixel AI."""
        if platform.system() == "Darwin":
            # macOS paths
            return [
                Path("/Applications/Topaz Gigapixel AI.app/Contents/Resources/bin/gigapixel"),
                Path("/Applications/Topaz Gigapixel AI.app/Contents/MacOS/Topaz Gigapixel AI"),
                Path.home() / "Applications/Topaz Gigapixel AI.app/Contents/Resources/bin/gigapixel",
            ]
        if platform.system() == "Windows":
            # Windows paths
            return [
                Path("C:/Program Files/Topaz Labs LLC/Topaz Gigapixel AI/bin/_gigapixel.exe"),
                Path("C:/Program Files (x86)/Topaz Labs LLC/Topaz Gigapixel AI/bin/_gigapixel.exe"),
            ]
        # Linux or other platforms
        return [Path("/usr/local/bin/_gigapixel"), Path("/opt/_gigapixel/bin/_gigapixel")]

    def validate_params(self, **kwargs) -> None:
        """
        Validate Gigapixel AI parameters.

        Args:
            **kwargs: Parameters to validate

        Raises:
            ValidationError: If parameters are invalid

        """
        # Extract Gigapixel-specific parameters
        model = kwargs.get("model", "std")
        scale = kwargs.get("scale", 2)
        denoise = kwargs.get("denoise")
        sharpen = kwargs.get("sharpen")
        compression = kwargs.get("compression")
        detail = kwargs.get("detail")
        creativity = kwargs.get("creativity")
        texture = kwargs.get("texture")
        face_recovery = kwargs.get("face_recovery")
        face_recovery_version = kwargs.get("face_recovery_version", 2)
        format_param = kwargs.get("format_output", "preserve")
        quality = kwargs.get("quality_output", 95)
        bit_depth = kwargs.get("bit_depth", 0)
        parallel_read = kwargs.get("parallel_read", 1)

        # Validate model
        valid_models = {
            "std",
            "standard",
            "hf",
            "high fidelity",
            "fidelity",
            "low",
            "lowres",
            "low resolution",
            "low res",
            "art",
            "cg",
            "cgi",
            "lines",
            "compression",
            "very compressed",
            "high compression",
            "vc",
            "text",
            "txt",
            "text refine",
            "recovery",
            "redefine",
        }
        if model.lower() not in valid_models:
            msg = f"Invalid model '{model}'. Valid models: {', '.join(sorted(valid_models))}"
            raise ValidationError(msg)

        # Validate scale
        if not (1 <= scale <= GIGA_MAX_SCALE):
            msg = f"Scale must be between 1 and {GIGA_MAX_SCALE}, got {scale}"
            raise ValidationError(msg)

        # Validate optional numeric parameters
        numeric_params = {
            "denoise": denoise,
            "sharpen": sharpen,
            "compression": compression,
            "detail": detail,
            "face_recovery": face_recovery,
        }

        for param_name, value in numeric_params.items():
            if value is not None and not (1 <= value <= GIGA_MAX_EFFECT_STRENGTH):
                msg = f"{param_name} must be between 1 and {GIGA_MAX_EFFECT_STRENGTH}, got {value}"
                raise ValidationError(msg)

        # Validate creativity and texture (special range)
        for param_name, value in [("creativity", creativity), ("texture", texture)]:
            if value is not None and not (1 <= value <= GIGA_MAX_CREATIVITY_TEXTURE):
                msg = f"{param_name} must be between 1 and {GIGA_MAX_CREATIVITY_TEXTURE}, got {value}"
                raise ValidationError(msg)

        # Validate face recovery version
        if face_recovery_version not in [1, 2]:
            msg = f"Face recovery version must be 1 or 2, got {face_recovery_version}"
            raise ValidationError(msg)

        # Validate output format_output
        valid_formats = {"preserve", "jpg", "jpeg", "png", "tif", "tiff"}
        if format_param.lower() not in valid_formats:
            msg = f"Invalid format_output '{format_param}'. Valid formats: {', '.join(sorted(valid_formats))}"
            raise ValidationError(msg)

        # Validate quality_output
        if not (1 <= quality <= GIGA_MAX_QUALITY):
            msg = f"Quality must be between 1 and {GIGA_MAX_QUALITY}, got {quality}"
            raise ValidationError(msg)

        # Validate bit depth
        if bit_depth not in [0, 8, 16]:
            msg = f"Bit depth must be 0, 8, or 16, got {bit_depth}"
            raise ValidationError(msg)

        # Validate parallel read
        if not (1 <= parallel_read <= GIGA_MAX_PARALLEL_READ):
            msg = f"Parallel read must be between 1 and {GIGA_MAX_PARALLEL_READ}, got {parallel_read}"
            raise ValidationError(msg)

    def build_command(self, input_path: Path, output_path: Path, **kwargs) -> CommandList:
        """
        Build Gigapixel AI command line using temporary output directory.

        Args:
            input_path: Input file path
            output_path: Output file path
            **kwargs: Gigapixel-specific parameters

        Returns:
            Command list ready for execution

        """
        executable = self.get_executable_path()
        cmd = [str(executable), "--cli", "-i", str(input_path.resolve()), "-o", str(output_path.resolve())]
        for key, value in kwargs.items():
            if value is not None and key not in ["output_path", "input_path"]:
                cmd.extend([f"--{key.replace('_', '-')}", str(value)])
        if self.options.verbose:
            cmd.append("--verbose")
        return cmd

    def parse_output(self, stdout: str, stderr: str) -> dict[str, Any]:
        """
        Parse Gigapixel AI command output.

        Args:
            stdout: Standard output from command
            stderr: Standard error from command

        Returns:
            Dictionary of parsed information

        """
        info = {}

        # Parse processing information from output
        lines = stdout.split("\n") if stdout else []

        for raw_line in lines:
            line = raw_line.strip()

            # Look for model information
            if "Model:" in line:
                info["model_used"] = line.split("Model:")[-1].strip()

            # Look for scale information
            if "Scale:" in line:
                with contextlib.suppress(ValueError):
                    info["scale_used"] = int(line.split("Scale:")[-1].strip().rstrip("x"))

            # Look for processing time
            if "Processing time:" in line:
                info["processing_time"] = line.split("Processing time:")[-1].strip()

            # Look for memory usage
            if "Memory used:" in line:
                info["memory_used"] = line.split("Memory used:")[-1].strip()

        # Check for licensing issues
        if stdout and ("Gigapixel CLI requires a Pro license" in stdout or stdout.strip().endswith("False")):
            info["licensing_error"] = True
            info["error_type"] = "licensing"
            info["user_message"] = (
                "Gigapixel AI CLI requires a Pro license. "
                "Please contact enterprise@topazlabs.com or upgrade your license to use CLI features. "
                "Alternatively, use the desktop application which works with your current license."
            )

        # Parse any errors from stderr
        if stderr:
            error_lines = [line.strip() for line in stderr.split("\n") if line.strip()]
            if error_lines:
                info["warnings"] = error_lines

        return info

    def get_default_params(self) -> GigapixelParams:
        """
        Get default parameters for Gigapixel AI.

        Returns:
            Default Gigapixel parameters

        """
        return GigapixelParams()

    def get_memory_requirements(self, **kwargs) -> dict[str, Any]:
        """
        Get memory requirements for processing.

        Args:
            **kwargs: Processing parameters

        Returns:
            Memory requirement information

        """
        scale = kwargs.get("scale", 2)
        model = kwargs.get("model", "std")

        # Base memory requirements (in GB)
        base_memory = 4  # Minimum for Gigapixel

        # Scale affects memory usage
        scale_multiplier = {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5, 5: 3.0, 6: 3.5}
        memory_for_scale = base_memory * scale_multiplier.get(scale, 1.0)

        # Model affects memory usage
        model_multipliers = {
            "std": 1.0,
            "standard": 1.0,
            "hf": 1.2,
            "high fidelity": 1.2,
            "fidelity": 1.2,
            "low": 0.8,
            "lowres": 0.8,
            "low resolution": 0.8,
            "low res": 0.8,
            "art": 1.3,
            "cg": 1.3,
            "cgi": 1.3,
            "lines": 1.1,
            "compression": 1.0,
            "very compressed": 1.0,
            "high compression": 1.0,
            "vc": 1.0,
            "text": 1.1,
            "txt": 1.1,
            "text refine": 1.1,
            "recovery": 1.2,
            "redefine": 1.4,
        }

        model_multiplier = model_multipliers.get(model.lower(), 1.0)
        total_memory = memory_for_scale * model_multiplier

        return {
            "minimum_memory_gb": base_memory,
            "recommended_memory_gb": total_memory,
            "scale_factor": scale,
            "model": model,
            "notes": "Memory usage varies by image size and complexity. "
            "Large images (>20MP) may require additional memory.",
        }

    def _get_output_suffix(self) -> str:
        """Get suffix to add to output filenames."""
        return "_iGigapixelAI"

    def _find_output_file(self, temp_dir: Path, input_path: Path) -> Path:
        """Find Gigapixel AI output file in temporary directory."""
        # Gigapixel AI preserves the input filename in the output directory
        output_file = temp_dir / input_path.name
        if not output_file.exists():
            msg = f"Output file not found in temp directory: {output_file}"
            raise ProcessingError(msg)
        return output_file
