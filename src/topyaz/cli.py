#!/usr/bin/env python3
# this_file: src/topyaz/cli.py
"""
Command-line interface for topyaz.

This module provides the main CLI wrapper that integrates all the modular
components into a unified interface compatible with the original topyazWrapper.

"""

import sys
from pathlib import Path
from typing import Any, Optional

import fire
from loguru import logger

from topyaz.core.config import Config
from topyaz.core.errors import TopazError
from topyaz.core.types import ProcessingOptions, Product, RemoteOptions
from topyaz.execution.local import LocalExecutor
from topyaz.execution.remote import RemoteExecutor
from topyaz.products import GigapixelAI, PhotoAI, VideoAI, create_product
from topyaz.system.environment import EnvironmentValidator
from topyaz.system.gpu import GPUManager
from topyaz.system.memory import MemoryManager
from topyaz.utils.logging import LoggingManager


class topyazWrapper:
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
        verbose: bool = True,
        dry_run: bool = False,
        timeout: int = 3600,
        parallel_jobs: int = 1,
        output_dir: str | None = None,
        preserve_structure: bool = True,
        backup_originals: bool = False,
        remote_host: str | None = None,
        remote_user: str | None = None,
        ssh_key: str | None = None,
        ssh_port: int = 22,
        connection_timeout: int = 30,
        config_file: str | None = None,
        **kwargs,
    ):
        """
        Initialize topyaz wrapper.

        Args:
            verbose: Enable verbose logging
            dry_run: Enable dry run mode (don't actually process)
            timeout: Command timeout in seconds
            parallel_jobs: Number of parallel jobs (not implemented yet)
            output_dir: Default output directory
            preserve_structure: Preserve directory structure in output
            backup_originals: Backup original files before processing
            remote_host: Remote host for SSH execution
            remote_user: Remote user for SSH
            ssh_key: SSH key file path
            ssh_port: SSH port number
            connection_timeout: SSH connection timeout
            config_file: Configuration file path
            **kwargs: Additional configuration options

        """
        # Set up logging first
        self.logging_manager = LoggingManager()
        self.logging_manager.setup_logging(verbose=verbose)

        logger.info("Initializing topyaz wrapper")

        # Parse options into data classes
        self.options = ProcessingOptions(
            verbose=verbose,
            dry_run=dry_run,
            timeout=timeout,
            parallel_jobs=parallel_jobs,
            output_dir=Path(output_dir) if output_dir else None,
            preserve_structure=preserve_structure,
            backup_originals=backup_originals,
        )

        self.remote_options = RemoteOptions(
            host=remote_host,
            user=remote_user,
            ssh_key=Path(ssh_key) if ssh_key else None,
            ssh_port=ssh_port,
            connection_timeout=connection_timeout,
        )

        # Initialize configuration
        config_path = Path(config_file) if config_file else None
        self.config = Config(config_path)

        # Initialize system components
        self.env_validator = EnvironmentValidator()
        self.gpu_manager = GPUManager()
        self.memory_manager = MemoryManager()

        # Set up executor
        if self.remote_options.host:
            logger.info(f"Using remote execution: {self.remote_options.user}@{self.remote_options.host}")
            self.executor = RemoteExecutor(self.remote_options)
        else:
            logger.info("Using local execution")
            self.executor = LocalExecutor(self.options)

        # Initialize products (lazy loading)
        self._gigapixel: GigapixelAI | None = None
        self._video_ai: VideoAI | None = None
        self._photo_ai: PhotoAI | None = None

        logger.info("topyaz wrapper initialized successfully")

    @property
    def gigapixel(self) -> GigapixelAI:
        """Get Gigapixel AI instance (lazy loaded)."""
        if self._gigapixel is None:
            self._gigapixel = GigapixelAI(self.executor, self.options)
        return self._gigapixel

    @property
    def video_ai(self) -> VideoAI:
        """Get Video AI instance (lazy loaded)."""
        if self._video_ai is None:
            self._video_ai = VideoAI(self.executor, self.options)
        return self._video_ai

    @property
    def photo_ai(self) -> PhotoAI:
        """Get Photo AI instance (lazy loaded)."""
        if self._photo_ai is None:
            self._photo_ai = PhotoAI(self.executor, self.options)
        return self._photo_ai

    def gp(
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
        format: str = "preserve",
        quality: int = 95,
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
            format: Output format (preserve, jpg, png, tiff)
            quality: JPEG quality (1-100)
            bit_depth: Output bit depth (0, 8, 16)
            parallel_read: Parallel file reading (1-10)
            output: Output path
            **kwargs: Additional parameters

        Returns:
            True if successful, False otherwise

        """
        try:
            logger.info(f"Processing {input_path} with Gigapixel AI")

            result = self.gigapixel.process(
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
                format=format,
                quality=quality,
                bit_depth=bit_depth,
                parallel_read=parallel_read,
                **kwargs,
            )

            return result.success

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
            quality: Video quality/CRF value (1-51)
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

            result = self.video_ai.process(
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
        autopilot_preset: str = "auto",
        format: str = "preserve",
        quality: int = 95,
        compression: int = 6,
        bit_depth: int = 8,
        tiff_compression: str = "lzw",
        show_settings: bool = False,
        skip_processing: bool = False,
        override_autopilot: bool = False,
        upscale: bool | None = None,
        noise: bool | None = None,
        sharpen: bool | None = None,
        lighting: bool | None = None,
        color: bool | None = None,
        output: str | None = None,
        **kwargs,
    ) -> bool:
        """
        Process photos with Photo AI.

        Args:
            input_path: Input file or directory path
            autopilot_preset: Autopilot preset to use
            format: Output format (preserve, jpg, png, tiff, dng)
            quality: JPEG quality (0-100)
            compression: PNG compression (0-10)
            bit_depth: TIFF bit depth (8 or 16)
            tiff_compression: TIFF compression (none, lzw, zip)
            show_settings: Show processing settings only
            skip_processing: Skip actual processing
            override_autopilot: Override autopilot with manual settings
            upscale: Enable/disable upscaling
            noise: Enable/disable noise reduction
            sharpen: Enable/disable sharpening
            lighting: Enable/disable lighting enhancement
            color: Enable/disable color enhancement
            output: Output path
            **kwargs: Additional parameters

        Returns:
            True if successful, False otherwise

        """
        try:
            logger.info(f"Processing {input_path} with Photo AI")

            input_path_obj = Path(input_path)
            output_path_obj = Path(output) if output else None

            # Handle batch processing for directories
            if input_path_obj.is_dir():
                if not output_path_obj:
                    output_path_obj = input_path_obj.parent / f"{input_path_obj.name}_processed"

                results = self.photo_ai.process_batch_directory(
                    input_dir=input_path_obj,
                    output_dir=output_path_obj,
                    autopilot_preset=autopilot_preset,
                    format=format,
                    quality=quality,
                    compression=compression,
                    bit_depth=bit_depth,
                    tiff_compression=tiff_compression,
                    show_settings=show_settings,
                    skip_processing=skip_processing,
                    override_autopilot=override_autopilot,
                    upscale=upscale,
                    noise=noise,
                    sharpen=sharpen,
                    lighting=lighting,
                    color=color,
                    **kwargs,
                )

                # Return True if all batches succeeded
                return all(result.get("success", False) for result in results)

            # Single file processing
            result = self.photo_ai.process(
                input_path=input_path,
                output_path=output,
                autopilot_preset=autopilot_preset,
                format=format,
                quality=quality,
                compression=compression,
                bit_depth=bit_depth,
                tiff_compression=tiff_compression,
                show_settings=show_settings,
                skip_processing=skip_processing,
                override_autopilot=override_autopilot,
                upscale=upscale,
                noise=noise,
                sharpen=sharpen,
                lighting=lighting,
                color=color,
                **kwargs,
            )

            return result.success

        except Exception as e:
            logger.error(f"Photo AI processing failed: {e}")
            return False

    def system_info(self) -> dict[str, Any]:
        """
        Get comprehensive system information.

        Returns:
            Dictionary with system information

        """
        try:
            return {
                "environment": self.env_validator.get_system_info(),
                "gpu": self.gpu_manager.get_status().to_dict(),
                "memory": self.memory_manager.get_status(),
                "products": {
                    "gigapixel": self.gigapixel.get_info(),
                    "video_ai": self.video_ai.get_info(),
                    "photo_ai": self.photo_ai.get_info(),
                },
                "executor": self.executor.get_info(),
            }
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {"error": str(e)}

    def validate_environment(self) -> bool:
        """
        Validate system environment and requirements.

        Returns:
            True if environment is valid

        """
        try:
            validation_results = self.env_validator.validate_all(raise_on_error=False)

            for check, result in validation_results.items():
                if result:
                    logger.info(f"✓ {check} validation passed")
                else:
                    logger.warning(f"✗ {check} validation failed")

            return all(validation_results.values())

        except Exception as e:
            logger.error(f"Environment validation failed: {e}")
            return False

    def get_optimal_batch_size(self, product: str, file_count: int) -> int:
        """
        Get optimal batch size for processing.

        Args:
            product: Product name (gigapixel, video_ai, photo_ai)
            file_count: Number of files to process

        Returns:
            Optimal batch size

        """
        try:
            return self.memory_manager.get_optimal_batch_size(file_count, product)
        except Exception as e:
            logger.error(f"Failed to calculate batch size: {e}")
            return 1

    def version_info(self) -> dict[str, str]:
        """
        Get version information for all components.

        Returns:
            Dictionary with version information

        """
        try:
            from topyaz import __version__

            return {
                "topyaz": __version__,
                "gigapixel": self.gigapixel.get_version() or "unknown",
                "video_ai": self.video_ai.get_version() or "unknown",
                "photo_ai": self.photo_ai.get_version() or "unknown",
            }
        except Exception as e:
            logger.error(f"Failed to get version info: {e}")
            return {"error": str(e)}


def main():
    """Main entry point for the CLI."""
    try:
        fire.Fire(topyazWrapper)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except TopazError as e:
        logger.error(f"Topaz error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
