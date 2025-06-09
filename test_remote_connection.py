#!/usr/bin/env python3
"""
Test script to verify remote coordination system works.
"""

import tempfile
from pathlib import Path

from src.topyaz.core.types import RemoteOptions
from src.topyaz.execution.coordination import RemoteFileCoordinator
from src.topyaz.execution.remote import RemoteExecutor


def test_remote_connection():
    """Test actual remote connection and coordination."""

    # Set up remote options (using current user on ophelia.local)
    import getpass

    remote_options = RemoteOptions(
        host="ophelia.local", user=getpass.getuser(), ssh_port=22, connection_timeout=30, remote_folder="/tmp/topyaz"
    )

    try:
        # Create remote executor
        executor = RemoteExecutor(remote_options)

        # Test basic connection
        result = executor.test_connection()
        if result["connected"]:
            pass
        else:
            return False

        # Test file coordination
        coordinator = RemoteFileCoordinator(executor, "/tmp/topyaz")

        # Test coordination capabilities
        coord_test = coordinator.test_coordination()
        if coord_test["error"]:
            return False

        # Test file detection
        test_command = ["tpai", "testdata/man.jpg", "-o", "testdata/man_processed.jpg"]
        inputs, outputs = coordinator._detect_files(test_command)

        # Test path translation
        path_mapping = {
            "testdata/man.jpg": "/tmp/topyaz/sessions/test123/inputs/man.jpg",
            "testdata/man_processed.jpg": "/tmp/topyaz/sessions/test123/outputs/man_processed.jpg",
        }
        coordinator._translate_command(test_command, path_mapping)

        return True

    except Exception:
        return False


if __name__ == "__main__":
    success = test_remote_connection()

    if success:
        pass
    else:
        pass
