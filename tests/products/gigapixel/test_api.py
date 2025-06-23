# this_file: tests/products/gigapixel/test_api.py
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# ProcessingError and ProcessingResult removed as they were unused.
from topyaz.core.errors import ValidationError
from topyaz.core.types import ProcessingOptions
from topyaz.products.gigapixel.api import (
    GIGA_MAX_CREATIVITY_TEXTURE,
    GIGA_MAX_EFFECT_STRENGTH,
    GIGA_MAX_PARALLEL_READ,
    GIGA_MAX_QUALITY,
    GIGA_MAX_SCALE,
    GigapixelAI,
)


@pytest.fixture
def mock_executor() -> Mock:
    return Mock()


@pytest.fixture
def processing_options() -> ProcessingOptions:
    return ProcessingOptions(verbose=False, dry_run=False)


@pytest.fixture
def gigapixel_api(mock_executor: Mock, processing_options: ProcessingOptions) -> GigapixelAI:
    with patch.object(GigapixelAI, "find_executable", return_value=Path("/fake/gigapixel_cli")):
        yield GigapixelAI(mock_executor, processing_options)


class TestGigapixelAPI:
    def test_validate_params_valid(self, gigapixel_api: GigapixelAI):
        gigapixel_api.validate_params(model="std", scale=2, denoise=50)
        gigapixel_api.validate_params(model="art", scale=6, creativity=GIGA_MAX_CREATIVITY_TEXTURE)
        gigapixel_api.validate_params(format_output="png", bit_depth=16)

    def test_validate_params_invalid_model(self, gigapixel_api: GigapixelAI):
        with pytest.raises(ValidationError, match="Invalid model"):
            gigapixel_api.validate_params(model="invalid_model")

    def test_validate_params_invalid_scale(self, gigapixel_api: GigapixelAI):
        with pytest.raises(ValidationError, match=f"Scale must be between 1 and {GIGA_MAX_SCALE}"):
            gigapixel_api.validate_params(scale=GIGA_MAX_SCALE + 1)
        with pytest.raises(ValidationError, match=f"Scale must be between 1 and {GIGA_MAX_SCALE}"):
            gigapixel_api.validate_params(scale=0)

    def test_validate_params_invalid_effect_strength(self, gigapixel_api: GigapixelAI):
        for param in ["denoise", "sharpen", "compression", "detail", "face_recovery"]:
            with pytest.raises(ValidationError, match=f"{param} must be between 1 and {GIGA_MAX_EFFECT_STRENGTH}"):
                gigapixel_api.validate_params(**{param: GIGA_MAX_EFFECT_STRENGTH + 1})
            with pytest.raises(ValidationError, match=f"{param} must be between 1 and {GIGA_MAX_EFFECT_STRENGTH}"):
                gigapixel_api.validate_params(**{param: 0})

    def test_validate_params_invalid_creativity_texture(self, gigapixel_api: GigapixelAI):
        for param in ["creativity", "texture"]:
            with pytest.raises(ValidationError, match=f"{param} must be between 1 and {GIGA_MAX_CREATIVITY_TEXTURE}"):
                gigapixel_api.validate_params(**{param: GIGA_MAX_CREATIVITY_TEXTURE + 1})
            with pytest.raises(ValidationError, match=f"{param} must be between 1 and {GIGA_MAX_CREATIVITY_TEXTURE}"):
                gigapixel_api.validate_params(**{param: 0})

    def test_validate_params_invalid_quality(self, gigapixel_api: GigapixelAI):
        with pytest.raises(ValidationError, match=f"Quality must be between 1 and {GIGA_MAX_QUALITY}"):
            gigapixel_api.validate_params(quality_output=GIGA_MAX_QUALITY + 1)
        with pytest.raises(ValidationError, match=f"Quality must be between 1 and {GIGA_MAX_QUALITY}"):
            gigapixel_api.validate_params(quality_output=0)

    def test_validate_params_invalid_parallel_read(self, gigapixel_api: GigapixelAI):
        with pytest.raises(ValidationError, match=f"Parallel read must be between 1 and {GIGA_MAX_PARALLEL_READ}"):
            gigapixel_api.validate_params(parallel_read=GIGA_MAX_PARALLEL_READ + 1)
        with pytest.raises(ValidationError, match=f"Parallel read must be between 1 and {GIGA_MAX_PARALLEL_READ}"):
            gigapixel_api.validate_params(parallel_read=0)

    def test_build_command_simple(self, gigapixel_api: GigapixelAI):
        cmd = gigapixel_api.build_command(Path("input.jpg"), Path("output_dir/output.jpg"), model="std", scale=2)
        cmd_str = " ".join(cmd)
        assert str(gigapixel_api.get_executable_path()) in cmd_str
        assert "--cli" in cmd_str
        assert "-i" in cmd_str
        assert "input.jpg" in cmd_str
        assert "-o" in cmd_str
        assert "output.jpg" in cmd_str
        assert "--model std" in cmd_str
        assert "--scale 2" in cmd_str
        assert "--verbose" not in cmd_str

    def test_build_command_all_params(self, gigapixel_api: GigapixelAI):  # mock_executor and processing_options removed
        original_verbose = gigapixel_api.options.verbose
        try:
            gigapixel_api.options.verbose = True
            api_verbose = gigapixel_api

            params = {
                "model": "art",
                "scale": 4,
                "denoise": 30,
                "sharpen": 70,
                "compression": 10,
                "detail": 60,
                "creativity": 3,
                "texture": 4,
                "prompt": "test prompt",
                "face_recovery": 80,
                "face_recovery_version": 1,
                "format_output": "png",
                "bit_depth": 16,
                "parallel_read": 3,
            }
            cmd = api_verbose.build_command(Path("in.png"), Path("out/final.png"), **params)

            assert "--verbose" in cmd
            expected_args = {
                "model": "art",
                "scale": "4",
                "denoise": "30",
                "sharpen": "70",
                "compression": "10",
                "detail": "60",
                "creativity": "3",
                "texture": "4",
                "prompt": "test prompt",
                "face-recovery": "80",
                "face-recovery-version": "1",
                "format-output": "png",
                "bit-depth": "16",
                "parallel-read": "3",
            }
            cmd_str = " ".join(cmd)
            for key_cli, value_str in expected_args.items():
                assert f"--{key_cli} {value_str}" in cmd_str
            assert "--quality" not in cmd_str
        finally:
            gigapixel_api.options.verbose = original_verbose  # Ensure restoration

    def test_parse_output_simple(self, gigapixel_api: GigapixelAI):
        stdout = "Model: std\nScale: 2x\nProcessing time: 10.5s\nMemory used: 1024MB"
        stderr = ""
        parsed = gigapixel_api.parse_output(stdout, stderr)
        assert parsed.get("model_used") == "std"
        assert parsed.get("scale_used") == 2
        assert parsed.get("processing_time") == "10.5s"
        assert parsed.get("memory_used") == "1024MB"

    def test_parse_output_licensing_error(self, gigapixel_api: GigapixelAI):
        stdout = "Gigapixel CLI requires a Pro license. Please contact enterprise@topazlabs.com"
        parsed = gigapixel_api.parse_output(stdout, "")
        assert parsed.get("licensing_error") is True
        assert "Pro license" in parsed.get("user_message", "")

    def test_parse_output_false_for_license(self, gigapixel_api: GigapixelAI):
        stdout = "False"
        parsed = gigapixel_api.parse_output(stdout, "")
        assert parsed.get("licensing_error") is True

    def test_process_success(self, gigapixel_api: GigapixelAI, mock_executor: Mock, tmp_path: Path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        final_output_path = tmp_path / "final_output.jpg"
        mock_temp_output_file = Path("/tmp/fake_temp_dir_placeholder/input.jpg")  # noqa: S108

        mock_executor.execute.return_value = (0, "Success", "")

        with (
            patch.object(GigapixelAI, "_find_output_file", return_value=mock_temp_output_file) as mock_find_actual,
            patch("shutil.move") as mock_move_actual,
            patch("os.stat") as mock_os_stat_actual,
        ):

            def stat_side_effect(*args, **_kwargs):  # Changed kwargs to _kwargs
                path_arg = Path(args[0])
                stat_result_mock = Mock(spec=os.stat_result)
                if path_arg == input_file:
                    stat_result_mock.st_size = 1000
                    stat_result_mock.st_mode = 0o100644
                elif path_arg == final_output_path:
                    stat_result_mock.st_size = 2000
                    stat_result_mock.st_mode = 0o100644
                elif path_arg == tmp_path or path_arg == final_output_path.parent or path_arg == input_file.parent:
                    stat_result_mock.st_mode = 0o040755
                    stat_result_mock.st_size = 4096
                else:
                    error_msg = f"[Errno 2] Mock os.stat: No such file or directory: '{path_arg!s}'"
                    raise FileNotFoundError(error_msg)
                return stat_result_mock

            mock_os_stat_actual.side_effect = stat_side_effect

            def move_side_effect(src, dst):
                pass

            mock_move_actual.side_effect = move_side_effect

            result = gigapixel_api.process(str(input_file), output_path=str(final_output_path))

            assert result.success is True
            assert result.output_path == final_output_path
            mock_executor.execute.assert_called_once()
            mock_find_actual.assert_called_once()
            mock_move_actual.assert_called_once_with(str(mock_temp_output_file), str(final_output_path))
            assert result.file_size_before == 1000
            assert result.file_size_after == 2000

    def test_process_failure_execution(self, gigapixel_api: GigapixelAI, mock_executor: Mock, tmp_path: Path):
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"
        mock_executor.execute.return_value = (1, "", "Error details")
        result = gigapixel_api.process(str(input_file), output_path=str(output_file))
        assert result.success is False
        assert "processing failed (exit code 1): error details" in result.error_message.lower()

    def test_process_dry_run(self, gigapixel_api: GigapixelAI, mock_executor: Mock, tmp_path: Path):
        gigapixel_api.options.dry_run = True
        input_file = tmp_path / "input.jpg"
        input_file.touch()
        output_file = tmp_path / "output.jpg"
        result = gigapixel_api.process(str(input_file), output_path=str(output_file))
        assert result.success is True
        assert "DRY RUN" in result.stdout
        mock_executor.execute.assert_not_called()
