#!/usr/bin/env python
# this_file: src/topyaz/cli.py
"""
Command-line interface for topyaz.

This module provides the main CLI wrapper that integrates all the modular
components into a unified interface compatible with the original TopyazCLI.

"""

from dataclasses import asdict
from pathlib import Path
from typing import Any

import fire
from loguru import logger

from topyaz.core.config import Config
from topyaz.core.types import ProcessingOptions
from topyaz.execution.local import LocalExecutor
from topyaz.products import GigapixelAI, PhotoAI, VideoAI
from topyaz.system.environment import EnvironmentValidator
from topyaz.system.gpu import GPUManager
from topyaz.system.memory import MemoryManager
from topyaz.utils.logging import setup_logging


class TopyazCLI:
    """
    Unified CLI wrapper for Topaz Labs products.

    This class provides a simplified interface that delegates to specialized
    components while maintaining backward compatibility with the original
    monolithic implementation.

    Used in:
    - topyaz/__init__.py
    - topyaz/__main__.py
    """

    def __init__(
        self,
        output_dir: str | None = None,
        backup_originals: bool = False,
        preserve_structure: bool = True,
        config_file: str | None = None,
        parallel_jobs: int = 1,
        dry_run: bool = False,
        timeout: int = 3600,
        verbose: bool = False,
        **kwargs,
    ):
        """
        Initialize topyaz wrapper.

        Args:
            output_dir: Default output directory
            backup_originals: Backup original files before processing
            preserve_structure: Preserve directory structure in output
            config_file: Configuration file path
            parallel_jobs: Number of parallel jobs (not implemented yet)
            dry_run: Enable dry run mode (don't actually process)
            timeout: Command timeout in seconds
            verbose: Enable verbose logging
            **kwargs: Additional configuration options

        """
        # Set up logging first
        setup_logging(verbose=verbose)

        logger.info("Initializing topyaz wrapper")

        # Parse _options into data classes
        self._options = ProcessingOptions(
            verbose=verbose,
            dry_run=dry_run,
            timeout=timeout,
            parallel_jobs=parallel_jobs,
            output_dir=Path(output_dir) if output_dir else None,
            preserve_structure=preserve_structure,
            backup_originals=backup_originals,
        )

        # Initialize configuration
        config_path = Path(config_file) if config_file else None
        self._config = Config(config_path)

        # Initialize system components
        self._env_validator = EnvironmentValidator()
        self._gpu_manager = GPUManager()
        self._memory_manager = MemoryManager()

        # Set up executor
        logger.info("Using local execution")
        from topyaz.execution.base import ExecutorContext

        context = ExecutorContext(timeout=self._options.timeout, dry_run=self._options.dry_run)
        self._executor = LocalExecutor(context)

        # Initialize products (lazy loading)
        self._iGigapixelAI: GigapixelAI | None = None
        self._iVideoAI: VideoAI | None = None
        self._iPhotoAI: PhotoAI | None = None

        logger.info("topyaz wrapper initialized successfully")

    @property
    def _gigapixel(self) -> GigapixelAI:
        """Get Gigapixel AI instance (lazy loaded)."""
        if self._iGigapixelAI is None:
            self._iGigapixelAI = GigapixelAI(self._executor, self._options)
        return self._iGigapixelAI

    @property
    def _video_ai(self) -> VideoAI:
        """Get Video AI instance (lazy loaded)."""
        if self._iVideoAI is None:
            self._iVideoAI = VideoAI(self._executor, self._options)
        return self._iVideoAI

    @property
    def _photo_ai(self) -> PhotoAI:
        """Get Photo AI instance (lazy loaded)."""
        if self._iPhotoAI is None:
            self._iPhotoAI = PhotoAI(self._executor, self._options)
        return self._iPhotoAI

    def giga(
        self,
        input_path: str,
        model: str = "std",
        scale: int = 2,
        denoise: int | None = None,
        sharpen: int | None = None,
        compression: int | None = None,
        detail: int | None = None,
        creativity: int | None = None,
        texture: int | None = None,
        prompt: str | None = None,
        face_recovery: int | None = None,
        face_recovery_version: int = 2,
        format_output: str = "preserve",
        quality_output: int = 95,
        bit_depth: int = 0,
        parallel_read: int = 1,
        output: str | None = None,
        **kwargs,
    ) -> bool:
        """
        Process images with Gigapixel AI.

        Args:
            input_path: Input file or directory path
            model: AI model to use
            scale: Upscale factor (1-6)
            denoise: Denoise strength (1-100)
            sharpen: Sharpen strength (1-100)
            compression: Compression reduction (1-100)
            detail: Detail enhancement (1-100)
            creativity: Creativity level for generative models (1-6)
            texture: Texture level for generative models (1-6)
            prompt: Text prompt for generative models
            face_recovery: Face recovery strength (1-100)
            face_recovery_version: Face recovery version (1 or 2)
            format_output: Output format (preserve, jpg, png, tiff)
            quality_output: JPEG quality (1-100)
            bit_depth: Output bit depth (0, 8, 16)
            parallel_read: Parallel file reading (1-10)
            output: Output path
            **kwargs: Additional parameters

        Returns:
            True if successful, False otherwise

        """
        try:
            logger.info(f"Processing {input_path} with Gigapixel AI")

            gigapixel_instance = self._gigapixel
            result = gigapixel_instance.process(
                input_path=input_path,
                output_path=output,
                model=model,
                scale=scale,
                denoise=denoise,
                sharpen=sharpen,
                compression=compression,
                detail=detail,
                creativity=creativity,
                texture=texture,
                prompt=prompt,
                face_recovery=face_recovery,
                face_recovery_version=face_recovery_version,
                format=format_output,
                quality=quality_output,
                bit_depth=bit_depth,
                parallel_read=parallel_read,
                **kwargs,
            )

            if result.success:
                logger.info(f"Successfully processed {input_path} -> {result.output_path}")
                return True
            # Display error information to user
            if result.error_message:
                logger.error(f"Gigapixel AI processing failed: {result.error_message}")
            else:
                logger.error("Gigapixel AI processing failed with unknown error")

            # Show additional error details if available
            if result.stderr and result.stderr.strip():
                logger.error(f"Error details: {result.stderr.strip()}")
            elif result.additional_info and result.additional_info.get("licensing_error"):
                # Enhanced licensing error message from parse_output
                logger.error(result.additional_info.get("user_message", "Licensing error detected"))
            elif result.stdout and "False" in result.stdout:
                # Fallback licensing issue pattern
                logger.error("This appears to be a licensing issue. Gigapixel AI CLI requires a Pro license.")
                logger.error("Please upgrade your license or use the desktop application instead.")

            return False

        except Exception as e:
            logger.error(f"Gigapixel AI processing failed: {e}")
            return False

    def video(
        self,
        input_path: str,
        model: str = "amq-13",
        scale: int = 2,
        fps: int | None = None,
        codec: str = "hevc_videotoolbox",
        quality: int = 18,
        denoise: int | None = None,
        details: int | None = None,
        halo: int | None = None,
        blur: int | None = None,
        compression: int | None = None,
        stabilize: bool = False,
        interpolate: bool = False,
        custom_filters: str | None = None,
        device: int = 0,
        output: str | None = None,
        **kwargs,
    ) -> bool:
        """
        Process videos with Video AI.

        Args:
            input_path: Input video file path
            model: AI model to use
            scale: Upscale factor (1-4)
            fps: Target frame rate for interpolation
            codec: Video codec (hevc_videotoolbox, hevc_nvenc, etc.)
            quality: Video quality_output/CRF value (1-51)
            denoise: Denoise strength (0-100)
            details: Detail enhancement (-100 to 100)
            halo: Halo reduction (0-100)
            blur: Blur reduction (0-100)
            compression: Compression artifact reduction (0-100)
            stabilize: Enable stabilization
            interpolate: Enable frame interpolation
            custom_filters: Custom FFmpeg filters
            device: GPU device index (-1 for CPU)
            output: Output file path
            **kwargs: Additional parameters

        Returns:
            True if successful, False otherwise

        """
        try:
            logger.info(f"Processing {input_path} with Video AI")

            video_ai_instance = self._video_ai
            result = video_ai_instance.process(
                input_path=input_path,
                output_path=output,
                model=model,
                scale=scale,
                fps=fps,
                codec=codec,
                quality=quality,
                denoise=denoise,
                details=details,
                halo=halo,
                blur=blur,
                compression=compression,
                stabilize=stabilize,
                interpolate=interpolate,
                custom_filters=custom_filters,
                device=device,
                **kwargs,
            )

            return result.success

        except Exception as e:
            logger.error(f"Video AI processing failed: {e}")
            return False

    def photo(
        self,
        input_path: str,
        preset: str = "auto",
        format: str = "preserve",
        quality: int = 95,
        compression: int = 6,
        bit_depth: int = 8,
        tiff_compression: str = "lzw",
        show_settings: bool = False,
        override_autopilot: bool = False,
        upscale: bool | None = None,
        noise: bool | None = None,
        sharpen: bool | None = None,
        lighting: bool | None = None,
        color: bool | None = None,
        face_strength: int | None = None,
        face_detection: str | None = None,
        face_parts: list[str] | None = None,
        denoise_model: str | None = None,
        denoise_levels: list[str] | None = None,
        denoise_strength: int | None = None,
        denoise_raw_model: str | None = None,
        denoise_raw_levels: list[str] | None = None,
        denoise_raw_strength: int | None = None,
        sharpen_model: str | None = None,
        sharpen_levels: list[str] | None = None,
        sharpen_strength: int | None = None,
        upscaling_model: str | None = None,
        upscaling_factor: float | None = None,
        upscaling_type: str | None = None,
        deblur_strength: int | None = None,
        denoise_upscale_strength: int | None = None,
        lighting_strength: int | None = None,
        raw_exposure_strength: int | None = None,
        adjust_color: bool | None = None,
        temperature_value: int | None = None,
        opacity_value: int | None = None,
        resolution_unit: int | None = None,
        default_resolution: float | None = None,
        overwrite_files: bool | None = None,
        recurse_directories: bool | None = None,
        append_filters: bool | None = None,
        output: str | None = None,
        **kwargs,
    ) -> bool:
        """
        Process a photo with Photo AI.

        Args:
            input_path: Input file or directory path
            preset: Autopilot preset to use
            format: Output format (preserve, jpg, png, tiff, dng)
            quality: JPEG quality (0-100)
            compression: PNG compression (0-10)
            bit_depth: TIFF bit depth (8 or 16)
            tiff_compression: TIFF compression (none, lzw, zip)
            show_settings: Show processing settings only
            override_autopilot: Override autopilot with manual settings
            upscale: Enable/disable upscaling
            noise: Enable/disable noise reduction
            sharpen: Enable/disable sharpening
            lighting: Enable/disable lighting enhancement
            color: Enable/disable color enhancement
            face_strength: Face recovery strength (0-100)
            face_detection: Face detection mode (auto, subject, all)
            face_parts: List of face parts to include
            denoise_model: Denoise model
            denoise_levels: Denoise levels
            denoise_strength: Denoise strength (0-10)
            denoise_raw_model: RAW denoise model
            denoise_raw_levels: RAW denoise levels
            denoise_raw_strength: RAW denoise strength (0-10)
            sharpen_model: Sharpen model
            sharpen_levels: Sharpen levels
            sharpen_strength: Sharpen strength (0-10)
            upscaling_model: Upscaling model
            upscaling_factor: Upscaling factor (1.0-6.0)
            upscaling_type: Upscaling type (auto, scale, width, height)
            deblur_strength: Deblur strength (0-10)
            denoise_upscale_strength: Denoise upscale strength (0-10)
            lighting_strength: Lighting enhancement strength (0-100)
            raw_exposure_strength: RAW exposure strength (0-100)
            adjust_color: Enable color adjustment
            temperature_value: White balance temperature (0-100)
            opacity_value: Opacity value (0-100)
            resolution_unit: Resolution unit (1=inches, 2=cm)
            default_resolution: Default resolution (-1=auto)
            overwrite_files: Allow overwriting files
            recurse_directories: Process directories recursively
            append_filters: Append filters to output
            output: Output path
            **kwargs: Additional parameters

        Returns:
            True if successful, False otherwise

        """
        try:
            logger.info(f"Processing {input_path} with Photo AI")

            result = self._photo_ai.process(
                input_path=input_path,
                output_path=output,
                autopilot_preset=preset,
                format_output=format,
                quality_output=quality,
                compression=compression,
                bit_depth=bit_depth,
                tiff_compression=tiff_compression,
                show_settings=show_settings,
                skip_processing=self._options.dry_run,
                override_autopilot=override_autopilot,
                upscale=upscale,
                noise=noise,
                sharpen=sharpen,
                lighting=lighting,
                color=color,
                face_strength=face_strength,
                face_detection=face_detection,
                face_parts=face_parts,
                denoise_model=denoise_model,
                denoise_levels=denoise_levels,
                denoise_strength=denoise_strength,
                denoise_raw_model=denoise_raw_model,
                denoise_raw_levels=denoise_raw_levels,
                denoise_raw_strength=denoise_raw_strength,
                sharpen_model=sharpen_model,
                sharpen_levels=sharpen_levels,
                sharpen_strength=sharpen_strength,
                upscaling_model=upscaling_model,
                upscaling_factor=upscaling_factor,
                upscaling_type=upscaling_type,
                deblur_strength=deblur_strength,
                denoise_upscale_strength=denoise_upscale_strength,
                lighting_strength=lighting_strength,
                raw_exposure_strength=raw_exposure_strength,
                adjust_color=adjust_color,
                temperature_value=temperature_value,
                opacity_value=opacity_value,
                resolution_unit=resolution_unit,
                default_resolution=default_resolution,
                overwrite_files=overwrite_files,
                recurse_directories=recurse_directories,
                append_filters=append_filters,
                **kwargs,
            )

            return result.success

        except Exception as e:
            logger.error(f"Photo AI processing failed: {e}")
            return False

    def _sysinfo(self) -> dict[str, Any]:
        """
        Get comprehensive system information.

        Returns:
            Dictionary with system information

        """
        try:
            return {
                "environment": self._env_validator.get_system_info(),
                "gpu": asdict(self._gpu_manager.get_status()),
                "memory": self._memory_manager.get_status(),
                "products": {
                    "_gigapixel": self._gigapixel.get_info(),
                    "_video_ai": self._video_ai.get_info(),
                    "_photo_ai": self._photo_ai.get_info(),
                },
                "_executor": self._executor.get_info(),
            }
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {"error": str(e)}

    def info(self) -> bool:
        """
        Validate system environment and requirements.

        Returns:
            True if environment is valid

        """
        logger.info(self._sysinfo())
        try:
            validation_results = self._env_validator.validate_all(raise_on_error=False)

            for check, result in validation_results.items():
                if result:
                    logger.info(f"✓ {check} validation passed")
                else:
                    logger.warning(f"✗ {check} validation failed")

            return all(validation_results.values())

        except Exception as e:
            logger.error(f"Environment validation failed: {e}")
            return False

    def version(self) -> dict[str, str]:
        """
        Get version information for all components.

        Returns:
            Dictionary with version information

        """
        try:
            from topyaz import __version__

            return {
                "topyaz": __version__,
                "_gigapixel": self._gigapixel.get_version() or "unknown",
                "_video_ai": self._video_ai.get_version() or "unknown",
                "_photo_ai": self._photo_ai.get_version() or "unknown",
            }
        except Exception as e:
            logger.error(f"Failed to get version info: {e}")
            return {"error": str(e)}


def main():
    """Main entry point for the CLI."""
    # Pass instance to avoid "command command" duplication
    cli_instance = TopyazCLI
    fire.Fire(cli_instance)


if __name__ == "__main__":
    main()
