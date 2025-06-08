
# topyaz: Unified Python CLI Wrapper for Topaz Labs Products

## Overview

`topyaz` is a comprehensive Python package that provides a unified command-line interface for Topaz Labs' three flagship products: Video AI, Gigapixel AI, and Photo AI. The package serves as an intelligent wrapper around the native CLI tools provided by Topaz Labs, offering both local and remote execution capabilities via SSH. The tool is designed to be robust, user-friendly, and production-ready for batch processing workflows.

## Architecture and Design Philosophy

### Core Design Principles

1. **Unified Interface**: A single Python class with consistent CLI options across all three Topaz products
2. **Remote Execution Support**: Native SSH and macOS remote execution capabilities
3. **Failsafe Operation**: Comprehensive error handling, validation, and recovery mechanisms
4. **Detailed Feedback**: Verbose logging and progress reporting for all operations
5. **Production Ready**: Designed for automated workflows and batch processing

### Implementation Strategy

The package implements a unified class structure using Python Fire for automatic CLI generation. The main class `topyazWrapper` serves as the entry point, with specialized methods for each Topaz product (`photo`, `video`, `gp` for Gigapixel). The design emphasizes parameter consistency while accommodating product-specific requirements.

## Package Structure and Implementation

### Python Package Structure

The topyaz package follows standard Python packaging conventions with the following structure:

```
topyaz/
├── src/topyaz/               # Main package source code
│   ├── __init__.py          # Package initialization
│   ├── topyaz.py           # Main module with topyazWrapper class
│   ├── __version__.py      # Dynamic version from git tags (generated)
│   └── py.typed            # Type hints marker file
├── tests/                  # Test suite
│   ├── test_package.py     # Basic package tests
│   └── test_*.py          # Additional test modules
├── pyproject.toml         # Project configuration and dependencies
├── README.md              # Package documentation
├── SPEC.md               # Technical specification
├── TODO.md               # Implementation roadmap
└── CLAUDE.md             # Development instructions
```

### Main Class: topyazWrapper (src/topyaz/topyaz.py)

```python
class topyazWrapper:
    def __init__(self, 
                 remote_host: str = None,
                 ssh_user: str = None, 
                 ssh_key: str = None,
                 verbose: bool = True,
                 dry_run: bool = False,
                 log_level: str = "INFO",
                 timeout: int = 3600,
                 parallel_jobs: int = 1,
                 output_dir: str = None,
                 preserve_structure: bool = True,
                 backup_originals: bool = False):
        """
        Initialize the topyaz wrapper with unified options.
        
        Args:
            remote_host: Remote machine hostname/IP for SSH execution
            ssh_user: SSH username for remote execution
            ssh_key: Path to SSH private key file
            verbose: Enable detailed output and progress reporting
            dry_run: Show commands without executing them
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            timeout: Maximum execution time in seconds per operation
            parallel_jobs: Number of concurrent operations (where supported)
            output_dir: Default output directory for processed files
            preserve_structure: Maintain input directory structure in output
            backup_originals: Create backup copies before processing
        """
```

### Product-Specific Methods

#### Video AI Method
```python
def video(self,
          input_path: str,
          model: str = "amq-13",
          scale: int = 2,
          fps: int = None,
          codec: str = "hevc_videotoolbox",
          quality: int = 18,
          denoise: int = None,
          details: int = None,
          halo: int = None,
          blur: int = None,
          compression: int = None,
          stabilize: bool = False,
          interpolate: bool = False,
          custom_filters: str = None,
          device: int = 0,
          **kwargs) -> bool:
    """
    Process videos using Topaz Video AI.
    
    Supports all major Video AI models and parameters including:
    - Artemis models: amq-13, ahq-10/11/12, alq-10/12/13, alqs-1/2, amqs-1/2, aaa-9/10
    - Proteus models: prob-2, prap-2
    - Dione models: ddv-1/2/3, dtd-1/3/4, dtds-1/2, dtv-1/3/4, dtvs-1/2
    - Gaia models: gcg-5, ghq-5
    - Theia models: thd-3, thf-4
    - Interpolation models: chr-1/2, chf-1/2/3, apo-8, apf-1
    - Stabilization workflow: cpe-1/2 (analysis) + ref-2 (correction)
    
    Environment variables automatically set:
    - TVAI_MODEL_DATA_DIR: ~/Library/Application Support/Topaz Labs LLC/Topaz Video AI/
    - TVAI_MODEL_DIR: /Applications/Topaz Video AI.app/Contents/Resources/models/
    """
```

#### Gigapixel AI Method
```python
def gp(self,
       input_path: str,
       model: str = "std",
       scale: int = 2,
       denoise: int = None,
       sharpen: int = None,
       compression: int = None,
       detail: int = None,
       creativity: int = None,
       texture: int = None,
       prompt: str = None,
       face_recovery: int = None,
       face_recovery_version: int = 2,
       format: str = "preserve",
       quality: int = 95,
       bit_depth: int = 0,
       parallel_read: int = 1,
       **kwargs) -> bool:
    """
    Process images using Topaz Gigapixel AI.
    
    Supports all Gigapixel AI models:
    - Standard models: "std", "standard"
    - High Fidelity: "hf", "high fidelity", "fidelity"
    - Low Resolution: "low", "lowres", "low resolution", "low res"
    - Art & CG: "art", "cg", "cgi"
    - Lines: "lines", "compression"
    - Very Compressed: "very compressed", "high compression", "vc"
    - Text & Shapes: "text", "txt", "text refine"
    - Recovery models: "recovery" (with --mv 1 or 2 for version)
    - Redefine generative: "redefine" (with prompts, creativity, texture)
    
    Face Recovery options:
    - --face-recovery-version: 1 or 2 (default 2)
    - --face-recovery-creativity: 0 (realistic) or 1 (creative)
    
    CLI executable paths:
    - Primary: /Applications/Topaz Gigapixel AI.app/Contents/MacOS/gigapixel
    - Alternative: /Applications/Topaz Gigapixel AI.app/Contents/Resources/bin/gpai
    
    Note: CLI functionality requires Gigapixel AI Pro license ($499/year)
    Performance: CLI is ~2x faster than GUI for batch operations
    """
```

#### Photo AI Method
```python
def photo(self,
          input_path: str,
          autopilot_preset: str = "default",
          format: str = "preserve",
          quality: int = 95,
          compression: int = 2,
          bit_depth: int = 16,
          tiff_compression: str = "zip",
          show_settings: bool = False,
          skip_processing: bool = False,
          override_autopilot: bool = False,
          upscale: bool = None,
          noise: bool = None,
          sharpen: bool = None,
          lighting: bool = None,
          color: bool = None,
          **kwargs) -> bool:
    """
    Process images using Topaz Photo AI.
    
    Photo AI operates primarily through Autopilot settings configured in the GUI.
    Limited CLI parameter control available, with most processing decisions 
    made by the Autopilot system based on image analysis.
    
    CLI executable paths:
    - Primary: /Applications/Topaz Photo AI.app/Contents/MacOS/Topaz Photo AI
    - Alternative: /Applications/Topaz Photo AI.app/Contents/Resources/bin/tpai
    
    Return codes:
    - 0: Success
    - 1: Partial Success (some files failed)
    - -1 (255): No valid files passed
    - -2 (254): Invalid log token (requires GUI login)
    - -3 (253): Invalid argument
    
    Experimental settings override (subject to change):
    - --override: Replace Autopilot settings completely
    - --upscale enabled=true/false: Toggle upscale enhancement
    - --noise enabled=true/false: Toggle denoise enhancement
    - --sharpen enabled=true/false: Toggle sharpen enhancement
    - --lighting enabled=true/false: Toggle lighting adjustment
    - --color enabled=true/false: Toggle color balance
    
    Note: Batch processing limit ~450 images per run
    """
```

## Feature Implementation Details

### Remote Execution Architecture

The remote execution system supports both traditional SSH and native macOS mechanisms for running Topaz tools on remote machines. This is particularly valuable for offloading processing to more powerful machines or distributed processing workflows.

#### SSH Implementation
```python
def _execute_remote_ssh(self, command: str, host: str, user: str, key_path: str = None) -> tuple:
    """
    Execute command on remote host via SSH.
    
    Features:
    - Automatic SSH key authentication
    - Connection pooling and reuse
    - Secure file transfer capabilities
    - Remote environment variable setup
    - Progress monitoring over SSH
    """
```

#### macOS Native Remote Execution
```python
def _execute_remote_macos(self, command: str, host: str, user: str) -> tuple:
    """
    Execute command on remote macOS host using native mechanisms.
    
    Utilizes macOS-specific features:
    - Screen Sharing integration
    - Remote Desktop protocols
    - Keychain integration for authentication
    - Native file sharing protocols (AFP/SMB)
    """
```

### Input Validation and Error Handling

The package implements comprehensive validation for all input parameters, file paths, and system requirements. Error handling covers common issues identified in the research:

#### Authentication Validation
```python
def _validate_authentication(self, product: str) -> bool:
    """
    Verify Topaz product authentication status.
    
    Checks:
    - License file existence and validity
    - Pro license requirements for Gigapixel AI CLI
    - Authentication token expiration
    - GUI login requirement detection
    """
```

#### Environment Validation
```python
def _validate_environment(self, product: str) -> bool:
    """
    Validate system environment for Topaz products.
    
    Validates:
    - macOS version compatibility
    - Required environment variables
    - Model file availability
    - Disk space requirements (~80GB for Video AI)
    - Memory and GPU requirements
    """
```

#### File and Path Validation
```python
def _validate_paths(self, input_path: str, output_path: str = None) -> tuple:
    """
    Comprehensive path validation and sanitization.
    
    Handles:
    - Path expansion and normalization
    - Permission checks for read/write access
    - Space character handling in paths
    - Recursive directory validation
    - Output directory creation with --create-folder equivalent
    """
```

### Progress Monitoring and Logging

The package provides detailed progress monitoring and logging capabilities, essential for long-running batch operations.

#### Progress Tracking
```python
class ProgressMonitor:
    """
    Advanced progress monitoring for batch operations.
    
    Features:
    - Real-time progress estimation
    - ETA calculation based on processing speed
    - Memory usage monitoring
    - GPU utilization tracking
    - Batch completion statistics
    """
    
    def track_video_processing(self, ffmpeg_output: str) -> dict:
        """Parse FFmpeg output for Video AI progress."""
        
    def track_image_processing(self, cli_output: str, total_files: int) -> dict:
        """Parse CLI output for Gigapixel/Photo AI progress."""
```

#### Logging System
```python
def _setup_logging(self, log_level: str, log_file: str = None) -> None:
    """
    Configure comprehensive logging system.
    
    Provides:
    - Structured logging with timestamps
    - Different log levels for various components
    - File and console output options
    - JSON-formatted logs for automation integration
    - Error aggregation and reporting
    """
```

## Command Line Interface Design

The CLI design emphasizes usability and consistency across all three Topaz products while accommodating their unique requirements.

### Basic Usage Examples

#### Video Processing
```bash
# Basic 2x upscaling with default settings
topyaz video input.mp4 --scale 2

# Advanced processing with multiple enhancements
topyaz video input.mp4 \
    --model amq-13 \
    --scale 2 \
    --interpolate \
    --fps 60 \
    --denoise 50 \
    --stabilize \
    --output-dir ./enhanced

# Remote processing on powerful machine
topyaz video input.mp4 \
    --remote-host gpu-server.local \
    --ssh-user admin \
    --scale 4 \
    --model prob-3
```

#### Image Processing with Gigapixel AI
```bash
# Batch upscaling with Pro license
topyaz gp photos/ \
    --scale 4 \
    --model recovery \
    --denoise 40 \
    --sharpen 20 \
    --face-recovery 80 \
    --parallel-read 4

# Generative upscaling with prompt
topyaz gp low_res_art/ \
    --model redefine \
    --scale 2 \
    --creativity 4 \
    --texture 3 \
    --prompt "high resolution digital artwork"
```

#### Photo AI Batch Processing
```bash
# Autopilot-based enhancement
topyaz photo raw_photos/ \
    --format jpg \
    --quality 95 \
    --show-settings

# Remote batch processing
topyaz photo photos/ \
    --remote-host photo-server \
    --format tiff \
    --bit-depth 16 \
    --preserve-structure
```

### Advanced Workflow Examples

#### Multi-Stage Processing Pipeline
```bash
# Process video: stabilize -> upscale -> interpolate
topyaz video shaky_video.mp4 \
    --stabilize \
    --model amq-13 \
    --scale 2 \
    --interpolate \
    --fps 60 \
    --backup-originals
```

#### Distributed Processing
```bash
# Split large batch across multiple machines
topyaz gp large_photo_collection/ \
    --remote-host server1,server2,server3 \
    --parallel-jobs 3 \
    --scale 2 \
    --load-balance
```

## Configuration and Settings Management

### Configuration File Support
The package supports configuration files for storing commonly used settings and remote connection details.

```yaml
# ~/.topyaz/config.yaml
defaults:
  output_dir: "~/processed"
  preserve_structure: true
  backup_originals: false
  log_level: "INFO"

video:
  default_model: "amq-13"
  default_codec: "hevc_videotoolbox"
  default_quality: 18

gigapixel:
  default_model: "std"
  default_format: "preserve"
  parallel_read: 4

photo:
  default_format: "jpg"
  default_quality: 95

remote_hosts:
  gpu-server:
    host: "192.168.1.100"
    user: "admin"
    key: "~/.ssh/topaz_key"
  render-farm:
    host: "render.local"
    user: "processor"
    key: "~/.ssh/render_key"
```

### Environment Variable Support
```bash
# Environment variables for common settings
export topyaz_DEFAULT_OUTPUT="~/processed"
export topyaz_REMOTE_HOST="gpu-server.local"
export topyaz_LOG_LEVEL="DEBUG"
export topyaz_BACKUP_ORIGINALS="true"
```

## Error Handling and Recovery

### Comprehensive Error Detection
The package implements robust error detection for common issues identified in the research:

1. **Authentication Failures**: Automatic detection and user guidance for re-authentication
   - Video AI: Check for valid auth.tpz file
   - Photo AI: Detect exit code -2 (254) for invalid log token
   - Gigapixel AI: Verify Pro license activation

2. **Memory Constraints**: Automatic batch size adjustment and memory monitoring
   - Video AI: CUDA out of memory error handling with instances parameter reduction
   - Photo AI: Batch size limitation detection (~450 images max)
   - Gigapixel AI: Parallel read optimization based on 8GB memory cap

3. **GPU Errors**: Fallback to CPU processing and device selection
   - "No such filter: 'tvai_up'" error handling (wrong FFmpeg binary)
   - Device selection for multi-GPU systems
   - VideoToolbox vs. software encoding fallback

4. **Path Issues**: Intelligent path handling with space character support
   - Automatic path quoting for spaces in filenames
   - macOS application bundle access permission handling
   - Write permission validation for output directories

5. **Model Download Failures**: Retry mechanisms and fallback strategies
   - TVAI_MODEL_DATA_DIR write permission issues
   - Symbolic link creation for restricted app bundle access
   - 80GB space requirement validation

6. **Network Issues**: Connection retry and timeout handling for remote operations
   - SSH connection pooling and reuse
   - Remote environment variable setup validation
   - Network diagnostic tools for remote hosts

### Recovery Mechanisms
```python
def _handle_processing_error(self, error: Exception, context: dict) -> bool:
    """
    Intelligent error handling with recovery attempts.
    
    Recovery strategies:
    - Reduce batch size for memory errors
    - Retry with different device for GPU errors
    - Fall back to local processing for remote failures
    - Prompt for re-authentication when needed
    - Resume processing from last successful file
    """
```

### Resumable Operations
```python
def _create_checkpoint(self, operation_id: str, state: dict) -> None:
    """
    Create operation checkpoint for resumable processing.
    
    Enables:
    - Resume interrupted batch operations
    - Skip already processed files
    - Maintain processing statistics
    - Recovery from system crashes
    """
```

## Performance Optimization

### Parallel Processing Support
The package implements intelligent parallel processing that respects the limitations of each Topaz product:

- **Video AI**: Sequential processing with optimal FFmpeg parameters
- **Gigapixel AI**: Parallel image loading with memory constraints
- **Photo AI**: Batch size optimization based on available memory

### Hardware Detection and Optimization
```python
def _detect_hardware_capabilities(self) -> dict:
    """
    Detect and optimize for available hardware.
    
    Detects:
    - Apple Silicon vs Intel architecture
    - Available GPU memory and capabilities
    - CPU core count and memory
    - Storage speed and available space
    - Network capabilities for remote processing
    """
```

### Memory Management
```python
def _optimize_memory_usage(self, file_list: list, available_memory: int) -> list:
    """
    Optimize batch processing based on available memory.
    
    Implements:
    - Dynamic batch size calculation
    - Memory usage prediction
    - Garbage collection optimization
    - Process memory monitoring
    """
```

## Testing and Validation

### Unit Test Coverage
The package includes comprehensive unit tests covering:

- All CLI parameter combinations
- Error handling scenarios
- Remote execution functionality
- File handling and validation
- Progress monitoring accuracy

### Integration Tests
```python
def test_video_ai_integration():
    """Test complete Video AI workflow with real files."""
    
def test_gigapixel_pro_features():
    """Test Gigapixel AI Pro-specific functionality."""
    
def test_remote_execution():
    """Test SSH and remote execution capabilities."""
    
def test_batch_processing():
    """Test large batch operations with various file types."""
```

### Validation Scripts
```bash
# Validation script for system requirements
topyaz validate --check-licenses --check-environment --check-connectivity

# Performance benchmarking
topyaz benchmark --test-local --test-remote --generate-report
```

## Documentation and User Guidance

### Comprehensive Help System
The package provides extensive help documentation accessible via CLI:

```bash
# General help
topyaz --help

# Product-specific help
topyaz video --help
topyaz gp --help
topyaz photo --help

# Show examples and tutorials
topyaz examples
topyaz tutorial video
topyaz troubleshoot
```

### Interactive Setup Wizard
```bash
# Initial setup and configuration
topyaz setup --interactive

# Remote host configuration
topyaz setup --add-remote-host

# License and authentication verification
topyaz setup --verify-licenses
```

## Installation and Dependencies

### Package Requirements

The package dependencies are defined in `pyproject.toml`:

```toml
[project]
dependencies = [
    "fire>=0.4.0",           # CLI framework
    "paramiko>=2.7.0",       # SSH functionality
    "pyyaml>=5.4.0",         # Configuration files
    "tqdm>=4.60.0",          # Progress bars
    "psutil>=5.8.0",         # System monitoring
    "pathlib>=1.0.0",        # Path handling
    "typing-extensions>=3.7.0",  # Type hints
]

[project.optional-dependencies]
dev = [
    "pre-commit>=4.1.0",
    "ruff>=0.9.7", 
    "mypy>=1.15.0",
    # ... (see pyproject.toml for full list)
]
test = [
    "pytest>=8.3.4",
    "pytest-cov>=6.0.0",
    # ... (see pyproject.toml for full list)
]
```

### Installation Methods
```bash
# PyPI installation (future)
pip install topyaz

# Development installation
git clone https://github.com/twardoch/topyaz.git
cd topyaz
pip install -e .

# Using uv (recommended for development)
uv pip install -e .[dev,test]
```

### System Requirements
- macOS 11.0 Big Sur or higher (Video AI requires 10.14 Mojave minimum for CPU, 10.16 Big Sur for GPU)
- macOS 13 Ventura or newer for advanced models (Rhea, Aion, Iris Enhancement)
- macOS 14 Sonoma for Gigapixel AI generative models (Recover, Redefine)
- Python 3.8 or higher
- Topaz Video AI, Gigapixel AI, and/or Photo AI installed
- Valid licenses for respective products (Pro license required for Gigapixel AI CLI - $499/year)
- Minimum 16GB RAM (32GB recommended for 4K video processing)
- Apple Silicon: 8GB unified memory minimum, Intel: 16GB system RAM
- 80GB+ free disk space for Video AI models
- 2GB+ VRAM for GPU acceleration

## Security Considerations

### SSH Security
- Support for SSH key-based authentication only
- No password storage or transmission
- SSH connection validation and host key verification
- Secure file transfer protocols

### File Security
- Input validation to prevent path traversal attacks
- Safe temporary file handling
- Backup verification and integrity checks
- Secure cleanup of temporary files

### Remote Execution Security
- Command injection prevention
- Environment variable sanitization
- Restricted command execution scope
- Audit logging for all remote operations

## Community Tools Integration

### Existing Community Projects
The package integrates with and references existing community tools:

1. **vai-docker**: Docker containerization for Video AI on Linux
   - GitHub: https://github.com/jojje/vai-docker
   - Enables cross-platform Video AI usage
   - GPU acceleration support within containers

2. **gigapixel-automator**: AppleScript automation for pre-CLI Gigapixel versions
   - GitHub: https://github.com/halfSpinDoctor/gigapixel-automator
   - Legacy GUI automation (now superseded by native CLI)
   - Compatible with older Gigapixel versions

3. **ComfyUI-TopazVideoAI**: Video AI integration for ComfyUI
   - GitHub: https://github.com/sh570655308/ComfyUI-TopazVideoAI
   - Node-based workflow integration
   - Custom filter pipeline support

4. **Python Gigapixel Package**: PyPI wrapper for Gigapixel AI
   - Programmatic control interface
   - Version compatibility requirements
   - Integration patterns for automation

### Integration Capabilities
```python
def integrate_community_tools(self):
    """
    Detect and integrate with community tools.
    
    Features:
    - Auto-detect vai-docker installations
    - Import existing automation scripts
    - ComfyUI workflow compatibility
    - Legacy script migration assistance
    """
```

## Future Enhancements

### Planned Features
1. **GUI Integration**: Optional web-based monitoring interface
2. **Cloud Processing**: Integration with cloud GPU services (AWS, GCP, Azure)
3. **Plugin System**: Extensible architecture for custom processing workflows
4. **API Server**: REST API for integration with other applications
5. **Distributed Processing**: Native distributed computing support across multiple machines
6. **Machine Learning**: Intelligent parameter optimization based on content analysis
7. **Docker Support**: Native containerization for cross-platform deployment
8. **Workflow Designer**: Visual pipeline designer for complex processing chains

### Community Integration
- GitHub repository with issue tracking and feature requests
- Community-contributed presets and workflows repository
- Plugin marketplace for extensions and custom integrations
- Documentation contributions and example workflows
- Community model and parameter sharing
- Integration with existing Topaz community forums and resources

## Support and Troubleshooting

### Built-in Diagnostics
```bash
# System diagnostic report
python -m topyaz diagnose --full-report

# Performance analysis  
python -m topyaz profile --operation video --input sample.mp4

# License verification
python -m topyaz license-check --all-products
```

### Development Commands

The package includes development commands via `pyproject.toml` configuration:

```bash
# Run tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Type checking
hatch run type-check

# Linting and formatting
hatch run lint
hatch run fmt

# Build documentation
hatch run docs:build
```

### Common Issue Resolution
The package includes automated detection and resolution guidance for common issues:

1. **"No such filter" errors**: Automatic Topaz FFmpeg detection
2. **Authentication failures**: Step-by-step re-authentication guidance
3. **Memory errors**: Automatic batch size reduction suggestions
4. **Permission errors**: Path and permission troubleshooting
5. **Remote connection issues**: Network diagnostic and troubleshooting tools

This specification provides a comprehensive foundation for implementing `topyaz` as a production-ready, user-friendly wrapper around Topaz Labs CLI tools, with extensive error handling, remote execution capabilities, and detailed user feedback throughout all operations.

# Appendix: Reference for Topaz CLI tools

## Topaz Gigapixel AI

Topaz Gigapixel AI in CLI operates via its `gigapixel` CLI tool. 

```
gpai="/Applications/Topaz Gigapixel AI.app/Contents/Resources/bin/gpai"
"${gpai}" --help

usage: Topaz Gigapixel AI [-v] [--cli] [-m MODEL] [--mv VERSION] 
       [--dn STRENGTH] [--sh STRENGTH] [--cm STRENGTH] [--dt STRENGTH] 
       [--cr STRENGTH] [--tx STRENGTH] [--prompt STR] [--pds FACTOR] 
       [--fr STRENGTH] [--frv VERSION] [--frc CREATIVITY] [--gc] 
       [--scale MULTIPLIER] [--width PIXELS] [--height PIXELS] 
       [--res RESOLUTION] [-i PATH [PATH ...]] [-r] [-o PATH] [--cf] 
       [--prefix STR] [--suffix STR] [--am] [--overwrite] [--se] [--flatten] 
       [-f {preserve, jpg, jpeg, png, tif, tiff}] [--tc {none, zip, lzw}] 
       [--pc LEVEL] [--bd {0, 8, 16}] [--jq QUALITY] 
       [--cs {preserve, prophoto, srgb, adobe, apple, wide, cmyk}] [--icc PATH] 
       [--verbose] [-q] [-p QUANTITY] [-d DEVICE] [--ld] [-h]

High quality image upscaler

arguments:
  -v, --version     Show version information.
  --cli             Force application to run in CLI mode.
  -m MODEL, --model MODEL
                    Model used to process images.
  --mv VERSION, --model-version VERSION
                    Version number of the model being used.
  --dn STRENGTH, --denoise STRENGTH
                    How much denoising to apply. Only applies to models that use 
                    the denoise parameter.
  --sh STRENGTH, --sharpen STRENGTH
                    How much sharpening to apply. Only applies to models that 
                    use the sharpen parameter.
  --cm STRENGTH, --compression STRENGTH
                    How much compression reduction to apply. Only applies to 
                    models that use the compression parameter.
  --dt STRENGTH, --detail STRENGTH
                    How much detail enhancement to apply. Only applies to models 
                    that use the detail parameter.
  --cr STRENGTH, --creativity STRENGTH
                    How much creativity the model should be allowed to have. 
                    Only applies to models that use the creativity parameter.
  --tx STRENGTH, --texture STRENGTH
                    How much texture the model should be allowed to add. Only 
                    applies to models that use the detail parameter.
  --prompt STR      What prompt to give to the model. Only applies to models 
                    that use the prompt parameter.
  --pds FACTOR, --predownscale FACTOR
                    Pre-downscale factor for Recovery V2. (Default: 100)
  --fr STRENGTH, --face-recovery STRENGTH
                    Face recovery strength.
  --frv VERSION, --face-recovery-version VERSION
                    Version number of the face recovery model being used.
  --frc CREATIVITY, --face-recovery-creativity CREATIVITY
                    Whether to use realistic or creative face recovery. Only 
                    applicable to Face Recovery v2.
  --gc, --gamma-correction
                    Enable gamma correction
  --scale MULTIPLIER
                    Upscale images by a specific multiplier.
  --width PIXELS    Upscale images to a specific width.
  --height PIXELS   Upscale images to a specific height.
  --res RESOLUTION, --resolution RESOLUTION
                    The output resolution to use. Takes values in format #(ppi/
                    ppcm), e.g., 300ppi, 100ppcm.
  -i PATH [PATH ...], --input PATH [PATH ...]
                    File and/or folders to process.
  -r, --recursive   Recurse into sub-folders when parsing input directories.
  -o PATH, --output PATH
                    Folder to save images to. Use --cf to create output folders 
                    automatically.
  --cf, --create-folder
                    Creates the output folder if it doesn't already exist.
  --prefix STR      Prefix to prepend to output filename.
  --suffix STR      Suffix to append to output filename.
  --am, --append-model
                    Append model name used to output filename.
  --overwrite       Overwrite input files with output. THIS IS DESTRUCTIVE.
  --se, --skip-existing
                    Skip files whose output file already exists. Helpful for 
                    resuming a previous run.
  --flatten         If input is recursive, place all files at single level in 
                    output folder.
  -f {preserve, jpg, jpeg, png, tif, tiff}, --image-format {preserve, jpg, jpeg, png, tif, tiff}
                    Image format to save to.
  --tc {none, zip, lzw}, --tiff-compression {none, zip, lzw}
                    Which compression scheme to use for TIFF outputs. (Default: zip)
  --pc LEVEL, --png-compression LEVEL
                    Which compression level to use for PNG outputs. (Default: 4)
  --bd {0, 8, 16}, --bit-depth {0, 8, 16}
                    What bit depth to use for PNG/TIFF outputs. 0 will preserve 
                    input file depth. (Default: 0)
  --jq QUALITY, --jpeg-quality QUALITY
                    What quality level to save JPEG outputs. (Default: 95)
  --cs {preserve, prophoto, srgb, adobe, apple, wide, cmyk}, --colorspace {preserve, prophoto, srgb, adobe, apple, wide, cmyk}
                    What color space to save the output with. (Default: preserve)
  --icc PATH        Save out with a specified ICC profile.
  --verbose         Display more information while processing.
  -q, --quiet       Display no information while processing.
  -p QUANTITY, --parallel QUANTITY
                    Maximum files to queue at once. (Default: 1)
  -d DEVICE, --device DEVICE
                    Which device to use. Use --list-devices / --ld to show 
                    current devices. (Default: -2)
  --ld, --list-devices
                    Print a list of current devices.
  -h, --help        Shows this help message
```


Released in version 7.3.0, Gigapixel's Command Line Interface (CLI) feature, [available exclusively to Pro License users](https://www.topazlabs.com/gigapixel-pro), offers advanced functionality for efficient batch processing and integration into automated workflows. Users can leverage this feature to upscale images with precision and speed directly from the command line, ensuring seamless integration with existing software systems and maximizing productivity.

---

#### Notes

*Updated May 21st, 2025
Command line flags subject to change.*

After install, you should be able to access it from the command line/powershell/terminal by typing in **gigapixel** (or **gigapixel-alpha/gigapixel-beta** depending on release type) as the command.

With no arguments, this should print a usage dialog.

The following examples are written with UNIX-style escape characters. Windows users may need to edit these commands to follow CMD/PowerShell formatting.

---

#### Basics

* -m, --model for model. Valid values are specified in json files but should account for common shortenings (e.g., art, cg, and cgi are valid for Art & CGI model)
  + If there is a short code missing that you tried and it didn't work let us know

**AI Models and their corresponding aliases**

|  |  |
| --- | --- |
| AI Models | Aliases |
| Art & CG | "art", "cg", "cgi" |
| Lines | "lines", "compression" |
| Very Compressed | "very compressed", "high compression", "vc" |
| High Fidelity | "hf", "high fidelity", "fidelity" |
| Low Resolution | "low", "lowres", "low resolution", "low res" |
| Standard | "std", "standard" |
| Text & Shapes | "text", "txt", "text refine" |
| Recover | "recovery" |
| Redefine | "redefine" |

* –mv, --model-version for model version. Valid values are based on the UI model versions, so version 2 is for standard, low res, and high fidelity models
* --dn/--denoise, --sh/--sharpen, --cm/--compression for the various model options. Accepts values 1-100.
* --fr, --face-recovery for both enabling and setting face recovery strength. Accepts values 1-100.
* --scale, --width, --height for setting upscale type/value. All mutually exclusive.
* --res, --resolution for setting pixel density
  + Valid values are stuff like 300ppi, 150ppcm
* -i or --input specifies which files or folders to process.
* -r, --recursive should recurse into subdirectories when finding input files
* -o, --output to specify output folder
* --cf, --create-folder will create the output folder if it doesn't exist
* --prefix adds a prefix to the output file name
* --suffix adds a suffix to the output file name
* --overwrite allows overwriting file **(CANNOT BE UNDONE)**
* --flatten will flatten folder structure if using recursive mode
  + e.g., input/a/1.png and input/b/2.png would be put in output folder without the a/b directories
* -f, --image-format specifies the output file type
  + Accepts jpg, jpeg, tif, tiff, png, and preserve (default)
  + jpg/tif vs jpeg/tiff will allow 3 vs 4 character output extensions for flexibility
* --tc, --tiff-compression sets the tiff compression type
  + Valid values are none, zip (default), and lzw
  + Only used if output type is tiff (either set directly or through preserve)
* --pc, --png-compression sets compression level for png outputs
  + Valid values are 0-9 (default 4)
  + Only used if output type is png (either set directly or through preserve)
* --bd, --bit-depth sets the bit depth of the output
  + Valid values are 0 (default), 8, and 16
  + 0 will preserve input bit depth
* --jq, --jpeg-quality sets output jpeg quality
  + Valid values are 0-100 (default 95)
* --cs, --colorspace sets what color space to use for output
  + Valid values are preserve (default), sRGB, Pro Photo, Apple, Adobe, Wide, and CMYK
* --icc specifies a custom color profile to use for output
  + Overrides --colorspace flag except in the case of CMYK
* --verbose turns on more logging lines
* --q, --quiet turns off all logging (some logs may still leak through though)
* -p, --parallel enables reading multiple files at once to save time at the cost of memory
  + Accepts any positive integer. A value of 1 is identical to normal flow, a value of 10 would load 10 images at once.
  + Note that the parallel reading is capped at 8GB estimate file size (image size + upscaled image size estimate)
* –am, --append-model appends model name and scale to the end of the filename (not implemented yet)
* --face-recovery-creativity, --frc for creativity, 0 or 1

---

#### Generative Models

New models for -m flag: "recovery" and "redefine".
recovery accepts additional --mv flag, either 1 or 2 (default).

**For "recovery"**

* --detail: 1-100, used by recovery
* --face-recovery-version or --frv
* --frv 2 for v2 (default) or --frv 1 for version
* --face-recovery-creativity, --frc for creativity, 0 or 1

**For "redefine"**

* --creativity, --cr: 1-6, redefine only
* --texture, --tx: 1-6, redefine only
* --prompt: Image description to pass to redefine model
* --denoise: 1-6 when used with redefine
* --sharpen: 1-6 when used with redefine

*Example for running Redefine with a prompt*

```
gigapixel.exe -i image.png -o output_folder -m redefine --cr 3 --tx 3 --prompt " This would be where I would put the image prompt if I had one" --am
```

*In more detail*

```
gigapixel.exe        # CLI executable command
    -i image.png     # Input image
    -o output_folder # Output folder/path
    -m redefine      # Model name
    --cr 3           # Creativity value
    --tx 3           # Texture value
    --dn 1           # Denoise value
    --sh 1           # Sharpen value
    --prompt "This would be where I would put the image prompt if I had one" # Prompt value
    --am             # Append model name to output
```

---

#### Examples

The **gigapixel** executable should be on the path by default after install, but if not you can add it to your path. The default paths should be:

**Windows**

```
C:\Program Files\Topaz Labs LLC\Topaz Gigapixel AI\bin

```

**Mac**

```
/Applications/Topaz Gigapixel AI.app/Contents/Resources/bin
```

*Upscale all files in a folder by 2x using auto settings, preserving all aspects of image format (extension, bit depth, etc)*

```
gigapixel --recursive -i ~/Pictures/inputs -o ~/Pictures/outputs --scale 2
```

*Upscale all files inside input directory recursively*

```
gigapixel --recursive -i ~/Pictures/inputs -o ~/Pictures/outputs --scale 2
```

Upscale a single raw and convert it to a jpg without using autopilot (all model parameters are set)

```
gigapixel --recursive -i ~/Pictures/input.cr3 -o ~/Pictures/outputs --scale 2 -m std \
--mv 2 --denoise 30 --sharpen 10 --compression 5 --image-format jpg \
--jpeg-quality 95
```

*Upscale using face recovery set to 80 strength*

```
gigapixel --recursive -i ~/Pictures/input.jpg -o ~/Pictures/outputs --scale 2 --face-recovery 80
```



## Topaz Photo AI

Topaz Photo AI in CLI operates via its `tpai` CLI tool. 

```
tpai='/Applications/Topaz Photo AI.app/Contents/Resources/bin/tpai'; "${tpai}" --help
```

or

```
tpai='/Applications/Topaz Photo AI.app/Contents/MacOS/Topaz Photo AI'; "${tpai}" --cli --help
```
returns:

```
Checking if log directory should be pruned. Currently have 11 log files.
Number of logs exceeds max number to keep ( 10 ). Cleaning excess logs.
Logger initialized
Options:
    --cli: Required to access CLI mode, otherwise images are treated as if passed by an external editor.
    --output, -o: Output folder to save images to. If it doesn't exist the program will attempt to create it.
    --overwrite: Allow overwriting of files. THIS IS DESTRUCTIVE.
    --recursive, -r: If given a folder path, it will recurse into subdirectories instead of just grabbing top level files.
        Note: If output folder is specified, the input folder's structure will be recreated within the output as necessary.
File Format Options:
    --format, -f: Set the output format. Accepts jpg, jpeg, png, tif, tiff, dng, or preserve. Default: preserve
        Note: Preserve will attempt to preserve the exact input extension, but RAW files will still be converted to DNG.
Format Specific Options:
    --quality, -q: JPEG quality for output. Must be between 0 and 100. Default: 95
    --compression, -c: PNG compression amount. Must be between 0 and 10. Default: 2
    --bit-depth, -d: TIFF bit depth. Must be either 8 or 16. Default: 16
    --tiff-compression: -tc: TIFF compression format. Must be "none", "lzw", or "zip".
        Note: lzw is not allowed on 16-bit output and will be converted to zip.
Debug Options:
    --showSettings: Shows the Autopilot settings for images before they are processed
    --skipProcessing: Skips processing the image (e.g., if you just want to know the settings)
    --verbose, -v: Print more log entries to console.
Settings Options:
    Note: EXPERIMENTAL. The API for changing the processing settings is experimental and subject to change.
          After enabling an enhancement you may specify settings to override.
    --showSettings: Prints out the final settings used when processing.
    --override: If specified, any model settings will fully replace Autopilot settings.
                Default behavior will merge other options into Autopilot settings.
    --upscale: Turn on the Upscale enhancement. Pass enabled=false to turn it off instead.
    --noise: Turn on the Denoise enhancement. Pass enabled=false to turn it off instead.
    --sharpen: Turn on the Sharpen enhancement. Pass enabled=false to turn it off instead.
    --lighting: Turn on the Adjust lighting enhancement. Pass enabled=false to turn it off instead.
    --color: Turn on the Balance color enhancement. Pass enabled=false to turn it off instead.

Return values:
    0 - Success
    1 - Partial Success (e.g., some files failed)
    -1 (255) - No valid files passed.
    -2 (254) - Invalid log token. Open the app normally to login.
    -3 (253) - An invalid argument was found.
```

To use the Topaz Photo AI command line interface (CLI), follow the below instructions for your operating system.

Windows Mac

Windows:

1. Open Command Prompt or Terminal
2. Type in:
   cd "C:\Program Files\Topaz Labs LLC\Topaz Photo AI"
3. Type in:
    .\tpai.exe --help
4. Type in:
    .\tpai.exe "folder/or/file/path/here"

![Example Output](https://cdn.sanity.io/images/r2plryeu/production/45fd256fb694c2ff306b5a16b987852a828d10cd-1787x919.png?q=90&fit=max&auto=format)

Mac:

1. Open Terminal
2. Type in:
   cd /Applications/Topaz\ Photo\ AI.app/Contents/MacOS
3. Type in:
   ./Topaz\ Photo\ AI --help
4. Type in:
   ./Topaz\ Photo\ AI --cli "folder/or/file/path/here"

![Example Output](https://cdn.sanity.io/images/r2plryeu/production/79d4022c3676d5b2df9457a354f39ec772ad98dc-1756x936.png?q=90&fit=max&auto=format)

---

## Processing Controls

The CLI will use your Autopilot settings to process images. Open Topaz Photo AI and go to the Preferences > Autopilot menu.

Instructions on using the Preferences > Autopilot menu are [here](https://docs.topazlabs.com/photo-ai/enhancements/autopilot-and-configuration).

### Command Options

--output, -o: Output folder to save images to. If it doesn't exist the program will attempt to create it.

--overwrite: Allow overwriting of files. THIS IS DESTRUCTIVE.

--recursive, -r: If given a folder path, it will recurse into subdirectories instead of just grabbing top level files.
Note: If output folder is specified, the input folder's structure will be recreated within the output as necessary.

### File Format Options:

--format, -f: Set the output format. Accepts jpg, jpeg, png, tif, tiff, dng, or preserve. Default: preserve
Note: Preserve will attempt to preserve the exact input extension, but RAW files will still be converted to DNG.Format Specific Options:

--quality, -q: JPEG quality for output. Must be between 0 and 100. Default: 95

--compression, -c: PNG compression amount. Must be between 0 and 10. Default: 2

--bit-depth, -d: TIFF bit depth. Must be either 8 or 16. Default: 16

--tiff-compression: -tc: TIFF compression format. Must be "none", "lzw", or "zip".
Note: lzw is not allowed on 16-bit output and will be converted to zip.

### Debug Options:

--showSettings: Shows the Autopilot settings for images before they are processed

--skipProcessing: Skips processing the image (e.g., if you just want to know the settings)

--verbose, -v: Print more log entries to console.

Return values:
0 - Success
1 - Partial Success (e.g., some files failed)
-1 (255) - No valid files passed.
-2 (254) - Invalid log token. Open the app normally to login.
-3 (253) - An invalid argument was found.




## Topaz Video AI

Topaz Video AI in CLI operates with help of `ffmpeg`. 


Topaz Video AI supports executing scripts using a command line interface.

This is designed for advanced users comfortable working in such an environment and offers more flexibility in customizing a variety of scripted processes.

We highly recommend using the app’s user interface for those not comfortable working in a command terminal.

The majority of the commands for this build will be FFmpeg commands.

There is no need to install FFmpeg, it is automatically included with the TVAI installer. This article will outline the basic functions for TVAI’s CLI, however, you will want to familiarize yourself with FFmpeg commands for more complex use cases.

### Getting Started with CLI

Before using the CLI for the first time, we recommend launching the GUI and logging into the app. This eliminates the need to use a command to log into the app and will allow you to launch the terminal directly from the GUI.

After logging in, select Process > Open Command Prompt, this will set the model directory automatically. The next time you want to launch the CLI without the GUI, follow the steps below:

Windows macOS

You must manually set the *TVAI\_MODEL\_DATA\_DIR* and *TVAI\_MODEL\_DIR* environment variables if launching without the GUI. Please see the Environment Variables section below.

```
cd "C:\Program Files\Topaz Labs LLC\Topaz Video AI"
```

If you log out and need to log back in without launching the GUI:

```
.\login
```

You must manually set the *TVAI\_MODEL\_DATA\_DIR* and *TVAI\_MODEL\_DIR* environment variables if launching without the GUI. Please see the Environment Variables section below.

```
cd /Applications/Topaz\ Video\ AI.app/Contents/MacOS
```

If you log out and need to log back in without launching the GUI:

```
./login
```

---

### Basic TVAI Filters

Upscaling & Enhancement

```
tvai_up
```

Interpolation

```
tvai_fi
```

Stabilization

```
tvai_cpe + tvai_stb
```

### Video AI Command Line Usage

#### Environment Variables

***TVAI\_MODEL\_DATA\_DIR***

* This variable should be set to the folder where you want model files to be downloaded. A location with ~80 GB of free space will work best.
* Default value:
  + Chosen during initial installation (Windows)
  + /Applications/Topaz Video AI.app/Contents/Resources/models (macOS)

***TVAI\_MODEL\_DIR***

* This variable should be set to the folder containing the model definition files (.json), your authentication file (*auth.tpz*), and the *tvai.tz* file.
* In most cases, this value should not be changed from its default setting.
* Default value:
  + Chosen during initial installation (Windows)
  + /Applications/Topaz Video AI.app/Contents/Resources/models (macOS)

---

### GPU-Specific Usage Notes

TVAI is used as an FFmpeg filter, and all models will work on graphics devices from Intel, AMD, Nvidia, and Apple using a command like this example:

```
-vf "tvai_up=model=aaa-10:scale=2"
```

However, different graphics cards may support different encoders and options. Similarly, different encoders support different options, so you may need to tweak settings on different machines. The following options can be used to take advantage of hardware acceleration features from different GPU manufacturers:

Intel NVIDIA AMD macOS (Intel & Apple Silicon)

On some newer Intel devices, it may be necessary to set the ***`Computer\HKEY\_CURRENT\_USER\Software\Topaz Labs LLC\Topaz Video AI\OVUseDeviceIndex`*** registry entry. You can set the device by adding **`device=#`** to the filter argument, where **#** is the device index:

```
-vf "tvai_up=model=aaa-10:scale=2:device=0"
```

#### General Usage

1. Add the **`-strict 2 -hwaccel auto`** flags
2. Set **`-c:v` to `hevc\_qsv` or `h264\_qsv`**
3. Add **`-profile main -preset medium -max\_frame\_size 65534`**
4. Set **`-global\_quality`** to the desired quality
5. Add **`-pix\_fmt yuv420p -movflags frag\_keyframe+empty\_moov`**
6. Provide **TVAI filter string**

Example Command:

```
./ffmpeg -hide_banner -nostdin -y -strict 2 -hwaccel auto -i "input.mp4" -c:v hevc_qsv -profile main -preset medium -max_frame_size 65534 -global_quality 19 -pix_fmt yuv420p -movflags frag_keyframe+empty_moov -vf "tvai_up=model=amq-13:scale=2:device=0" "output-artemis.mp4"
```

The above command performs the following:

* Hides the FFmpeg startup banner
* Enables hardware acceleration, and uses the hevc\_qsv encoder (H.265)
* Uses the main profile with the medium preset for the encoder
* Sets the CRF to 19
* Sets the output pixel format to yuv420p
* Creates 100% fragmented output, allowing the file to be read if the processing is interrupted
* Upscales 2x using Artemis v13 on GPU #0

1. Add the **`-strict 2 -hwaccel auto`** flags
2. Set **`-c:v` to `hevc\_nvenc` or `h264\_nvenc`**
3. Add **`-profile main -preset medium`**
4. Set **`-global\_quality`**to the desired quality
5. Add **`-pix\_fmt yuv420p -movflags frag\_keyframe+empty\_moov`**
6. Provide **TVAI filter string**

Example Command:

```
./ffmpeg -hide_banner -nostdin -y -strict 2 -hwaccel auto -i "input.mp4" -c:v hevc_nvenc -profile main -preset medium -global_quality 19 -pix_fmt yuv420p -movflags frag_keyframe+empty_moov -vf "tvai_up=model=amq-13:scale=2" "output-artemis.mp4"
```

The above command performs the following:

* Hides the FFmpeg startup banner
* Enables hardware acceleration, and uses the hevc\_nvenc encoder (H.265)
* Uses the main profile with the medium preset for the encoder
* Sets the CRF to 19
* Sets the output pixel format to yuv420p
* Creates 100% fragmented output, allowing the file to be read if the processing is interrupted
* Upscales 2x using Artemis v13

1. Add the **`-strict 2 -hwaccel auto`** flags
2. Set **`-c:v` to `hevc\_amf` or `h264\_amf`**
3. Add **`-profile main`**
4. Set **`-global\_quality`**to the desired quality
5. Add **`-pix\_fmt yuv420p -movflags frag\_keyframe+empty\_moov`**
6. Provide **TVAI filter string**

Example Command:

```
./ffmpeg -hide_banner -nostdin -y -strict 2 -hwaccel auto -i "input.mp4" -c:v hevc_amf -profile main -global_quality 19 -pix_fmt yuv420p -movflags frag_keyframe+empty_moov -vf "tvai_up=model=amq-13:scale=2" "output-artemis.mp4"
```

The above command performs the following:

* Hides the FFmpeg startup banner
* Enables hardware acceleration, and uses the hevc\_amf encoder (H.265)
* Uses the main profile for the encoder
* Sets the CRF to 19
* Sets the output pixel format to yuv420p
* Creates 100% fragmented output, allowing the file to be read if the processing is interrupted
* Upscales 2x using Artemis v13

1. Add the **`-strict 2 -hwaccel auto`** flags
2. Set **`-c:v` to `h264\_videotoolbox` or `hevc\_videotoolbox` or `prores\_videotoolbox`**
3. Add **`-profile main`** for H264 or HEVC outputs, or **`-profile hq`** for ProRes 422 HQ output
4. Set **`-global\_quality`**to the desired quality
5. Add **`-pix\_fmt yuv420p`** for H.264 or HEVC, add **`-pix\_fmt p210le`** for ProRes
6. Provide **TVAI filter string**

Example Command:

```
./ffmpeg -hide_banner -nostdin -y -strict 2 -hwaccel auto -i "input.mp4" -c:v "hevc_videotoolbox" "-profile:v" "main" "-pix_fmt" "yuv420p" "-allow_sw" "1" -vf "tvai_up=model=amq-13:scale=2" "output-artemis.mp4"
```

The above command performs the following:

* Hides the FFmpeg startup banner
* Enables hardware acceleration, and uses the VideoToolbox encoder (H.265)
* Uses the main profile for the encoder
* Sets the output pixel format to yuv420p
* Upscales 2x using Artemis v13

### Selecting Models with CLI

#### Scaling Models

|  |  |
| --- | --- |
| aaa-10 | Artemis Aliased & Moire v10 |
| aaa-9 | Artemis Aliased & Moire v9 |
| ahq-10 | Artemis High Quality v10 |
| ahq-11 | Artemis High Quality v11 |
| ahq-12 | Artemis High Quality v12 |
| alq-10 | Artemis Low Quality v10 |
| alq-12 | Artemis Low Quality v12 |
| alq-13 | Artemis Low Quality v13 |
| alqs-1 | Artemis Strong Dehalo v1 |
| alqs-2 | Artemis Strong Dehalo v2 |
| amq-10 | Artemis Medium Quality v10 |
| amq-12 | Artemis Medium Quality v12 |
| amq-13 | Artemis Medium Quality v13 |
| amqs-1 | Artemis Dehalo v1 |
| amqs-2 | Artemis Dehalo v2 |
| ddv-1 | Dione Interlaced DV v1 |
| ddv-2 | Dione Interlaced DV v2 |
| ddv-3 | Dione Interlaced DV v3 |
| dtd-1 | Dione Interlaced Robust v1 |
| dtd-3 | Dione Interlaced Robust v3 |
| dtd-4 | Dione Interlaced Robust v4 |
| dtds-1 | Dione Interlaced Robust Dehalo v1 |
| dtds-2 | Dione Interlaced Robust Dehalo v2 |
| dtv-1 | Dione Interlaced TV v1 |
| dtv-3 | Dione Interlaced TV v3 |
| dtv-4 | Dione Interlaced TV v4 |
| dtvs-1 | Dione Interlaced Dehalo v1 |
| dtvs-2 | Dione Interlaced Dehalo v2 |
| gcg-5 | Gaia Computer Graphics v5 |
| ghq-5 | Gaia High Quality v5 |
| prap-2 | Proteus Auto-Parameter v2 |
| prob-2 | Proteus 6-Parameter v2 |
| thd-3 | Theia Fine Tune Detail v3 |
| thf-4 | Theia Fine Tune Fidelity v4 |

#### **Interpolation Models**

|  |  |
| --- | --- |
| apo-8 | Apollo v8 |
| apf-1 | Apollo Fast v1 |
| chr-2 | Chronos v2 |
| chf-1 | Chronos Fast v1 |
| chf-2 | Chronos Fast v2 |
| chf-3 | Chronos Fast v3 |
| chr-1 | Chronos Slo-Mo / FPS Conversion v1 |
| chr-2 | Chronos Slo-Mo / FPS Conversion v2 |

#### **Stabilization Models**

|  |  |
| --- | --- |
| cpe-1 | Camera Pose Estimation (first pass) |
| cpe-2 | Camera Pose Estimation (first pass) + rolling shutter correction |
| ref-2 | Stabilization Model (final pass) |

**Additional Information on the Stabilization Models:** To use the stabilization model, there are two commands that need to be run one after another.

Step 1:

```
./ffmpeg -hide_banner -nostdin -y -i /path/to/input_video -vf tvai_cpe=model=cpe-1:filename=temp/path/cpe.json -f null -
```

Step 2 (Full-Frame):

```
./ffmpeg -hide_banner -nostdin -y -i /path/to/input_video -vf tvai_stb=filename=temp/path/cpe.json:smoothness=6:full=1 path/to/output_video
```

Step 2 (Auto-Crop):

```
./ffmpeg -hide_banner -nostdin -y -i /path/to/input_video -vf tvai_stb=filename=temp/path/cpe.json:smoothness=6:full=0 path/to/output_video
```

## Custom Encoder Options

Topaz Video AI uses ffmpeg to produce output files and apply different encoding settings.

While the graphical menu for export options includes some of the more popular encoders and containers, there is a way to add custom settings that can be used for more advanced workflows.

The video-encoders.json file can be modified to add additional options for encoding. This file is found in the 'models' folder on both Windows and macOS versions of Video AI:

Windows macOS Linux

```
C:\ProgramData\Topaz Labs LLC\Topaz Video AI\models
```

```
/Applications/Topaz Video AI.app/Contents/Resources/models
```

```
/opt/TopazVideoAIBETA/models/
```

As an example of a custom encoder option, we will be updating the "H265 Main10 (NVIDIA)" encoder setting to use the 'slow' preset and B-frame referencing for more efficient compression.

Some of these features are only available on certain GPU models, so it's recommended to research which exact encoder features your specific graphics card supports.

* Copy the preset that most closely matches the custom option you'd like to create
  + In this case, "H265 Main10 (NVIDIA)" will be duplicated directly underneath the original in the video-encoders.json file

```
  {
    "text": "H265 Main10 (NVIDIA) - Slow Preset with B-frame referencing",
    "encoder": "-c:v hevc_nvenc -profile:v main10 -preset slow -pix_fmt p010le -b_ref_mode each -tag:v hvc1",
    "ext": [
      "mov",
      "mkv",
      "mp4"
    ],
    "maxBitRate": 2000,
    "transcode": "aac -b:a 320k -ac 2",
    "os": "windows",
    "device": "nvidia",
    "minSize": [129,129],
    "maxSize": [8192,8192],
    "maxBitDepth": 12
  },
```

In addition to options for the video encoder, this json entry can be edited with a different audio transcode setting, maximum bitrate, bit depth, and OS compatibility to prevent settings being shown on incompatible devices.

It is highly recommended to test any custom video-encoders.json entries with a short video and inspect the result using [MediaInfo](https://mediaarea.net/en/MediaInfo) to ensure that the output matches the expected results.

