"""Shared pytest fixtures and configuration."""

import asyncio
import os
import time
from dataclasses import dataclass
from typing import AsyncGenerator
from unittest.mock import Mock

import aiohttp
import pytest

# Import our common test utilities for integration tests
try:
    from tests.common import async_test_home_assistant, async_mock_service
    HAS_COMMON = True
except ImportError:
    HAS_COMMON = False

# Import fast_hass fixture
try:
    from tests.helpers.fast_ha_test import fast_hass, mock_service_calls
except ImportError:
    # Create mock fixture when HA not available
    @pytest.fixture
    async def fast_hass():
        """Mock fast_hass fixture when HA not available."""
        from tests.helpers.ha_mocks import MockHomeAssistant
        mock_ha = MockHomeAssistant()
        # Add methods to match FastHATest interface
        mock_ha.add_automation = lambda config: None
        mock_ha.trigger_automation = lambda id, skip_condition=False: None
        mock_ha.wait_for_state = lambda entity_id, state, timeout=5: True
        yield mock_ha


@dataclass
class HAClient:
    """Home Assistant client for integration tests."""

    base_url: str
    token: str = None
    session: aiohttp.ClientSession = None

    async def get_state(self, entity_id: str):
        """Get entity state."""
        url = f"{self.base_url}/api/states/{entity_id}"
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        async with self.session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            return None

    async def set_state(self, entity_id: str, state: str, attributes: dict = None):
        """Set entity state."""
        url = f"{self.base_url}/api/states/{entity_id}"
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        data = {"state": state}
        if attributes:
            data["attributes"] = attributes

        async with self.session.post(url, headers=headers, json=data) as resp:
            return resp.status == 200 or resp.status == 201

    async def call_service(self, domain: str, service: str, data: dict = None):
        """Call a service."""
        url = f"{self.base_url}/api/services/{domain}/{service}"
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        async with self.session.post(url, headers=headers, json=data or {}) as resp:
            return resp.status == 200

    async def create_automation(self, config: dict):
        """Create an automation via the API."""
        # This would typically use the config flow API
        # For testing, we'll simulate by calling the automation reload service
        return await self.call_service("automation", "reload")

    async def wait_for_state(
        self, entity_id: str, expected_state: str, timeout: int = 10
    ):
        """Wait for entity to reach expected state."""
        start = time.time()
        while time.time() - start < timeout:
            state = await self.get_state(entity_id)
            if state and state.get("state") == expected_state:
                return True
            await asyncio.sleep(0.5)
        return False


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ha_client() -> AsyncGenerator[HAClient, None]:
    """Create Home Assistant client for integration tests."""
    from tests.helpers.auth import TestAuth

    base_url = os.getenv("HA_URL", "http://localhost:8123")
    token = TestAuth.get_token()  # Handles bypass auth automatically

    # Wait for HA to be ready
    max_attempts = 30
    for i in range(max_attempts):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/api/") as resp:
                    if resp.status == 200:
                        break
        except:
            pass
        if i < max_attempts - 1:
            await asyncio.sleep(2)
    else:
        pytest.skip("Home Assistant not available")

    # Create persistent session
    session = aiohttp.ClientSession()
    client = HAClient(base_url, token, session)

    yield client

    await session.close()


@pytest.fixture
def mock_notification_service():
    """Mock notification service for testing."""
    calls = []

    class MockNotificationService:
        def __init__(self):
            self.calls = calls

        async def async_send_message(self, message, **kwargs):
            self.calls.append({"message": message, "kwargs": kwargs})

    return MockNotificationService()


@pytest.fixture
async def clean_ha_state(ha_client):
    """Ensure clean state before each test."""
    # Reset common test entities to known states
    test_entities = [
        ("light.test_light", "off"),
        ("light.entrance", "off"),
        ("light.hallway", "off"),
        ("light.living_room", "off"),
        ("binary_sensor.test_water_leak", "off"),
        ("person.john", "not_home"),
        ("person.test_user", "not_home"),
        ("climate.living_room", "off"),
        ("input_boolean.test_water_leak", "off"),
        ("input_boolean.test_water_leak_2", "off"),
    ]

    for entity_id, state in test_entities:
        await ha_client.set_state(entity_id, state)

    yield

    # Cleanup after test
    for entity_id, state in test_entities:
        await ha_client.set_state(entity_id, state)


# New Home Assistant-style fixtures
if HAS_COMMON:
    @pytest.fixture
    async def hass():
        """Provide a test Home Assistant instance using our common utilities."""
        hass = await async_test_home_assistant()
        yield hass
        await hass.async_stop()
    
    @pytest.fixture
    def mock_service(hass):
        """Provide a helper to mock services."""
        return lambda domain, service: async_mock_service(hass, domain, service)
