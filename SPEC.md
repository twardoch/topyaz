
# topyaz: Unified Python CLI Wrapper for Topaz Labs Products

## 1. Overview

`topyaz` is a comprehensive Python package that provides a unified command-line interface for Topaz Labs' three flagship products: Video AI, Gigapixel AI, and Photo AI. The package serves as an intelligent wrapper around the native CLI tools provided by Topaz Labs, offering both local and remote execution capabilities via SSH. The tool is designed to be robust, user-friendly, and production-ready for batch processing workflows.

## 2. Architecture and Design Philosophy

### 2.1. Core Design Principles

1. **Unified Interface**: A single Python class with consistent CLI options across all three Topaz products
2. **Remote Execution Support**: Native SSH and macOS remote execution capabilities
3. **Failsafe Operation**: Comprehensive error handling, validation, and recovery mechanisms
4. **Detailed Feedback**: Verbose logging and progress reporting for all operations
5. **Production Ready**: Designed for automated workflows and batch processing

### 2.2. Implementation Strategy

The package implements a unified class structure using Python Fire for automatic CLI generation. The main class `topyazWrapper` serves as the entry point, with specialized methods for each Topaz product (`photo`, `video`, `gp` for Gigapixel). The design emphasizes parameter consistency while accommodating product-specific requirements.

## 3. Package Structure and Implementation

### 3.1. Python Package Structure

The topyaz package follows standard Python packaging conventions with the following structure:

```
topyaz/
├── src/topyaz/               # Main package source code
│   ├── __init__.py          # Package initialization and exports
│   ├── __main__.py          # CLI entry point
│   ├── cli.py               # Main topyazWrapper class (simplified)
│   ├── core/                # Core infrastructure
│   │   ├── __init__.py
│   │   ├── errors.py        # Custom exception hierarchy
│   │   ├── types.py         # Type definitions and dataclasses
│   │   └── config.py        # Configuration management
│   ├── system/              # System components
│   │   ├── __init__.py
│   │   ├── environment.py   # Environment validation
│   │   ├── gpu.py           # Multi-platform GPU detection
│   │   ├── memory.py        # Memory management and optimization
│   │   └── paths.py         # Path validation and utilities
│   ├── execution/           # Command execution layer
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract executor interfaces
│   │   ├── local.py         # Local command execution
│   │   ├── remote.py        # SSH remote execution
│   │   └── progress.py      # Progress monitoring utilities
│   ├── products/            # Product implementations
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract product interfaces
│   │   ├── gigapixel.py     # Gigapixel AI implementation
│   │   ├── video_ai.py      # Video AI implementation
│   │   └── photo_ai.py      # Photo AI implementation
│   ├── utils/               # Utility modules
│   │   ├── __init__.py
│   │   └── logging.py       # Centralized logging configuration
│   ├── __version__.py       # Dynamic version from git tags (generated)
│   └── py.typed             # Type hints marker file
├── tests/                   # Test suite
│   ├── test_package.py      # Basic package tests
│   ├── test_refactoring.py  # Refactoring validation tests
│   └── test_*.py           # Additional test modules
├── pyproject.toml          # Project configuration and dependencies
├── README.md               # Package documentation
├── SPEC.md                # Technical specification
├── TODO.md                # Implementation roadmap
├── PLAN.md                # Implementation phases
├── CHANGELOG.md           # Change history
└── CLAUDE.md              # Development instructions
```

### 3.2. Modular Architecture (Refactored from monolithic topyaz.py)

The topyaz package has been refactored from a single 1750+ line monolithic file into a clean, modular architecture with 18+ focused modules. This provides excellent maintainability, testability, and extensibility.

#### 3.2.1. Core Infrastructure (`src/topyaz/core/`)

**Errors Module (`core/errors.py`)**
```python
class TopazError(Exception):
    """Base exception for all topyaz errors."""
    pass

class AuthenticationError(TopazError):
    """Authentication-related errors."""
    pass

class EnvironmentError(TopazError):
    """Environment validation errors."""
    pass

class ProcessingError(TopazError):
    """Processing-related errors."""
    pass

class RemoteExecutionError(TopazError):
    """Remote execution errors."""
    pass
```

**Type Definitions (`core/types.py`)**
```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

class Product(Enum):
    """Supported Topaz products."""
    VIDEO_AI = "video_ai"
    GIGAPIXEL_AI = "gigapixel"
    PHOTO_AI = "photo_ai"

class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

@dataclass
class ProcessingOptions:
    """Common processing options across all products."""
    verbose: bool = True
    dry_run: bool = False
    timeout: int = 3600
    parallel_jobs: int = 1
    output_dir: Path | None = None
    preserve_structure: bool = True
    backup_originals: bool = False

@dataclass
class RemoteOptions:
    """Remote execution configuration."""
    host: str | None = None
    user: str | None = None
    ssh_key: Path | None = None
    ssh_port: int = 22
    connection_timeout: int = 30

@dataclass
class ProcessingResult:
    """Result of a processing operation."""
    success: bool
    output_path: Path | None = None
    error_message: str | None = None
    processing_time: float = 0.0
    files_processed: int = 0
    files_failed: int = 0
```

**Configuration Management (`core/config.py`)**
```python
class Config:
    """Centralized configuration management with YAML support."""
    
    def __init__(self, config_file: Path | None = None):
        self.config_file = config_file or Path.home() / ".topyaz" / "config.yaml"
        self.config = self._load_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support."""
        # Supports nested keys like "video.default_model"
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value with dot notation support."""
        
    def save(self) -> None:
        """Save configuration to YAML file."""
```

#### 3.2.2. System Components (`src/topyaz/system/`)

**Environment Validation (`system/environment.py`)**
```python
class EnvironmentValidator:
    """Validates system requirements and environment."""
    
    def validate_all(self, raise_on_error: bool = True) -> dict[str, bool]:
        """Validate all system requirements."""
        
    def validate_macos_version(self) -> bool:
        """Validate macOS version compatibility."""
        
    def validate_memory(self, required_gb: int = 16) -> bool:
        """Validate available memory."""
        
    def validate_disk_space(self, required_gb: int = 80) -> bool:
        """Validate available disk space."""
```

**GPU Detection (`system/gpu.py`)**
```python
class GPUManager:
    """Multi-platform GPU detection and monitoring."""
    
    def get_status(self, use_cache: bool = True) -> GPUStatus:
        """Get current GPU status and utilization."""
        
    def get_available_devices(self) -> list[GPUDevice]:
        """Get list of available GPU devices."""
```

**Memory Management (`system/memory.py`)**
```python
class MemoryManager:
    """Memory constraint checking and batch optimization."""
    
    def get_optimal_batch_size(self, file_count: int, operation_type: str | Product = "processing") -> int:
        """Calculate optimal batch size based on available memory."""
        
    def check_constraints(self, operation_type: str = "processing") -> dict[str, Any]:
        """Check current memory constraints and provide recommendations."""
```

#### 3.2.3. Execution Layer (`src/topyaz/execution/`)

**Base Executor Interface (`execution/base.py`)**
```python
class CommandExecutor(ABC):
    """Abstract base class for command execution."""
    
    @abstractmethod
    def execute(self, command: CommandList, input_data: str | None = None) -> tuple[int, str, str]:
        """Execute a command and return (returncode, stdout, stderr)."""
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this executor is available."""
        pass

class ProgressAwareExecutor(CommandExecutor):
    """Base class for executors that support progress monitoring."""
    
    @abstractmethod
    def execute_with_progress(
        self, command: CommandList, callback: ProgressCallback, **kwargs
    ) -> tuple[int, str, str]:
        """Execute command with progress monitoring."""
        pass
```

**Local Execution (`execution/local.py`)**
```python
class LocalExecutor(ProgressAwareExecutor):
    """Executes commands locally with progress monitoring."""
    
    def execute_with_progress(self, command: CommandList, callback: ProgressCallback) -> tuple[int, str, str]:
        """Execute command locally with real-time progress monitoring."""
```

**Remote Execution (`execution/remote.py`)**
```python
class RemoteExecutor(ProgressAwareExecutor):
    """Executes commands on remote machines via SSH."""
    
    def __init__(self, remote_options: RemoteOptions, context: Optional[ExecutorContext] = None):
        """Initialize with SSH connection options and context."""
        
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to remote host via SFTP."""
        
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file from remote host via SFTP."""
```

#### 3.2.4. Product Implementations (`src/topyaz/products/`)

**Base Product Interface (`products/base.py`)**
```python
class TopazProduct(ABC):
    """Abstract base class for all Topaz products."""
    
    @abstractmethod
    def process(self, input_path: Path | str, output_path: Path | str | None = None, **kwargs) -> ProcessingResult:
        """Process files with this product."""
        pass
        
    @abstractmethod
    def validate_params(self, **kwargs) -> None:
        """Validate product-specific parameters."""
        pass
        
    @abstractmethod
    def find_executable(self) -> Path | None:
        """Find the product executable."""
        pass

class MacOSTopazProduct(TopazProduct):
    """Base class for macOS-specific Topaz products."""
    
    def validate_macos_environment(self) -> None:
        """Validate macOS-specific requirements."""
```

**Gigapixel AI Implementation (`products/gigapixel.py`)**
```python
class GigapixelAI(MacOSTopazProduct):
    """Topaz Gigapixel AI implementation with CLI support."""
    
    def build_command(self, input_path: Path, output_path: Path, **kwargs) -> CommandList:
        """Build gigapixel CLI command with all parameters."""
        
    def validate_pro_license(self) -> bool:
        """Validate Pro license requirement for CLI access."""
```

**Video AI Implementation (`products/video_ai.py`)**
```python
class VideoAI(MacOSTopazProduct):
    """Topaz Video AI implementation using FFmpeg."""
    
    def _setup_environment(self) -> None:
        """Set up Video AI environment variables."""
        os.environ["TVAI_MODEL_DIR"] = model_dir
        os.environ["TVAI_MODEL_DATA_DIR"] = data_dir
        
    def build_ffmpeg_command(self, input_path: Path, output_path: Path, **kwargs) -> CommandList:
        """Build FFmpeg command with Video AI filters."""
```

**Photo AI Implementation (`products/photo_ai.py`)**
```python
class PhotoAI(MacOSTopazProduct):
    """Topaz Photo AI implementation with batch handling."""
    
    MAX_BATCH_SIZE = 400  # Conservative limit for Photo AI
    
    def process_batch_directory(self, input_dir: Path, output_dir: Path, **kwargs) -> list[ProcessingResult]:
        """Handle Photo AI's ~450 image batch limit with automatic batching."""
```

#### 3.2.5. Unified CLI Interface (`src/topyaz/cli.py`)

```python
class topyazWrapper:
    """Unified wrapper that delegates to specialized components."""
    
    def __init__(self, **kwargs):
        # Parse options into structured data classes
        self.options = ProcessingOptions(**kwargs)
        self.remote_options = RemoteOptions(**kwargs)
        
        # Initialize components
        self.config = Config(kwargs.get('config_file'))
        self.env_validator = EnvironmentValidator()
        self.gpu_manager = GPUManager()
        self.memory_manager = MemoryManager()
        
        # Set up executor based on options
        if self.remote_options.host:
            self.executor = RemoteExecutor(self.remote_options)
        else:
            self.executor = LocalExecutor(ExecutorContext(
                timeout=self.options.timeout,
                dry_run=self.options.dry_run
            ))
        
        # Initialize products with dependency injection
        self.gigapixel = GigapixelAI(self.executor, self.options)
        self.video_ai = VideoAI(self.executor, self.options)
        self.photo_ai = PhotoAI(self.executor, self.options)
    
    def gp(self, input_path: str, **kwargs) -> bool:
        """Process with Gigapixel AI - delegates to GigapixelAI class."""
        return self.gigapixel.process(Path(input_path), **kwargs).success
    
    def video(self, input_path: str, **kwargs) -> bool:
        """Process with Video AI - delegates to VideoAI class."""
        return self.video_ai.process(Path(input_path), **kwargs).success
    
    def photo(self, input_path: str, **kwargs) -> bool:
        """Process with Photo AI - delegates to PhotoAI class."""
        return self.photo_ai.process(Path(input_path), **kwargs).success
```

### 3.3. Product-Specific Methods

#### 3.3.1. Video AI Method
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

#### 3.3.2. Gigapixel AI Method
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

#### 3.3.3. Photo AI Method
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

## 4. Feature Implementation Details

### 4.1. Remote Execution Architecture

The remote execution system supports both traditional SSH and native macOS mechanisms for running Topaz tools on remote machines. This is particularly valuable for offloading processing to more powerful machines or distributed processing workflows.

#### 4.1.1. SSH Implementation
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

#### 4.1.2. macOS Native Remote Execution
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

### 4.2. Input Validation and Error Handling

The package implements comprehensive validation for all input parameters, file paths, and system requirements. Error handling covers common issues identified in the research:

#### 4.2.1. Authentication Validation
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

#### 4.2.2. Environment Validation
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

#### 4.2.3. File and Path Validation
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

### 4.3. Progress Monitoring and Logging

The package provides detailed progress monitoring and logging capabilities, essential for long-running batch operations.

#### 4.3.1. Progress Tracking
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

#### 4.3.2. Logging System
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

## 5. Command Line Interface Design

The CLI design emphasizes usability and consistency across all three Topaz products while accommodating their unique requirements.

### 5.1. Basic Usage Examples

#### 5.1.1. Video Processing
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

#### 5.1.2. Image Processing with Gigapixel AI
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

#### 5.1.3. Photo AI Batch Processing
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

### 5.2. Advanced Workflow Examples

#### 5.2.1. Multi-Stage Processing Pipeline
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

#### 5.2.2. Distributed Processing
```bash
# Split large batch across multiple machines
topyaz gp large_photo_collection/ \
    --remote-host server1,server2,server3 \
    --parallel-jobs 3 \
    --scale 2 \
    --load-balance
```

## 6. Configuration and Settings Management

### 6.1. Configuration File Support
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

### 6.2. Environment Variable Support
```bash
# Environment variables for common settings
export topyaz_DEFAULT_OUTPUT="~/processed"
export topyaz_REMOTE_HOST="gpu-server.local"
export topyaz_LOG_LEVEL="DEBUG"
export topyaz_BACKUP_ORIGINALS="true"
```

## 7. Error Handling and Recovery

### 7.1. Comprehensive Error Detection
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

### 7.2. Recovery Mechanisms
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

### 7.3. Resumable Operations
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

## 8. Performance Optimization

### 8.1. Parallel Processing Support
The package implements intelligent parallel processing that respects the limitations of each Topaz product:

- **Video AI**: Sequential processing with optimal FFmpeg parameters
- **Gigapixel AI**: Parallel image loading with memory constraints
- **Photo AI**: Batch size optimization based on available memory

### 8.2. Hardware Detection and Optimization
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

### 8.3. Memory Management
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

## 9. Testing and Validation

### 9.1. Unit Test Coverage
The package includes comprehensive unit tests covering:

- All CLI parameter combinations
- Error handling scenarios
- Remote execution functionality
- File handling and validation
- Progress monitoring accuracy

### 9.2. Integration Tests
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

### 9.3. Validation Scripts
```bash
# Validation script for system requirements
topyaz validate --check-licenses --check-environment --check-connectivity

# Performance benchmarking
topyaz benchmark --test-local --test-remote --generate-report
```

## 10. Documentation and User Guidance

### 10.1. Comprehensive Help System
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

### 10.2. Interactive Setup Wizard
```bash
# Initial setup and configuration
topyaz setup --interactive

# Remote host configuration
topyaz setup --add-remote-host

# License and authentication verification
topyaz setup --verify-licenses
```

## 11. Installation and Dependencies

### 11.1. Package Requirements

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

### 11.2. Installation Methods
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

### 11.3. System Requirements
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

## 12. Security Considerations

### 12.1. SSH Security
- Support for SSH key-based authentication only
- No password storage or transmission
- SSH connection validation and host key verification
- Secure file transfer protocols

### 12.2. File Security
- Input validation to prevent path traversal attacks
- Safe temporary file handling
- Backup verification and integrity checks
- Secure cleanup of temporary files

### 12.3. Remote Execution Security
- Command injection prevention
- Environment variable sanitization
- Restricted command execution scope
- Audit logging for all remote operations

## 13. Community Tools Integration

### 13.1. Existing Community Projects
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

### 13.2. Integration Capabilities
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

## 14. Future Enhancements

### 14.1. Planned Features
1. **GUI Integration**: Optional web-based monitoring interface
2. **Cloud Processing**: Integration with cloud GPU services (AWS, GCP, Azure)
3. **Plugin System**: Extensible architecture for custom processing workflows
4. **API Server**: REST API for integration with other applications
5. **Distributed Processing**: Native distributed computing support across multiple machines
6. **Machine Learning**: Intelligent parameter optimization based on content analysis
7. **Docker Support**: Native containerization for cross-platform deployment
8. **Workflow Designer**: Visual pipeline designer for complex processing chains

### 14.2. Community Integration
- GitHub repository with issue tracking and feature requests
- Community-contributed presets and workflows repository
- Plugin marketplace for extensions and custom integrations
- Documentation contributions and example workflows
- Community model and parameter sharing
- Integration with existing Topaz community forums and resources

## 15. Support and Troubleshooting

### 15.1. Built-in Diagnostics
```bash
# System diagnostic report
python -m topyaz diagnose --full-report

# Performance analysis  
python -m topyaz profile --operation video --input sample.mp4

# License verification
python -m topyaz license-check --all-products
```

### 15.2. Development Commands

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

### 15.3. Common Issue Resolution
The package includes automated detection and resolution guidance for common issues:

1. **"No such filter" errors**: Automatic Topaz FFmpeg detection
2. **Authentication failures**: Step-by-step re-authentication guidance
3. **Memory errors**: Automatic batch size reduction suggestions
4. **Permission errors**: Path and permission troubleshooting
5. **Remote connection issues**: Network diagnostic and troubleshooting tools

This specification provides a comprehensive foundation for implementing `topyaz` as a production-ready, user-friendly wrapper around Topaz Labs CLI tools, with extensive error handling, remote execution capabilities, and detailed user feedback throughout all operations.

# Appendix 1: Reference for Topaz CLI tools

## 16. Topaz Gigapixel AI

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

#### 16.0.1. Notes

*Updated May 21st, 2025
Command line flags subject to change.*

After install, you should be able to access it from the command line/powershell/terminal by typing in **gigapixel** (or **gigapixel-alpha/gigapixel-beta** depending on release type) as the command.

With no arguments, this should print a usage dialog.

The following examples are written with UNIX-style escape characters. Windows users may need to edit these commands to follow CMD/PowerShell formatting.

---

#### 16.0.2. Basics

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

#### 16.0.3. Generative Models

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

#### 16.0.4. Examples

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



## 17. Topaz Photo AI

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

## 18. Processing Controls

The CLI will use your Autopilot settings to process images. Open Topaz Photo AI and go to the Preferences > Autopilot menu.

Instructions on using the Preferences > Autopilot menu are [here](https://docs.topazlabs.com/photo-ai/enhancements/autopilot-and-configuration).

### 18.1. Command Options

--output, -o: Output folder to save images to. If it doesn't exist the program will attempt to create it.

--overwrite: Allow overwriting of files. THIS IS DESTRUCTIVE.

--recursive, -r: If given a folder path, it will recurse into subdirectories instead of just grabbing top level files.
Note: If output folder is specified, the input folder's structure will be recreated within the output as necessary.

### 18.2. File Format Options:

--format, -f: Set the output format. Accepts jpg, jpeg, png, tif, tiff, dng, or preserve. Default: preserve
Note: Preserve will attempt to preserve the exact input extension, but RAW files will still be converted to DNG.Format Specific Options:

--quality, -q: JPEG quality for output. Must be between 0 and 100. Default: 95

--compression, -c: PNG compression amount. Must be between 0 and 10. Default: 2

--bit-depth, -d: TIFF bit depth. Must be either 8 or 16. Default: 16

--tiff-compression: -tc: TIFF compression format. Must be "none", "lzw", or "zip".
Note: lzw is not allowed on 16-bit output and will be converted to zip.

### 18.3. Debug Options:

--showSettings: Shows the Autopilot settings for images before they are processed

--skipProcessing: Skips processing the image (e.g., if you just want to know the settings)

--verbose, -v: Print more log entries to console.

Return values:
0 - Success
1 - Partial Success (e.g., some files failed)
-1 (255) - No valid files passed.
-2 (254) - Invalid log token. Open the app normally to login.
-3 (253) - An invalid argument was found.




## 19. Topaz Video AI

Topaz Video AI in CLI operates with help of `ffmpeg`. 


Topaz Video AI supports executing scripts using a command line interface.

This is designed for advanced users comfortable working in such an environment and offers more flexibility in customizing a variety of scripted processes.

We highly recommend using the app’s user interface for those not comfortable working in a command terminal.

The majority of the commands for this build will be FFmpeg commands.

There is no need to install FFmpeg, it is automatically included with the TVAI installer. This article will outline the basic functions for TVAI’s CLI, however, you will want to familiarize yourself with FFmpeg commands for more complex use cases.

### 19.1. Getting Started with CLI

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

### 19.2. Basic TVAI Filters

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

### 19.3. Video AI Command Line Usage

#### 19.3.1. Environment Variables

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

### 19.4. GPU-Specific Usage Notes

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

#### 19.4.1. General Usage

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

### 19.5. Selecting Models with CLI

#### 19.5.1. Scaling Models

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

#### 19.5.2. **Interpolation Models**

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

#### 19.5.3. **Stabilization Models**

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

## 20. Custom Encoder Options

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


# Appendix 2: Assorted code samples

Here are some assorted code samples that are useful for the project.

Excellent. Based on the provided `vendor.txt` code assortment and the `SPEC.md` for `topyaz`, here is the new appendix to be added to the specification. It includes the best implementation excerpts and code snippets for locating and running Topaz tools, as requested.

***

# Appendix B: Implementation Reference from Community Tools

This appendix provides practical code excerpts and implementation patterns derived from the provided `vendor.txt`. These snippets serve as a reference for implementing the core functionalities of `topyaz`, such as locating executables, executing commands, and managing processing workflows.

## 21. Locating Topaz Executables

A robust wrapper must reliably find the Topaz command-line tools across different operating systems. The `init_topaz` function from `Comfy-Topaz-Photo/topaz.py` provides an excellent, comprehensive example of how to achieve this for Photo AI. This pattern can be adapted for Video AI and Gigapixel AI.

**Key Features:**
*   Checks a user-provided custom path first.
*   Includes standard installation paths for Windows, macOS, and Linux.
*   Executes the tool with `--version` to confirm it's working and to log the version information.
*   Provides graceful error handling.

```python
# From: Comfy-Topaz-Photo/topaz.py

def init_topaz(custom_path=None):
    """
    Initializes Topaz Photo AI by finding its executable.

    Args:
        custom_path (str, optional): A user-specified path to tpai.exe.

    Returns:
        (str, str): A tuple containing the executable path and its version.
    """
    # If a custom path is provided, check it first.
    if custom_path and os.path.isfile(custom_path):
        try:
            result = subprocess.run(
                f'"{custom_path}" --version',
                shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore'
            )
            version = result.stdout.strip() if result.returncode == 0 else "Unknown Version"
            print(f"[topyaz] Using custom Topaz Photo AI path: {custom_path} (Version: {version})")
            return (custom_path, version)
        except Exception as e:
            print(f"[topyaz] Warning: Found Topaz Photo AI but couldn't get version: {custom_path}, Error: {e}")
            return (custom_path, "Unknown Version")

    # Standard paths for different operating systems
    executable_paths = []
    if platform.system() == "Windows":
        paths = [
            os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Topaz Labs LLC', 'Topaz Photo AI', 'tpai.exe'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Topaz Labs LLC', 'Topaz Photo AI', 'tpai.exe'),
        ]
        executable_paths.extend(paths)
    elif platform.system() == "Darwin": # macOS
        paths = [
            '/Applications/Topaz Photo AI.app/Contents/MacOS/tpai',
            os.path.expanduser('~/Applications/Topaz Photo AI.app/Contents/MacOS/tpai')
        ]
        executable_paths.extend(paths)
    
    # Check each potential path
    for path in executable_paths:
        if os.path.isfile(path):
            try:
                result = subprocess.run(f'"{path}" --version', shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                version = result.stdout.strip() if result.returncode == 0 else "Unknown Version"
                print(f"[topyaz] Found Topaz Photo AI: {path} (Version: {version})")
                return (path, version)
            except Exception as e:
                print(f"[topyaz] Warning: Found Topaz Photo AI but couldn't get version: {path}, Error: {e}")
                return (path, "Unknown Version")

    raise FileNotFoundError("Could not find Topaz Photo AI executable. Please specify the path or ensure it's installed correctly.")
```

## 22. Executing Topaz CLI Commands

### 22.1. Topaz Photo AI (`tpai`)

The `topaz_upscale` method in `Comfy-Topaz/topaz.py` demonstrates how to build and execute a command for `tpai.exe` with multiple, complex parameter groups.

**Key Features:**
*   Dynamically builds a list of command-line arguments.
*   Handles multiple parameter groups (`--upscale`, `--sharpen`).
*   Toggles features using `enabled=true/false`.
*   Captures and logs stdout and stderr from the subprocess.

```python
# From: Comfy-Topaz/topaz.py

def topaz_upscale(self, img_file, compression=0, format='png', tpai_exe=None,
                  upscale: Optional[TopazUpscaleSettings]=None,
                  sharpen: Optional[TopazSharpenSettings]=None):
    if not os.path.exists(tpai_exe):
        raise ValueError('Topaz AI Upscaler not found at %s' % tpai_exe)
    
    target_dir = os.path.join(self.output_dir, self.subfolder)
    tpai_args = [
        tpai_exe,
        '--output', target_dir,
        '--compression', str(compression),
        '--format', format,
        '--showSettings',
    ]
    
    if upscale:
        tpai_args.append('--upscale')
        if upscale.enabled:
            tpai_args.append(f'scale={upscale.scale}')
            tpai_args.append(f'param1={upscale.denoise}') # Minor Denoise
            tpai_args.append(f'param2={upscale.deblur}')  # Minor Deblur
            tpai_args.append(f'param3={upscale.detail}')  # Fix Compression
            tpai_args.append(f'model={upscale.model}')
        else:
            tpai_args.append('enabled=false')
            
    if sharpen:
        tpai_args.append('--sharpen')
        if sharpen.enabled:
            tpai_args.append(f'model=Sharpen {sharpen.model}')
            tpai_args.append(f'param1={sharpen.strength}')
            tpai_args.append(f'param2={sharpen.denoise}')
        else:
            tpai_args.append('enabled=false')
        
    tpai_args.append(img_file)
    print('[topyaz] Executing command:', pprint.pformat(tpai_args))
    p_tpai = subprocess.run(tpai_args, capture_output=True, text=True, shell=False)
    print('[topyaz] Return code:', p_tpai.returncode)
    print('[topyaz] STDOUT:', p_tpai.stdout)
    print('[topyaz] STDERR:', p_tpai.stderr)

    # ... (output parsing follows)
```

### 22.2. Topaz Video AI (`ffmpeg`)

Processing with Video AI is done via `ffmpeg` using custom filters (`tvai_up`, `tvai_fi`). The `process_video` method in `ComfyUI-TopazVideoAI/topaz_video_node.py` shows how to construct a complex filter chain.

**Key Features:**
*   Builds a video filter chain (`-vf`) by joining multiple filter strings.
*   Demonstrates chaining enhancements like upscaling (`tvai_up`) and frame interpolation (`tvai_fi`).
*   Sets hardware acceleration and encoder-specific options (`hevc_nvenc`).
*   Handles multiple input/output stages by chaining `ffmpeg` commands.

```python
# From: ComfyUI-TopazVideoAI/topaz_video_node.py

def process_video(self, images, enable_upscale, upscale_factor, upscale_model, ...):
    
    # ... (input video is created from image batch) ...
    
    current_input = input_video
    current_output = intermediate_video

    if enable_upscale:
        # Example for building a filter chain
        upscale_filters = []
        # In a loop for multi-pass processing:
        upscale_filters.append(
            f"tvai_up=model={params['upscale_model']}"
            f":scale={params['upscale_factor']}"
            f":compression={params['compression']}"
            f":blend={params['blend']}"
        )
        filter_chain = ','.join(upscale_filters)
        
        ffmpeg_exe = self._get_topaz_ffmpeg_path(...)
        cmd = [
            ffmpeg_exe, "-y", "-i", current_input,
            "-vf", filter_chain,
            "-c:v", "hevc_nvenc", # Hardware encoding
            # ... other encoder options ...
            current_output
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg upscale error: {result.stderr}")
        
        current_input = current_output
        current_output = output_video

    if enable_interpolation:
        interpolation_filter = f"tvai_fi=model={interpolation_model}:fps={target_fps}"
        cmd = [
            ffmpeg_exe, "-y", "-i", current_input,
            "-vf", interpolation_filter,
            # ... other options ...
            current_output
        ]
        # ... run subprocess ...
```

### 22.3. Topaz Gigapixel AI (GUI Automation)

When a proper CLI is unavailable or requires a costly license, GUI automation is a viable alternative. The `Gigapixel` class in `Gigapixel/gigapixel/gigapixel.py` uses `pywinauto` to control the application on Windows. This approach is fragile but effective.

**Key Features:**
*   Connects to a running instance or starts a new one.
*   Uses keyboard shortcuts (`send_keys`) for common actions like Open (`^o`) and Save (`^s`).
*   Interacts with UI elements by title and control type.
*   Uses retry logic (`the_retry` decorator) to handle timing issues in the GUI.

```python
# From: Gigapixel/gigapixel/gigapixel.py
# Note: This uses pywinauto for GUI automation, not a direct CLI.

class Gigapixel:
    class _App:
        def __init__(self, app: Application, processing_timeout: int):
            # ...
            self.app = app
            self._main_window = self.app.window()
            # ...

        @retry(...)
        def open_photo(self, photo_path: Path) -> None:
            while photo_path.name not in self._main_window.element_info.name:
                logger.debug("Trying to open photo")
                self._main_window.set_focus()
                send_keys('{ESC}^o') # Send Escape, then Ctrl+O
                clipboard.copy(str(photo_path))
                send_keys('^v {ENTER}{ESC}') # Paste path, press Enter, press Escape
                
        def save_photo(self) -> None:
            self._open_export_dialog()
            send_keys('{ENTER}')
            # ... wait for processing to finish ...
            self._close_export_dialog()

        def set_processing_options(self, scale: Optional[Scale] = None, mode: Optional[Mode] = None) -> None:
            if scale:
                self._main_window.child_window(title=scale.value).click_input()
            if mode:
                self._main_window.child_window(title=mode.value).click_input()
```

## 23. Workflow Patterns and Best Practices

### 23.1. Temporary File Management

Workflows should be atomic and clean up after themselves. The `process_images` method from `Comfy-Topaz-Photo/topaz.py` shows a standard pattern of creating temporary input files and a temporary output directory, then cleaning them up in a `finally` block.

```python
# From: Comfy-Topaz-Photo/topaz.py

def process_images(self, images, tpai_exe, ...):
    # Create a unique temporary output folder for this run
    output_folder = tempfile.mkdtemp(prefix="topaz_output_")
    input_paths = []

    try:
        # Save input images from memory (e.g., tensors) to temporary files
        timestamp = int(time.time())
        file_prefix = f"{output_prefix}{timestamp}_"
        input_paths = save_images(images, file_prefix=file_prefix)
        
        # Call Topaz Photo AI, which writes to output_folder
        output_paths = process_topaz_image(...)
        
        # Load the processed images back into memory
        upscaled_images = []
        for upscaled_path in output_paths:
            # ... load image ...
            upscaled_images.append(img_tensor)
        
        return (result,)
    
    finally:
        # Ensure cleanup of all temporary files and directories
        for path in input_paths:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
```

### 23.2. Parsing CLI Output

When tools provide structured output (like JSON), it can be parsed to extract valuable information. The `get_settings` function from `Comfy-Topaz/topaz.py` shows a clever way to isolate a JSON object from noisy `stdout` text.

```python
# From: Comfy-Topaz/topaz.py

def get_settings(self, stdout):
    '''
    Extracts the settings JSON string from the stdout of the tpai.exe process
    '''        
    # Find the start of the settings block
    settings_start = stdout.find('Final Settings for')
    # Find the first opening brace after that
    settings_start = stdout.find('{', settings_start)
    
    # Count braces to find the end of the JSON object
    count = 0
    settings_end = settings_start
    for i in range(settings_start, len(stdout)):            
        if stdout[i] == '{':
            count += 1
        elif stdout[i] == '}':
            count -= 1
        if count == 0:
            settings_end = i
            break
            
    settings_json = str(stdout[settings_start : settings_end + 1])
    settings = json.loads(settings_json)
    
    # ... further processing of the parsed settings ...
    return user_settings_json, autopilot_settings_json
```

### 23.3. Handling File Output and Retries

External tools may not always produce predictable output filenames or might fail intermittently. The `process_topaz_image` logic in `Comfy-Topaz-Photo/topaz.py` demonstrates a robust way to handle this with retries and dynamic output file discovery.

```python
# From: Comfy-Topaz-Photo/topaz.py

def process_topaz_image(tpai_exe, input_images, ...):
    # ...
    output_images = []
    max_retries = 2
    
    for input_path in input_images:
        # ...
        
        # Record file list before processing to detect new files
        before_files = set(os.listdir(output_folder))
        
        for retry in range(max_retries + 1):
            try:
                result = subprocess.run(...) # Execute command
                
                if result.returncode == 0:
                    # Attempt 1: Find by predictable name
                    output_file = find_output_file(input_path, output_folder, output_format)
                    if output_file:
                        output_images.append(output_file)
                        break

                    # Attempt 2: Find any new file created in the output folder
                    after_files = set(os.listdir(output_folder))
                    new_files = after_files - before_files
                    if new_files:
                        # ... get the latest new file ...
                        output_images.append(output_path)
                        break
                    else:
                        # Handle case where command succeeds but no file is found
                        raise TopazError("Topaz Photo AI may have processed successfully but no output file was detected")
                else:
                    # Handle command failure
                    error_msg = f"Processing failed: {result.stderr}"
                    if retry < max_retries:
                        time.sleep(2) # Wait before retrying
                    else:
                        raise TopazError(error_msg)
            
            except (subprocess.TimeoutExpired, Exception) as e:
                # Handle timeouts and other exceptions with retry logic
                # ...
```

