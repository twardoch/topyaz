# topyaz: Unified CLI Wrapper for Topaz Labs Products

This document provides technical documentation for `topyaz`, a Python-based command-line interface (CLI) that provides a unified wrapper for Topaz Labs' AI-powered media enhancement products: Video AI, Gigapixel AI, and Photo AI. It is designed for professionals and developers who require efficient batch processing, automation, and integration into larger workflows.

The tool addresses the limitations of using separate graphical user interfaces for each product by offering a single, scriptable interface. It is particularly beneficial for processing large collections of media files and ensuring reproducible results through configuration.

## Table of Contents

- [Core Features](#core-features)
- [Requirements](#requirements)
  - [System Requirements](#system-requirements)
  - [Topaz Products & Licenses](#topaz-products--licenses)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Video AI](#video-ai)
  - [Gigapixel AI](#gigapixel-ai)
  - [Photo AI](#photo-ai)
  - [System Commands](#system-commands)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Support](#support)

## Core Features

- **Unified Interface**: Control Video AI, Gigapixel AI, and Photo AI from a single, consistent CLI.
- **Batch Processing**: Process entire directories of files with support for recursive searching.
- **Advanced Configuration**: Utilize YAML files for presets and consistent workflow settings.
- **Hardware Optimization**: Automatic detection and utilization of available hardware resources, including GPUs (Metal, CUDA, ROCm).
- **Failsafe Design**: Robust error handling, progress monitoring, and clear feedback.
- **Enhanced Photo AI Control**: Programmatically manipulates application preferences to expose over 20 additional autopilot settings not available in the standard Photo AI CLI.

## Requirements

### System Requirements

- **Operating System**: macOS 11.0 (Big Sur) or higher.
  - macOS 13 (Ventura) or newer is recommended for advanced Video AI models.
  - macOS 14 (Sonoma) or newer is recommended for Gigapixel AI generative models.
- **Python**: Version 3.10 or higher.
- **Memory (RAM)**: A minimum of 16GB. 32GB or more is highly recommended for 4K video processing.
- **Storage**: At least 80GB of free disk space is required for Video AI models.
- **GPU**: A dedicated GPU with at least 2GB of VRAM is recommended for hardware acceleration.

### Topaz Products & Licenses

- **Topaz Video AI**: A valid license is required.
- **Topaz Photo AI**: A valid license is required.
- **Topaz Gigapixel AI**: A **Pro license** is mandatory for CLI access.

Ensure that the Topaz Labs applications are installed in their default locations (e.g., `/Applications/`).

## Installation

Install `topyaz` using a modern Python package manager like `uv` or `pip`.

```bash
uv pip install topyaz
```

## Configuration

`topyaz` can be configured via a YAML file located at `~/.topyaz/config.yaml`. This allows you to set default parameters for different products and workflows, streamlining command-line usage.

**Example `config.yaml`:**

```yaml
defaults:
  output_dir: '~/processed_media'
  preserve_structure: true
  backup_originals: false
  log_level: 'INFO'
  timeout: 3600

video:
  default_model: 'amq-13'
  default_codec: 'hevc_videotoolbox'
  default_quality: 18
  device: 0

gigapixel:
  default_model: 'std'
  default_format: 'preserve'
  parallel_read: 4
  quality_output: 95

photo:
  default_format: 'jpg'
  default_quality: 95
  autopilot_preset: 'default'
  bit_depth: 16
```

Configuration values can also be overridden by environment variables prefixed with `TOPYAZ_`. Use a double underscore (`__`) to denote nested keys (e.g., `TOPYAZ_VIDEO__DEFAULT_MODEL=prob-3`).

## Usage

The general command structure is `topyaz [product] [input_path] [options]`.

For a complete and up-to-date list of all available parameters for any command, run `topyaz [product] --help`.

### Video AI

The `video` command interfaces with Topaz Video AI's `ffmpeg`-based engine.

**Basic Example:**

```bash
# Upscale a video to 2x its original resolution
topyaz video input.mp4 --scale 2 --model amq-13
```

**Parameters:**

- `input_path` (`str`, required): Path to the input video file or directory.
- `--output OUTPUT`, `-o OUTPUT` (`str`, optional): Path for the output file or directory.
- `--model MODEL`, `-m MODEL` (`str`, default: `amq-13`): AI model to use.
- `--scale SCALE` (`int`, default: `2`): Upscale factor (1-4).
- `--fps FPS`, `-f FPS` (`int`, optional): Target frame rate for interpolation.
- `--codec CODEC` (`str`, default: `hevc_videotoolbox`): Video codec (e.g., `hevc_videotoolbox`, `hevc_nvenc`).
- `--quality QUALITY`, `-q QUALITY` (`int`, default: `18`): Video quality/CRF value (1-51). Lower is better.
- `--denoise DENOISE` (`int`, optional): Denoise strength (0-100).
- `--details DETAILS` (`int`, optional): Detail enhancement (-100 to 100).
- `--halo HALO`, `-h HALO` (`int`, optional): Halo reduction (0-100).
- `--blur BLUR`, `-b BLUR` (`int`, optional): Blur reduction (0-100).
- `--compression COMPRESSION` (`int`, optional): Compression artifact reduction (0-100).
- `--stabilize` (`bool`, default: `False`): Enable stabilization.
- `--interpolate`, `-i` (`bool`, default: `False`): Enable frame interpolation.
- `--custom_filters FILTERS` (`str`, optional): Custom FFmpeg filter string.
- `--device DEVICE` (`int`, default: `0`): GPU device index (-1 for CPU).

### Gigapixel AI

The `giga` command interfaces with Topaz Gigapixel AI. A **Pro license** is required.

**Basic Example:**

```bash
# Upscale an image to 4x its resolution using the standard model.
topyaz giga input.jpg --scale 4 --model std
```

**Parameters:**

- `input_path` (`str`, required): Path to the input image or directory.
- `--output OUTPUT`, `-o OUTPUT` (`str`, optional): Path for the output file or directory.
- `--model MODEL`, `-m MODEL` (`str`, default: `std`): AI model to use (`std`, `hf`, `art`, `lowres`, `recovery`, `redefine`).
- `--scale SCALE` (`int`, default: `2`): Upscale factor (1-6).
- `--denoise DENOISE` (`int`, optional): Denoise strength (1-100).
- `--sharpen SHARPEN` (`int`, optional): Sharpening strength (1-100).
- `--compression COMPRESSION` (`int`, optional): Compression reduction (1-100).
- `--detail DETAIL` (`int`, optional): Detail enhancement (1-100).
- `--face_recovery STRENGTH` (`int`, optional): Face recovery strength (1-100).
- `--face_recovery_version VERSION` (`int`, default: `2`): Face recovery model version (1 or 2).
- `--format_output FORMAT` (`str`, default: `preserve`): Output format (`preserve`, `jpg`, `png`, `tiff`).
- `--quality_output QUALITY`, `-q QUALITY` (`int`, default: `95`): JPEG quality (1-100).
- `--bit_depth BIT_DEPTH`, `-b BIT_DEPTH` (`int`, default: `0`): Output bit depth (0=preserve, 8, 16).
- `--parallel_read COUNT` (`int`, default: `1`): Number of files to read in parallel (1-10).

**Generative Model Parameters (`--model redefine`):**

- `--creativity LEVEL` (`int`, optional): Creativity level (1-6).
- `--texture LEVEL`, `-t LEVEL` (`int`, optional): Texture level (1-6).
- `--prompt PROMPT` (`str`, optional): Text prompt for image generation.

**Generative AI Example:**

```bash
# Use the 'redefine' model with a text prompt.
topyaz giga portrait.png --model redefine --scale 2 \
    --creativity 4 --texture 3 \
    --prompt "ultra-realistic portrait, detailed skin texture, 8k"
```

### Photo AI

The `photo` command provides two modes of operation:
1.  A standard CLI interface with basic parameters.
2.  An enhanced mode that temporarily modifies the Photo AI preferences file to control over 20 additional autopilot settings, providing fine-grained control over the enhancement process.

**Basic Example (Autopilot):**

```bash
# Process a directory of RAW files, letting Autopilot decide settings,
# and output as high-quality JPEGs.
topyaz photo ./raw_images/ --format jpg --quality 95
```

**Enhanced Control Example:** The following command uses parameters that are not part of the standard `tpai` CLI. `topyaz` applies them by modifying the preferences before execution and restoring them afterward.

```bash
# Process a photo with specific autopilot settings.
topyaz photo portrait.cr3 --output enhanced_portrait.dng \
    --face_strength 80 \
    --denoise_model "Low Light Beta" \
    --sharpen_model "Lens Blur v2" \
    --upscaling_model "High Fidelity V2" \
    --upscaling_factor 2.0
```

**Parameters:**

The `photo` command accepts numerous parameters. Standard parameters are passed directly to the `tpai` CLI. Enhanced parameters are applied by modifying Photo AI's preferences file before execution.

- `input_path` (`str`, required): Path to the input image or directory.
- `--output OUTPUT` (`str`, optional): Path for the output file or directory.

**Standard CLI Parameters:**
- `--preset PRESET`, `-p PRESET`: (`str`, default: `auto`) - Autopilot preset to use.
- `--format FORMAT`: (`str`, default: `preserve`) - Output format (`preserve`, `jpg`, `png`, `tiff`, `dng`).
- `--quality QUALITY`, `-q QUALITY`: (`int`, default: `95`) - JPEG quality (0-100).
- `--compression COMPRESSION`: (`int`, default: `6`) - PNG compression (0-10).
- `--bit_depth BIT_DEPTH`, `-b BIT_DEPTH`: (`int`, default: `8`) - TIFF bit depth (8 or 16).
- `--tiff_compression COMPRESSION`: (`str`, default: `lzw`) - TIFF compression (`none`, `lzw`, `zip`).
- `--override_autopilot`: (`bool`, default: `False`) - Override Autopilot with manual settings.
- `--upscale [enabled=false]`: (`bool`, optional) - Enable/disable upscaling.
- `--noise [enabled=false]`, `-n`: (`bool`, optional) - Enable/disable noise reduction.
- `--sharpen [enabled=false]`: (`bool`, optional) - Enable/disable sharpening.
- `--lighting [enabled=false]`: (`bool`, optional) - Enable/disable lighting enhancement.
- `--color [enabled=false]`: (`bool`, optional) - Enable/disable color enhancement.

**Enhanced Parameters (via Preferences):**

These parameters provide fine-grained control over the Autopilot settings.

*Face Recovery:*
- `--face_strength STRENGTH`: (`int`, 0-100) - Strength of Face Recovery.
- `--face_detection MODE`: (`str`, `auto`|`subject`|`all`) - Face detection mode.
- `--face_parts PARTS`: (`list[str]`) - Parts to enhance (e.g., `hair,necks`).

*Denoising:*
- `--denoise_model MODEL`: (`str`) - Denoise model (e.g., `Low Light Beta`).
- `--denoise_strength STRENGTH`: (`int`, 0-10) - Denoising strength.
- `--denoise_raw_model MODEL`: (`str`) - Denoise model for RAW files.
- `--denoise_raw_strength STRENGTH`: (`int`, 0-10) - Denoise strength for RAW files.

*Sharpening:*
- `--sharpen_model MODEL`: (`str`) - Sharpen model (e.g., `Lens Blur v2`).
- `--sharpen_strength STRENGTH`: (`int`, 0-10) - Sharpening strength.

*Upscaling:*
- `--upscaling_model MODEL`: (`str`) - Upscaling model (e.g., `High Fidelity V2`).
- `--upscaling_factor FACTOR`: (`float`, 1.0-6.0) - Upscaling factor.
- `--deblur_strength STRENGTH`: (`int`, 0-10) - Deblur strength.

*Color & Tone:*
- `--lighting_strength STRENGTH`: (`int`, 0-100) - Lighting adjustment strength.
- `--raw_exposure_strength STRENGTH`: (`int`, 0-100) - Exposure adjustment for RAW files.
- `--adjust_color`: (`bool`, optional) - Enable color adjustment.
- `--temperature_value VALUE`: (`int`, 0-100) - White balance temperature.

### System Commands

`topyaz` provides commands for system inspection.

- **`topyaz info`**: Displays a comprehensive report on your system environment, including OS, hardware, detected GPUs, and located Topaz product executables.
- **`topyaz version`**: Shows the version of `topyaz` and the detected versions of the installed Topaz applications.

## Architecture

`topyaz` is built on a modular architecture to ensure maintainability and extensibility.

- **`src/topyaz/core`**: Contains fundamental components like configuration management (`config.py`), custom error types (`errors.py`), and data type definitions (`types.py`).
- **`src/topyaz/system`**: Handles system-level interactions, including environment validation (`environment.py`), GPU detection (`gpu.py`), memory management (`memory.py`), and path handling (`paths.py`).
- **`src/topyaz/execution`**: Provides the logic for running commands. It includes a base abstraction (`base.py`) and a concrete implementation for local command execution (`local.py`).
- **`src/topyaz/products`**: Contains the specific implementations for each Topaz product. A base class (`base.py`) defines the common interface, and each product (`gigapixel/`, `photo_ai/`, `video_ai/`) has its own module for parameter validation, command construction, and output parsing.
- **`src/topyaz/cli.py`**: The main entry point that integrates all components and exposes the command-line interface using the `fire` library.

This design promotes separation of concerns, simplifies testing, and makes it easier to add support for new products or features in the future.

## Troubleshooting

- **"Executable not found"**: Ensure the Topaz Labs applications are installed in the default `/Applications` directory. `topyaz` automatically searches standard installation paths. Use `topyaz info` to check which executables were found.
- **Video AI "No such filter: tvai_up"**: This error typically means the environment variables required by Video AI are not set correctly. `topyaz` attempts to set these automatically, but a manual launch of the Video AI GUI once can resolve this by letting it create necessary files.
- **Gigapixel AI "Pro license required"**: The Gigapixel AI CLI requires a Pro license. There is no workaround for this; you must have an active Pro license to use the `topyaz giga` command.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Support

This is a community-driven tool and is not officially affiliated with or supported by Topaz Labs. For issues, questions, or feature requests, please use the [GitHub Issues](https://github.com/twardoch/topyaz/issues) page for this project.
