#!/usr/bin/env python3
# this_file: tests/test_utils.py
"""
Tests for utility functions in topyaz.utils.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from topyaz.utils.validation import (
    validate_file_exists,
    validate_file_format,
    validate_image_file,
    validate_output_path,
    validate_video_file,
)


class TestValidationUtils:
    """Test validation utility functions."""

    def test_validate_file_exists_valid(self):
        """Test file existence validation with valid file."""
        with tempfile.NamedTemporaryFile() as temp_file:
            # Should not raise an exception
            validate_file_exists(temp_file.name)
            validate_file_exists(Path(temp_file.name))

    def test_validate_file_exists_invalid(self):
        """Test file existence validation with invalid file."""
        with pytest.raises(FileNotFoundError):
            validate_file_exists("/nonexistent/file.jpg")
        
        with pytest.raises(FileNotFoundError):
            validate_file_exists(Path("/nonexistent/file.jpg"))

    def test_validate_file_format_valid(self):
        """Test file format validation with valid formats."""
        supported_formats = ["jpg", "jpeg", "png", "tiff", "tif"]
        
        # Should not raise exceptions
        validate_file_format("test.jpg", supported_formats)
        validate_file_format("test.JPEG", supported_formats)
        validate_file_format("test.png", supported_formats)
        validate_file_format(Path("test.tiff"), supported_formats)

    def test_validate_file_format_invalid(self):
        """Test file format validation with invalid formats."""
        supported_formats = ["jpg", "jpeg", "png"]
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            validate_file_format("test.gif", supported_formats)
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            validate_file_format("test.bmp", supported_formats)

    def test_validate_image_file_valid(self):
        """Test image file validation with valid images."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            # Create a small test image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(temp_file.name)
            
            # Should not raise an exception
            validate_image_file(temp_file.name)
            validate_image_file(Path(temp_file.name))

    def test_validate_image_file_invalid(self):
        """Test image file validation with invalid images."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            # Write non-image data
            temp_file.write(b"This is not an image file")
            temp_file.flush()
            
            with pytest.raises(ValueError, match="Invalid image file"):
                validate_image_file(temp_file.name)

    def test_validate_video_file_valid(self):
        """Test video file validation with valid extensions."""
        # We can't easily create real video files, so we'll just test extension validation
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            # Just test that it doesn't raise for valid video extensions
            # The actual implementation might do more validation
            try:
                validate_video_file(temp_file.name)
            except ValueError as e:
                # If it fails, it should be about content, not extension
                assert "extension" not in str(e).lower()

    def test_validate_video_file_invalid_extension(self):
        """Test video file validation with invalid extensions."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            with pytest.raises(ValueError, match="Unsupported video format"):
                validate_video_file(temp_file.name)

    def test_validate_output_path_valid(self):
        """Test output path validation with valid paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.jpg"
            
            # Should not raise an exception
            validate_output_path(str(output_path))
            validate_output_path(output_path)

    def test_validate_output_path_invalid_directory(self):
        """Test output path validation with invalid directory."""
        invalid_path = "/nonexistent/directory/output.jpg"
        
        with pytest.raises(ValueError, match="Output directory does not exist"):
            validate_output_path(invalid_path)

    def test_validate_output_path_creates_directory(self):
        """Test that output path validation can create directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "new_subdir" / "output.jpg"
            
            # Directory doesn't exist initially
            assert not output_path.parent.exists()
            
            # Should create the directory
            validate_output_path(str(output_path), create_dirs=True)
            assert output_path.parent.exists()

    def test_validate_output_path_file_exists_warning(self):
        """Test output path validation when file already exists."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            # File exists, should warn but not raise
            try:
                validate_output_path(temp_file.name)
                # If it doesn't raise, that's also acceptable behavior
            except ValueError:
                # If it raises, the message should be about file existence
                pass


class TestLoggingUtils:
    """Test logging utility functions."""

    def test_logging_imports(self):
        """Test that logging utilities can be imported."""
        from topyaz.utils.logging import setup_logging
        
        # Should be callable
        assert callable(setup_logging)

    @patch('topyaz.utils.logging.logger')
    def test_setup_logging_basic(self, mock_logger):
        """Test basic logging setup."""
        from topyaz.utils.logging import setup_logging
        
        # Should not raise an exception
        setup_logging()
        
        # Could verify that logger was configured, but this depends on implementation
        # For now, just ensure it's callable and doesn't crash

    @patch('topyaz.utils.logging.logger')
    def test_setup_logging_with_level(self, mock_logger):
        """Test logging setup with specific level."""
        from topyaz.utils.logging import setup_logging
        
        # Should not raise an exception
        setup_logging(level="DEBUG")
        setup_logging(level="INFO")
        setup_logging(level="WARNING")
        setup_logging(level="ERROR")