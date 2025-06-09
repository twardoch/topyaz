#!/usr/bin/env python3
# this_file: src/topyaz/core/types.py
"""
Type definitions and data classes for topyaz.

This module contains all type definitions, data classes, and enums used
throughout the topyaz package for type safety and better code organization.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Type aliases for clarity
FilePath = Path | str
CommandList = list[str]
ConfigDict = dict[str, Any]
ParamDict = dict[str, Any]


class Product(Enum):
    """Enumeration of supported Topaz products.

    Used in:
    - topyaz/cli.py
    - topyaz/core/__init__.py
    - topyaz/products/base.py
    - topyaz/products/gigapixel.py
    - topyaz/products/photo_ai.py
    - topyaz/products/video_ai.py
    - topyaz/system/memory.py
    - topyaz/system/paths.py
    """

    GIGAPIXEL = "gigapixel"
    VIDEO_AI = "video_ai"
    PHOTO_AI = "photo_ai"


class LogLevel(Enum):
    """Logging level enumeration.

    Used in:
    - topyaz/core/__init__.py
    - topyaz/utils/logging.py
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ProcessingOptions:
    """
    Common processing options used across all products.

    These options control general behavior like logging, output handling,
    and execution modes.

    Used in:
    - topyaz/cli.py
    - topyaz/core/__init__.py
    - topyaz/products/base.py
    - topyaz/products/gigapixel.py
    - topyaz/products/photo_ai.py
    - topyaz/products/video_ai.py
    """

    verbose: bool = True
    dry_run: bool = False
    timeout: int = 3600
    parallel_jobs: int = 1
    output_dir: Path | None = None
    preserve_structure: bool = True
    backup_originals: bool = False
    log_level: str = "INFO"


@dataclass
class RemoteOptions:
    """
    Remote execution options for SSH operations.

    These options are used when executing commands on remote machines.

    Used in:
    - topyaz/cli.py
    - topyaz/core/__init__.py
    - topyaz/execution/remote.py
    """

    host: str | None = None
    user: str | None = None
    ssh_key: Path | None = None
    ssh_port: int = 22
    connection_timeout: int = 30


@dataclass
class GigapixelParams:
    """
    Gigapixel AI processing parameters.

    Contains all parameters specific to Gigapixel AI processing operations.

    Used in:
    - topyaz/core/__init__.py
    - topyaz/products/gigapixel.py
    """

    model: str = "std"
    scale: int = 2
    denoise: int | None = None
    sharpen: int | None = None
    compression: int | None = None
    detail: int | None = None
    creativity: int | None = None
    texture: int | None = None
    prompt: str | None = None
    face_recovery: int | None = None
    face_recovery_version: int = 2
    format: str = "preserve"
    quality: int = 95
    bit_depth: int = 0
    parallel_read: int = 1


@dataclass
class VideoAIParams:
    """
    Video AI processing parameters.

    Contains all parameters specific to Video AI processing operations.

    Used in:
    - topyaz/core/__init__.py
    - topyaz/products/video_ai.py
    """

    model: str = "amq-13"
    scale: int = 2
    fps: int | None = None
    codec: str = "hevc_videotoolbox"
    quality: int = 18
    denoise: int | None = None
    details: int | None = None
    halo: int | None = None
    blur: int | None = None
    compression: int | None = None
    stabilize: bool = False
    interpolate: bool = False
    custom_filters: str | None = None
    device: int = 0


@dataclass
class PhotoAIParams:
    """
    Photo AI processing parameters.

    Contains all parameters specific to Photo AI processing operations.

    Used in:
    - topyaz/core/__init__.py
    - topyaz/products/photo_ai.py
    """

    autopilot_preset: str = "default"
    format: str = "preserve"
    quality: int = 95
    compression: int = 2
    bit_depth: int = 16
    tiff_compression: str = "zip"
    show_settings: bool = False
    skip_processing: bool = False
    override_autopilot: bool = False
    upscale: bool | None = None
    noise: bool | None = None
    sharpen: bool | None = None
    lighting: bool | None = None
    color: bool | None = None


@dataclass
class GPUInfo:
    """Information about a GPU device.

    Used in:
    - topyaz/core/__init__.py
    - topyaz/system/gpu.py
    """

    name: str
    type: str  # nvidia, amd, intel, metal
    memory_total_mb: int | None = None
    memory_used_mb: int | None = None
    memory_free_mb: int | None = None
    utilization_percent: int | None = None
    temperature_c: int | None = None
    power_draw_w: float | None = None
    vram: str | None = None  # For Metal GPUs
    device_id: int = 0


@dataclass
class GPUStatus:
    """Overall GPU status and available devices.

    Used in:
    - topyaz/core/__init__.py
    - topyaz/system/gpu.py
    """

    available: bool
    devices: list[GPUInfo] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        """Get number of available GPU devices."""
        return len(self.devices)

    @property
    def total_memory_mb(self) -> int:
        """Get total memory across all GPUs."""
        return sum(device.memory_total_mb for device in self.devices if device.memory_total_mb)


@dataclass
class MemoryConstraints:
    """Memory constraint information and recommendations.

    Used in:
    - topyaz/core/__init__.py
    - topyaz/system/memory.py
    """

    available_gb: float
    total_gb: float
    percent_used: float
    recommendations: list[str] = field(default_factory=list)

    @property
    def is_low(self) -> bool:
        """Check if available memory is critically low."""
        return self.available_gb < 4 or self.percent_used > 90

    @property
    def is_constrained(self) -> bool:
        """Check if memory is constrained for heavy operations."""
        return self.available_gb < 8 or self.percent_used > 85


@dataclass
class BatchInfo:
    """Information about batch processing.

    Used in:
    - topyaz/core/__init__.py
    """

    total_files: int
    batch_size: int
    num_batches: int
    current_batch: int = 0
    processed_files: int = 0
    failed_files: int = 0

    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        total_processed = self.processed_files + self.failed_files
        if total_processed == 0:
            return 100.0
        return (self.processed_files / total_processed) * 100


@dataclass
class ProcessingResult:
    """Result of a processing operation.

    Used in:
    - topyaz/core/__init__.py
    - topyaz/execution/progress.py
    - topyaz/products/base.py
    """

    success: bool
    input_path: Path
    output_path: Path | None = None
    error_message: str | None = None
    processing_time: float = 0.0
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    command: CommandList | None = None
    execution_time: float = 0.0
    file_size_before: int = 0
    file_size_after: int = 0
    additional_info: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemRequirements:
    """System requirements for Topaz products.

    Used in:
    - topyaz/core/__init__.py
    - topyaz/system/environment.py
    """

    min_memory_gb: int = 16
    min_disk_space_gb: int = 80
    min_macos_version: tuple[int, int] = (11, 0)
    required_gpu: bool = True
    gpu_memory_mb: int = 4096  # Minimum GPU memory
