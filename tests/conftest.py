#!/usr/bin/env python3
# this_file: tests/conftest.py
"""
Shared pytest fixtures for the topyaz test suite.

Topaz Labs desktop applications are never installed in CI, so every test that
exercises a product must avoid touching the real executable-discovery logic.
The autouse fixture below patches ``TopazProduct.find_executable`` so that all
products resolve to a deterministic fake path, letting us validate command
building, dry-run behaviour, and CLI orchestration without any real binaries.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from topyaz.products.base import TopazProduct


@pytest.fixture(autouse=True)
def mock_topaz_executable_discovery(request: pytest.FixtureRequest):
    """Make every Topaz product resolve to a fake executable path.

    Individual tests may still override ``find_executable`` on a concrete
    subclass (e.g. ``patch.object(PhotoAI, "find_executable", ...)``); that
    subclass-level patch shadows this base-class patch via the MRO.

    Mark a test with ``@pytest.mark.no_executable_mock`` to opt out.
    """
    if "no_executable_mock" in request.keywords:
        yield
        return

    def _fake_find_executable(self: TopazProduct) -> Path:
        return Path(f"/fake/topaz/bin/{self.executable_name}")

    with patch.object(TopazProduct, "find_executable", _fake_find_executable):
        yield


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers used by the suite."""
    config.addinivalue_line(
        "markers",
        "no_executable_mock: disable the autouse Topaz executable-discovery mock",
    )
