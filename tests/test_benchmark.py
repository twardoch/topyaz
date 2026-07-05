#!/usr/bin/env python3
# this_file: tests/test_benchmark.py
"""
Benchmark tests for topyaz performance measurement.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from topyaz.cli import TopyazCLI
from topyaz.core.config import Config
from topyaz.core.types import ProcessingOptions
from topyaz.execution.base import ExecutorContext
from topyaz.execution.local import LocalExecutor
from topyaz.products.gigapixel import GigapixelAI
from topyaz.products.photo_ai import PhotoAI
from topyaz.products.video_ai import VideoAI
from topyaz.system.environment import EnvironmentValidator
from topyaz.system.gpu import GPUManager
from topyaz.system.memory import MemoryManager
from topyaz.utils.validation import validate_output_file


class TestBenchmarks:
    """Benchmark tests for performance measurement."""

    @pytest.mark.benchmark
    def test_cli_initialization_benchmark(self, benchmark):
        """Benchmark CLI initialization performance."""

        def init_cli():
            return TopyazCLI(verbose=False, dry_run=True)

        result = benchmark(init_cli)
        assert result is not None

    @pytest.mark.benchmark
    def test_product_lazy_loading_benchmark(self, benchmark):
        """Benchmark product lazy loading performance."""

        def load_products():
            cli = TopyazCLI(verbose=False, dry_run=True)
            # Force lazy loading
            return cli._gigapixel, cli._video_ai, cli._photo_ai

        result = benchmark(load_products)
        assert len(result) == 3

    @pytest.mark.benchmark
    def test_config_loading_benchmark(self, benchmark):
        """Benchmark configuration loading performance."""

        def load_config():
            return Config()

        result = benchmark(load_config)
        assert result is not None

    @pytest.mark.benchmark
    def test_parameter_validation_benchmark(self, benchmark):
        """Benchmark parameter validation performance."""

        def validate_params():
            executor = Mock()
            options = ProcessingOptions()

            with patch(
                "topyaz.products.gigapixel.api.GigapixelAI.find_executable", return_value=Path("/fake/gigapixel")
            ):
                gp = GigapixelAI(executor, options)
                gp.validate_params(model="std", scale=2, denoise=50)

            with patch("topyaz.products.video_ai.api.VideoAI.find_executable", return_value=Path("/fake/ffmpeg")):
                video = VideoAI(executor, options)
                video.validate_params(model="amq-13", scale=2, quality=18)

            with patch("topyaz.products.photo_ai.api.PhotoAI.find_executable", return_value=Path("/fake/tpai")):
                photo = PhotoAI(executor, options)
                photo.validate_params(format="jpg", quality=95)

            return True

        result = benchmark(validate_params)
        assert result is True

    @pytest.mark.benchmark
    def test_command_building_benchmark(self, benchmark):
        """Benchmark command building performance."""

        def build_commands():
            executor = Mock()
            options = ProcessingOptions()

            with patch(
                "topyaz.products.gigapixel.api.GigapixelAI.find_executable", return_value=Path("/fake/gigapixel")
            ):
                gp = GigapixelAI(executor, options)
                gp_cmd = gp.build_command(Path("input.jpg"), Path("output.jpg"), model="std", scale=2, denoise=50)

            with patch("topyaz.products.video_ai.api.VideoAI.find_executable", return_value=Path("/fake/ffmpeg")):
                video = VideoAI(executor, options)
                video_cmd = video.build_command(
                    Path("input.mp4"), Path("output.mp4"), model="amq-13", scale=2, quality=18
                )

            with patch("topyaz.products.photo_ai.api.PhotoAI.find_executable", return_value=Path("/fake/tpai")):
                photo = PhotoAI(executor, options)
                photo_cmd = photo.build_command(Path("input.jpg"), Path("output.jpg"), format="jpg", quality=95)

            return gp_cmd, video_cmd, photo_cmd

        result = benchmark(build_commands)
        assert len(result) == 3

    @pytest.mark.benchmark
    def test_output_parsing_benchmark(self, benchmark):
        """Benchmark output parsing performance."""

        def parse_outputs():
            executor = Mock()
            options = ProcessingOptions()

            # Sample outputs for parsing
            gp_stdout = "Model: std\nScale: 2x\nProcessing time: 10.5s\nMemory used: 1024MB"
            video_stdout = "frame= 1000 fps= 30 q=18.0 size= 1024kB time=00:00:33.33 bitrate= 251.2kbits/s speed=1.0x"
            photo_stdout = "Processing completed successfully\nOutput saved to: output.jpg\nFile size: 1024KB"

            with patch(
                "topyaz.products.gigapixel.api.GigapixelAI.find_executable", return_value=Path("/fake/gigapixel")
            ):
                gp = GigapixelAI(executor, options)
                gp_parsed = gp.parse_output(gp_stdout, "")

            with patch("topyaz.products.video_ai.api.VideoAI.find_executable", return_value=Path("/fake/ffmpeg")):
                video = VideoAI(executor, options)
                video_parsed = video.parse_output(video_stdout, "")

            with patch("topyaz.products.photo_ai.api.PhotoAI.find_executable", return_value=Path("/fake/tpai")):
                photo = PhotoAI(executor, options)
                photo_parsed = photo.parse_output(photo_stdout, "")

            return gp_parsed, video_parsed, photo_parsed

        result = benchmark(parse_outputs)
        assert len(result) == 3

    @pytest.mark.benchmark
    def test_dry_run_processing_benchmark(self, benchmark):
        """Benchmark dry run processing performance."""

        def dry_run_process():
            cli = TopyazCLI(verbose=False, dry_run=True)

            # Each product validates the input extension, so the video product
            # needs a real video file rather than the image used by the others.
            with (
                tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as image_file,
                tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as video_file,
            ):
                gp_result = cli._gigapixel.process(image_file.name, output="gp_output.jpg", model="std", scale=2)
                video_result = cli._video_ai.process(
                    video_file.name, output="video_output.mp4", model="amq-13", scale=2
                )
                photo_result = cli._photo_ai.process(
                    image_file.name, output="photo_output.jpg", format="jpg", quality=95
                )

            return gp_result, video_result, photo_result

        result = benchmark(dry_run_process)
        assert len(result) == 3
        assert all(r.success for r in result)

    @pytest.mark.benchmark
    def test_system_info_benchmark(self, benchmark):
        """Benchmark system information gathering performance."""

        def gather_system_info():
            return (
                EnvironmentValidator().get_system_info(),
                GPUManager().get_status(),
                MemoryManager().check_constraints(),
            )

        result = benchmark(gather_system_info)
        assert len(result) == 3

    @pytest.mark.benchmark
    def test_validation_utils_benchmark(self, benchmark):
        """Benchmark output-file validation utilities performance."""

        def validate_files():
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                input_path = temp_path / "input.jpg"
                input_path.write_bytes(b"input-bytes")

                results = []
                for name in ("out1.jpg", "out2.png", "out3.mp4"):
                    output_path = temp_path / name
                    output_path.write_bytes(b"output-bytes")
                    results.append(validate_output_file(input_path, output_path))

                # Also validate a missing output to exercise the error path.
                results.append(validate_output_file(input_path, temp_path / "missing.jpg"))

            return all(isinstance(r, dict) for r in results)

        result = benchmark(validate_files)
        assert result is True

    @pytest.mark.benchmark
    def test_executor_initialization_benchmark(self, benchmark):
        """Benchmark executor initialization performance."""

        def init_executor():
            context = ExecutorContext(timeout=300, dry_run=False)
            return LocalExecutor(context)

        result = benchmark(init_executor)
        assert result is not None

    @pytest.mark.benchmark
    def test_multiple_cli_instances_benchmark(self, benchmark):
        """Benchmark multiple CLI instance creation."""

        def create_multiple_clis():
            instances = []
            for i in range(10):
                cli = TopyazCLI(verbose=bool(i % 2), dry_run=True)
                instances.append(cli)
            return instances

        result = benchmark(create_multiple_clis)
        assert len(result) == 10

    @pytest.mark.benchmark
    def test_parameter_validation_stress_benchmark(self, benchmark):
        """Benchmark parameter validation under stress."""

        def stress_validation():
            executor = Mock()
            options = ProcessingOptions()

            with patch(
                "topyaz.products.gigapixel.api.GigapixelAI.find_executable", return_value=Path("/fake/gigapixel")
            ):
                gp = GigapixelAI(executor, options)

                # Test many parameter combinations
                models = ["std", "art", "low"]
                scales = [1, 2, 3, 4, 5, 6]
                denoises = [1, 25, 50, 75, 100]

                for model in models:
                    for scale in scales:
                        for denoise in denoises:
                            gp.validate_params(model=model, scale=scale, denoise=denoise)

            return True

        result = benchmark(stress_validation)
        assert result is True
