# `topyaz`: Technical Specification

This document provides supplementary technical details for the `topyaz` project. For general usage, installation, and configuration, please refer to the main [`README.md`](README.md) file.

## 1. Architecture & Design Philosophy

`topyaz` is built with a modular architecture to separate concerns and improve maintainability. The key design principles are:

- **Dependency Injection**: The main `TopyazCLI` class receives dependencies like executors and configuration handlers, making components interchangeable and testable.
- **Abstract Base Classes**: The `execution` and `products` modules use Abstract Base Classes (ABCs) to define common interfaces, ensuring that all implementations (e.g., `LocalExecutor`, `GigapixelAI`) adhere to a consistent contract.
- **Lazy Loading**: Product-specific classes (`GigapixelAI`, `VideoAI`, `PhotoAI`) are lazy-loaded to improve startup performance of the CLI.
- **Configuration-driven**: A centralized configuration system (`core/config.py`) allows for easy management of settings and presets.

## 2. Enhanced Photo AI CLI via Preferences Manipulation

A key feature of `topyaz` is its ability to control Topaz Photo AI beyond the standard CLI parameters. This is achieved by programmatically manipulating the application's property list (`.plist`) file before and after execution.

**Workflow:**

1.  **Backup**: A safe backup of the current preferences file (`~/Library/Preferences/com.topazlabs.Topaz Photo AI.plist`) is created.
2.  **Modify**: The user-provided parameters (e.g., `face_strength`, `denoise_model`) are written into the `.plist` file, overriding the default autopilot settings.
3.  **Execute**: The standard `tpai` command-line tool is executed. It reads the modified preferences file and applies the enhanced settings during processing.
4.  **Restore**: The original preferences file is restored from the backup, ensuring that the user's GUI settings are not permanently altered.

This process is handled by the `PhotoAIPreferences` class in `src/topyaz/products/photo_ai/preferences.py` and is wrapped in a context manager to guarantee restoration even if errors occur.

### 2.1. Available Enhanced Parameters

This mechanism exposes over 20 parameters. Below are some of the key ones:

- **Face Recovery**: `face_strength`, `face_detection`, `face_parts`.
- **Denoising**: `denoise_model`, `denoise_levels`, `denoise_strength`.
- **Sharpening**: `sharpen_model`, `sharpen_levels`, `sharpen_strength`.
- **Upscaling**: `upscaling_model`, `upscaling_factor`, `upscaling_type`, `deblur_strength`.
- **Lighting & Color**: `lighting_strength`, `raw_exposure_strength`, `adjust_color`, `temperature_value`.

For a complete list of parameters and their valid values, refer to the `PhotoAIAutopilotSettings` dataclass in `src/topyaz/products/photo_ai/preferences.py`.

## 3. Video AI FFmpeg Integration

Topaz Video AI's CLI is built on top of `ffmpeg`. `topyaz` constructs `ffmpeg` commands that leverage Video AI's custom filters.

**Core Filters:**

- `tvai_up`: Handles upscaling and enhancement. It takes parameters like `model`, `scale`, `denoise`, etc.
- `tvai_fi`: Handles frame interpolation. It takes parameters like `model` and `fps`.
- `tvai_stb`: Handles video stabilization.

**Example Command Construction:**

When a user runs a command like:
`topyaz video input.mp4 --scale 2 --model amq-13 --interpolate --fps 60`

`topyaz` builds an `ffmpeg` command that looks something like this:
```bash
/Applications/Topaz\ Video\ AI.app/Contents/MacOS/ffmpeg -i input.mp4 -vf "tvai_up=model=amq-13:scale=2,tvai_fi=model=chr-2:fps=60" -c:v hevc_videotoolbox ... output.mp4
```
The `VideoAIParams` class in `src/topyaz/products/video_ai/params.py` is responsible for validating parameters and building this filter chain.

### 3.1. Environment Variables

For `ffmpeg` to find the AI models, `topyaz` automatically sets the following environment variables during runtime:

- `TVAI_MODEL_DIR`: Path to the model definition files.
- `TVAI_MODEL_DATA_DIR`: Path to the downloaded model data.

This is handled in the `VideoAI._setup_environment` method.

## 4. CLI Tool Reference

The following sections provide a reference for the underlying CLI tools from Topaz Labs. For `topyaz` usage, refer to the `README.md`.

### 4.1. Gigapixel AI (`gpai`)

The `gpai` CLI tool (part of Gigapixel AI) offers a wide range of parameters. `topyaz` maps its `giga` command options to these parameters. To see the full, up-to-date list of options from the source, run the tool with `--help`:

```bash
/Applications/Topaz\ Gigapixel\ AI.app/Contents/Resources/bin/gpai --help
```

### 4.2. Photo AI (`tpai`)

The `tpai` CLI tool has a limited set of direct arguments. Most of its behavior is controlled by the preferences file, which `topyaz` manipulates. To see the direct CLI options, run:

```bash
/Applications/Topaz\ Photo\ AI.app/Contents/MacOS/Topaz\ Photo\ AI --cli --help
```