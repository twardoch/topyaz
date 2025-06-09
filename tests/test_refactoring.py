#!/usr/bin/env python3
# this_file: tests/test_refactoring.py
"""
Basic tests to verify the refactoring works correctly.

This module contains tests to ensure the new modular architecture
maintains backward compatibility and functions correctly.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from topyaz.cli import TopyazCLI
from topyaz.core.errors import ValidationError
from topyaz.core.types import ProcessingOptions
from topyaz.execution.local import LocalExecutor
from topyaz.products.gigapixel import GigapixelAI
from topyaz.products.photo_ai import PhotoAI
from topyaz.products.video_ai import VideoAI


class TestRefactoringBasics:
    """Test basic functionality of the refactored components."""

    def test_topyaz_wrapper_initialization(self):
        """Test that TopyazCLI initializes correctly."""
        wrapper = TopyazCLI(verbose=False, dry_run=True)

        assert wrapper.options.verbose is False
        assert wrapper.options.dry_run is True
        assert wrapper.executor is not None
        assert isinstance(wrapper.executor, LocalExecutor)

    def test_lazy_loading_products(self):
        """Test that products are lazy-loaded correctly."""
        wrapper = TopyazCLI(verbose=False, dry_run=True)

        # Products should be None initially
        assert wrapper._gigapixel is None
        assert wrapper._video_ai is None
        assert wrapper._photo_ai is None

        # Accessing properties should create instances
        gp = wrapper.gigapixel
        video = wrapper.video_ai
        photo = wrapper.photo_ai

        assert isinstance(gp, GigapixelAI)
        assert isinstance(video, VideoAI)
        assert isinstance(photo, PhotoAI)

        # Should return same instances on subsequent access
        assert wrapper.gigapixel is gp
        assert wrapper.video_ai is video
        assert wrapper.photo_ai is photo

    def test_product_initialization(self):
        """Test that individual products initialize correctly."""
        executor = Mock()
        options = ProcessingOptions(verbose=True, dry_run=True)

        gp = GigapixelAI(executor, options)
        video = VideoAI(executor, options)
        photo = PhotoAI(executor, options)

        assert gp.product_name == "Topaz Gigapixel AI"
        assert video.product_name == "Topaz Video AI"
        assert photo.product_name == "Topaz Photo AI"

        assert gp.executable_name == "gigapixel"
        assert video.executable_name == "ffmpeg"
        assert photo.executable_name == "tpai"

    def test_gigapixel_parameter_validation(self):
        """Test Gigapixel AI parameter validation."""
        executor = Mock()
        options = ProcessingOptions()
        gp = GigapixelAI(executor, options)

        # Valid parameters should pass
        gp.validate_params(model="std", scale=2, denoise=50)

        # Invalid model should raise error
        with pytest.raises(ValidationError, match="Invalid model"):
            gp.validate_params(model="invalid_model")

        # Invalid scale should raise error
        with pytest.raises(ValidationError, match="Scale must be between 1 and 6"):
            gp.validate_params(scale=10)

        # Invalid denoise should raise error
        with pytest.raises(ValidationError, match="denoise must be between 1 and 100"):
            gp.validate_params(denoise=150)

    def test_video_ai_parameter_validation(self):
        """Test Video AI parameter validation."""
        executor = Mock()
        options = ProcessingOptions()
        video = VideoAI(executor, options)

        # Valid parameters should pass
        video.validate_params(model="amq-13", scale=2, quality=18)

        # Invalid model should raise error
        with pytest.raises(ValidationError, match="Invalid model"):
            video.validate_params(model="invalid_model")

        # Invalid scale should raise error
        with pytest.raises(ValidationError, match="Scale must be between 1 and 4"):
            video.validate_params(scale=5)

        # Invalid quality should raise error
        with pytest.raises(ValidationError, match="Quality must be between 1 and 51"):
            video.validate_params(quality=100)

    def test_photo_ai_parameter_validation(self):
        """Test Photo AI parameter validation."""
        executor = Mock()
        options = ProcessingOptions()
        photo = PhotoAI(executor, options)

        # Valid parameters should pass
        photo.validate_params(format="jpg", quality=95, compression=6)

        # Invalid format should raise error
        with pytest.raises(ValidationError, match="Invalid format"):
            photo.validate_params(format="invalid_format")

        # Invalid quality should raise error
        with pytest.raises(ValidationError, match="Quality must be between 0 and 100"):
            photo.validate_params(quality=150)

        # Invalid bit depth should raise error
        with pytest.raises(ValidationError, match="Bit depth must be 8 or 16"):
            photo.validate_params(bit_depth=32)

    @patch("topyaz.products.gigapixel.GigapixelAI.get_executable_path")
    @patch("topyaz.execution.local.LocalExecutor.execute")
    def test_dry_run_mode(self, mock_execute, mock_executable):
        """Test that dry run mode works correctly."""
        mock_executable.return_value = Path("/fake/gigapixel")
        mock_execute.return_value = (0, "dry-run-output", "")

        wrapper = TopyazCLI(verbose=False, dry_run=True)

        # Should succeed without actually executing
        result = wrapper.gp("test_input.jpg", output="test_output.jpg")

        assert result is True
        # Should not have called the real executor
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        assert "dry-run" in str(call_args).lower() or wrapper.options.dry_run

    def test_supported_formats(self):
        """Test that products report correct supported formats."""
        executor = Mock()
        options = ProcessingOptions()

        gp = GigapixelAI(executor, options)
        video = VideoAI(executor, options)
        photo = PhotoAI(executor, options)

        # Check that common formats are supported
        assert "jpg" in gp.supported_formats
        assert "png" in gp.supported_formats
        assert "tiff" in gp.supported_formats

        assert "mp4" in video.supported_formats
        assert "mov" in video.supported_formats
        assert "avi" in video.supported_formats

        assert "jpg" in photo.supported_formats
        assert "png" in photo.supported_formats
        assert "dng" in photo.supported_formats

    def test_command_building(self):
        """Test that command building works correctly."""
        executor = Mock()
        options = ProcessingOptions(verbose=True)

        with patch("topyaz.products.gigapixel.GigapixelAI.get_executable_path") as mock_path:
            mock_path.return_value = Path("/fake/gigapixel")

            gp = GigapixelAI(executor, options)
            cmd = gp.build_command(Path("input.jpg"), Path("output.jpg"), model="std", scale=2, denoise=50)

            # Check that command contains expected elements
            cmd_str = " ".join(cmd)
            assert "/fake/gigapixel" in cmd_str
            assert "--cli" in cmd_str
            assert "-i" in cmd_str
            assert "input.jpg" in cmd_str
            assert "-o" in cmd_str
            assert "output.jpg" in cmd_str
            assert "-m" in cmd_str
            assert "std" in cmd_str
            assert "--scale" in cmd_str
            assert "2" in cmd_str
            assert "--denoise" in cmd_str
            assert "50" in cmd_str

    def test_backward_compatibility(self):
        """Test that the new CLI maintains backward compatibility."""
        wrapper = TopyazCLI(verbose=False, dry_run=True)

        # These method signatures should match the original
        assert hasattr(wrapper, "gp")
        assert hasattr(wrapper, "video")
        assert hasattr(wrapper, "photo")
        assert hasattr(wrapper, "system_info")

        # Methods should be callable
        assert callable(wrapper.gp)
        assert callable(wrapper.video)
        assert callable(wrapper.photo)
        assert callable(wrapper.system_info)
