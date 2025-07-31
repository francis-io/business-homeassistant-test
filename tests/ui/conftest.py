"""Minimal UI test configuration for pytest-playwright."""

import os

import pytest


@pytest.fixture
def ha_url() -> str:
    """Get Home Assistant URL from environment or default."""
    return os.getenv("HA_URL", "http://localhost:8123")


# Let pytest-playwright handle browser, context, and page fixtures automatically
