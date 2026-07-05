#!/usr/bin/env python3
# this_file: tests/test_integration.py
"""
Integration tests for the topyaz package.

The public CLI methods (``giga``, ``video``, ``photo``) return a ``bool`` -
``True`` on success, ``False`` when processing fails - and swallow exceptions
so the command-line surface never crashes. Topaz executables are stubbed by the
autouse fixture in ``conftest.py``, so dry-run workflows succeed without any
installed binaries while real execution of the fake binary fails gracefully.
"""

import tempfile
import threading
from pathlib import Path

import pytest

from topyaz.cli import TopyazCLI
from topyaz.core.config import Config


class TestIntegration:
    """Integration tests for the complete topyaz system."""

    @pytest.mark.integration
    def test_full_workflow_gigapixel(self):
        """A dry-run Gigapixel workflow reports success."""
        cli = TopyazCLI(verbose=True, dry_run=True)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            input_path = temp_file.name

        assert cli.giga(input_path, output="output.jpg", model="std", scale=2, denoise=50) is True

    @pytest.mark.integration
    def test_full_workflow_video_ai(self):
        """A dry-run Video AI workflow reports success."""
        cli = TopyazCLI(verbose=True, dry_run=True)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            input_path = temp_file.name

        assert cli.video(input_path, output="output.mp4", model="amq-13", scale=2, quality=18) is True

    @pytest.mark.integration
    def test_full_workflow_photo_ai(self):
        """A dry-run Photo AI workflow reports success."""
        cli = TopyazCLI(verbose=True, dry_run=True)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            input_path = temp_file.name

        assert cli.photo(input_path, output="output.jpg", quality=95) is True

    @pytest.mark.integration
    def test_config_system_integration(self):
        """Configuration loads sensible defaults and products are reachable."""
        config = Config()

        assert config.get("defaults.log_level") is not None
        assert config.get("defaults.timeout") is not None

        cli = TopyazCLI(verbose=True, dry_run=True)
        assert cli._gigapixel is not None

    @pytest.mark.integration
    def test_error_handling_integration(self):
        """A non-existent input file makes the CLI return False, not raise."""
        cli = TopyazCLI(verbose=True, dry_run=False)

        assert cli.giga("/nonexistent/file.jpg", output="output.jpg", model="std", scale=2) is False

    @pytest.mark.integration
    def test_multiple_product_usage(self):
        """Multiple products can be driven in sequence in dry-run mode."""
        cli = TopyazCLI(verbose=True, dry_run=True)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as img_file:
            img_path = img_file.name
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as vid_file:
            vid_path = vid_file.name

        assert cli.giga(img_path, output="gp_output.jpg", model="std", scale=2) is True
        assert cli.video(vid_path, output="video_output.mp4", model="amq-13", scale=2) is True
        assert cli.photo(img_path, output="photo_output.jpg", quality=95) is True

    @pytest.mark.integration
    def test_system_info_integration(self):
        """The system-info method returns a dictionary without raising."""
        cli = TopyazCLI()

        sysinfo = cli._sysinfo()
        assert isinstance(sysinfo, dict)

    @pytest.mark.integration
    def test_parameter_validation_integration(self):
        """Invalid parameters are caught internally and reported as failure."""
        cli = TopyazCLI(verbose=True, dry_run=True)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            input_path = temp_file.name

        assert cli.giga(input_path, output="output.jpg", model="invalid_model", scale=2) is False
        assert cli.video(input_path, output="output.mp4", model="invalid_model", scale=2) is False
        assert cli.photo(input_path, output="output.jpg", format="invalid_format", quality=95) is False

    @pytest.mark.integration
    def test_verbose_logging_integration(self):
        """Verbose dry-run processing still reports success."""
        cli = TopyazCLI(verbose=True, dry_run=True)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            input_path = temp_file.name

        assert cli.giga(input_path, output="output.jpg", model="std", scale=2) is True

    @pytest.mark.integration
    def test_timeout_integration(self):
        """A short timeout is handled gracefully and returns a boolean."""
        cli = TopyazCLI(verbose=True, dry_run=False, timeout=1)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            input_path = temp_file.name

        result = cli.giga(input_path, output="output.jpg", model="std", scale=2)
        assert isinstance(result, bool)

    @pytest.mark.integration
    def test_parallel_jobs_integration(self):
        """The parallel_jobs setting does not affect dry-run success."""
        cli = TopyazCLI(verbose=True, dry_run=True, parallel_jobs=2)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            input_path = temp_file.name

        assert cli.giga(input_path, output="output.jpg", model="std", scale=2) is True

    @pytest.mark.integration
    def test_file_format_validation_integration(self):
        """Supported image and video formats route to the right product."""
        cli = TopyazCLI(verbose=True, dry_run=True)

        image_formats = ["jpg", "png", "tiff"]
        video_formats = ["mp4", "mov"]

        for fmt in image_formats:
            with tempfile.NamedTemporaryFile(suffix=f".{fmt}", delete=False) as temp_file:
                assert cli.giga(temp_file.name, output=f"output.{fmt}", model="std", scale=2) is True

        for fmt in video_formats:
            with tempfile.NamedTemporaryFile(suffix=f".{fmt}", delete=False) as temp_file:
                assert cli.video(temp_file.name, output=f"output.{fmt}", model="amq-13", scale=2) is True

    @pytest.mark.integration
    def test_output_path_handling_integration(self):
        """Both absolute and relative output paths succeed in dry-run mode."""
        cli = TopyazCLI(verbose=True, dry_run=True)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            input_path = temp_file.name

        with tempfile.TemporaryDirectory() as temp_dir:
            full_output = Path(temp_dir) / "output.jpg"
            assert cli.giga(input_path, output=str(full_output), model="std", scale=2) is True
            assert cli.giga(input_path, output="relative_output.jpg", model="std", scale=2) is True

    @pytest.mark.integration
    def test_backward_compatibility_integration(self):
        """The backward-compatibility command surface is present and callable."""
        cli = TopyazCLI()

        for name in ("giga", "video", "photo", "_sysinfo"):
            assert hasattr(cli, name)
            assert callable(getattr(cli, name))

    @pytest.mark.integration
    def test_memory_efficiency_integration(self):
        """Multiple independent CLI instances remain isolated."""
        instances = [TopyazCLI(verbose=False, dry_run=True) for _ in range(10)]

        for cli in instances:
            assert cli._options.dry_run is True
            assert cli._gigapixel is not None

    @pytest.mark.integration
    def test_error_recovery_integration(self):
        """Error scenarios are recovered as a False result without crashing."""
        cli = TopyazCLI(verbose=True, dry_run=False)

        for input_path in ("/nonexistent/file.jpg", ""):
            result = cli.giga(input_path, output="output.jpg", model="std", scale=2)
            assert result is False

    @pytest.mark.integration
    def test_concurrent_access_integration(self):
        """Concurrent CLI usage across threads all succeed in dry-run mode."""
        results: list[tuple[int, bool]] = []

        def process_file(index: int) -> None:
            cli = TopyazCLI(verbose=False, dry_run=True)
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                result = cli.giga(temp_file.name, output=f"output_{index}.jpg", model="std", scale=2)
                results.append((index, result))

        threads = [threading.Thread(target=process_file, args=(i,)) for i in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(results) == 5
        assert all(result for _index, result in results)
