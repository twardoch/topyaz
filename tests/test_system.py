#!/usr/bin/env python3
# this_file: tests/test_system.py
"""
Tests for system-related functionality in topyaz.system.

The system layer is class-based: ``EnvironmentValidator`` gathers OS/hardware
info, ``GPUManager`` wraps platform-specific GPU detectors, ``MemoryManager``
reports memory constraints, and ``PathValidator`` handles path validation and
output-path generation. These tests target that real API.
"""

import platform
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from topyaz.core.errors import ValidationError
from topyaz.core.types import GPUInfo, GPUStatus, MemoryConstraints, Product
from topyaz.system.environment import EnvironmentValidator
from topyaz.system.gpu import GPUManager, MetalGPUDetector
from topyaz.system.memory import MemoryManager
from topyaz.system.paths import PathValidator


class TestEnvironmentValidator:
    """Test system information gathering via EnvironmentValidator."""

    def test_get_system_info_structure(self):
        """System info exposes platform, memory, disk, and CPU sections."""
        info = EnvironmentValidator().get_system_info()

        assert isinstance(info, dict)
        for section in ("platform", "memory", "disk", "cpu"):
            assert section in info
            assert isinstance(info[section], dict)

    def test_get_system_info_platform_matches(self):
        """The reported platform system matches the host."""
        info = EnvironmentValidator().get_system_info()

        assert info["platform"]["system"] == platform.system()

    def test_get_system_info_hardware_values(self):
        """CPU count and total memory are positive numbers."""
        info = EnvironmentValidator().get_system_info()

        assert info["cpu"]["count"] > 0
        assert info["memory"]["total_gb"] > 0

    def test_validate_memory_sufficient(self):
        """validate_memory passes when the required amount is trivially small."""
        validator = EnvironmentValidator()

        assert validator.validate_memory(required_gb=1, raise_on_error=False) is True

    def test_validate_all_returns_bool_map(self):
        """validate_all returns a mapping of check name to boolean result."""
        results = EnvironmentValidator().validate_all(raise_on_error=False)

        assert set(results) >= {"os_version", "memory", "disk_space", "gpu"}
        assert all(isinstance(v, bool) for v in results.values())


class TestGPUManager:
    """Test GPU detection via GPUManager."""

    def test_get_status_returns_gpu_status(self):
        """get_status returns a GPUStatus with a boolean availability flag."""
        status = GPUManager().get_status()

        assert isinstance(status, GPUStatus)
        assert isinstance(status.available, bool)
        assert isinstance(status.devices, list)

    def test_get_status_is_cached(self):
        """Repeated calls return the same cached GPUStatus instance."""
        manager = GPUManager()

        first = manager.get_status()
        second = manager.get_status()

        assert first is second

    def test_get_status_with_mocked_detector(self):
        """A mocked detector's devices are surfaced through the manager."""
        manager = GPUManager()
        fake_status = GPUStatus(
            available=True,
            devices=[GPUInfo(name="Test GPU", type="metal", memory_total_mb=8192, device_id=0)],
        )
        manager._detector = Mock()
        manager._detector.detect.return_value = fake_status
        manager.clear_cache()

        status = manager.get_status()

        assert status.available is True
        assert status.count == 1
        assert status.devices[0].name == "Test GPU"

    def test_metal_detector_off_darwin_reports_unavailable(self):
        """The Metal detector reports unavailable when not on macOS."""
        with patch("topyaz.system.gpu.platform.system", return_value="Linux"):
            status = MetalGPUDetector().detect()

        assert status.available is False
        assert status.errors


class TestMemoryManager:
    """Test memory reporting via MemoryManager."""

    def test_check_constraints_returns_constraints(self):
        """check_constraints returns a populated MemoryConstraints object."""
        constraints = MemoryManager().check_constraints()

        assert isinstance(constraints, MemoryConstraints)
        assert constraints.total_gb > 0
        assert constraints.available_gb >= 0
        assert 0 <= constraints.percent_used <= 100

    def test_check_constraints_low_memory_recommendation(self):
        """Critically low memory yields recommendations."""
        fake_memory = Mock()
        fake_memory.total = 4 * 1024**3
        fake_memory.available = 1 * 1024**3  # 1 GB available -> low
        fake_memory.percent = 95.0

        with patch("topyaz.system.memory.psutil.virtual_memory", return_value=fake_memory):
            constraints = MemoryManager().check_constraints(Product.PHOTO_AI)

        assert constraints.available_gb == pytest.approx(1.0)
        assert constraints.recommendations

    def test_optimal_batch_size_never_exceeds_file_count(self):
        """The optimal batch size is clamped to the file count."""
        batch = MemoryManager().get_optimal_batch_size(3, Product.GIGAPIXEL)

        assert 1 <= batch <= 3

    def test_optimal_batch_size_zero_files(self):
        """Zero files yields a zero batch size."""
        assert MemoryManager().get_optimal_batch_size(0) == 0


class TestPathValidator:
    """Test path validation and output-path generation."""

    def test_validate_input_path_valid(self, tmp_path: Path):
        """A real image file validates and resolves for its product."""
        image = tmp_path / "photo.jpg"
        image.touch()

        result = PathValidator().validate_input_path(image, file_type=Product.GIGAPIXEL)

        assert result == image.resolve()

    def test_validate_input_path_missing_raises(self, tmp_path: Path):
        """A missing input path raises ValidationError."""
        with pytest.raises(ValidationError, match="does not exist"):
            PathValidator().validate_input_path(tmp_path / "missing.jpg")

    def test_validate_input_path_bad_extension_raises(self, tmp_path: Path):
        """An unsupported extension for a product raises ValidationError."""
        bad = tmp_path / "notes.txt"
        bad.touch()

        with pytest.raises(ValidationError, match="Unsupported file type"):
            PathValidator().validate_input_path(bad, file_type=Product.GIGAPIXEL)

    def test_generate_output_path_adds_suffix(self, tmp_path: Path):
        """generate_output_path adds a suffix to a file's stem, keeping its extension."""
        source = tmp_path / "pic.jpg"
        source.touch()

        out = PathValidator().generate_output_path(source, suffix="_x")

        assert out.name == "pic_x.jpg"
        assert out.parent == tmp_path

    def test_find_files_filters_by_product(self, tmp_path: Path):
        """find_files returns only files matching the product's extensions."""
        (tmp_path / "a.jpg").touch()
        (tmp_path / "b.png").touch()
        (tmp_path / "c.mp4").touch()

        found = PathValidator().find_files(tmp_path, product=Product.GIGAPIXEL, recursive=False)

        names = {p.name for p in found}
        assert names == {"a.jpg", "b.png"}

    def test_format_size_human_readable(self):
        """format_size renders bytes as a human-readable string."""
        assert PathValidator().format_size(1536) == "1.5 KB"
