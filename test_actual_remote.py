#!/usr/bin/env python3
"""
Test the actual remote coordination by directly using the coordination layer
to show it works properly.
"""

import getpass
from pathlib import Path

from src.topyaz.core.types import RemoteOptions
from src.topyaz.execution.coordination import RemoteFileCoordinator
from src.topyaz.execution.remote import RemoteExecutor


def test_remote_coordination_with_ophelia():
    """Test remote coordination with the actual ophelia.local host."""

    # Set up remote options
    remote_options = RemoteOptions(
        host="othello.local",
        user=getpass.getuser(),  # Current user
        ssh_port=22,
        connection_timeout=30,
        remote_folder="/tmp/topyaz",
    )

    try:
        # Create remote executor
        executor = RemoteExecutor(remote_options)

        # Test connection
        connection_test = executor.test_connection()

        if not connection_test["connected"]:
            return False

        # Test file coordination
        coordinator = RemoteFileCoordinator(executor, "/tmp/topyaz")

        # Test coordination capabilities
        coord_test = coordinator.test_coordination()

        if coord_test["error"]:
            return False

        # Test with a real file
        test_input = Path("testdata/poster.jpg")

        if not test_input.exists():
            pass
        else:
            # Simulate the command that would be run
            command = ["echo", "Processing", str(test_input), "->", "output.jpg"]

            # Test file detection
            inputs, outputs = coordinator._detect_files(command)

            # Test path translation
            if inputs:
                mapping = {str(test_input): "/tmp/topyaz/session123/inputs/poster.jpg"}
                coordinator._translate_command(command, mapping)

        return True

    except Exception:
        return False


def explain_photo_ai_issue():
    """Explain the Photo AI preferences issue."""


if __name__ == "__main__":
    success = test_remote_coordination_with_ophelia()
    explain_photo_ai_issue()

    if success:
        pass
    else:
        pass
