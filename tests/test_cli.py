#!/usr/bin/env python3
# this_file: tests/test_cli.py
"""
Tests for the main CLI interface in topyaz.cli.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from topyaz.cli import TopyazCLI
from topyaz.core.errors import ValidationError
from topyaz.core.types import ProcessingOptions


class TestTopyazCLI:
    """Test the main CLI interface."""

    def test_initialization_defaults(self):
        """Test CLI initialization with default values."""
        cli = TopyazCLI()
        assert cli._options.verbose is False
        assert cli._options.dry_run is False
        assert cli._options.timeout == 300
        assert cli._options.parallel_jobs == 1

    def test_initialization_custom_options(self):
        """Test CLI initialization with custom options."""
        cli = TopyazCLI(verbose=True, dry_run=True, timeout=600, parallel_jobs=4)
        assert cli._options.verbose is True
        assert cli._options.dry_run is True
        assert cli._options.timeout == 600
        assert cli._options.parallel_jobs == 4

    def test_lazy_product_loading(self):
        """Test that product instances are created lazily."""
        cli = TopyazCLI()
        
        # Initially should be None
        assert cli._iGigapixelAI is None
        assert cli._iVideoAI is None
        assert cli._iPhotoAI is None
        
        # Access should create instances
        gigapixel = cli._gigapixel
        video = cli._video_ai
        photo = cli._photo_ai
        
        # Should be same instances on subsequent access
        assert cli._gigapixel is gigapixel
        assert cli._video_ai is video
        assert cli._photo_ai is photo

    def test_backward_compatibility_methods(self):
        """Test backward compatibility method names."""
        cli = TopyazCLI()
        
        # These methods should exist for backward compatibility
        assert hasattr(cli, 'giga')
        assert hasattr(cli, 'video')
        assert hasattr(cli, 'photo')
        assert hasattr(cli, '_sysinfo')
        
        # They should be callable
        assert callable(cli.giga)
        assert callable(cli.video)
        assert callable(cli.photo)
        assert callable(cli._sysinfo)

    @patch('topyaz.products.gigapixel.api.GigapixelAI.process')
    def test_giga_method_delegation(self, mock_process):
        """Test that giga method properly delegates to GigapixelAI."""
        cli = TopyazCLI()
        mock_process.return_value = Mock(success=True)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_file:
            cli.giga(temp_file.name, output='output.jpg', model='std', scale=2)
            mock_process.assert_called_once()

    @patch('topyaz.products.video_ai.api.VideoAI.process')
    def test_video_method_delegation(self, mock_process):
        """Test that video method properly delegates to VideoAI."""
        cli = TopyazCLI()
        mock_process.return_value = Mock(success=True)
        
        with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_file:
            cli.video(temp_file.name, output='output.mp4', model='amq-13', scale=2)
            mock_process.assert_called_once()

    @patch('topyaz.products.photo_ai.api.PhotoAI.process')
    def test_photo_method_delegation(self, mock_process):
        """Test that photo method properly delegates to PhotoAI."""
        cli = TopyazCLI()
        mock_process.return_value = Mock(success=True)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_file:
            cli.photo(temp_file.name, output='output.jpg', format='jpg', quality=95)
            mock_process.assert_called_once()

    def test_sysinfo_method(self):
        """Test the system information method."""
        cli = TopyazCLI()
        
        # Should return system info without errors
        result = cli._sysinfo()
        assert result is not None
        # The actual implementation may vary, but it should not raise exceptions

    def test_dry_run_propagation(self):
        """Test that dry_run option is properly propagated to products."""
        cli = TopyazCLI(dry_run=True)
        
        assert cli._gigapixel.options.dry_run is True
        assert cli._video_ai.options.dry_run is True
        assert cli._photo_ai.options.dry_run is True

    def test_verbose_propagation(self):
        """Test that verbose option is properly propagated to products."""
        cli = TopyazCLI(verbose=True)
        
        assert cli._gigapixel.options.verbose is True
        assert cli._video_ai.options.verbose is True
        assert cli._photo_ai.options.verbose is True

    def test_timeout_propagation(self):
        """Test that timeout option is properly propagated to products."""
        cli = TopyazCLI(timeout=600)
        
        assert cli._gigapixel.options.timeout == 600
        assert cli._video_ai.options.timeout == 600
        assert cli._photo_ai.options.timeout == 600

    def test_parallel_jobs_propagation(self):
        """Test that parallel_jobs option is properly propagated to products."""
        cli = TopyazCLI(parallel_jobs=4)
        
        assert cli._gigapixel.options.parallel_jobs == 4
        assert cli._video_ai.options.parallel_jobs == 4
        assert cli._photo_ai.options.parallel_jobs == 4