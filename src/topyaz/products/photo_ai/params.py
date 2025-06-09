from pathlib import Path

from loguru import logger

from topyaz.core.errors import ValidationError
from topyaz.core.types import CommandList


class PhotoAIParams:
    def validate_params(self, **kwargs) -> None:
        """
        Validate Photo AI parameters including enhanced autopilot settings.
        """
        format_param = kwargs.get("format", "preserve")
        quality = kwargs.get("quality", 95)
        compression = kwargs.get("compression", 6)
        bit_depth = kwargs.get("bit_depth", 8)
        tiff_compression = kwargs.get("tiff_compression", "lzw")

        valid_formats = {"preserve", "jpg", "jpeg", "png", "tif", "tiff", "dng"}
        if format_param.lower() not in valid_formats:
            msg = f"Invalid format '{format_param}'. Valid formats: {', '.join(sorted(valid_formats))}"
            raise ValidationError(msg)

        if not (0 <= quality <= 100):
            msg = f"Quality must be between 0 and 100, got {quality}"
            raise ValidationError(msg)

        if not (0 <= compression <= 10):
            msg = f"Compression must be between 0 and 10, got {compression}"
            raise ValidationError(msg)

        if bit_depth not in [8, 16]:
            msg = f"Bit depth must be 8 or 16, got {bit_depth}"
            raise ValidationError(msg)

        valid_tiff_compression = {"none", "lzw", "zip"}
        if tiff_compression.lower() not in valid_tiff_compression:
            msg = f"Invalid TIFF compression '{tiff_compression}'. Valid _options: {', '.join(sorted(valid_tiff_compression))}"
            raise ValidationError(msg)

        autopilot_params = {k: v for k, v in kwargs.items() if self._is_autopilot_param(k)}
        if autopilot_params:
            try:
                from topyaz.system.photo_ai_prefs import PhotoAIPreferences

                prefs_handler = PhotoAIPreferences()
                prefs_handler.validate_setting_values(**autopilot_params)
            except ImportError:
                logger.warning("Preferences system not available - skipping autopilot parameter validation")
            except Exception as e:
                msg = f"Invalid autopilot parameter: {e}"
                raise ValidationError(msg)

    def _is_autopilot_param(self, param_name: str) -> bool:
        autopilot_params = {
            "face_strength",
            "face_detection",
            "face_parts",
            "denoise_model",
            "denoise_levels",
            "denoise_strength",
            "denoise_raw_model",
            "denoise_raw_levels",
            "denoise_raw_strength",
            "sharpen_model",
            "sharpen_levels",
            "sharpen_strength",
            "upscaling_model",
            "upscaling_factor",
            "upscaling_type",
            "deblur_strength",
            "denoise_upscale_strength",
            "lighting_strength",
            "raw_exposure_strength",
            "adjust_color",
            "temperature_value",
            "opacity_value",
            "resolution_unit",
            "default_resolution",
            "overwrite_files",
            "recurse_directories",
            "append_filters",
        }
        return param_name in autopilot_params

    def build_command(
        self, executable: Path, input_path: Path, output_path: Path, verbose: bool, **kwargs
    ) -> CommandList:
        """
        Build Photo AI command line.
        """
        autopilot_preset = kwargs.get("autopilot_preset", "auto")
        format_param = kwargs.get("format", "preserve")
        quality = kwargs.get("quality", 95)
        compression = kwargs.get("compression", 6)
        bit_depth = kwargs.get("bit_depth", 8)
        tiff_compression = kwargs.get("tiff_compression", "lzw")
        show_settings = kwargs.get("show_settings", False)
        skip_processing = kwargs.get("skip_processing", False)
        override_autopilot = kwargs.get("override_autopilot", False)
        upscale = kwargs.get("upscale")
        noise = kwargs.get("noise")
        sharpen = kwargs.get("sharpen")
        lighting = kwargs.get("lighting")
        color = kwargs.get("color")

        cmd = [str(executable), "--cli", str(input_path.resolve()), "-o", str(output_path.resolve())]

        if autopilot_preset and autopilot_preset != "auto":
            cmd.extend(["--autopilot", autopilot_preset])

        if format_param.lower() != "preserve":
            cmd.extend(["-f", format_param])

        if format_param.lower() in ["jpg", "jpeg"]:
            cmd.extend(["-q", str(quality)])
        elif format_param.lower() == "png":
            cmd.extend(["-c", str(compression)])
        elif format_param.lower() in ["tif", "tiff"]:
            cmd.extend(["-d", str(bit_depth), "-tc", tiff_compression])

        if show_settings:
            cmd.append("--showSettings")
        if skip_processing:
            cmd.append("--skipProcessing")

        if override_autopilot or any([upscale, noise, sharpen, lighting, color]):
            cmd.append("--override")
            self._add_boolean_parameter(cmd, "upscale", upscale)
            self._add_boolean_parameter(cmd, "noise", noise)
            self._add_boolean_parameter(cmd, "sharpen", sharpen)
            self._add_boolean_parameter(cmd, "lighting", lighting)
            self._add_boolean_parameter(cmd, "color", color)

        if input_path.is_dir():
            cmd.append("--recursive")
        if verbose:
            cmd.append("--verbose")

        return cmd

    def _add_boolean_parameter(self, cmd: CommandList, param_name: str, value: bool | None) -> None:
        if value is True:
            cmd.append(f"--{param_name}")
        elif value is False:
            cmd.append(f"--{param_name}")
            cmd.append("enabled=false")
