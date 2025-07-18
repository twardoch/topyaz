#!/usr/bin/env python3
# this_file: src/topyaz/products/video_ai/api.py
"""
Topaz Video AI implementation for topyaz.

This module provides the Video AI product implementation with support
for video upscaling, frame interpolation, and enhancement.

"""

import os
import platform
import time  # Moved from process method
from pathlib import Path
from typing import Any

from loguru import logger

# from topyaz.core.errors import ValidationError # F401: Unused import
# ProcessingResult moved here from process method
from topyaz.core.types import CommandList, ProcessingOptions, ProcessingResult, Product
from topyaz.execution.base import CommandExecutor
from topyaz.products.base import MacOSTopazProduct
from topyaz.products.video_ai.params import VideoAIParams  # Kept this direct import


class VideoAI(MacOSTopazProduct):
    """
    Topaz Video AI implementation.

    Provides video upscaling, frame interpolation, and enhancement capabilities
    using Video AI's FFmpeg-based processing pipeline.

    Used in:
    - topyaz/cli.py
    - topyaz/products/__init__.py
    - topyaz/products/base.py
    """

    def __init__(self, executor: CommandExecutor, options: ProcessingOptions):
        """
        Initialize Video AI instance.

        Args:
            executor: Command _executor for running operations
            options: Processing _options and configuration

        """
        super().__init__(executor, options, Product.VIDEO_AI)
        self.param_handler = VideoAIParams()
        self._setup_environment()

    @property
    def product_name(self) -> str:
        """Human-readable product name."""
        return "Topaz Video AI"

    @property
    def executable_name(self) -> str:
        """Name of the executable file."""
        return "ffmpeg"

    @property
    def app_name(self) -> str:
        """Name of the macOS application."""
        return "Topaz Video AI.app"

    @property
    def app_executable_path(self) -> str:
        """Relative path to executable within app bundle."""
        return "Contents/MacOS/ffmpeg"

    @property
    def supported_formats(self) -> list[str]:
        """List of supported video formats."""
        return [
            "mp4",
            "mov",
            "avi",
            "mkv",
            "webm",
            "m4v",
            "3gp",
            "flv",
            "wmv",
            "asf",
            "m2ts",
            "mts",
            "ts",
            "vob",
            "ogv",
            "dv",
        ]

    def get_search_paths(self) -> list[Path]:
        """Get platform-specific search paths for Video AI."""
        if platform.system() == "Darwin":
            # macOS paths
            return [
                Path("/Applications/Topaz Video AI.app/Contents/MacOS/ffmpeg"),
                Path.home() / "Applications/Topaz Video AI.app/Contents/MacOS/ffmpeg",
            ]
        if platform.system() == "Windows":
            # Windows paths
            return [
                Path("C:/Program Files/Topaz Labs LLC/Topaz Video AI/ffmpeg.exe"),
                Path("C:/Program Files (x86)/Topaz Labs LLC/Topaz Video AI/ffmpeg.exe"),
            ]
        # Linux or other platforms
        return [Path("/usr/local/bin/tvai-ffmpeg"), Path("/opt/video-ai/bin/ffmpeg")]

    def _setup_environment(self) -> None:
        """Set up Video AI environment variables."""
        try:
            if platform.system() == "Darwin":
                # macOS paths
                model_dir = "/Applications/Topaz Video AI.app/Contents/Resources/models"
                user_data_dir = str(Path.home() / "Library/Application Support/Topaz Labs LLC/Topaz Video AI/models")
            elif platform.system() == "Windows":
                # Windows paths
                model_dir = "C:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\models"
                user_data_dir = str(Path.home() / "AppData/Roaming/Topaz Labs LLC/Topaz Video AI/models")
            else:
                # Linux fallback
                model_dir = "/opt/video-ai/models"
                user_data_dir = str(Path.home() / "._config/topaz-video-ai/models")

            # Set environment variables
            os.environ["TVAI_MODEL_DIR"] = model_dir
            os.environ["TVAI_MODEL_DATA_DIR"] = user_data_dir

            logger.debug(f"Set TVAI_MODEL_DIR to: {model_dir}")
            logger.debug(f"Set TVAI_MODEL_DATA_DIR to: {user_data_dir}")

            # Validate authentication
            self._validate_authentication()

        except Exception as e:
            logger.warning(f"Could not set up Video AI environment: {e}")

    def _validate_authentication(self) -> None:
        """Validate Video AI authentication."""
        try:
            auth_locations = self._get_auth_file_locations()

            for auth_path in auth_locations:
                if auth_path.exists():
                    logger.debug(f"Found Video AI auth file: {auth_path}")

                    # Check if auth file is valid (basic existence check)
                    if auth_path.stat().st_size > 0:
                        logger.debug("Video AI authentication appears valid")
                        return
                    logger.warning(f"Video AI auth file is empty: {auth_path}")

            logger.debug("No Video AI auth files found - user may need to log in via GUI")

        except Exception as e:
            logger.warning(f"Could not validate Video AI authentication: {e}")

    def _get_auth_file_locations(self) -> list[Path]:
        """Get potential authentication file locations."""
        locations = []

        if platform.system() == "Darwin":
            # macOS locations
            base_path = Path.home() / "Library/Application Support/Topaz Labs LLC/Topaz Video AI"
            app_path = Path("/Applications/Topaz Video AI.app/Contents/Resources/models")

            # User data directory
            for auth_file in ["auth.tpz", "auth.json", "login.json", "user.json"]:
                locations.append(base_path / auth_file)

            # Application bundle
            locations.append(app_path / "auth.tpz")

        elif platform.system() == "Windows":
            # Windows locations
            base_path = Path.home() / "AppData/Roaming/Topaz Labs LLC/Topaz Video AI"

            for auth_file in ["auth.tpz", "auth.json", "login.json", "user.json"]:
                locations.append(base_path / auth_file)

        return locations

    def validate_params(self, **kwargs) -> None:
        """
        Validate Video AI parameters.

        Args:
            **kwargs: Parameters to validate

        Raises:
            ValidationError: If parameters are invalid

        """
        self.param_handler.validate_params(**kwargs)

    def build_command(self, input_path: Path, output_path: Path, **kwargs) -> CommandList:
        """
        Build Video AI command line with Topaz AI filters and high-quality_output encoding.

        Combines Topaz Video AI filters (tvai_up, tvai_fi, tvai_stb) with
        high-quality_output H.265 encoding settings as specified in TODO.

        Args:
            input_path: Input video file path
            output_path: Output video file path
            **kwargs: Video AI-specific parameters

        Returns:
            Command list ready for execution

        """
        executable = self.get_executable_path()
        return self.param_handler.build_command(
            executable, input_path, output_path, verbose=self.options.verbose, **kwargs
        )

    def parse_output(self, stdout: str, stderr: str) -> dict[str, Any]:
        """
        Parse Video AI FFmpeg output.

        Args:
            stdout: Standard output from command
            stderr: Standard error from command

        Returns:
            Dictionary of parsed information

        """
        info = {}

        # Parse FFmpeg progress output
        if stdout:
            lines = stdout.split("\n")
            for raw_line in lines:
                line = raw_line.strip()

                # Parse progress information
                if "frame=" in line:
                    try:
                        frame_match = line.split("frame=")[1].split()[0]
                        info["frames_processed"] = int(frame_match)
                    except (IndexError, ValueError):
                        pass

                if "time=" in line:
                    try:
                        time_match = line.split("time=")[1].split()[0]
                        info["time_processed"] = time_match
                    except IndexError:
                        pass

                if "speed=" in line:
                    try:
                        speed_match = line.split("speed=")[1].split()[0]
                        info["processing_speed"] = speed_match
                    except IndexError:
                        pass

        # Parse error information
        if stderr:
            error_lines = [line.strip() for line in stderr.split("\n") if line.strip()]
            if error_lines:
                info["errors"] = error_lines

        return info

    def get_default_params(self) -> VideoAIParams:
        """
        Get default parameters for Video AI.

        Returns:
            Default Video AI parameters

        """
        return VideoAIParams()

    def get_memory_requirements(self, **kwargs) -> dict[str, Any]:
        """
        Get memory requirements for Video AI processing.

        Args:
            **kwargs: Processing parameters

        Returns:
            Memory requirement information

        """
        scale = kwargs.get("scale", 2)
        model = kwargs.get("model", "amq-13")
        fps = kwargs.get("fps")

        # Base memory requirements (in GB)
        base_memory = 8  # Minimum for Video AI

        # Scale affects memory usage significantly for video
        scale_multiplier = {1: 1.0, 2: 2.0, 3: 3.5, 4: 5.0}
        memory_for_scale = base_memory * scale_multiplier.get(scale, 1.0)

        # Model complexity affects memory
        if "amq" in model.lower():
            model_multiplier = 1.0  # Standard models
        elif "prob" in model.lower():
            model_multiplier = 1.2  # More complex models
        elif "ahq" in model.lower():
            model_multiplier = 1.1  # High quality_output models
        else:
            model_multiplier = 1.0  # Default

        # Frame interpolation increases memory usage
        if fps:
            memory_for_scale *= 1.5

        total_memory = memory_for_scale * model_multiplier

        return {
            "minimum_memory_gb": base_memory,
            "recommended_memory_gb": total_memory,
            "scale_factor": scale,
            "model": model,
            "frame_interpolation": fps is not None,
            "notes": "Video processing is memory-intensive. "
            "4K videos may require 16GB+ RAM. "
            "Consider processing shorter segments for large files.",
        }

    def _get_output_suffix(self) -> str:
        """Get suffix to add to output filenames."""
        return "_iVideoAI"

    def _find_output_file(self, temp_dir: Path, input_path: Path) -> Path:
        """
        VideoAI doesn't use temporary directories, so this method is not used.
        It's implemented to satisfy the abstract base class requirement.
        """
        msg = "VideoAI uses direct output writing, not temp directories"
        raise NotImplementedError(msg)

    def process(self, input_path: Path | str, output_path: Path | str | None = None, **kwargs):
        """
        Process video with Video AI using direct output approach.

        VideoAI writes directly to the final output file rather than using
        temporary directories like Gigapixel and Photo AI.

        Args:
            input_path: Input video file path
            output_path: Output video file path (optional)
            **kwargs: Video AI-specific parameters

        Returns:
            Processing result
        """
        # from topyaz.core.types import ProcessingResult # Moved to top

        # Convert to Path objects
        input_path = Path(input_path)
        if output_path:
            output_path = Path(output_path)

        # Validate inputs
        self.validate_input_path(input_path)
        self.validate_params(**kwargs)

        # Determine final output path
        if output_path:
            final_output_path = self.path_validator.validate_output_path(output_path)
        else:
            output_dir = input_path.parent
            suffix = self._get_output_suffix()
            stem = input_path.stem
            extension = ".mp4"  # VideoAI typically outputs MP4
            output_filename = f"{stem}{suffix}{extension}"
            final_output_path = output_dir / output_filename

        # Ensure executable is available
        self.get_executable_path()

        # Build command with direct output
        command = self.build_command(input_path, final_output_path, **kwargs)

        try:
            logger.info(f"Processing {input_path} with {self.product_name}")

            if self.options.dry_run:
                logger.info(f"DRY RUN: Would execute: {' '.join(command)}")
                return ProcessingResult(
                    success=True,
                    input_path=input_path,
                    output_path=final_output_path,
                    command=command,
                    stdout="DRY RUN - no output",
                    stderr="",
                    execution_time=0.0,
                    file_size_before=0,
                    file_size_after=0,
                )

                # import time # Moved to top
            start_time = time.time()
            file_size_before = input_path.stat().st_size if input_path.is_file() else 0

            # Execute the command
            exit_code, stdout, stderr = self.executor.execute(command, timeout=self.options.timeout)
            execution_time = time.time() - start_time

            # Check if processing was successful
            if exit_code != 0:
                error_msg = f"{self.product_name} processing failed (exit code {exit_code})"
                if stderr:
                    error_msg += f": {stderr}"
                return ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path=final_output_path,
                    command=command,
                    stdout=stdout,
                    stderr=stderr,
                    execution_time=execution_time,
                    file_size_before=file_size_before,
                    file_size_after=0,
                    error_message=error_msg,
                )

            # Get file size after processing
            file_size_after = final_output_path.stat().st_size if final_output_path.exists() else 0

            # Parse output for additional information
            parsed_info = self.parse_output(stdout, stderr)

            logger.info(f"Successfully processed {input_path} -> {final_output_path} in {execution_time:.2f}s")

            return ProcessingResult(
                success=True,
                input_path=input_path,
                output_path=final_output_path,
                command=command,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                file_size_before=file_size_before,
                file_size_after=file_size_after,
                additional_info=parsed_info,
            )

        except Exception as e:
            logger.error(f"Error processing {input_path} with {self.product_name}: {e}")
            return ProcessingResult(
                success=False,
                input_path=input_path,
                output_path=final_output_path,
                command=command,
                stdout="",
                stderr=str(e),
                execution_time=0.0,
                file_size_before=0,
                file_size_after=0,
                error_message=str(e),
            )
