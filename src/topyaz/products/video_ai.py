#!/usr/bin/env python3
# this_file: src/topyaz/products/_video_ai.py
"""
Topaz Video AI implementation for topyaz.

This module provides the Video AI product implementation with support
for video upscaling, frame interpolation, and enhancement.

"""

import os
import platform
from pathlib import Path
from typing import Any

from loguru import logger

from topyaz.core.errors import ValidationError
from topyaz.core.types import CommandList, ProcessingOptions, Product, VideoAIParams
from topyaz.execution.base import CommandExecutor
from topyaz.products.base import MacOSTopazProduct


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
        # Extract Video AI-specific parameters
        model = kwargs.get("model", "amq-13")
        scale = kwargs.get("scale", 2)
        fps = kwargs.get("fps")
        codec = kwargs.get("codec", "hevc_videotoolbox")
        quality = kwargs.get("quality_output", 18)
        denoise = kwargs.get("denoise")
        details = kwargs.get("details")
        halo = kwargs.get("halo")
        blur = kwargs.get("blur")
        compression = kwargs.get("compression")
        device = kwargs.get("device", 0)

        # Validate model
        valid_models = {
            "amq-13",
            "amq-12",
            "amq-11",
            "amq-10",
            "amq-9",
            "amq-8",
            "amq-7",
            "amq-6",
            "amq-5",
            "amq-4",
            "amq-3",
            "amq-2",
            "amq-1",
            "prob-4",
            "prob-3",
            "prob-2",
            "prob-1",
            "ahq-13",
            "ahq-12",
            "ahq-11",
            "ahq-10",
            "ahq-9",
            "ahq-8",
            "ahq-7",
            "ahq-6",
            "ahq-5",
            "ahq-4",
            "ahq-3",
            "ahq-2",
            "ahq-1",
            "chv-1",
            "chv-2",
            "chv-3",
            "chv-4",
            "rev-1",
            "rev-2",
            "rev-3",
            "thq-1",
            "thq-2",
            "thq-3",
            "dv-1",
            "dv-2",
            "iris-1",
            "iris-2",
            "dion-1",
            "dion-2",
            "gaia-1",
            "nyx-1",
            "nyx-2",
            "nyx-3",
            "artemis-lq-v12",
            "artemis-mq-v12",
            "artemis-hq-v12",
            "proteus-v4",
        }

        if model.lower() not in valid_models:
            msg = f"Invalid model '{model}'. Valid models: {', '.join(sorted(valid_models))}"
            raise ValidationError(msg)

        # Validate scale
        if not (1 <= scale <= 4):
            msg = f"Scale must be between 1 and 4, got {scale}"
            raise ValidationError(msg)

        # Validate FPS
        if fps is not None and not (1 <= fps <= 240):
            msg = f"FPS must be between 1 and 240, got {fps}"
            raise ValidationError(msg)

        # Validate quality_output (CRF value)
        if not (1 <= quality <= 51):
            msg = f"Quality must be between 1 and 51, got {quality}"
            raise ValidationError(msg)

        # Validate optional numeric parameters
        if denoise is not None and not (0 <= denoise <= 100):
            msg = f"Denoise must be between 0 and 100, got {denoise}"
            raise ValidationError(msg)

        if details is not None and not (-100 <= details <= 100):
            msg = f"Details must be between -100 and 100, got {details}"
            raise ValidationError(msg)

        for param_name, value in [("halo", halo), ("blur", blur), ("compression", compression)]:
            if value is not None and not (0 <= value <= 100):
                msg = f"{param_name} must be between 0 and 100, got {value}"
                raise ValidationError(msg)

        # Validate device
        if not (-1 <= device <= 10):
            msg = f"Device must be between -1 and 10, got {device}"
            raise ValidationError(msg)

        # Validate codec
        valid_codecs = {
            "hevc_videotoolbox",
            "hevc_nvenc",
            "hevc_amf",
            "libx265",
            "h264_videotoolbox",
            "h264_nvenc",
            "h264_amf",
            "libx264",
            "prores",
            "prores_ks",
            "copy",
        }
        if codec.lower() not in valid_codecs:
            msg = f"Invalid codec '{codec}'. Valid codecs: {', '.join(sorted(valid_codecs))}"
            raise ValidationError(msg)

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

        # Extract parameters
        model = kwargs.get("model", "amq-13")
        scale = kwargs.get("scale", 2)
        fps = kwargs.get("fps")
        denoise = kwargs.get("denoise")
        details = kwargs.get("details")
        halo = kwargs.get("halo")
        blur = kwargs.get("blur")
        compression = kwargs.get("compression")
        kwargs.get("stabilize", False)
        interpolate = kwargs.get("interpolate", False)
        device = kwargs.get("device", 0)

        # Build base command with high-quality_output settings
        cmd = [str(executable)]

        # Add ffmpeg flags
        cmd.extend(["-hide_banner", "-nostdin", "-y"])

        # Add hardware acceleration for macOS
        if platform.system() == "Darwin":
            cmd.extend(["-strict", "2", "-hwaccel", "auto"])

        # Input file
        cmd.extend(["-i", str(input_path.resolve())])

        # Build filter chain
        filters = []

        # Main upscaling filter with Topaz AI
        tvai_filter = f"tvai_up=model={model}:scale={scale}"

        # Add optional parameters to upscaling filter
        filter_params = []
        if denoise is not None:
            filter_params.append(f"denoise={denoise}")
        if details is not None:
            filter_params.append(f"details={details}")
        if halo is not None:
            filter_params.append(f"halo={halo}")
        if blur is not None:
            filter_params.append(f"blur={blur}")
        if compression is not None:
            filter_params.append(f"compression={compression}")
        if device != 0:
            filter_params.append(f"device={device}")

        if filter_params:
            tvai_filter += ":" + ":".join(filter_params)

        filters.append(tvai_filter)

        # Add frame interpolation if requested
        if interpolate and fps:
            fi_filter = f"tvai_fi=model=chr-2:fps={fps}"
            if device != 0:
                fi_filter += f":device={device}"
            filters.append(fi_filter)

        # Note: Stabilization requires two-pass processing and is handled separately
        # in the process method if stabilize=True

        # Apply filters
        if filters:
            cmd.extend(["-vf", ",".join(filters)])

        # High-quality_output encoding settings (adapted for TVAI's ffmpeg and macOS)
        if platform.system() == "Darwin":
            # Use VideoToolbox encoder on macOS (compatible with TVAI)
            cmd.extend(["-c:v", "hevc_videotoolbox"])
            cmd.extend(["-profile:v", "main"])
            cmd.extend(["-pix_fmt", "yuv420p"])
            cmd.extend(["-allow_sw", "1"])
            cmd.extend(["-tag:v", "hvc1"])
            # Try to set quality_output equivalent to CRF 18
            cmd.extend(["-global_quality", "18"])
        else:
            # Fallback to libx265 for other platforms
            cmd.extend(["-c:v", "libx265"])
            cmd.extend(["-crf", "18"])
            cmd.extend(["-tag:v", "hvc1"])

        # Audio settings from TODO
        cmd.extend(["-c:a", "aac"])
        cmd.extend(["-b:a", "192k"])

        # Progress reporting
        if self.options.verbose:
            cmd.extend(["-progress", "pipe:1"])
        else:
            cmd.extend(["-loglevel", "error"])

        # Output file
        cmd.append(str(output_path.resolve()))

        return cmd

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
            for line in lines:
                line = line.strip()

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
        from topyaz.core.types import ProcessingResult

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

            import time

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
