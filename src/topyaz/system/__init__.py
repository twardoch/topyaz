#!/usr/bin/env python3
# this_file: src/topyaz/system/__init__.py
"""
System module for topyaz.

This module contains system-level utilities for environment validation,
GPU detection, memory management, and path handling.
"""

from topyaz.system.environment import EnvironmentValidator
from topyaz.system.gpu import (
    AMDGPUDetector,
    GPUDetector,
    GPUManager,
    IntelGPUDetector,
    MetalGPUDetector,
    NvidiaGPUDetector,
)
from topyaz.system.memory import MemoryManager
from topyaz.system.paths import PathManager, PathValidator

__all__ = [
    "AMDGPUDetector",
    # Environment
    "EnvironmentValidator",
    # GPU
    "GPUDetector",
    "GPUManager",
    "IntelGPUDetector",
    # Memory
    "MemoryManager",
    "MetalGPUDetector",
    "NvidiaGPUDetector",
    "PathManager",
    # Paths
    "PathValidator",
]
