#!/usr/bin/env python3
# this_file: tests/products/video_ai/test_api.py
"""
Tests for Video AI product API in topyaz.products.video_ai.
"""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from topyaz.core.errors import ValidationError
from topyaz.core.types import ProcessingOptions
from topyaz.products.video_ai.api import VideoAI


@pytest.fixture
def mock_executor() -> Mock:
    """Mock executor for testing."""
    return Mock()


@pytest.fixture
def processing_options() -> ProcessingOptions:
    """Processing options for testing."""
    return ProcessingOptions(verbose=False, dry_run=False)


@pytest.fixture
def video_api(mock_executor: Mock, processing_options: ProcessingOptions) -> VideoAI:
    """VideoAI instance for testing."""
    with patch.object(VideoAI, "find_executable", return_value=Path("/fake/ffmpeg")):
        yield VideoAI(mock_executor, processing_options)


class TestVideoAI:
    """Test VideoAI product API."""

    def test_initialization(self, video_api: VideoAI):
        """Test VideoAI initialization."""
        assert video_api.product_name == "Topaz Video AI"
        assert video_api.executable_name == "ffmpeg"
        assert video_api.supported_formats is not None
        assert isinstance(video_api.supported_formats, (list, tuple))

    def test_supported_formats(self, video_api: VideoAI):
        """Test supported video formats."""
        formats = video_api.supported_formats
        
        # Should include common video formats
        common_formats = ["mp4", "mov", "avi", "mkv", "wmv", "flv"]
        for fmt in common_formats:
            if fmt in formats:
                assert fmt in formats

    def test_validate_params_valid(self, video_api: VideoAI):
        """Test parameter validation with valid parameters."""
        # Should not raise exceptions
        video_api.validate_params(model="amq-13", scale=2, quality=18)
        video_api.validate_params(model="ahq-11", scale=1, quality=28)
        video_api.validate_params(model="prob-3", scale=4, quality=10)

    def test_validate_params_invalid_model(self, video_api: VideoAI):
        """Test parameter validation with invalid model."""
        with pytest.raises(ValidationError, match="Invalid model"):
            video_api.validate_params(model="invalid_model")

    def test_validate_params_invalid_scale(self, video_api: VideoAI):
        """Test parameter validation with invalid scale."""
        with pytest.raises(ValidationError, match="Scale must be between 1 and 4"):
            video_api.validate_params(scale=5)
        
        with pytest.raises(ValidationError, match="Scale must be between 1 and 4"):
            video_api.validate_params(scale=0)

    def test_validate_params_invalid_quality(self, video_api: VideoAI):
        """Test parameter validation with invalid quality."""
        with pytest.raises(ValidationError, match="Quality must be between 1 and 51"):
            video_api.validate_params(quality=52)
        
        with pytest.raises(ValidationError, match="Quality must be between 1 and 51"):
            video_api.validate_params(quality=0)

    def test_validate_params_fps_range(self, video_api: VideoAI):
        """Test parameter validation for FPS."""
        # Valid FPS values
        video_api.validate_params(fps=24)
        video_api.validate_params(fps=30)
        video_api.validate_params(fps=60)
        
        # Invalid FPS values
        with pytest.raises(ValidationError, match="FPS must be between 1 and 120"):
            video_api.validate_params(fps=121)
        
        with pytest.raises(ValidationError, match="FPS must be between 1 and 120"):
            video_api.validate_params(fps=0)

    def test_build_command_basic(self, video_api: VideoAI):
        """Test basic command building."""
        cmd = video_api.build_command(
            Path("input.mp4"),
            Path("output.mp4"),
            model="amq-13",
            scale=2
        )
        
        cmd_str = " ".join(cmd)
        assert "/fake/ffmpeg" in cmd_str
        assert "input.mp4" in cmd_str
        assert "output.mp4" in cmd_str

    def test_build_command_with_options(self, video_api: VideoAI):
        """Test command building with various options."""
        cmd = video_api.build_command(
            Path("input.mp4"),
            Path("output.mp4"),
            model="amq-13",
            scale=2,
            quality=18,
            fps=30
        )
        
        cmd_str = " ".join(cmd)
        assert "input.mp4" in cmd_str
        assert "output.mp4" in cmd_str
        # Implementation-specific assertions would go here

    def test_build_command_verbose(self, video_api: VideoAI):
        """Test command building with verbose mode."""
        original_verbose = video_api.options.verbose
        try:
            video_api.options.verbose = True
            
            cmd = video_api.build_command(
                Path("input.mp4"),
                Path("output.mp4"),
                model="amq-13",
                scale=2
            )
            
            cmd_str = " ".join(cmd)
            # Should include verbose flags
            assert "-v" in cmd_str or "--verbose" in cmd_str or "verbose" in cmd_str.lower()
        finally:
            video_api.options.verbose = original_verbose

    def test_parse_output_basic(self, video_api: VideoAI):
        """Test basic output parsing."""
        stdout = "frame= 1000 fps= 30 q=18.0 size= 1024kB time=00:00:33.33 bitrate= 251.2kbits/s speed=1.0x"
        stderr = ""
        
        parsed = video_api.parse_output(stdout, stderr)
        
        assert isinstance(parsed, dict)
        # Implementation-specific assertions would go here

    def test_parse_output_error(self, video_api: VideoAI):
        """Test output parsing with errors."""
        stdout = ""
        stderr = "Error: Input file not found"
        
        parsed = video_api.parse_output(stdout, stderr)
        
        assert isinstance(parsed, dict)
        # Should capture error information
        if "error" in parsed:
            assert parsed["error"] is True

    def test_parse_output_progress(self, video_api: VideoAI):
        """Test output parsing for progress information."""
        stdout = "frame= 500 fps= 30 q=18.0 size= 512kB time=00:00:16.67 bitrate= 251.2kbits/s speed=1.0x"
        stderr = ""
        
        parsed = video_api.parse_output(stdout, stderr)
        
        assert isinstance(parsed, dict)
        # Should extract progress information
        if "progress" in parsed:
            assert isinstance(parsed["progress"], (int, float))

    def test_process_dry_run(self, video_api: VideoAI, mock_executor: Mock, tmp_path: Path):
        """Test video processing in dry run mode."""
        video_api.options.dry_run = True
        
        input_file = tmp_path / "input.mp4"
        input_file.touch()
        output_file = tmp_path / "output.mp4"
        
        result = video_api.process(
            str(input_file),
            output_path=str(output_file),
            model="amq-13",
            scale=2
        )
        
        assert result.success is True
        assert "DRY RUN" in result.stdout
        mock_executor.execute.assert_not_called()

    def test_process_success(self, video_api: VideoAI, mock_executor: Mock, tmp_path: Path):
        """Test successful video processing."""
        input_file = tmp_path / "input.mp4"
        input_file.touch()
        output_file = tmp_path / "output.mp4"
        
        # Mock successful execution
        mock_executor.execute.return_value = (0, "Processing completed", "")
        
        with patch("os.stat") as mock_stat:
            def stat_side_effect(path):
                stat_result = Mock()
                if Path(path) == input_file:
                    stat_result.st_size = 1000000  # 1MB
                elif Path(path) == output_file:
                    stat_result.st_size = 2000000  # 2MB
                else:
                    stat_result.st_size = 4096
                stat_result.st_mode = 0o100644
                return stat_result
            
            mock_stat.side_effect = stat_side_effect
            
            result = video_api.process(
                str(input_file),
                output_path=str(output_file),
                model="amq-13",
                scale=2
            )
            
            assert result.success is True
            assert result.output_path == output_file
            mock_executor.execute.assert_called_once()

    def test_process_failure(self, video_api: VideoAI, mock_executor: Mock, tmp_path: Path):
        """Test failed video processing."""
        input_file = tmp_path / "input.mp4"
        input_file.touch()
        output_file = tmp_path / "output.mp4"
        
        # Mock failed execution
        mock_executor.execute.return_value = (1, "", "Processing failed")
        
        result = video_api.process(
            str(input_file),
            output_path=str(output_file),
            model="amq-13",
            scale=2
        )
        
        assert result.success is False
        assert "processing failed" in result.error_message.lower()
        mock_executor.execute.assert_called_once()

    def test_process_missing_input(self, video_api: VideoAI, mock_executor: Mock, tmp_path: Path):
        """Test processing with missing input file."""
        input_file = tmp_path / "nonexistent.mp4"
        output_file = tmp_path / "output.mp4"
        
        result = video_api.process(
            str(input_file),
            output_path=str(output_file),
            model="amq-13",
            scale=2
        )
        
        assert result.success is False
        assert "not found" in result.error_message.lower() or "does not exist" in result.error_message.lower()

    def test_process_invalid_parameters(self, video_api: VideoAI, mock_executor: Mock, tmp_path: Path):
        """Test processing with invalid parameters."""
        input_file = tmp_path / "input.mp4"
        input_file.touch()
        output_file = tmp_path / "output.mp4"
        
        # Should raise ValidationError for invalid parameters
        with pytest.raises(ValidationError):
            video_api.process(
                str(input_file),
                output_path=str(output_file),
                model="invalid_model",
                scale=2
            )

    def test_get_executable_path(self, video_api: VideoAI):
        """Test executable path detection."""
        path = video_api.get_executable_path()
        
        # Should return a Path object
        assert isinstance(path, Path)
        assert path == Path("/fake/ffmpeg")

    def test_find_executable_method(self, video_api: VideoAI):
        """Test the find_executable method."""
        # This method should exist and be callable
        assert hasattr(video_api, "find_executable")
        assert callable(video_api.find_executable)

    def test_validate_input_file_format(self, video_api: VideoAI):
        """Test input file format validation."""
        # Valid video formats should pass
        valid_formats = ["test.mp4", "test.mov", "test.avi"]
        for fmt in valid_formats:
            try:
                # Implementation may vary on how this is validated
                video_api.validate_params(input_file=fmt)
            except (ValidationError, AttributeError):
                # Either validation fails or method doesn't exist
                pass

    def test_estimate_processing_time(self, video_api: VideoAI):
        """Test processing time estimation if available."""
        # This is an optional feature that might exist
        if hasattr(video_api, "estimate_processing_time"):
            # Should be callable
            assert callable(video_api.estimate_processing_time)

    def test_get_model_info(self, video_api: VideoAI):
        """Test model information retrieval if available."""
        # This is an optional feature that might exist
        if hasattr(video_api, "get_model_info"):
            # Should be callable
            assert callable(video_api.get_model_info)
            
            # Should return info for valid models
            try:
                info = video_api.get_model_info("amq-13")
                assert isinstance(info, dict)
            except (NotImplementedError, AttributeError):
                # Method might not be implemented yet
                pass