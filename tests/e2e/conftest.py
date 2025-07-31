"""E2E test configuration and fixtures."""

import os

import pytest


@pytest.fixture(scope="session")
def docker_compose_setup():
    """Home Assistant should already be running via docker-compose."""
    # When running in the test container, HA is already started
    # by the docker-compose command
    # Get URL from environment variable, default to the docker service name
    return os.getenv("HA_URL", "http://homeassistant:8123")


@pytest.fixture(scope="session")
def ha_url(docker_compose_setup):
    """Provide the Home Assistant URL for tests."""
    return docker_compose_setup


@pytest.fixture(scope="session")
def ha_credentials():
    """Provide the default credentials created by onboarding."""
    return {"username": "admin", "password": "admin"}


@pytest.fixture
def authenticated_session(ha_url):
    """Create an authenticated session for API tests."""
    import requests

    session = requests.Session()

    # Login to get auth token
    # login_data = {
    #     "username": ha_credentials["username"],
    #     "password": ha_credentials["password"],
    #     "client_id": ha_url,
    # }

    # Note: You may need to implement proper auth flow here
    # For now, return the session as-is since we have trusted networks
    return session


# Mark all tests in this directory as e2e
def pytest_collection_modifyitems(items):
    """Add e2e marker to all tests in this directory."""
    for item in items:
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
