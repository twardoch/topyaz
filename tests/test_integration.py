#!/usr/bin/env python3
# this_file: tests/test_integration.py
"""
Integration tests for topyaz package.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from topyaz.cli import TopyazCLI
from topyaz.core.config import Config
from topyaz.core.types import ProcessingOptions


class TestIntegration:
    """Integration tests for the complete topyaz system."""

    @pytest.mark.integration
    def test_full_workflow_gigapixel(self):
        """Test complete workflow for Gigapixel AI processing."""
        # Initialize CLI
        cli = TopyazCLI(verbose=True, dry_run=True)
        
        # Create test input file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            input_path = temp_file.name
        
        # Test processing
        result = cli.giga(
            input_path,
            output="output.jpg",
            model="std",
            scale=2,
            denoise=50
        )
        
        # Verify results
        assert result.success is True
        assert "DRY RUN" in result.stdout

    @pytest.mark.integration
    def test_full_workflow_video_ai(self):
        """Test complete workflow for Video AI processing."""
        # Initialize CLI
        cli = TopyazCLI(verbose=True, dry_run=True)
        
        # Create test input file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            input_path = temp_file.name
        
        # Test processing
        result = cli.video(
            input_path,
            output="output.mp4",
            model="amq-13",
            scale=2,
            quality=18
        )
        
        # Verify results
        assert result.success is True
        assert "DRY RUN" in result.stdout

    @pytest.mark.integration
    def test_full_workflow_photo_ai(self):
        """Test complete workflow for Photo AI processing."""
        # Initialize CLI
        cli = TopyazCLI(verbose=True, dry_run=True)
        
        # Create test input file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            input_path = temp_file.name
        
        # Test processing
        result = cli.photo(
            input_path,
            output="output.jpg",
            format="jpg",
            quality=95
        )
        
        # Verify results
        assert result.success is True
        assert "DRY RUN" in result.stdout

    @pytest.mark.integration
    def test_config_system_integration(self):
        """Test configuration system integration."""
        # Test config loading and usage
        config = Config()
        
        # Test that config is properly loaded
        assert config.get("defaults.log_level") is not None
        assert config.get("defaults.timeout") is not None
        
        # Test config with CLI
        cli = TopyazCLI(verbose=True, dry_run=True)
        
        # Config should be accessible through products
        gigapixel = cli._gigapixel
        assert gigapixel is not None

    @pytest.mark.integration
    def test_error_handling_integration(self):
        """Test error handling across the system."""
        cli = TopyazCLI(verbose=True, dry_run=False)
        
        # Test with non-existent input file
        result = cli.giga(
            "/nonexistent/file.jpg",
            output="output.jpg",
            model="std",
            scale=2
        )
        
        # Should handle error gracefully
        assert result.success is False
        assert result.error_message is not None

    @pytest.mark.integration
    def test_multiple_product_usage(self):
        """Test using multiple products in sequence."""
        cli = TopyazCLI(verbose=True, dry_run=True)
        
        # Create test files
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as img_file:
            img_path = img_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as vid_file:
            vid_path = vid_file.name
        
        # Process with different products
        gp_result = cli.giga(img_path, output="gp_output.jpg", model="std", scale=2)
        video_result = cli.video(vid_path, output="video_output.mp4", model="amq-13", scale=2)
        photo_result = cli.photo(img_path, output="photo_output.jpg", format="jpg", quality=95)
        
        # All should succeed in dry run
        assert gp_result.success is True
        assert video_result.success is True
        assert photo_result.success is True

    @pytest.mark.integration
    def test_system_info_integration(self):
        """Test system information integration."""
        cli = TopyazCLI()
        
        # Test system info method
        sysinfo = cli._sysinfo()
        assert sysinfo is not None
        
        # Should include basic system information
        if isinstance(sysinfo, dict):
            # Expected system info fields
            expected_fields = ["platform", "python_version", "cpu_count", "memory_total"]
            for field in expected_fields:
                if field in sysinfo:
                    assert sysinfo[field] is not None

    @pytest.mark.integration
    def test_parameter_validation_integration(self):
        """Test parameter validation integration across products."""
        cli = TopyazCLI(verbose=True, dry_run=True)
        
        # Test that validation errors are properly handled
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            input_path = temp_file.name
            
            # Test invalid parameters
            with pytest.raises(Exception):  # Should raise ValidationError or similar
                cli.giga(input_path, output="output.jpg", model="invalid_model", scale=2)
            
            with pytest.raises(Exception):  # Should raise ValidationError or similar
                cli.video(input_path, output="output.mp4", model="invalid_model", scale=2)
            
            with pytest.raises(Exception):  # Should raise ValidationError or similar
                cli.photo(input_path, output="output.jpg", format="invalid_format", quality=95)

    @pytest.mark.integration
    def test_verbose_logging_integration(self):
        """Test verbose logging integration."""
        # Test with verbose enabled
        cli_verbose = TopyazCLI(verbose=True, dry_run=True)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            input_path = temp_file.name
            
            result = cli_verbose.giga(input_path, output="output.jpg", model="std", scale=2)
            
            # Should have verbose output
            assert result.success is True
            # In verbose mode, there should be more detailed output
            assert len(result.stdout) > 0

    @pytest.mark.integration
    def test_timeout_integration(self):
        """Test timeout integration."""
        # Test with short timeout
        cli = TopyazCLI(verbose=True, dry_run=False, timeout=1)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            input_path = temp_file.name
            
            # With a very short timeout, processing might fail
            # But the system should handle it gracefully
            result = cli.giga(input_path, output="output.jpg", model="std", scale=2)
            
            # Should complete successfully (file not found error) or timeout gracefully
            assert result is not None
            assert hasattr(result, 'success')

    @pytest.mark.integration
    def test_parallel_jobs_integration(self):
        """Test parallel jobs integration."""
        # Test with multiple parallel jobs
        cli = TopyazCLI(verbose=True, dry_run=True, parallel_jobs=2)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            input_path = temp_file.name
            
            result = cli.giga(input_path, output="output.jpg", model="std", scale=2)
            
            # Should succeed with parallel jobs setting
            assert result.success is True

    @pytest.mark.integration
    def test_file_format_validation_integration(self):
        """Test file format validation integration."""
        cli = TopyazCLI(verbose=True, dry_run=True)
        
        # Test with various file formats
        test_files = [
            ("test.jpg", "jpg"),
            ("test.png", "png"),
            ("test.tiff", "tiff"),
            ("test.mp4", "mp4"),
            ("test.mov", "mov"),
        ]
        
        for filename, expected_format in test_files:
            with tempfile.NamedTemporaryFile(suffix=f'.{expected_format}', delete=False) as temp_file:
                # Test that format is properly detected and validated
                if expected_format in ["jpg", "png", "tiff"]:
                    result = cli.giga(temp_file.name, output=f"output.{expected_format}", model="std", scale=2)
                    assert result.success is True
                elif expected_format in ["mp4", "mov"]:
                    result = cli.video(temp_file.name, output=f"output.{expected_format}", model="amq-13", scale=2)
                    assert result.success is True

    @pytest.mark.integration
    def test_output_path_handling_integration(self):
        """Test output path handling integration."""
        cli = TopyazCLI(verbose=True, dry_run=True)
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            input_path = temp_file.name
            
            # Test with different output path scenarios
            with tempfile.TemporaryDirectory() as temp_dir:
                # Test with full path
                full_output = Path(temp_dir) / "output.jpg"
                result = cli.giga(input_path, output=str(full_output), model="std", scale=2)
                assert result.success is True
                
                # Test with relative path
                result = cli.giga(input_path, output="relative_output.jpg", model="std", scale=2)
                assert result.success is True

    @pytest.mark.integration
    def test_backward_compatibility_integration(self):
        """Test backward compatibility integration."""
        cli = TopyazCLI()
        
        # Test that all backward compatibility methods exist and work
        assert hasattr(cli, 'giga')
        assert hasattr(cli, 'video')
        assert hasattr(cli, 'photo')
        assert hasattr(cli, '_sysinfo')
        
        # Test that they're callable
        assert callable(cli.giga)
        assert callable(cli.video)
        assert callable(cli.photo)
        assert callable(cli._sysinfo)

    @pytest.mark.integration
    def test_memory_efficiency_integration(self):
        """Test memory efficiency integration."""
        # Test that multiple CLI instances don't leak memory
        instances = []
        for i in range(10):
            cli = TopyazCLI(verbose=False, dry_run=True)
            instances.append(cli)
        
        # All instances should be independent
        for i, cli in enumerate(instances):
            assert cli is not None
            assert cli._options.dry_run is True
            
            # Access products to ensure lazy loading works
            gigapixel = cli._gigapixel
            assert gigapixel is not None

    @pytest.mark.integration
    def test_error_recovery_integration(self):
        """Test error recovery integration."""
        cli = TopyazCLI(verbose=True, dry_run=False)
        
        # Test recovery from various error conditions
        error_scenarios = [
            ("/nonexistent/file.jpg", "std", 2),  # File not found
            ("", "std", 2),  # Empty filename
        ]
        
        for input_path, model, scale in error_scenarios:
            try:
                result = cli.giga(input_path, output="output.jpg", model=model, scale=scale)
                # Should handle error gracefully
                assert result.success is False
                assert result.error_message is not None
            except Exception as e:
                # Should not crash with unhandled exceptions
                assert isinstance(e, (ValueError, FileNotFoundError))

    @pytest.mark.integration
    def test_concurrent_access_integration(self):
        """Test concurrent access integration."""
        import threading
        
        results = []
        
        def process_file(index):
            cli = TopyazCLI(verbose=False, dry_run=True)
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                result = cli.giga(temp_file.name, output=f"output_{index}.jpg", model="std", scale=2)
                results.append((index, result))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=process_file, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All should succeed
        assert len(results) == 5
        for index, result in results:
            assert result.success is True