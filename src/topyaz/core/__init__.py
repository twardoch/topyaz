#!/usr/bin/env python3
# this_file: src/topyaz/core/__init__.py
"""
Core module for topyaz.

This module contains fundamental components like configuration management,
error definitions, and type declarations.
"""

from topyaz.core.config import Config
from topyaz.core.errors import (
    AuthenticationError,
    EnvironmentError,
    ExecutableNotFoundError,
    ProcessingError,
    RemoteExecutionError,
    TopazError,
    ValidationError,
)
from topyaz.core.types import (
    BatchInfo,
    ConfigDict,
    GigapixelParams,
    GPUInfo,
    GPUStatus,
    LogLevel,
    MemoryConstraints,
    PhotoAIParams,
    ProcessingOptions,
    ProcessingResult,
    Product,
    RemoteOptions,
    SystemRequirements,
    VideoAIParams,
)

__all__ = [
    "AuthenticationError",
    "BatchInfo",
    # Config
    "Config",
    "ConfigDict",
    "EnvironmentError",
    "ExecutableNotFoundError",
    "GPUInfo",
    "GPUStatus",
    "GigapixelParams",
    "LogLevel",
    "MemoryConstraints",
    "PhotoAIParams",
    "ProcessingError",
    "ProcessingOptions",
    "ProcessingResult",
    # Types
    "Product",
    "RemoteExecutionError",
    "RemoteOptions",
    "SystemRequirements",
    # Errors
    "TopazError",
    "ValidationError",
    "VideoAIParams",
]
