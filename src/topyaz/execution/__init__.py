#!/usr/bin/env python3
# this_file: src/topyaz/execution/__init__.py
"""
Execution module for topyaz.

This module contains components for executing commands locally and remotely,
with support for progress monitoring and error handling.
"""

from topyaz.execution.base import (
    CommandExecutor,
    ExecutorContext,
    ProgressAwareExecutor,
    ProgressCallback,
)
from topyaz.execution.local import LocalExecutor
from topyaz.execution.progress import (
    BatchProgressTracker,
    ConsoleProgressCallback,
    LoggingProgressCallback,
    OutputProgressParser,
    SilentProgressCallback,
    create_batch_tracker,
    create_output_parser,
    create_progress_callback,
)
from topyaz.execution.remote import (
    RemoteConnectionPool,
    RemoteExecutor,
    get_remote_executor,
    return_remote_executor,
)

__all__ = [
    "BatchProgressTracker",
    # Base interfaces
    "CommandExecutor",
    "ConsoleProgressCallback",
    "ExecutorContext",
    # Local execution
    "LocalExecutor",
    "LoggingProgressCallback",
    "OutputProgressParser",
    "ProgressAwareExecutor",
    "ProgressCallback",
    "RemoteConnectionPool",
    # Remote execution
    "RemoteExecutor",
    # Progress monitoring
    "SilentProgressCallback",
    "create_batch_tracker",
    "create_output_parser",
    "create_progress_callback",
    "get_remote_executor",
    "return_remote_executor",
]
