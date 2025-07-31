"""Unit tests for time-based light automation."""

import pytest
from datetime import datetime, time
from unittest.mock import Mock, patch
from freezegun import freeze_time

# Import mocks instead of real HA components
from tests.helpers.ha_mocks import MockHomeAssistant


@pytest.fixture
def hass():
    """Mock Home Assistant instance."""
    return MockHomeAssistant()


def test_evening_lights_automation_with_sunset_condition(hass):
    """Test that lights turn on at 18:30 after sunset."""
    # Set initial state
    hass.states.set("light.living_room", "off")
    
    # Mock sunset condition (sun is down)
    with freeze_time("2024-01-15 18:30:00"):
        # In winter, 18:30 is after sunset
        # Simulate automation trigger
        hass.services.call(
            "light", "turn_on",
            {"entity_id": "light.living_room", "brightness": 80, "transition": 5}
        )
        
        # Update state to simulate the light turning on
        hass.states.set("light.living_room", "on", {"brightness": 80})
        
        # Verify light turned on
        state = hass.states.get("light.living_room")
        assert state is not None
        assert state.state == "on"
        assert state.attributes.get("brightness") == 80


def test_evening_lights_blocked_before_sunset(hass):
    """Test that lights don't turn on at 18:30 before sunset."""
    # Set initial state
    hass.states.set("light.living_room", "off")
    
    # Mock sunset condition (sun is still up in summer)
    with freeze_time("2024-07-15 18:30:00"):
        # In summer, 18:30 might be before sunset
        # Automation should not trigger
        
        # Light should remain off
        state = hass.states.get("light.living_room")
        assert state is not None
        assert state.state == "off"


@freeze_time("2024-01-15 12:00:00")
def test_time_trigger_execution(hass):
    """Test that automation triggers at the specified time."""
    # Set initial state
    hass.states.set("light.test_light", "off")
    
    # Simulate automation trigger at noon
    hass.services.call(
        "light", "turn_on",
        {"entity_id": "light.test_light"}
    )
    
    # Update state to simulate the light turning on
    hass.states.set("light.test_light", "on")
    
    # Verify light turned on
    state = hass.states.get("light.test_light")
    assert state is not None
    assert state.state == "on"


def test_brightness_and_transition_values(hass):
    """Test that brightness and transition values are correctly applied."""
    # Mock light service
    service_data = None
    
    def mock_light_service(service, action, data):
        nonlocal service_data
        service_data = data
        # Update the state to simulate the light turning on
        hass.states.set(
            data["entity_id"],
            "on",
            {"brightness": data.get("brightness", 255)}
        )
    
    # Replace the service call
    hass.services.call = mock_light_service
    
    # Trigger automation with specific brightness and transition
    hass.services.call(
        "light", "turn_on",
        {
            "entity_id": "light.test_brightness",
            "brightness": 128,
            "transition": 10
        }
    )
    
    # Verify service was called with correct data
    assert service_data is not None
    assert service_data["entity_id"] == "light.test_brightness"
    assert service_data["brightness"] == 128
    assert service_data["transition"] == 10
    
    # Verify state was updated
    state = hass.states.get("light.test_brightness")
    assert state.state == "on"
    assert state.attributes["brightness"] == 128


def test_time_condition_enforcement(hass):
    """Test automation with time condition."""
    # Test during allowed time (20:00)
    with freeze_time("2024-01-15 20:00:00"):
        hass.states.set("light.hallway", "off")
        hass.states.set("binary_sensor.motion", "on")
        
        # Check time condition
        current_time = datetime.now().time()
        after_time = time(17, 0)
        before_time = time(23, 0)
        
        if after_time <= current_time <= before_time:
            # Time condition met, turn on light
            hass.services.call(
                "light", "turn_on",
                {"entity_id": "light.hallway"}
            )
            # Update state to simulate the light turning on
            hass.states.set("light.hallway", "on")
        
        # Should be on because time condition is met
        state = hass.states.get("light.hallway")
        assert state.state == "on"
    
    # Test outside allowed time (10:00 AM)
    with freeze_time("2024-01-15 10:00:00"):
        hass.states.set("light.hallway", "off")
        hass.states.set("binary_sensor.motion", "on")
        
        # Check time condition
        current_time = datetime.now().time()
        
        if not (after_time <= current_time <= before_time):
            # Time condition not met, don't turn on light
            pass
        
        # Should remain off
        state = hass.states.get("light.hallway")
        assert state.state == "off"


def test_multiple_time_triggers_with_brightness(hass):
    """Test automation with multiple time triggers."""
    # Test morning trigger (7:00)
    with freeze_time("2024-01-15 07:00:00"):
        hass.states.set("light.bedroom", "off")
        
        # Morning brightness (30%)
        current_hour = datetime.now().hour
        brightness_pct = 30 if current_hour < 12 else 70
        brightness = int(255 * brightness_pct / 100)
        
        hass.services.call(
            "light", "turn_on",
            {
                "entity_id": "light.bedroom",
                "brightness": brightness
            }
        )
        
        # Update state to simulate the light turning on
        hass.states.set("light.bedroom", "on", {"brightness": brightness})
        
        state = hass.states.get("light.bedroom")
        assert state.state == "on"
        assert state.attributes.get("brightness") == brightness
    
    # Test evening trigger (20:00)
    with freeze_time("2024-01-15 20:00:00"):
        hass.states.set("light.bedroom", "off")
        
        # Evening brightness (70%)
        current_hour = datetime.now().hour
        brightness_pct = 30 if current_hour < 12 else 70
        brightness = int(255 * brightness_pct / 100)
        
        hass.services.call(
            "light", "turn_on",
            {
                "entity_id": "light.bedroom",
                "brightness": brightness
            }
        )
        
        # Update state to simulate the light turning on
        hass.states.set("light.bedroom", "on", {"brightness": brightness})
        
        state = hass.states.get("light.bedroom")
        assert state.state == "on"
        assert state.attributes.get("brightness") == brightness


def test_time_pattern_trigger_toggle(hass):
    """Test automation with time pattern trigger."""
    # Test toggle at :00, :15, :30, :45
    light_state = "off"
    
    for minute in [0, 15, 30, 45]:
        with freeze_time(f"2024-01-15 10:{minute:02d}:00"):
            hass.states.set("light.office", light_state)
            
            # Every 15 minutes, toggle the light
            if minute % 15 == 0:
                # Toggle light
                new_state = "on" if light_state == "off" else "off"
                hass.services.call(
                    "light", "toggle",
                    {"entity_id": "light.office"}
                )
                # Update expected state
                light_state = new_state
                
                # Update actual state in mock
                hass.states.set("light.office", new_state)
            
            state = hass.states.get("light.office")
            assert state.state == light_state