#!/usr/bin/env python3
# this_file: tests/test_system.py
"""
Tests for system-related functionality in topyaz.system.
"""

import platform
from unittest.mock import Mock, patch

import pytest

from topyaz.system.environment import get_system_info
from topyaz.system.gpu import detect_gpu_info
from topyaz.system.memory import get_memory_info
from topyaz.system.paths import get_default_paths


class TestSystemInfo:
    """Test system information gathering."""

    def test_get_system_info(self):
        """Test basic system information retrieval."""
        info = get_system_info()
        
        # Should return a dictionary with basic system info
        assert isinstance(info, dict)
        assert "platform" in info
        assert "python_version" in info
        assert "architecture" in info
        
        # Platform should be a known value
        assert info["platform"] in ["Darwin", "Linux", "Windows"]

    def test_get_system_info_includes_hardware(self):
        """Test that system info includes hardware information."""
        info = get_system_info()
        
        # Should include hardware details
        assert "cpu_count" in info
        assert "memory_total" in info
        assert isinstance(info["cpu_count"], int)
        assert info["cpu_count"] > 0

    @patch('platform.system')
    def test_get_system_info_macos(self, mock_system):
        """Test system info on macOS."""
        mock_system.return_value = "Darwin"
        
        info = get_system_info()
        assert info["platform"] == "Darwin"

    @patch('platform.system')
    def test_get_system_info_linux(self, mock_system):
        """Test system info on Linux."""
        mock_system.return_value = "Linux"
        
        info = get_system_info()
        assert info["platform"] == "Linux"

    @patch('platform.system')
    def test_get_system_info_windows(self, mock_system):
        """Test system info on Windows."""
        mock_system.return_value = "Windows"
        
        info = get_system_info()
        assert info["platform"] == "Windows"


class TestGPUInfo:
    """Test GPU information detection."""

    def test_detect_gpu_info_basic(self):
        """Test basic GPU information detection."""
        info = detect_gpu_info()
        
        # Should return a dictionary
        assert isinstance(info, dict)
        
        # Should have basic GPU info fields
        assert "gpu_available" in info
        assert isinstance(info["gpu_available"], bool)

    @patch('subprocess.run')
    def test_detect_gpu_info_nvidia(self, mock_run):
        """Test GPU detection with NVIDIA GPU."""
        # Mock nvidia-smi output
        mock_run.return_value = Mock(
            returncode=0,
            stdout="NVIDIA-SMI 450.80.02\nTesla V100-SXM2-16GB\n",
            stderr=""
        )
        
        info = detect_gpu_info()
        
        # Should detect NVIDIA GPU
        assert info["gpu_available"] is True
        if "gpu_type" in info:
            assert "nvidia" in info["gpu_type"].lower()

    @patch('subprocess.run')
    def test_detect_gpu_info_amd(self, mock_run):
        """Test GPU detection with AMD GPU."""
        # Mock command failure (no nvidia-smi) and success for AMD
        mock_run.side_effect = [
            Mock(returncode=1, stdout="", stderr="command not found"),  # nvidia-smi fails
            Mock(returncode=0, stdout="Radeon RX 6800 XT", stderr="")   # AMD tool succeeds
        ]
        
        info = detect_gpu_info()
        
        # Should be callable without errors
        assert isinstance(info, dict)
        assert "gpu_available" in info

    @patch('subprocess.run')
    def test_detect_gpu_info_no_gpu(self, mock_run):
        """Test GPU detection when no GPU is available."""
        # Mock all GPU detection commands to fail
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="No GPU found"
        )
        
        info = detect_gpu_info()
        
        # Should handle gracefully
        assert isinstance(info, dict)
        # May or may not detect GPU depending on implementation


class TestMemoryInfo:
    """Test memory information gathering."""

    def test_get_memory_info_basic(self):
        """Test basic memory information retrieval."""
        info = get_memory_info()
        
        # Should return a dictionary with memory info
        assert isinstance(info, dict)
        assert "total" in info
        assert "available" in info
        assert "used" in info
        assert "percent" in info
        
        # Values should be reasonable
        assert info["total"] > 0
        assert info["available"] >= 0
        assert info["used"] >= 0
        assert 0 <= info["percent"] <= 100

    def test_get_memory_info_types(self):
        """Test that memory info returns correct types."""
        info = get_memory_info()
        
        # Should be numeric values
        assert isinstance(info["total"], (int, float))
        assert isinstance(info["available"], (int, float))
        assert isinstance(info["used"], (int, float))
        assert isinstance(info["percent"], (int, float))

    @patch('psutil.virtual_memory')
    def test_get_memory_info_mocked(self, mock_psutil):
        """Test memory info with mocked psutil."""
        # Mock psutil.virtual_memory return value
        mock_memory = Mock()
        mock_memory.total = 16 * 1024 * 1024 * 1024  # 16GB
        mock_memory.available = 8 * 1024 * 1024 * 1024  # 8GB
        mock_memory.used = 8 * 1024 * 1024 * 1024  # 8GB
        mock_memory.percent = 50.0
        mock_psutil.return_value = mock_memory
        
        info = get_memory_info()
        
        assert info["total"] == 16 * 1024 * 1024 * 1024
        assert info["available"] == 8 * 1024 * 1024 * 1024
        assert info["used"] == 8 * 1024 * 1024 * 1024
        assert info["percent"] == 50.0


class TestPathInfo:
    """Test path utilities."""

    def test_get_default_paths_basic(self):
        """Test basic default paths functionality."""
        paths = get_default_paths()
        
        # Should return a dictionary
        assert isinstance(paths, dict)
        
        # Should have paths for different products
        expected_products = ["gigapixel", "video_ai", "photo_ai"]
        for product in expected_products:
            if product in paths:
                assert isinstance(paths[product], (str, list))

    @patch('platform.system')
    def test_get_default_paths_macos(self, mock_system):
        """Test default paths on macOS."""
        mock_system.return_value = "Darwin"
        
        paths = get_default_paths()
        
        # Should include typical macOS paths
        assert isinstance(paths, dict)
        # Implementation-specific assertions would go here

    @patch('platform.system')
    def test_get_default_paths_linux(self, mock_system):
        """Test default paths on Linux."""
        mock_system.return_value = "Linux"
        
        paths = get_default_paths()
        
        # Should include typical Linux paths
        assert isinstance(paths, dict)
        # Implementation-specific assertions would go here

    @patch('platform.system')
    def test_get_default_paths_windows(self, mock_system):
        """Test default paths on Windows."""
        mock_system.return_value = "Windows"
        
        paths = get_default_paths()
        
        # Should include typical Windows paths
        assert isinstance(paths, dict)
        # Implementation-specific assertions would go here

    def test_get_default_paths_consistency(self):
        """Test that default paths are consistent across calls."""
        paths1 = get_default_paths()
        paths2 = get_default_paths()
        
        # Should return the same results
        assert paths1 == paths2