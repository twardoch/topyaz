#!/usr/bin/env python3
# this_file: src/topyaz/execution/__init__.py
"""
Execution module for topyaz.

This module contains components for executing commands locally and remotely.
"""

from topyaz.execution.base import CommandExecutor, ExecutorContext
from topyaz.execution.local import LocalExecutor
from topyaz.execution.remote import (
    RemoteConnectionPool,
    RemoteExecutor,
    get_remote_executor,
    return_remote_executor,
)

__all__ = [
    # Base interfaces
    "CommandExecutor",
    "ExecutorContext",
    # Local execution
    "LocalExecutor",
    # Remote execution
    "RemoteConnectionPool",
    "RemoteExecutor",
    "get_remote_executor",
    "return_remote_executor",
]
