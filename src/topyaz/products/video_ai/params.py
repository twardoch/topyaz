import platform
from pathlib import Path

from topyaz.core.errors import ValidationError
from topyaz.core.types import CommandList

# Constants for VideoAI parameter validation
VIDEOAI_MAX_SCALE = 4
VIDEOAI_MAX_FPS = 240
VIDEOAI_MAX_QUALITY = 51  # CRF-like, but this is the max valid value in range
VIDEOAI_MAX_EFFECT_STRENGTH = 100
VIDEOAI_MIN_DETAILS_STRENGTH = -100
VIDEOAI_MAX_DEVICE_INDEX = 10


class VideoAIParams:
    def validate_params(self, **kwargs) -> None:
        model = kwargs.get("model", "amq-13")
        scale = kwargs.get("scale", 2)
        fps = kwargs.get("fps")
        codec = kwargs.get("codec", "hevc_videotoolbox")
        quality = kwargs.get("quality", 18)
        denoise = kwargs.get("denoise")
        details = kwargs.get("details")
        halo = kwargs.get("halo")
        blur = kwargs.get("blur")
        compression = kwargs.get("compression")
        device = kwargs.get("device", 0)

        valid_models = {
            "amq-13",
            "amq-12",
            "amq-11",
            "amq-10",
            "amq-9",
            "amq-8",
            "amq-7",
            "amq-6",
            "amq-5",
            "amq-4",
            "amq-3",
            "amq-2",
            "amq-1",
            "prob-4",
            "prob-3",
            "prob-2",
            "prob-1",
            "ahq-13",
            "ahq-12",
            "ahq-11",
            "ahq-10",
            "ahq-9",
            "ahq-8",
            "ahq-7",
            "ahq-6",
            "ahq-5",
            "ahq-4",
            "ahq-3",
            "ahq-2",
            "ahq-1",
            "chv-1",
            "chv-2",
            "chv-3",
            "chv-4",
            "rev-1",
            "rev-2",
            "rev-3",
            "thq-1",
            "thq-2",
            "thq-3",
            "dv-1",
            "dv-2",
            "iris-1",
            "iris-2",
            "dion-1",
            "dion-2",
            "gaia-1",
            "nyx-1",
            "nyx-2",
            "nyx-3",
            "artemis-lq-v12",
            "artemis-mq-v12",
            "artemis-hq-v12",
            "proteus-v4",
        }
        if model.lower() not in valid_models:
            msg = f"Invalid model '{model}'. Valid models: {', '.join(sorted(valid_models))}"
            raise ValidationError(msg)
        if not (1 <= scale <= VIDEOAI_MAX_SCALE):
            msg = f"Scale must be between 1 and {VIDEOAI_MAX_SCALE}, got {scale}"
            raise ValidationError(msg)
        if fps is not None and not (1 <= fps <= VIDEOAI_MAX_FPS):
            msg = f"FPS must be between 1 and {VIDEOAI_MAX_FPS}, got {fps}"
            raise ValidationError(msg)
        if not (1 <= quality <= VIDEOAI_MAX_QUALITY):
            msg = f"Quality must be between 1 and {VIDEOAI_MAX_QUALITY}, got {quality}"
            raise ValidationError(msg)
        for param_name, value in [("denoise", denoise), ("halo", halo), ("blur", blur), ("compression", compression)]:
            if value is not None and not (0 <= value <= VIDEOAI_MAX_EFFECT_STRENGTH):
                msg = f"{param_name} must be between 0 and {VIDEOAI_MAX_EFFECT_STRENGTH}, got {value}"
                raise ValidationError(msg)
        if details is not None and not (VIDEOAI_MIN_DETAILS_STRENGTH <= details <= VIDEOAI_MAX_EFFECT_STRENGTH):
            msg = (
                f"Details must be between {VIDEOAI_MIN_DETAILS_STRENGTH} "
                f"and {VIDEOAI_MAX_EFFECT_STRENGTH}, got {details}"
            )
            raise ValidationError(msg)
        if not (-1 <= device <= VIDEOAI_MAX_DEVICE_INDEX):
            msg = f"Device must be between -1 and {VIDEOAI_MAX_DEVICE_INDEX}, got {device}"
            raise ValidationError(msg)
        valid_codecs = {
            "hevc_videotoolbox",
            "hevc_nvenc",
            "hevc_amf",
            "libx265",
            "h264_videotoolbox",
            "h264_nvenc",
            "h264_amf",
            "libx264",
            "prores",
            "prores_ks",
            "copy",
        }
        if codec.lower() not in valid_codecs:
            msg = f"Invalid codec '{codec}'. Valid codecs: {', '.join(sorted(valid_codecs))}"
            raise ValidationError(msg)

    def build_command(
        self, executable: Path, input_path: Path, output_path: Path, *, verbose: bool, **kwargs
    ) -> CommandList:
        cmd = [str(executable), "-hide_banner", "-nostdin", "-y"]
        if platform.system() == "Darwin":
            cmd.extend(["-strict", "2", "-hwaccel", "auto"])
        cmd.extend(["-i", str(input_path.resolve())])

        filters = []
        tvai_filter = f"tvai_up=model={kwargs.get('model', 'amq-13')}:scale={kwargs.get('scale', 2)}"
        filter_params = []
        for p in ["denoise", "details", "halo", "blur", "compression"]:
            if kwargs.get(p) is not None:
                filter_params.append(f"{p}={kwargs.get(p)}")
        if kwargs.get("device", 0) != 0:
            filter_params.append(f"device={kwargs.get('device')}")
        if filter_params:
            tvai_filter += ":" + ":".join(filter_params)
        filters.append(tvai_filter)

        if kwargs.get("interpolate") and kwargs.get("fps"):
            fi_filter = f"tvai_fi=model=chr-2:fps={kwargs.get('fps')}"
            if kwargs.get("device", 0) != 0:
                fi_filter += f":device={kwargs.get('device')}"
            filters.append(fi_filter)

        if filters:
            cmd.extend(["-vf", ",".join(filters)])

        if platform.system() == "Darwin":
            cmd.extend(
                [
                    "-c:v",
                    "hevc_videotoolbox",
                    "-profile:v",
                    "main",
                    "-pix_fmt",
                    "yuv420p",
                    "-allow_sw",
                    "1",
                    "-tag:v",
                    "hvc1",
                    "-global_quality",
                    "18",
                ]
            )
        else:
            cmd.extend(["-c:v", "libx265", "-crf", "18", "-tag:v", "hvc1"])

        cmd.extend(["-c:a", "aac", "-b:a", "192k"])

        if verbose:
            cmd.extend(["-progress", "pipe:1"])
        else:
            cmd.extend(["-loglevel", "error"])

        cmd.append(str(output_path.resolve()))
        return cmd
