#!/usr/bin/env python3
# this_file: src/topyaz/system/paths.py
"""
Path validation and utilities for topyaz.

This module provides path handling, validation, and manipulation utilities
including support for recursive operations and output path generation.

"""

import os
import shutil
from pathlib import Path
from typing import Optional, Union

from loguru import logger

from topyaz.core.errors import ValidationError
from topyaz.core.types import Product


class PathValidator:
    """
    Validates and normalizes file system paths.

    Provides methods for:
    - Path expansion and normalization
    - Permission checking
    - Output path generation
    - Directory structure preservation

    Used in:
    - topyaz/products/base.py
    - topyaz/system/__init__.py
    """

    # Supported image extensions for each product
    IMAGE_EXTENSIONS = {
        Product.GIGAPIXEL: {
            ".jpg",
            ".jpeg",
            ".png",
            ".tif",
            ".tiff",
            ".bmp",
            ".webp",
            ".dng",
            ".raw",
            ".cr2",
            ".nef",
            ".arw",
        },
        Product.PHOTO_AI: {
            ".jpg",
            ".jpeg",
            ".png",
            ".tif",
            ".tiff",
            ".bmp",
            ".webp",
            ".dng",
            ".raw",
            ".cr2",
            ".nef",
            ".arw",
            ".heic",
            ".heif",
        },
    }

    # Supported video extensions
    VIDEO_EXTENSIONS = {
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".webm",
        ".m4v",
        ".wmv",
        ".flv",
        ".f4v",
        ".mpg",
        ".mpeg",
        ".3gp",
    }

    def __init__(self, preserve_structure: bool = True):
        """
        Initialize path validator.

        Args:
            preserve_structure: Whether to preserve directory structure in output

        """
        self.preserve_structure = preserve_structure

    def validate_input_path(self, path: str | Path, must_exist: bool = True, file_type: Product | None = None) -> Path:
        """
        Validate and normalize input path.

        Args:
            path: Input path to validate
            must_exist: Whether path must exist
            file_type: Product type for extension validation

        Returns:
            Normalized Path object

        Raises:
            ValidationError: If path is invalid

        Used in:
        - topyaz/products/base.py
        """
        # Expand and resolve path
        try:
            path_obj = Path(path).expanduser().resolve()
        except Exception as e:
            msg = f"Invalid path '{path}': {e}"
            raise ValidationError(msg)

        # Check existence
        if must_exist and not path_obj.exists():
            msg = f"Path does not exist: {path_obj}"
            raise ValidationError(msg)

        # Check readability
        if must_exist and not os.access(path_obj, os.R_OK):
            msg = f"Path is not readable: {path_obj}"
            raise ValidationError(msg)

        # Validate file extension if checking a file
        if path_obj.is_file() and file_type:
            self._validate_file_extension(path_obj, file_type)

        logger.debug(f"Validated input path: {path_obj}")
        return path_obj

    def validate_output_path(self, path: str | Path, create_dirs: bool = True, check_writable: bool = True) -> Path:
        """
        Validate and prepare output path.

        Args:
            path: Output path to validate
            create_dirs: Create parent directories if needed
            check_writable: Check if path/parent is writable

        Returns:
            Normalized Path object

        Raises:
            ValidationError: If path is invalid

        Used in:
        - topyaz/products/base.py
        """
        # Expand and resolve path
        try:
            path_obj = Path(path).expanduser().resolve()
        except Exception as e:
            msg = f"Invalid output path '{path}': {e}"
            raise ValidationError(msg)

        # Create parent directory if needed
        parent_dir = path_obj.parent
        if create_dirs and not parent_dir.exists():
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created output directory: {parent_dir}")
            except Exception as e:
                msg = f"Failed to create directory: {e}"
                raise ValidationError(msg)

        # Check writability
        if check_writable:
            check_dir = path_obj if path_obj.is_dir() else parent_dir
            if not os.access(check_dir, os.W_OK):
                msg = f"Output path is not writable: {check_dir}"
                raise ValidationError(msg)

        logger.debug(f"Validated output path: {path_obj}")
        return path_obj

    def generate_output_path(
        self,
        input_path: Path,
        output_base: Path | None = None,
        suffix: str = "_processed",
        preserve_structure: bool | None = None,
        product: Product | None = None,
    ) -> Path:
        """
        Generate output path based on input path.

        Args:
            input_path: Input file/directory path
            output_base: Base output directory
            suffix: Suffix to add to filenames
            preserve_structure: Override instance setting
            product: Product type for naming

        Returns:
            Generated output path

        """
        preserve = preserve_structure if preserve_structure is not None else self.preserve_structure

        if input_path.is_file():
            # Single file processing
            if output_base and output_base.is_dir():
                # Output to specified directory
                if preserve and input_path.parent != Path():
                    # Preserve relative directory structure
                    rel_path = input_path.relative_to(input_path.parent.parent)
                    output_path = output_base / rel_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"
                else:
                    # Flat output
                    output_path = output_base / f"{input_path.stem}{suffix}{input_path.suffix}"
            elif output_base:
                # Specific output file
                output_path = output_base
            else:
                # Same directory as input
                output_path = input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"

        # Directory processing
        elif output_base:
            output_path = output_base
        else:
            # Create processed directory next to input
            output_path = input_path.parent / f"{input_path.name}{suffix}"

        return output_path

    def find_files(
        self,
        root_path: Path,
        product: Product | None = None,
        recursive: bool = True,
        extensions: set[str] | None = None,
    ) -> list[Path]:
        """
        Find all supported files in a directory.

        Args:
            root_path: Root directory to search
            product: Product type for filtering
            recursive: Search recursively
            extensions: Custom extensions to search for

        Returns:
            List of file paths

        """
        if not root_path.is_dir():
            return [root_path] if root_path.is_file() else []

        # Determine extensions to search for
        if extensions:
            search_extensions = extensions
        elif product == Product.VIDEO_AI:
            search_extensions = self.VIDEO_EXTENSIONS
        elif product in (Product.GIGAPIXEL, Product.PHOTO_AI):
            search_extensions = self.IMAGE_EXTENSIONS.get(product, set())
        else:
            # All supported extensions
            search_extensions = (
                self.VIDEO_EXTENSIONS
                | self.IMAGE_EXTENSIONS.get(Product.GIGAPIXEL, set())
                | self.IMAGE_EXTENSIONS.get(Product.PHOTO_AI, set())
            )

        # Find files
        files = []
        pattern = "**/*" if recursive else "*"

        for ext in search_extensions:
            files.extend(root_path.glob(f"{pattern}{ext}"))
            files.extend(root_path.glob(f"{pattern}{ext.upper()}"))

        # Remove duplicates and sort
        files = sorted(set(files))

        logger.debug(f"Found {len(files)} files in {root_path}")
        return files

    def _validate_file_extension(self, path: Path, product: Product) -> None:
        """
        Validate file extension for a product.

        Args:
            path: File path to validate
            product: Product type

        Raises:
            ValidationError: If extension not supported

        """
        ext = path.suffix.lower()

        if product == Product.VIDEO_AI:
            valid_extensions = self.VIDEO_EXTENSIONS
        else:
            valid_extensions = self.IMAGE_EXTENSIONS.get(product, set())

        if ext not in valid_extensions:
            msg = f"Unsupported file type '{ext}' for {product.value}. Supported: {', '.join(sorted(valid_extensions))}"
            raise ValidationError(msg)

    def create_backup(self, source_path: Path, backup_suffix: str = ".backup") -> Path | None:
        """
        Create a backup of a file.

        Args:
            source_path: File to backup
            backup_suffix: Suffix for backup file

        Returns:
            Path to backup file or None if failed

        """
        if not source_path.is_file():
            return None

        backup_path = source_path.parent / f"{source_path.name}{backup_suffix}"

        # Find unique backup name
        counter = 1
        while backup_path.exists():
            backup_path = source_path.parent / f"{source_path.name}{backup_suffix}.{counter}"
            counter += 1

        try:
            shutil.copy2(source_path, backup_path)
            logger.debug(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None

    def ensure_unique_path(self, path: Path) -> Path:
        """
        Ensure path is unique by adding number suffix if needed.

        Args:
            path: Path to make unique

        Returns:
            Unique path

        """
        if not path.exists():
            return path

        # Split into stem and suffix
        if path.is_file():
            stem = path.stem
            suffix = path.suffix
            parent = path.parent

            counter = 1
            while True:
                new_path = parent / f"{stem}_{counter}{suffix}"
                if not new_path.exists():
                    return new_path
                counter += 1
        else:
            # Directory
            counter = 1
            while True:
                new_path = path.parent / f"{path.name}_{counter}"
                if not new_path.exists():
                    return new_path
                counter += 1

    def calculate_directory_size(self, path: Path) -> int:
        """
        Calculate total size of a directory.

        Args:
            path: Directory path

        Returns:
            Total size in bytes

        """
        if path.is_file():
            return path.stat().st_size

        total_size = 0
        for file_path in path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        return total_size

    def format_size(self, size_bytes: int) -> str:
        """
        Format byte size as human-readable string.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string

        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0

        return f"{size_bytes:.1f} PB"


class PathManager:
    """
    High-level path management for topyaz operations.

    Combines path validation with output generation and
    structure preservation logic.

    Used in:
    - topyaz/system/__init__.py
    """

    def __init__(self, output_dir: Path | None = None, preserve_structure: bool = True, backup_originals: bool = False):
        """
        Initialize path manager.

        Args:
            output_dir: Default output directory
            preserve_structure: Preserve input directory structure
            backup_originals: Create backups before processing

        """
        self.output_dir = output_dir
        self.preserve_structure = preserve_structure
        self.backup_originals = backup_originals
        self.validator = PathValidator(preserve_structure)

    def prepare_paths(
        self, input_path: str | Path, output_path: str | Path | None = None, product: Product | None = None
    ) -> tuple[Path, Path]:
        """
        Prepare and validate input/output paths.

        Args:
            input_path: Input path
            output_path: Output path (optional)
            product: Product type for validation

        Returns:
            Tuple of (input_path, output_path)

        Raises:
            ValidationError: If paths are invalid

        """
        # Validate input
        input_obj = self.validator.validate_input_path(input_path, file_type=product)

        # Determine output
        if output_path:
            output_obj = self.validator.validate_output_path(output_path)
        else:
            output_obj = self.validator.generate_output_path(input_obj, self.output_dir, product=product)

        # Create backup if requested
        if self.backup_originals and input_obj.is_file():
            self.validator.create_backup(input_obj)

        return input_obj, output_obj
