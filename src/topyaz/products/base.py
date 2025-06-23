#!/usr/bin/env python3
# this_file: src/topyaz/products/base.py
"""
Base product interface for topyaz.

This module provides abstract base classes and interfaces for Topaz products,
defining common functionality and ensuring consistent implementation across
all supported products.

Used in:
- topyaz/products/_gigapixel.py
- topyaz/products/_photo_ai.py
- topyaz/products/_video_ai.py
"""

import platform
import re  # Moved from _parse_version
import shutil
import subprocess  # Moved from validate_macos_version
import tempfile  # Moved from process
import time  # Moved from process
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from loguru import logger

from topyaz.core.errors import ExecutableNotFoundError, ValidationError
from topyaz.core.types import (
    CommandList,
    ProcessingOptions,
    ProcessingResult,
    Product,
)
from topyaz.execution.base import CommandExecutor
from topyaz.system.paths import PathValidator


class TopazProduct(ABC):
    """
    Abstract base class for all Topaz products.

    Provides common functionality and defines the interface that all
    Topaz product implementations must follow.

    Used in:
    - topyaz/products/__init__.py
    """

    def __init__(self, executor: CommandExecutor, options: ProcessingOptions, product_type: Product):
        """
        Initialize product instance.

        Args:
            executor: Command _executor for running operations
            options: Processing _options and configuration
            product_type: Type of product (from Product enum)

        Used in:
        - topyaz/products/_gigapixel.py
        - topyaz/products/_photo_ai.py
        - topyaz/products/_video_ai.py
        """
        self.executor = executor
        self.options = options
        self.product_type = product_type
        self.path_validator = PathValidator()
        self._executable_path: Path | None = None
        self._version: str | None = None

    @property
    @abstractmethod
    def product_name(self) -> str:
        """Human-readable product name."""
        pass

    @property
    @abstractmethod
    def executable_name(self) -> str:
        """Name of the executable file."""
        pass

    @property
    @abstractmethod
    def supported_formats(self) -> list[str]:
        """List of supported file formats (extensions without dots)."""
        pass

    @abstractmethod
    def get_search_paths(self) -> list[Path]:
        """
        Get list of paths to search for the executable.

        Returns:
            List of potential executable locations

        """
        pass

    @abstractmethod
    def validate_params(self, **kwargs) -> None:
        """
        Validate product-specific parameters.

        Args:
            **kwargs: Parameters to validate

        Raises:
            ValidationError: If parameters are invalid
        """
        pass

    @abstractmethod
    def build_command(self, input_path: Path, output_path: Path, **kwargs) -> CommandList:
        """
        Build command line for processing.

        Args:
            input_path: Input file or directory path
            output_path: Output file or directory path
            **kwargs: Product-specific parameters

        Returns:
            Command list ready for execution
        """
        pass

    @abstractmethod
    def parse_output(self, stdout: str, stderr: str) -> dict[str, Any]:
        """
        Parse command output for useful information.

        Args:
            stdout: Standard output from command
            stderr: Standard error from command

        Returns:
            Dictionary of parsed information
        """
        pass

    @abstractmethod
    def _find_output_file(self, temp_dir: Path, input_path: Path) -> Path:
        """
        Find the generated output file within a temporary directory.
        This must be implemented by subclasses that use the temp dir workflow.

        Args:
            temp_dir: Temporary directory where output was generated
            input_path: Original input file path

        Returns:
            Path to the generated output file

        Raises:
            ProcessingError: If output file cannot be found
        """
        pass

    def find_executable(self) -> Path | None:
        """
        Find the product executable.

        Returns:
            Path to executable if found, None otherwise

        """
        if self._executable_path and self._executable_path.exists():
            return self._executable_path

        # Search in standard locations
        search_paths = self.get_search_paths()

        for search_path in search_paths:
            if search_path.exists():
                logger.debug(f"Found {self.product_name} at: {search_path}")
                self._executable_path = search_path
                return search_path

        # Try system PATH as fallback
        system_executable = shutil.which(self.executable_name)
        if system_executable:
            path = Path(system_executable)
            logger.debug(f"Found {self.product_name} in PATH: {path}")
            self._executable_path = path
            return path

        logger.warning(f"{self.product_name} executable not found")
        return None

    def get_executable_path(self) -> Path:
        """
        Get the executable path, finding it if necessary.

        Returns:
            Path to executable

        Raises:
            ExecutableNotFoundError: If executable cannot be found

        Used in:
        - topyaz/products/_gigapixel.py
        - topyaz/products/_photo_ai.py
        - topyaz/products/_video_ai.py
        """
        executable = self.find_executable()
        if not executable:
            msg = f"{self.product_name} executable not found. Please ensure {self.product_name} is installed."
            raise ExecutableNotFoundError(msg)
        return executable

    def get_version(self) -> str | None:
        """
        Get product version.

        Returns:
            Version string if available

        Used in:
        - topyaz/cli.py
        """
        if self._version:
            return self._version

        try:
            executable = self.get_executable_path()
            # Most Topaz products support --version
            result = self.executor.execute([str(executable), "--version"])

            if result[0] == 0 and result[1]:
                # Parse version from output
                self._version = self._parse_version(result[1])
                return self._version

        except Exception as e:
            logger.debug(f"Could not get {self.product_name} version: {e}")

        return None

    def _parse_version(self, version_output: str) -> str:
        """
        Parse version from command output.

        Args:
            version_output: Raw version output

        Returns:
            Parsed version string

        """
        # Basic version parsing - can be overridden by subclasses
        lines = version_output.strip().split("\n")
        if lines:
            # Look for version numbers in first few lines
            # import re # Moved to top

            version_pattern = re.compile(r"(\d+\.\d+(?:\.\d+)*)")
            for line in lines[:3]:
                match = version_pattern.search(line)
                if match:
                    return match.group(1)

        return version_output.strip()

    def validate_input_path(self, input_path: Path) -> None:
        """
        Validate input path for this product.

        Args:
            input_path: Path to validate

        Raises:
            ValidationError: If path is invalid

        """
        # Use centralized path validator with product-specific file type checking
        self.path_validator.validate_input_path(input_path, file_type=self.product_type)

    def prepare_output_path(self, input_path: Path, output_path: Path | None = None) -> Path:
        """
        Prepare output path based on input and _options.

        Args:
            input_path: Input file path
            output_path: Optional output path

        Returns:
            Prepared output path

        """
        if output_path:
            return self.path_validator.validate_output_path(output_path)

        # Auto-generate output path
        output_dir = self.options.output_dir if self.options.output_dir else input_path.parent

        # Generate filename with product-specific suffix
        suffix = self._get_output_suffix()
        stem = input_path.stem
        extension = input_path.suffix

        output_filename = f"{stem}{suffix}{extension}"
        output_path = output_dir / output_filename

        return self.path_validator.validate_output_path(output_path)

    def _get_output_suffix(self) -> str:
        """Get suffix to add to output filenames."""
        return f"_{self.product_type.value.lower()}"

    def process(self, input_path: Path | str, output_path: Path | str | None = None, **kwargs) -> ProcessingResult:
        """
        Template method for processing files. Uses temporary directory workflow.
        Override this method only if you need different behavior (like VideoAI).

        Args:
            input_path: Input file or directory path
            output_path: Output file or directory path
            **kwargs: Product-specific parameters

        Returns:
            Processing result

        Raises:
            ValidationError: If parameters are invalid
            ProcessingError: If processing fails

        Used in:
        - topyaz/cli.py
        """
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
            extension = input_path.suffix
            output_filename = f"{stem}{suffix}{extension}"
            final_output_path = output_dir / output_filename

        # Ensure executable is available
        self.get_executable_path()

        # Create temporary directory for processing
        # import tempfile # Moved to top

        with tempfile.TemporaryDirectory(prefix=f"topyaz_{self.product_type.value}_") as temp_dir:
            temp_output_dir = Path(temp_dir)

            # Build command with temp directory
            command = self.build_command(input_path, temp_output_dir, **kwargs)

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
                    # Parse output for additional error information
                    parsed_info = self.parse_output(stdout, stderr)

                    # Create more specific error message
                    if parsed_info.get("licensing_error"):
                        error_msg = parsed_info.get("user_message", "Licensing error detected")
                    elif parsed_info.get("error_type"):
                        error_msg = f"{self.product_name} processing failed: {parsed_info.get('error_type')}"
                    else:
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
                        additional_info=parsed_info,
                    )

                # Find the generated file using subclass-specific logic
                temp_output_file = self._find_output_file(temp_output_dir, input_path)

                # Ensure output directory exists and move file to final location
                final_output_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(temp_output_file), str(final_output_path))

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

    def get_info(self) -> dict[str, Any]:
        """
        Get information about this product.

        Returns:
            Dictionary with product information

        Used in:
        - topyaz/cli.py
        """
        executable = self.find_executable()
        version = self.get_version()

        return {
            "product_name": self.product_name,
            "product_type": self.product_type.value,
            "executable_name": self.executable_name,
            "executable_path": str(executable) if executable else None,
            "executable_found": executable is not None,
            "version": version,
            "supported_formats": self.supported_formats,
            "platform": platform.system(),
        }


class MacOSTopazProduct(TopazProduct):
    """
    Base class for Topaz products on macOS.

    Provides macOS-specific functionality like finding applications
    in /Applications directory.

    Used in:
    - topyaz/products/__init__.py
    - topyaz/products/_gigapixel.py
    - topyaz/products/_photo_ai.py
    - topyaz/products/_video_ai.py
    """

    @property
    @abstractmethod
    def app_name(self) -> str:
        """Name of the macOS application."""
        pass

    @property
    @abstractmethod
    def app_executable_path(self) -> str:
        """Relative path to executable within app bundle."""
        pass

    def get_search_paths(self) -> list[Path]:
        """Get macOS-specific search paths."""
        app_path = Path("/Applications") / self.app_name
        executable_path = app_path / self.app_executable_path

        paths = [executable_path]

        # Also check user Applications folder
        user_app_path = Path.home() / "Applications" / self.app_name
        user_executable_path = user_app_path / self.app_executable_path
        paths.append(user_executable_path)

        return paths

    def validate_macos_version(self) -> None:
        """
        Validate macOS version compatibility.

        Raises:
            ValidationError: If macOS version is incompatible

        """
        if platform.system() != "Darwin":
            msg = f"{self.product_name} is only available on macOS"
            raise ValidationError(msg)

        # Check minimum macOS version (most Topaz products require 10.15+)
        try:
            # import subprocess # Moved to top
            # S607: Use full path for sw_vers
            result = subprocess.run(["/usr/bin/sw_vers", "-productVersion"], capture_output=True, text=True, check=True)
            version_str = result.stdout.strip()

            # Parse version
            version_parts = [int(x) for x in version_str.split(".")]

            # Check minimum version (macOS 10.15 = [10, 15])
            min_version = [10, 15]
            if version_parts < min_version:
                msg = f"{self.product_name} requires macOS 10.15 or later. Current version: {version_str}"
                raise ValidationError(msg)

        except Exception as e:
            logger.warning(f"Could not verify macOS version: {e}")


def create_product(product_type: Product, executor: CommandExecutor, options: ProcessingOptions) -> TopazProduct:
    """
    Create a product instance based on product type.

    Args:
        product_type: Type of product to create
        executor: Command _executor
        options: Processing _options

    Returns:
        Product instance

    Raises:
        ValueError: If product type is not supported

    Used in:
    - topyaz/cli.py
    - topyaz/products/__init__.py
    """
    # Import here to avoid circular imports
    if product_type == Product.GIGAPIXEL:
        from topyaz.products.gigapixel.api import GigapixelAI  # noqa: PLC0415

        return GigapixelAI(executor, options)
    if product_type == Product.VIDEO_AI:
        from topyaz.products.video_ai.api import VideoAI  # noqa: PLC0415

        return VideoAI(executor, options)
    if product_type == Product.PHOTO_AI:
        from topyaz.products.photo_ai.api import PhotoAI  # noqa: PLC0415

        return PhotoAI(executor, options)
    msg = f"Unsupported product type: {product_type}"
    raise ValueError(msg)
