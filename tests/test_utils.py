#!/usr/bin/env python3
# this_file: tests/test_utils.py
"""
Tests for utility functions in topyaz.utils.

The validation utilities operate on *output* files produced by Topaz products:
``validate_output_file`` inspects an output path, ``get_media_info`` reads image
and video metadata, ``compare_media_files`` diffs input vs output, and
``enhance_processing_result`` augments a ProcessingResult with validation data.
"""

from pathlib import Path

import pytest
from PIL import Image

from topyaz.core.types import ProcessingResult
from topyaz.utils.logging import setup_logging
from topyaz.utils.validation import (
    compare_media_files,
    enhance_processing_result,
    get_media_info,
    validate_output_file,
)


@pytest.fixture
def image_file(tmp_path: Path) -> Path:
    """Create a small real JPEG on disk."""
    path = tmp_path / "image.jpg"
    Image.new("RGB", (64, 48), color="red").save(path)
    return path


class TestValidateOutputFile:
    """Test validate_output_file."""

    def test_missing_output_reports_error(self, tmp_path: Path):
        """A non-existent output file is reported as missing with an error."""
        result = validate_output_file(tmp_path / "in.jpg", tmp_path / "out.jpg")

        assert result["file_exists"] is False
        assert result["errors"]

    def test_valid_image_output(self, image_file: Path, tmp_path: Path):
        """A real image output is recognised as a valid media format."""
        input_path = tmp_path / "in.jpg"
        Image.new("RGB", (32, 24), color="blue").save(input_path)

        result = validate_output_file(input_path, image_file)

        assert result["file_exists"] is True
        assert result["is_valid_format"] is True
        assert result["mime_type"] == "image/jpeg"
        assert result["file_size"] > 0
        assert result["media_info"].get("width") == 64
        assert result["media_info"].get("height") == 48

    def test_non_media_output_is_invalid(self, tmp_path: Path):
        """A text output file is flagged as an unexpected media type."""
        output = tmp_path / "out.txt"
        output.write_text("not media")

        result = validate_output_file(tmp_path / "in.jpg", output)

        assert result["file_exists"] is True
        assert result["is_valid_format"] is False
        assert result["errors"]


class TestGetMediaInfo:
    """Test get_media_info."""

    def test_image_dimensions(self, image_file: Path):
        """Image media info includes width, height, and format."""
        info = get_media_info(image_file)

        assert info["width"] == 64
        assert info["height"] == 48
        assert info["mode"] == "RGB"

    def test_unknown_extension_returns_empty(self, tmp_path: Path):
        """A non-media extension yields an empty info dict."""
        other = tmp_path / "data.bin"
        other.write_bytes(b"\x00\x01")

        assert get_media_info(other) == {}


class TestCompareMediaFiles:
    """Test compare_media_files."""

    def test_compare_two_images(self, tmp_path: Path):
        """Comparing two valid images reports both as valid and a size ratio."""
        input_path = tmp_path / "in.jpg"
        output_path = tmp_path / "out.jpg"
        Image.new("RGB", (32, 24), color="blue").save(input_path)
        Image.new("RGB", (64, 48), color="blue").save(output_path)

        comparison = compare_media_files(input_path, output_path)

        assert comparison["input_valid"] is True
        assert comparison["output_valid"] is True
        assert comparison["resolution_changed"] is True
        assert comparison["size_ratio"] > 0

    def test_compare_missing_input(self, image_file: Path, tmp_path: Path):
        """A missing input file is recorded as an issue."""
        comparison = compare_media_files(tmp_path / "missing.jpg", image_file)

        assert comparison["input_valid"] is False
        assert comparison["issues"]


class TestEnhanceProcessingResult:
    """Test enhance_processing_result."""

    def test_enhances_successful_result(self, image_file: Path, tmp_path: Path):
        """A successful result gains validation metadata in additional_info."""
        input_path = tmp_path / "in.jpg"
        Image.new("RGB", (32, 24), color="green").save(input_path)

        result = ProcessingResult(success=True, input_path=input_path, output_path=image_file)
        enhanced = enhance_processing_result(result)

        assert enhanced.success is True
        assert "output_validation" in enhanced.additional_info
        assert "file_comparison" in enhanced.additional_info

    def test_failed_result_passes_through(self, tmp_path: Path):
        """A failed result without output is returned unchanged."""
        result = ProcessingResult(success=False, input_path=tmp_path / "in.jpg", output_path=None)

        enhanced = enhance_processing_result(result)

        assert enhanced.success is False
        assert enhanced.additional_info == {}

    def test_marks_missing_output_as_failure(self, tmp_path: Path):
        """A 'successful' result pointing at a missing output is flipped to failure."""
        result = ProcessingResult(
            success=True,
            input_path=tmp_path / "in.jpg",
            output_path=tmp_path / "missing_out.jpg",
        )

        enhanced = enhance_processing_result(result)

        assert enhanced.success is False
        assert enhanced.error_message


class TestLoggingUtils:
    """Test logging setup helpers."""

    def test_setup_logging_callable(self):
        """setup_logging is importable and callable."""
        assert callable(setup_logging)

    def test_setup_logging_runs(self):
        """setup_logging runs in both verbose and quiet modes without error."""
        setup_logging(verbose=True)
        setup_logging(verbose=False)
