#!/usr/bin/env python3
# this_file: src/topyaz/products/photo_ai.py
"""
Topaz Photo AI implementation for topyaz.

This module provides the Photo AI product implementation with support
for automatic and manual photo enhancement, including batch processing
with Photo AI's 450 image limit handling.

"""

import platform
import shutil
import tempfile
from pathlib import Path
from typing import Any, Optional

from loguru import logger

from topyaz.core.errors import ProcessingError, ValidationError
from topyaz.core.types import CommandList, PhotoAIParams, ProcessingOptions, Product
from topyaz.execution.base import CommandExecutor
from topyaz.products.base import MacOSTopazProduct


class PhotoAI(MacOSTopazProduct):
    """
    Topaz Photo AI implementation.

    Provides automatic and manual photo enhancement capabilities with
    support for batch processing and Photo AI's specific constraints.

    Used in:
    - topyaz/cli.py
    - topyaz/products/__init__.py
    - topyaz/products/base.py
    """

    # Photo AI has a hard limit of ~450 images per batch
    MAX_BATCH_SIZE = 400  # Conservative limit

    def __init__(self, executor: CommandExecutor, options: ProcessingOptions):
        """
        Initialize Photo AI instance.

        Args:
            executor: Command executor for running operations
            options: Processing options and configuration

        """
        super().__init__(executor, options, Product.PHOTO_AI)

    @property
    def product_name(self) -> str:
        """Human-readable product name."""
        return "Topaz Photo AI"

    @property
    def executable_name(self) -> str:
        """Name of the executable file."""
        return "tpai"

    @property
    def app_name(self) -> str:
        """Name of the macOS application."""
        return "Topaz Photo AI.app"

    @property
    def app_executable_path(self) -> str:
        """Relative path to executable within app bundle."""
        return "Contents/Resources/bin/tpai"

    @property
    def supported_formats(self) -> list[str]:
        """List of supported image formats."""
        return ["jpg", "jpeg", "png", "tiff", "tif", "bmp", "webp", "dng", "raw", "cr2", "nef", "arw", "orf", "rw2"]

    def get_search_paths(self) -> list[Path]:
        """Get platform-specific search paths for Photo AI."""
        if platform.system() == "Darwin":
            # macOS paths
            return [
                Path("/Applications/Topaz Photo AI.app/Contents/Resources/bin/tpai"),
                Path("/Applications/Topaz Photo AI.app/Contents/MacOS/Topaz Photo AI"),
                Path.home() / "Applications/Topaz Photo AI.app/Contents/Resources/bin/tpai",
            ]
        if platform.system() == "Windows":
            # Windows paths
            return [
                Path("C:/Program Files/Topaz Labs LLC/Topaz Photo AI/tpai.exe"),
                Path("C:/Program Files (x86)/Topaz Labs LLC/Topaz Photo AI/tpai.exe"),
            ]
        # Linux or other platforms
        return [Path("/usr/local/bin/tpai"), Path("/opt/photo-ai/bin/tpai")]

    def validate_params(self, **kwargs) -> None:
        """
        Validate Photo AI parameters.

        Args:
            **kwargs: Parameters to validate

        Raises:
            ValidationError: If parameters are invalid

        """
        # Extract Photo AI-specific parameters
        format_param = kwargs.get("format", "preserve")
        quality = kwargs.get("quality", 95)
        compression = kwargs.get("compression", 6)
        bit_depth = kwargs.get("bit_depth", 8)
        tiff_compression = kwargs.get("tiff_compression", "lzw")

        # Validate output format
        valid_formats = {"preserve", "jpg", "jpeg", "png", "tif", "tiff", "dng"}
        if format_param.lower() not in valid_formats:
            msg = f"Invalid format '{format_param}'. Valid formats: {', '.join(sorted(valid_formats))}"
            raise ValidationError(msg)

        # Validate quality (for JPEG)
        if not (0 <= quality <= 100):
            msg = f"Quality must be between 0 and 100, got {quality}"
            raise ValidationError(msg)

        # Validate compression (for PNG)
        if not (0 <= compression <= 10):
            msg = f"Compression must be between 0 and 10, got {compression}"
            raise ValidationError(msg)

        # Validate bit depth (for TIFF)
        if bit_depth not in [8, 16]:
            msg = f"Bit depth must be 8 or 16, got {bit_depth}"
            raise ValidationError(msg)

        # Validate TIFF compression
        valid_tiff_compression = {"none", "lzw", "zip"}
        if tiff_compression.lower() not in valid_tiff_compression:
            msg = (
                f"Invalid TIFF compression '{tiff_compression}'. "
                f"Valid options: {', '.join(sorted(valid_tiff_compression))}"
            )
            raise ValidationError(msg)

    def build_command(self, input_path: Path, output_path: Path, **kwargs) -> CommandList:
        """
        Build Photo AI command line.

        Args:
            input_path: Input file or directory path
            output_path: Output file or directory path
            **kwargs: Photo AI-specific parameters

        Returns:
            Command list ready for execution

        """
        executable = self.get_executable_path()

        # Extract parameters
        autopilot_preset = kwargs.get("autopilot_preset", "auto")
        format_param = kwargs.get("format", "preserve")
        quality = kwargs.get("quality", 95)
        compression = kwargs.get("compression", 6)
        bit_depth = kwargs.get("bit_depth", 8)
        tiff_compression = kwargs.get("tiff_compression", "lzw")
        show_settings = kwargs.get("show_settings", False)
        skip_processing = kwargs.get("skip_processing", False)
        override_autopilot = kwargs.get("override_autopilot", False)

        # Enhancement toggles
        upscale = kwargs.get("upscale")
        noise = kwargs.get("noise")
        sharpen = kwargs.get("sharpen")
        lighting = kwargs.get("lighting")
        color = kwargs.get("color")

        # Build base command
        cmd = [str(executable), "--cli"]

        # Add input and output paths
        cmd.extend(["-i", str(input_path)])
        cmd.extend(["-o", str(output_path)])

        # Add autopilot preset
        if autopilot_preset and autopilot_preset != "auto":
            cmd.extend(["--autopilot", autopilot_preset])

        # Add output format
        if format_param.lower() != "preserve":
            cmd.extend(["-f", format_param])

        # Add format-specific options
        if format_param.lower() in ["jpg", "jpeg"]:
            cmd.extend(["-q", str(quality)])
        elif format_param.lower() == "png":
            cmd.extend(["-c", str(compression)])
        elif format_param.lower() in ["tif", "tiff"]:
            cmd.extend(["-d", str(bit_depth)])
            cmd.extend(["-tc", tiff_compression])

        # Add debug options
        if show_settings:
            cmd.append("--showSettings")

        if skip_processing:
            cmd.append("--skipProcessing")

        # Add override autopilot if manual enhancements are specified
        if override_autopilot or any([upscale, noise, sharpen, lighting, color]):
            cmd.append("--override")

            # Add enhancement toggles with proper boolean formatting
            self._add_boolean_parameter(cmd, "upscale", upscale)
            self._add_boolean_parameter(cmd, "noise", noise)
            self._add_boolean_parameter(cmd, "sharpen", sharpen)
            self._add_boolean_parameter(cmd, "lighting", lighting)
            self._add_boolean_parameter(cmd, "color", color)

        # Add directory processing flag if input is a directory
        if input_path.is_dir():
            cmd.append("--recursive")

        # Add verbose output if requested
        if self.options.verbose:
            cmd.append("--verbose")

        return cmd

    def _add_boolean_parameter(self, cmd: CommandList, param_name: str, value: bool | None) -> None:
        """
        Add boolean parameter to command with Photo AI's specific formatting.

        Args:
            cmd: Command list to modify
            param_name: Parameter name
            value: Parameter value (True, False, or None)

        """
        if value is True:
            # Enabled: just add the flag
            cmd.append(f"--{param_name}")
        elif value is False:
            # Disabled: add flag with enabled=false
            cmd.append(f"--{param_name}")
            cmd.append("enabled=false")
        # None: don't add anything (use autopilot)

    def parse_output(self, stdout: str, stderr: str) -> dict[str, Any]:
        """
        Parse Photo AI command output.

        Args:
            stdout: Standard output from command
            stderr: Standard error from command

        Returns:
            Dictionary of parsed information

        """
        info = {}

        # Parse processing information from output
        if stdout:
            lines = stdout.split("\n")
            for line in lines:
                line = line.strip()

                # Look for processed file count
                if "images processed" in line.lower():
                    try:
                        count = int(line.split()[0])
                        info["images_processed"] = count
                    except (ValueError, IndexError):
                        pass

                # Look for autopilot information
                if "autopilot:" in line.lower():
                    info["autopilot_preset"] = line.split(":")[-1].strip()

                # Look for enhancement information
                if "enhancements applied:" in line.lower():
                    enhancements = line.split(":")[-1].strip()
                    info["enhancements_applied"] = enhancements.split(", ")

        # Parse error information
        if stderr:
            error_lines = [line.strip() for line in stderr.split("\n") if line.strip()]
            if error_lines:
                info["errors"] = error_lines

        return info

    def process_batch_directory(self, input_dir: Path, output_dir: Path, **kwargs) -> list[dict[str, Any]]:
        """
        Process directory with Photo AI's 450 image batch limit handling.

        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            **kwargs: Photo AI parameters

        Returns:
            List of batch results

        Used in:
        - topyaz/cli.py
        """
        # Find all supported image files
        image_files = []
        for ext in self.supported_formats:
            # Case-insensitive glob
            image_files.extend(input_dir.rglob(f"*.{ext}"))
            image_files.extend(input_dir.rglob(f"*.{ext.upper()}"))

        if not image_files:
            logger.warning(f"No supported image files found in {input_dir}")
            return []

        logger.info(f"Found {len(image_files)} images to process")

        # Split into batches
        batches = [image_files[i : i + self.MAX_BATCH_SIZE] for i in range(0, len(image_files), self.MAX_BATCH_SIZE)]

        logger.info(f"Processing {len(batches)} batch(es) of up to {self.MAX_BATCH_SIZE} images each")

        results = []

        for batch_num, batch_files in enumerate(batches, 1):
            logger.info(f"Processing batch {batch_num}/{len(batches)} ({len(batch_files)} images)")

            try:
                result = self._process_batch(batch_files, output_dir, batch_num, **kwargs)
                results.append(result)

                if not result.get("success", False):
                    logger.error(f"Batch {batch_num} failed")
                    break

            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {e}")
                results.append(
                    {"batch_num": batch_num, "success": False, "error": str(e), "files_count": len(batch_files)}
                )
                break

        return results

    def _process_batch(self, batch_files: list[Path], output_dir: Path, batch_num: int, **kwargs) -> dict[str, Any]:
        """
        Process a single batch of images.

        Args:
            batch_files: List of image files to process
            output_dir: Output directory
            batch_num: Batch number for logging
            **kwargs: Photo AI parameters

        Returns:
            Batch processing result

        """
        # Create temporary directory for batch processing
        with tempfile.TemporaryDirectory(prefix=f"topyaz_batch_{batch_num}_") as temp_dir:
            temp_path = Path(temp_dir)
            batch_input_dir = temp_path / "input"
            batch_input_dir.mkdir()

            # Create symlinks (or copy files) to batch directory
            for file_path in batch_files:
                target_path = batch_input_dir / file_path.name

                try:
                    # Try to create symlink first (faster)
                    target_path.symlink_to(file_path)
                except OSError:
                    # Fall back to copying if symlinks not supported
                    shutil.copy2(file_path, target_path)

            # Build command for batch processing
            cmd = self.build_command(batch_input_dir, output_dir, **kwargs)

            # Execute batch
            try:
                exit_code, stdout, stderr = self.executor.execute(cmd, timeout=self.options.timeout)

                success = self._handle_photo_ai_result(exit_code, stdout, stderr, batch_num)

                return {
                    "batch_num": batch_num,
                    "success": success,
                    "exit_code": exit_code,
                    "files_count": len(batch_files),
                    "stdout": stdout,
                    "stderr": stderr,
                }

            except Exception as e:
                logger.error(f"Batch {batch_num} execution failed: {e}")
                return {
                    "batch_num": batch_num,
                    "success": False,
                    "error": str(e),
                    "files_count": len(batch_files),
                }

    def _handle_photo_ai_result(self, exit_code: int, stdout: str, stderr: str, batch_num: int) -> bool:
        """
        Handle Photo AI-specific return codes.

        Args:
            exit_code: Command exit code
            stdout: Standard output
            stderr: Standard error
            batch_num: Batch number for logging

        Returns:
            True if processing was successful

        """
        if exit_code == 0:
            logger.info(f"Batch {batch_num} completed successfully")
            return True
        if exit_code == 1:
            logger.warning(f"Batch {batch_num} completed with some failures (partial success)")
            return True  # Partial success is still acceptable
        if exit_code == 255:  # -1 as unsigned
            logger.error(f"Batch {batch_num} failed: No valid files found")
            return False
        if exit_code == 254:  # -2 as unsigned
            logger.error(f"Batch {batch_num} failed: Invalid log token - login required")
            msg = "Photo AI authentication required. Please log in via the Photo AI GUI."
            raise ProcessingError(msg)
        if exit_code == 253:  # -3 as unsigned
            logger.error(f"Batch {batch_num} failed: Invalid argument")
            if stderr:
                logger.error(f"Error details: {stderr}")
            return False
        logger.error(f"Batch {batch_num} failed with exit code {exit_code}")
        if stderr:
            logger.error(f"Error details: {stderr}")
        return False

    def get_default_params(self) -> PhotoAIParams:
        """
        Get default parameters for Photo AI.

        Returns:
            Default Photo AI parameters

        """
        return PhotoAIParams()

    def get_memory_requirements(self, **kwargs) -> dict[str, Any]:
        """
        Get memory requirements for Photo AI processing.

        Args:
            **kwargs: Processing parameters

        Returns:
            Memory requirement information

        """
        # Photo AI memory usage is relatively predictable
        base_memory = 4  # Minimum for Photo AI

        # Batch size affects memory usage
        batch_size = min(kwargs.get("batch_size", self.MAX_BATCH_SIZE), self.MAX_BATCH_SIZE)

        # Memory scales with batch size
        if batch_size <= 100:
            recommended_memory = 8
        elif batch_size <= 200:
            recommended_memory = 12
        else:
            recommended_memory = 16

        return {
            "minimum_memory_gb": base_memory,
            "recommended_memory_gb": recommended_memory,
            "max_batch_size": self.MAX_BATCH_SIZE,
            "current_batch_size": batch_size,
            "notes": "Photo AI has a hard limit of ~450 images per batch. "
            "Memory usage scales with batch size and image resolution.",
        }

    def _get_output_suffix(self) -> str:
        """Get suffix to add to output filenames."""
        return "_photo_ai"
