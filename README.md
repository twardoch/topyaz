# topyaz: Unified CLI for Topaz Labs AI Products

**topyaz** is a powerful Python-based command-line interface (CLI) wrapper that brings Topaz Labs' acclaimed AI-powered image and video enhancement tools—Gigapixel AI, Photo AI, and Video AI—into a single, streamlined interface. It's designed for professionals, content creators, and developers who need to incorporate Topaz AI capabilities into batch processing workflows, automated scripts, or remote processing setups.

**Current Status:** This project is under active development. While core functionality for local processing is implemented, some advanced features like remote execution are planned for future releases.

## Table of Contents

*   [Why topyaz?](#why-topyaz)
*   [Who is it for?](#who-is-it-for)
*   [Key Features](#key-features)
*   [Requirements](#requirements)
*   [Installation](#installation)
*   [Usage](#usage)
    *   [Command-Line Interface (CLI)](#command-line-interface-cli)
        *   [Global Options](#global-options)
        *   [Gigapixel AI (`giga`)](#gigapixel-ai-giga)
        *   [Photo AI (`photo`)](#photo-ai-photo)
        *   [Video AI (`video`)](#video-ai-video)
        *   [Utility Commands (`info`, `version`)](#utility-commands-info-version)
    *   [Programmatic Usage (Python API)](#programmatic-usage-python-api)
*   [Technical Deep Dive](#technical-deep-dive)
    *   [Project Structure](#project-structure)
    *   [Core Components](#core-components)
    *   [Configuration](#configuration)
    *   [Execution Flow](#execution-flow)
*   [Coding and Contributing](#coding-and-contributing)
    *   [Development Philosophy](#development-philosophy)
    *   [Python Coding Standards](#python-coding-standards)
    *   [Commit and Workflow Practices](#commit-and-workflow-practices)
*   [License](#license)

## Why topyaz?

Topaz Labs' AI products offer exceptional quality but are primarily GUI-driven. `topyaz` unlocks their power for automated and high-volume tasks by:

*   **Unifying Access:** Control Gigapixel AI, Photo AI, and Video AI from a single, consistent CLI.
*   **Enabling Automation:** Easily integrate Topaz AI processing into scripts and larger workflows.
*   **Facilitating Batch Processing:** Process large numbers of files efficiently.
*   **Preparing for Remote Execution:** Designed with future support for processing on powerful remote servers (planned feature).
*   **Potentially Faster Operations:** For batch tasks, CLI interaction can be significantly faster than manual GUI operations.

## Who is it for?

*   **Photo and Video Professionals:** Streamline editing and enhancement pipelines.
*   **Content Creators:** Batch-enhance images and videos for various platforms.
*   **Developers & System Integrators:** Add Topaz AI capabilities to custom applications or automated systems.
*   **Power Users:** Gain finer control and scripting capabilities over Topaz AI tools.

## Key Features

*   **Unified Interface:** Single CLI for Gigapixel AI, Photo AI, and Video AI.
*   **Comprehensive Parameter Control:** Access a wide range of processing parameters for each Topaz product.
*   **Local Execution:** Leverages your existing Topaz Labs application installations.
*   **Configuration Management:** Customize default settings and executable paths via a YAML configuration file or environment variables.
*   **Cross-Platform (Primarily macOS):** While Topaz products are Mac-focused, `topyaz` aims for broader compatibility where possible. Current executable path configurations are primarily for macOS and Windows.
*   **Informative Output:** Verbose logging and system information commands.

## Requirements

*   **Operating System:**
    *   macOS 11+ (Recommended, as Topaz products are primarily optimized for Mac)
    *   Windows (Supported, executable paths are configured)
    *   Linux (Potentially, with manual path configuration)
*   **Topaz Labs Applications:** You **must** have the respective Topaz Labs applications installed:
    *   Topaz Gigapixel AI
    *   Topaz Photo AI
    *   Topaz Video AI
*   **Topaz Labs Licenses:**
    *   **Gigapixel AI CLI usage requires a Gigapixel AI Pro license.** Standard licenses may not permit CLI operation.
    *   Ensure your Photo AI and Video AI licenses are active for full functionality.
*   **Python:** Python 3.9 or newer.
*   **System Resources:**
    *   RAM: 16GB+ recommended (32GB+ for heavy video processing).
    *   Storage: 80GB+ free space for applications, models, and temporary files.
    *   GPU: A dedicated GPU (NVIDIA, AMD, or Apple Silicon) is highly recommended for acceptable performance.

## Installation

1.  **Install Topaz Labs Applications:** Download and install Gigapixel AI, Photo AI, and Video AI from the [Topaz Labs website](https://www.topazlabs.com/). Ensure they are licensed and functioning correctly.

2.  **Install Python:** If you don't have Python 3.9+ and `uv` (a fast Python package installer), install them.
    *   Python: [python.org](https://www.python.org/downloads/)
    *   uv: `pip install uv` or see [uv installation guide](https://github.com/astral-sh/uv#installation).

3.  **Install `topyaz`:**
    Clone the repository and install using `uv`:
    ```bash
    git clone https://github.com/your-username/topyaz.git # Replace with actual repo URL
    cd topyaz
    uv pip install .
    ```
    Alternatively, if/when available on PyPI:
    ```bash
    uv pip install topyaz
    ```

4.  **Verify Installation:**
    ```bash
    topyaz version
    topyaz info
    ```
    These commands should report version information and details about your system and detected Topaz products. If executables are not found, you might need to configure their paths (see [Configuration](#configuration)).

## Usage

### Command-Line Interface (CLI)

The basic structure of a `topyaz` command is:
`topyaz [global_options] <product_command> [product_options] <input_path>`

#### Global Options

These options can be used before the product command (e.g., `topyaz --verbose giga ...`):

*   `--output_dir <path>`: Default directory for output files.
*   `--config_file <path>`: Path to a custom `topyaz` configuration YAML file.
*   `--parallel_jobs <int>`: Number of parallel jobs (Note: current implementation might be limited for actual parallelism across Topaz CLIs).
*   `--timeout <seconds>`: Command timeout in seconds (default: 3600).
*   `--backup_originals`: Backup original files before processing.
*   `--preserve_structure`: Preserve directory structure in the output directory.
*   `--dry_run`: Show what commands would be run without actually processing files.
*   `--verbose`: Enable verbose logging.

#### Gigapixel AI (`giga`)

Processes images using Topaz Gigapixel AI.

```bash
topyaz giga <input_path> [options...]
```

**Common Gigapixel Options:**

*   `--model <name>`: AI model (e.g., `std`, `hf`, `art`, `lowres`). Default: `std`.
*   `--scale <int>`: Upscale factor (1-6). Default: 2.
*   `--denoise <1-100>`: Denoise strength.
*   `--sharpen <1-100>`: Sharpen strength.
*   `--face_recovery <1-100>`: Face recovery strength.
*   `--format_output <format>`: Output format (e.g., `preserve`, `jpg`, `png`, `tiff`). Default: `preserve`.
*   `--quality_output <1-100>`: JPEG quality. Default: 95.
*   `--output <output_path>`: Specific output file path.

**Example:**
```bash
topyaz giga ./input/image.jpg --scale 4 --model hf --output ./output/image_upscaled.jpg
```

#### Photo AI (`photo`)

Processes images using Topaz Photo AI.

```bash
topyaz photo <input_path> [options...]
```

**Common Photo AI Options:**

*   `--preset <name>`: Autopilot preset (e.g., `auto`, `standard`, `strong`). Default: `auto`.
*   `--override_autopilot`: Allow manual overrides of autopilot settings.
*   `--upscale <bool>`: Enable/disable upscaling.
*   `--noise <bool>`: Enable/disable noise reduction.
*   `--sharpen <bool>`: Enable/disable sharpening.
*   `--format_output <format>`: Output format (e.g., `preserve`, `jpg`, `png`, `dng`). Default: `preserve`.
*   `--output <output_path>`: Specific output file path.
*   Many more fine-grained controls are available (e.g., `--denoise_strength`, `--sharpen_model`, `--upscaling_factor`). Use `topyaz photo -- --help` for a full list.

**Example:**
```bash
topyaz photo ./input/raw_image.cr2 --override_autopilot --upscale True --sharpen True --noise False --format_output dng
```

#### Video AI (`video`)

Processes videos using Topaz Video AI.

```bash
topyaz video <input_path> [options...]
```

**Common Video AI Options:**

*   `--model <name>`: AI model (e.g., `amq-13`, `prob-3`). Default: `amq-13`.
*   `--scale <int>`: Upscale factor (1-4). Default: 2.
*   `--fps <int>`: Target frame rate for interpolation.
*   `--codec <name>`: Video codec (e.g., `hevc_videotoolbox`, `av1_nvenc`). Default: `hevc_videotoolbox`.
*   `--quality <value>`: Video quality/CRF value (e.g., 18 for H.265). Default: 18.
*   `--stabilize`: Enable stabilization.
*   `--interpolate`: Enable frame interpolation.
*   `--output <output_path>`: Specific output file path.

**Example:**
```bash
topyaz video ./input/clip.mp4 --model prob-3 --scale 2 --interpolate --fps 60 --codec hevc_nvenc --output ./output/clip_enhanced.mp4
```

#### Utility Commands (`info`, `version`)

*   `topyaz info`: Displays system information, detected Topaz products, GPU status, and memory.
*   `topyaz version`: Shows the version of `topyaz` and detected Topaz product versions.

### Programmatic Usage (Python API)

You can use `topyaz` functionalities within your Python scripts.

**1. Using `TopyazCLI` (recommended for simplicity):**

```python
from topyaz.cli import TopyazCLI
from topyaz.core.types import ProcessingOptions

# Configure global options if needed
cli_options = {
    "output_dir": "./processed_media",
    "verbose": True,
    "dry_run": False
}

# Instantiate TopyazCLI. Global options are passed to the constructor.
# Product-specific options are passed to the respective methods.
cli = TopyazCLI(**cli_options)

# Process an image with Gigapixel AI
giga_success = cli.giga(
    input_path="./my_images/photo.jpg",
    model="hf",
    scale=2,
    denoise=50
)
if giga_success:
    print("Gigapixel AI processing successful!")

# Process a video with Video AI
video_success = cli.video(
    input_path="./my_videos/short.mov",
    model="amq-13",
    scale=2,
    interpolate=True,
    fps=60
)
if video_success:
    print("Video AI processing successful!")

# Process a photo with Photo AI
photo_success = cli.photo(
    input_path="./my_images/portrait.nef",
    preset="auto",
    override_autopilot=True,
    sharpen=True
)
if photo_success:
    print("Photo AI processing successful!")
```

**2. Using individual product classes (for more direct control):**

```python
from topyaz.execution.local import LocalExecutor
from topyaz.execution.base import ExecutorContext
from topyaz.core.types import ProcessingOptions
from topyaz.products.gigapixel.api import GigapixelAI
from pathlib import Path

# Common processing options
options = ProcessingOptions(
    output_dir=Path("./api_output"),
    verbose=True,
    timeout=7200 # 2 hours
)

# Setup executor
executor_context = ExecutorContext(timeout=options.timeout, dry_run=options.dry_run)
executor = LocalExecutor(context=executor_context)

# Gigapixel AI example
gigapixel_processor = GigapixelAI(executor=executor, options=options)
result = gigapixel_processor.process(
    input_path="./my_images/landscape.tiff",
    output_path="./api_output/landscape_giga.tiff", # Optional, can be auto-generated
    model="standard",
    scale=2,
    sharpen=30
)

if result.success:
    print(f"Gigapixel processed: {result.output_path}")
    print(f"Execution time: {result.execution_time:.2f}s")
else:
    print(f"Gigapixel processing failed: {result.error_message}")

# Similar instantiation and usage for PhotoAI and VideoAI classes
# from topyaz.products.photo_ai.api import PhotoAI
# from topyaz.products.video_ai.api import VideoAI
```

## Technical Deep Dive

### Project Structure

The `topyaz` codebase is organized into several key directories under `src/topyaz/`:

*   `core/`: Contains core data types (`types.py`), configuration management (`config.py`), and error definitions (`errors.py`).
*   `cli.py`: Defines the main `TopyazCLI` class, which `python-fire` uses to generate the command-line interface.
*   `execution/`: Handles command execution.
    *   `base.py`: Abstract base class for executors.
    *   `local.py`: Implements local command execution using `subprocess`.
*   `products/`: Contains implementations for each Topaz Labs product.
    *   `base.py`: Abstract base class `TopazProduct` for all product integrations.
    *   `gigapixel/`, `photo_ai/`, `video_ai/`: Subdirectories for each product, typically containing:
        *   `api.py`: The main class for interacting with the product (e.g., `GigapixelAI`).
        *   `params.py`: Parameter handling and validation logic.
        *   Other product-specific modules (e.g., `preferences.py` for Photo AI).
*   `system/`: Modules for interacting with the system (environment validation, GPU info, memory status, path handling).
*   `utils/`: Utility modules like logging.

### Core Components

*   **`TopyazCLI` (`cli.py`):** The main entry point for CLI operations. It instantiates product handlers and delegates commands.
*   **`TopazProduct` (`products/base.py`):** An abstract base class defining the interface for all product integrations (finding executables, building commands, parsing output, etc.). `MacOSTopazProduct` extends this with macOS-specific helpers.
*   **Product API Classes (e.g., `GigapixelAI` in `products/gigapixel/api.py`):** Implement the `TopazProduct` interface for a specific Topaz tool. They manage parameter validation, command construction using the tool's CLI syntax, and parsing its output.
*   **`CommandExecutor` (`execution/base.py` & `local.py`):** Responsible for actually running the generated commands. `LocalExecutor` uses Python's `subprocess` module.
*   **`Config` (`core/config.py`):** Loads and manages configuration settings from YAML files (default: `~/.topyaz/config.yaml`) and environment variables (e.g., `TOPYAZ_DEFAULTS__OUTPUT_DIR`). This includes paths to Topaz product executables.
*   **Data Classes (`core/types.py`):** Define structured data for options, parameters, results, and system information, promoting type safety and clarity.

### Configuration

`topyaz` uses a hierarchical configuration system:

1.  **Default Values:** Hardcoded in `core/config.py`.
2.  **System Config File:** `~/.topyaz/config.yaml` (on Linux/macOS) or user profile equivalent on Windows.
3.  **User-Specified Config File:** Passed via the `--config_file` global option.
4.  **Environment Variables:** Prefixed with `TOPYAZ_` (e.g., `TOPYAZ_VIDEO__DEFAULT_MODEL=amq-13`). Double underscores (`__`) denote nesting.

The most important configuration items are the paths to the Topaz product executables. `topyaz` attempts to find these automatically, but they can be explicitly set in the `config.yaml` under the `paths` key if needed:

```yaml
# Example ~/.topyaz/config.yaml
defaults:
  output_dir: "~/topyaz_output"
  verbose: true

paths:
  gigapixel:
    macos: ["/Applications/Topaz Gigapixel AI.app/Contents/Resources/bin/gigapixel"]
    # windows: ["C:/Program Files/Topaz Labs LLC/Topaz Gigapixel AI/gigapixel.exe"]
  photo_ai:
    macos: ["/Applications/Topaz Photo AI.app/Contents/Resources/bin/tpai"]
  video_ai:
    macos: ["/Applications/Topaz Video AI.app/Contents/MacOS/ffmpeg"]
```

### Execution Flow (Local Processing)

1.  User runs a `topyaz` command (e.g., `topyaz giga input.jpg --scale 2`).
2.  `python-fire` routes this to the appropriate method in `TopyazCLI` (e.g., `TopyazCLI.giga()`).
3.  `TopyazCLI` initializes common `ProcessingOptions` and the relevant product handler (e.g., `GigapixelAI`).
4.  The product handler (`GigapixelAI`):
    *   Finds the Gigapixel AI executable using configured/default paths.
    *   Validates the provided parameters (e.g., scale is within range).
    *   Builds the command-line string specific to Gigapixel AI's CLI syntax (e.g., `gigapixel --cli -i input.jpg -o output_temp.jpg --scale 2 ...`).
    *   For Gigapixel/Photo AI, output is typically directed to a temporary directory. Video AI often writes directly.
5.  The `LocalExecutor` runs this command using `subprocess.run()`.
6.  After execution:
    *   The product handler parses the `stdout` and `stderr` from the Topaz tool for information or errors.
    *   If a temporary directory was used, the output file is moved to its final destination.
7.  A `ProcessingResult` object is returned, indicating success/failure and other details.
8.  `TopyazCLI` logs the result and exits.

## Coding and Contributing

Contributions are welcome! Please adhere to the following guidelines.

### Development Philosophy

(Summarized from `CLAUDE.md`)

*   **Iterate Gradually:** Make small, incremental changes.
*   **Preserve Existing Code:** Avoid unnecessary refactoring or removal of existing structure unless essential.
*   **Focus on MVP:** Prioritize minimal viable increments and ship early.
*   **Clarity and Simplicity:** Write clear, descriptive names and comments. Explain the "what" and "why."
*   **Robustness:** Handle failures gracefully, validate inputs, and address edge cases.
*   **Modularity:** Encapsulate repeated logic into concise, single-purpose functions.
*   **Maintain Overview:** Keep a holistic understanding of the codebase and how components interact.

### Python Coding Standards

(Summarized from `CLAUDE.md`)

*   **Package Management:** Use `uv pip` for managing dependencies.
*   **Running Code:** Use `python -m` when applicable.
*   **Formatting:** Adhere to PEP 8 for consistent formatting and naming.
*   **Simplicity & Readability (PEP 20):** Prioritize clean, explicit code over overly complex solutions.
*   **Type Hints:** Use simple type hints (e.g., `list`, `dict`, `|` for unions).
*   **Docstrings (PEP 257):** Write clear, imperative docstrings for modules, classes, and functions.
*   **F-strings:** Preferred for string formatting.
*   **Logging:** Implement `loguru`-based logging, including verbose/debug modes.
*   **CLI Scripts:** If adding new top-level scripts, consider using `python-fire` and `rich` for output. Start scripts with:
    ```python
    #!/usr/bin/env -S uv run -s
    # /// script
    # dependencies = ["PKG1", "PKG2"]
    # ///
    # this_file: path/to/current_file.py
    ```
*   **File Path Records:** Maintain an up-to-date `this_file` comment near the top of each source file, indicating its path relative to the project root.

### Commit and Workflow Practices

(Summarized from `CLAUDE.md`)

*   **Planning:** Use `PLAN.md` for detailed flat plans and `TODO.md` for tracking items.
*   **Changelog:** Update `CHANGELOG.md` after each significant round of changes.
*   **README Updates:** Keep `README.md` synchronized with codebase changes.
*   **Cleanup:** After Python changes, run `./cleanup.sh` if it performs necessary actions like formatting or linting.
*   **Testing:** Write tests for new features and bug fixes. Ensure tests pass before submitting changes.

## License

This project is licensed under the [MIT License](./LICENSE). Please note that the underlying Topaz Labs products have their own commercial licenses and terms of service.
