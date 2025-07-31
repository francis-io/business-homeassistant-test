"""Simple demo tests that work without Home Assistant."""

import asyncio
from unittest.mock import AsyncMock, Mock

import aiohttp
import pytest
from freezegun import freeze_time


def test_simple_addition():
    """Test basic functionality."""
    assert 2 + 2 == 4


def test_mock_usage():
    """Test that mocking works."""
    mock_service = Mock()
    mock_service.call_service = Mock(return_value={"status": "ok"})

    result = mock_service.call_service("light", "turn_on")

    assert result["status"] == "ok"
    mock_service.call_service.assert_called_once_with("light", "turn_on")


@pytest.mark.asyncio
async def test_async_mock():
    """Test async functionality."""
    mock_client = AsyncMock()
    mock_client.get_state = AsyncMock(return_value={"state": "on"})

    result = await mock_client.get_state("light.test")

    assert result["state"] == "on"
    mock_client.get_state.assert_called_once_with("light.test")


@pytest.mark.asyncio
async def test_aiohttp_mock():
    """Test HTTP mocking with aioresponses."""
    from aioresponses import aioresponses

    with aioresponses() as m:
        m.get("http://localhost:8123/api/states", payload={"test": "data"})

        async with aiohttp.ClientSession() as session:
            resp = await session.get("http://localhost:8123/api/states")
            data = await resp.json()

        assert data == {"test": "data"}


@freeze_time("2024-01-15 18:30:00")
def test_freezegun_time():
    """Test time manipulation."""
    from datetime import datetime

    # Test that freezegun properly freezes time
    now = datetime.now()
    # Time should be frozen at the specified time
    assert now.year == 2024
    assert now.month == 1
    assert now.day == 15
    assert now.hour == 18
    assert now.minute == 30


class TestLightAutomation:
    """Test suite for light automation logic."""

    def test_should_turn_on_after_sunset(self):
        """Test light should turn on after sunset."""
        # Mock sunset check
        is_after_sunset = Mock(return_value=True)
        current_time = "18:30"

        # Logic: turn on if time matches and after sunset
        should_turn_on = current_time == "18:30" and is_after_sunset()

        assert should_turn_on is True

    def test_should_not_turn_on_before_sunset(self):
        """Test light should not turn on before sunset."""
        # Mock sunset check
        is_after_sunset = Mock(return_value=False)
        current_time = "18:30"

        # Logic: turn on if time matches and after sunset
        should_turn_on = current_time == "18:30" and is_after_sunset()

        assert should_turn_on is False


class TestNotificationLogic:
    """Test suite for notification logic."""

    def test_notification_on_water_leak(self):
        """Test notification is sent when water leak detected."""
        notifications = []

        def send_notification(title, message, priority="normal"):
            notifications.append(
                {"title": title, "message": message, "priority": priority}
            )

        # Simulate water leak
        water_leak_detected = True

        if water_leak_detected:
            send_notification(
                "Water Leak Detected!",
                "Water leak in kitchen - immediate attention required",
                "high",
            )

        assert len(notifications) == 1
        assert notifications[0]["priority"] == "high"
        assert "Water Leak" in notifications[0]["title"]


class TestZoneLogic:
    """Test suite for zone entry logic."""

    @pytest.mark.asyncio
    async def test_welcome_home_actions(self):
        """Test actions when person arrives home."""
        actions_performed = []

        async def turn_on_lights():
            actions_performed.append("lights_on")

        async def set_temperature(temp):
            actions_performed.append(f"temp_set_{temp}")

        async def send_notification(msg):
            actions_performed.append(f"notified_{msg}")

        # Simulate person arriving home at 18:00
        current_hour = 18
        person_home = True

        if person_home and 17 <= current_hour < 22:
            await turn_on_lights()
            await set_temperature(22)
            await send_notification("welcome")

        assert "lights_on" in actions_performed
        assert "temp_set_22" in actions_performed
        assert "notified_welcome" in actions_performed
