#!/usr/bin/env python3
# this_file: src/topyaz/core/errors.py
"""
Custom exception classes for topyaz.

This module defines all custom exceptions used throughout the topyaz package.
These exceptions provide specific error handling for different failure scenarios.

"""


class TopazError(Exception):
    """
    Base exception for all topyaz errors.

    This is the parent class for all custom exceptions in topyaz.
    It allows catching all topyaz-specific errors with a single except clause.

    Used by:
    - All other exception classes (as parent)
    - Error handling throughout the package

    Used in:
    - topyaz/__init__.py
    - topyaz/cli.py
    - topyaz/core/__init__.py
    """

    pass


class AuthenticationError(TopazError):
    """
    Authentication-related errors.

    Raised when authentication fails for any Topaz product, including:
    - Missing license files
    - Expired tokens
    - Invalid credentials
    - GUI login requirements

    Used by:
    - Video AI authentication validation
    - Remote SSH authentication
    - License verification

    Used in:
    - topyaz/__init__.py
    - topyaz/core/__init__.py
    - topyaz/execution/remote.py
    - topyaz/products/video_ai.py
    """

    pass


class EnvironmentError(TopazError):
    """
    Environment validation errors.

    Raised when system environment doesn't meet requirements:
    - Insufficient memory
    - Insufficient disk space
    - Unsupported OS version
    - Missing dependencies

    Used by:
    - Environment validation during initialization
    - Pre-processing checks

    Used in:
    - topyaz/__init__.py
    - topyaz/core/__init__.py
    - topyaz/system/environment.py
    """

    pass


class ProcessingError(TopazError):
    """
    Processing-related errors.

    Raised when processing operations fail:
    - Command execution failures
    - File I/O errors
    - Timeout errors
    - GPU/memory allocation failures

    Used by:
    - Command execution (local and remote)
    - Product processing methods
    - Batch processing operations

    Used in:
    - topyaz/__init__.py
    - topyaz/core/__init__.py
    - topyaz/execution/local.py
    - topyaz/execution/remote.py
    - topyaz/products/base.py
    - topyaz/products/photo_ai.py
    """

    pass


class ValidationError(TopazError):
    """
    Parameter validation errors.

    Raised when input parameters are invalid:
    - Out of range values
    - Invalid file formats
    - Invalid model names
    - Path validation failures

    Used by:
    - Parameter validation methods
    - Input path validation

    Used in:
    - topyaz/__init__.py
    - topyaz/core/__init__.py
    - topyaz/products/base.py
    - topyaz/products/gigapixel.py
    - topyaz/products/photo_ai.py
    - topyaz/products/video_ai.py
    - topyaz/system/paths.py
    """

    pass


class ExecutableNotFoundError(EnvironmentError):
    """
    Executable not found error.

    Raised when a Topaz product executable cannot be located.

    Used by:
    - Executable finding methods
    - Product initialization

    Used in:
    - topyaz/__init__.py
    - topyaz/core/__init__.py
    - topyaz/products/base.py
    """

    def __init__(self, product: str, search_paths: list[str] | None = None):
        """
        Initialize executable not found error.

        Args:
            product: Name of the Topaz product
            search_paths: List of paths that were searched

        """
        self.product = product
        self.search_paths = search_paths or []

        msg = f"{product} executable not found"
        if self.search_paths:
            msg += f". Searched paths: {', '.join(self.search_paths)}"

        super().__init__(msg)


class RemoteExecutionError(ProcessingError):
    """
    Remote execution specific errors.

    Raised when remote command execution fails:
    - SSH connection failures
    - Remote command failures
    - File transfer errors

    Used by:
    - Remote execution module
    - SSH operations

    Used in:
    - topyaz/__init__.py
    - topyaz/core/__init__.py
    - topyaz/execution/remote.py
    """

    pass
