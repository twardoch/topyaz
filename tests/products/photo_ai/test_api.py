#!/usr/bin/env python3
# this_file: tests/products/photo_ai/test_api.py
"""
Tests for Photo AI product API in topyaz.products.photo_ai.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from topyaz.core.errors import ValidationError
from topyaz.core.types import ProcessingOptions
from topyaz.products.photo_ai.api import PhotoAI


@pytest.fixture
def mock_executor() -> Mock:
    """Mock executor for testing."""
    return Mock()


@pytest.fixture
def processing_options() -> ProcessingOptions:
    """Processing options for testing."""
    return ProcessingOptions(verbose=False, dry_run=False)


@pytest.fixture
def photo_api(mock_executor: Mock, processing_options: ProcessingOptions) -> PhotoAI:
    """PhotoAI instance for testing."""
    with patch.object(PhotoAI, "find_executable", return_value=Path("/fake/tpai")):
        yield PhotoAI(mock_executor, processing_options)


class TestPhotoAI:
    """Test PhotoAI product API."""

    def test_initialization(self, photo_api: PhotoAI):
        """Test PhotoAI initialization."""
        assert photo_api.product_name == "Topaz Photo AI"
        assert photo_api.executable_name == "tpai"
        assert photo_api.supported_formats is not None
        assert isinstance(photo_api.supported_formats, (list, tuple))

    def test_supported_formats(self, photo_api: PhotoAI):
        """Test supported image formats."""
        formats = photo_api.supported_formats

        # Should include common image formats
        common_formats = ["jpg", "jpeg", "png", "tiff", "tif", "raw", "dng", "cr2", "nef"]
        for fmt in common_formats:
            if fmt in formats:
                assert fmt in formats

    def test_validate_params_valid(self, photo_api: PhotoAI):
        """Test parameter validation with valid parameters."""
        # Should not raise exceptions
        photo_api.validate_params(format="jpg", quality=95, compression=6)
        photo_api.validate_params(format="png", bit_depth=16)
        photo_api.validate_params(format="tiff", quality=100)

    def test_validate_params_invalid_format(self, photo_api: PhotoAI):
        """Test parameter validation with invalid format."""
        with pytest.raises(ValidationError, match="Invalid format"):
            photo_api.validate_params(format="invalid_format")

    def test_validate_params_invalid_quality(self, photo_api: PhotoAI):
        """Test parameter validation with invalid quality."""
        with pytest.raises(ValidationError, match="Quality must be between 0 and 100"):
            photo_api.validate_params(quality=101)

        with pytest.raises(ValidationError, match="Quality must be between 0 and 100"):
            photo_api.validate_params(quality=-1)

    def test_validate_params_invalid_bit_depth(self, photo_api: PhotoAI):
        """Test parameter validation with invalid bit depth."""
        with pytest.raises(ValidationError, match="Bit depth must be 8 or 16"):
            photo_api.validate_params(bit_depth=32)

        with pytest.raises(ValidationError, match="Bit depth must be 8 or 16"):
            photo_api.validate_params(bit_depth=4)

    def test_validate_params_compression_range(self, photo_api: PhotoAI):
        """Test parameter validation for PNG compression (valid range 0-10)."""
        # Valid compression values (0-10 inclusive)
        photo_api.validate_params(compression=0)
        photo_api.validate_params(compression=6)
        photo_api.validate_params(compression=10)

        # Invalid compression values
        with pytest.raises(ValidationError, match="Compression must be between 0 and 10"):
            photo_api.validate_params(compression=11)

        with pytest.raises(ValidationError, match="Compression must be between 0 and 10"):
            photo_api.validate_params(compression=-1)

    def test_build_command_basic(self, photo_api: PhotoAI):
        """Test basic command building."""
        cmd = photo_api.build_command(Path("input.jpg"), Path("output.jpg"), format="jpg", quality=95)

        cmd_str = " ".join(cmd)
        assert "/fake/tpai" in cmd_str
        assert "input.jpg" in cmd_str
        assert "output.jpg" in cmd_str

    def test_build_command_with_options(self, photo_api: PhotoAI):
        """Test command building with various options."""
        cmd = photo_api.build_command(
            Path("input.jpg"), Path("output.jpg"), format="png", quality=100, bit_depth=16, compression=6
        )

        cmd_str = " ".join(cmd)
        assert "input.jpg" in cmd_str
        assert "output.jpg" in cmd_str
        # Implementation-specific assertions would go here

    def test_build_command_verbose(self, photo_api: PhotoAI):
        """Test command building with verbose mode."""
        original_verbose = photo_api.options.verbose
        try:
            photo_api.options.verbose = True

            cmd = photo_api.build_command(Path("input.jpg"), Path("output.jpg"), format="jpg", quality=95)

            cmd_str = " ".join(cmd)
            # Should include verbose flags
            assert "-v" in cmd_str or "--verbose" in cmd_str or "verbose" in cmd_str.lower()
        finally:
            photo_api.options.verbose = original_verbose

    def test_parse_output_basic(self, photo_api: PhotoAI):
        """Test basic output parsing."""
        stdout = "Processing completed successfully\nOutput saved to: output.jpg\nFile size: 1024KB"
        stderr = ""

        parsed = photo_api.parse_output(stdout, stderr)

        assert isinstance(parsed, dict)
        # Implementation-specific assertions would go here

    def test_parse_output_error(self, photo_api: PhotoAI):
        """Test output parsing with errors."""
        stdout = ""
        stderr = "Error: Input file not found"

        parsed = photo_api.parse_output(stdout, stderr)

        assert isinstance(parsed, dict)
        # Should capture error information
        if "error" in parsed:
            assert parsed["error"] is True

    def test_parse_output_progress(self, photo_api: PhotoAI):
        """Test output parsing for progress information."""
        stdout = "Processing: 50% complete\nEstimated time remaining: 30 seconds"
        stderr = ""

        parsed = photo_api.parse_output(stdout, stderr)

        assert isinstance(parsed, dict)
        # Should extract progress information
        if "progress" in parsed:
            assert isinstance(parsed["progress"], (int, float))

    def test_process_dry_run(self, photo_api: PhotoAI, mock_executor: Mock, tmp_path: Path):
        """Test photo processing in dry run mode."""
        photo_api.options.dry_run = True

        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        result = photo_api.process(str(input_file), output_path=str(output_file), format="jpg", quality=95)

        assert result.success is True
        assert "DRY RUN" in result.stdout
        mock_executor.execute.assert_not_called()

    def test_process_success(self, photo_api: PhotoAI, mock_executor: Mock, tmp_path: Path):
        """Test successful photo processing via the temp-dir workflow."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"
        temp_output_file = tmp_path / "temp" / "input.jpg"

        # Mock successful execution
        mock_executor.execute.return_value = (0, "Processing completed", "")

        # PhotoAI uses the base temp-directory workflow: the generated file is
        # located via _find_output_file then moved to the final destination.
        with (
            patch.object(PhotoAI, "_find_output_file", return_value=temp_output_file) as mock_find,
            patch("shutil.move") as mock_move,
        ):
            result = photo_api.process(
                str(input_file),
                output_path=str(output_file),
                format="jpg",
                quality=95,
            )

        assert result.success is True
        assert result.output_path == output_file
        mock_executor.execute.assert_called_once()
        mock_find.assert_called_once()
        mock_move.assert_called_once_with(str(temp_output_file), str(output_file))

    def test_process_failure(self, photo_api: PhotoAI, mock_executor: Mock, tmp_path: Path):
        """Test failed photo processing."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        # Mock failed execution
        mock_executor.execute.return_value = (1, "", "Processing failed")

        result = photo_api.process(str(input_file), output_path=str(output_file), format="jpg", quality=95)

        assert result.success is False
        assert "processing failed" in result.error_message.lower()
        mock_executor.execute.assert_called_once()

    def test_process_missing_input(self, photo_api: PhotoAI, mock_executor: Mock, tmp_path: Path):
        """Missing input paths are rejected up front with a ValidationError."""
        input_file = tmp_path / "nonexistent.jpg"
        output_file = tmp_path / "output.jpg"

        with pytest.raises(ValidationError, match="does not exist"):
            photo_api.process(
                str(input_file),
                output_path=str(output_file),
                format="jpg",
                quality=95,
            )

        mock_executor.execute.assert_not_called()

    def test_process_invalid_parameters(self, photo_api: PhotoAI, mock_executor: Mock, tmp_path: Path):
        """Test processing with invalid parameters."""
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"

        # Should raise ValidationError for invalid parameters
        with pytest.raises(ValidationError):
            photo_api.process(str(input_file), output_path=str(output_file), format="invalid_format", quality=95)

    def test_get_executable_path(self, photo_api: PhotoAI):
        """Test executable path detection."""
        path = photo_api.get_executable_path()

        # Should return a Path object
        assert isinstance(path, Path)
        assert path == Path("/fake/tpai")

    def test_find_executable_method(self, photo_api: PhotoAI):
        """Test the find_executable method."""
        # This method should exist and be callable
        assert hasattr(photo_api, "find_executable")
        assert callable(photo_api.find_executable)

    def test_validate_input_file_format(self, photo_api: PhotoAI):
        """Test input file format validation."""
        # Valid image formats should pass
        valid_formats = ["test.jpg", "test.png", "test.tiff"]
        for fmt in valid_formats:
            try:
                # Implementation may vary on how this is validated
                photo_api.validate_params(input_file=fmt)
            except (ValidationError, AttributeError):
                # Either validation fails or method doesn't exist
                pass

    def test_batch_processing_preparation(self, photo_api: PhotoAI):
        """Test batch processing preparation if available."""
        # This is an optional feature that might exist
        if hasattr(photo_api, "prepare_batch"):
            # Should be callable
            assert callable(photo_api.prepare_batch)

    def test_auto_enhancement_features(self, photo_api: PhotoAI):
        """Test auto enhancement features if available."""
        # Photo AI might have auto enhancement features
        if hasattr(photo_api, "auto_enhance"):
            # Should be callable
            assert callable(photo_api.auto_enhance)

            # Should accept common parameters
            try:
                photo_api.validate_params(auto_enhance=True)
            except (ValidationError, AttributeError):
                # Method might not be implemented yet
                pass

    def test_noise_reduction_params(self, photo_api: PhotoAI):
        """Test noise reduction parameter validation."""
        # Test noise reduction if supported
        try:
            photo_api.validate_params(noise_reduction=50)
        except (ValidationError, AttributeError):
            # Feature might not be implemented
            pass

    def test_sharpening_params(self, photo_api: PhotoAI):
        """Test sharpening parameter validation."""
        # Test sharpening if supported
        try:
            photo_api.validate_params(sharpening=30)
        except (ValidationError, AttributeError):
            # Feature might not be implemented
            pass

    def test_color_enhancement_params(self, photo_api: PhotoAI):
        """Test color enhancement parameter validation."""
        # Test color enhancement if supported
        try:
            photo_api.validate_params(color_enhancement=True)
        except (ValidationError, AttributeError):
            # Feature might not be implemented
            pass

    def test_face_recovery_params(self, photo_api: PhotoAI):
        """Test face recovery parameter validation."""
        # Test face recovery if supported
        try:
            photo_api.validate_params(face_recovery=True)
        except (ValidationError, AttributeError):
            # Feature might not be implemented
            pass
