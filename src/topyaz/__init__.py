#!/usr/bin/env python3
# this_file: src/topyaz/__init__.py
"""
topyaz: Unified Python CLI wrapper for Topaz Labs products.

This package provides a unified command-line interface for Topaz Video AI,
Gigapixel AI, and Photo AI products with support for local and remote execution.
"""

try:
    from topyaz.__version__ import __version__
except ImportError:
    __version__ = "0.1.0-dev"

from topyaz.cli import TopyazCLI
from topyaz.core.errors import (
    AuthenticationError,
    ExecutableNotFoundError,
    ProcessingError,
    RemoteExecutionError,
    TopazError,
    TopyazEnvironmentError,  # Renamed
    ValidationError,
)

__all__ = [
    "AuthenticationError",
    "ExecutableNotFoundError",
    "ProcessingError",
    "RemoteExecutionError",
    "TopazError",
    "TopyazCLI",
    "TopyazEnvironmentError",  # Renamed
    "ValidationError",
    "__version__",
]
