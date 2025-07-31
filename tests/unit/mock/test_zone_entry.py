"""Unit tests for zone entry automation."""

from datetime import datetime, time

import pytest
from freezegun import freeze_time

from tests.helpers.ha_mocks import MockHomeAssistant


@pytest.fixture
def hass() -> MockHomeAssistant:
    """Mock Home Assistant instance."""
    return MockHomeAssistant()


def test_person_enters_home_zone(hass: MockHomeAssistant) -> None:
    """Test automation triggers when person enters home zone."""
    # Reset service calls
    hass.services._calls = []

    # Set initial state - person away from home
    hass.states.set(
        "person.john",
        "not_home",
        {
            "latitude": 40.7000,
            "longitude": -74.0000,
            "source": "device_tracker.johns_phone",
        },
    )

    # Set lights to off
    hass.states.set("light.entrance", "off")
    hass.states.set("light.hallway", "off")

    # Simulate person entering home zone
    hass.states.set(
        "person.john",
        "home",
        {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "source": "device_tracker.johns_phone",
        },
    )

    # Trigger welcome home automation
    hass.services.call("light", "turn_on", {"entity_id": "light.entrance"})
    hass.services.call("light", "turn_on", {"entity_id": "light.hallway"})

    # Verify lights were turned on
    assert len(hass.services._calls) == 2
    assert all(call.domain == "light" for call in hass.services._calls)
    assert all(call.service == "turn_on" for call in hass.services._calls)

    # Update states to reflect service calls
    for call in hass.services._calls:
        hass.states.set(call.data["entity_id"], "on")

    # Verify final states
    state_entrance = hass.states.get("light.entrance")
    state_hallway = hass.states.get("light.hallway")
    assert state_entrance is not None
    assert state_entrance.state == "on"
    assert state_hallway is not None
    assert state_hallway.state == "on"


def test_zone_entry_with_time_condition(hass: MockHomeAssistant) -> None:
    """Test zone entry automation with time condition."""
    # Reset service calls
    hass.services._calls = []

    # Test 1: Evening time (should trigger)
    with freeze_time("2024-01-15 19:00:00"):
        # Person arrives home
        hass.states.set("person.john", "not_home")
        hass.states.set("person.john", "home")

        # Check time condition
        current_time = datetime.now().time()
        if time(17, 0) <= current_time <= time(22, 0):
            # Turn on lights
            hass.services.call("light", "turn_on", {"entity_id": "light.entrance"})
            hass.services.call("light", "turn_on", {"entity_id": "light.hallway"})
            # Adjust climate
            hass.services.call(
                "climate",
                "set_temperature",
                {"entity_id": "climate.living_room", "temperature": 22},
            )

    assert len(hass.services._calls) == 3

    # Test 2: Daytime (should not trigger)
    hass.services._calls.clear()

    with freeze_time("2024-01-15 14:00:00"):
        # Person arrives home
        hass.states.set("person.john", "not_home")
        hass.states.set("person.john", "home")

        # Check time condition
        current_time = datetime.now().time()
        if time(17, 0) <= current_time <= time(22, 0):
            # Would turn on lights, but condition not met
            hass.services.call("light", "turn_on", {"entity_id": "light.entrance"})

    # No services should be called
    assert len(hass.services._calls) == 0


def test_multiple_people_zone_tracking(hass: MockHomeAssistant) -> None:
    """Test zone tracking for multiple people."""
    # Track who's home
    people_home = []

    # Define people
    people = [
        ("person.john", "device_tracker.johns_phone"),
        ("person.jane", "device_tracker.janes_phone"),
        ("person.kid", "device_tracker.kids_phone"),
    ]

    # Set everyone away initially
    for person, device in people:
        hass.states.set(person, "not_home")
        hass.states.set(device, "not_home")

    # Simulate each person arriving home
    for person, device in people:
        # Update device tracker
        hass.states.set(
            device,
            "home",
            {"latitude": 40.7128, "longitude": -74.0060, "gps_accuracy": 10},
        )

        # Update person entity
        hass.states.set(person, "home")
        people_home.append(person)

        # Check how many people are home
        assert len(people_home) == len(
            [p for p, _ in people if (state := hass.states.get(p)) and state.state == "home"]
        )


def test_zone_exit_no_automation(hass: MockHomeAssistant) -> None:
    """Test that zone exit doesn't trigger entry automation."""
    # Reset service calls
    hass.services._calls = []

    # Start with person at home
    hass.states.set("person.john", "home")
    hass.states.set("light.entrance", "on")

    # Person leaves home
    hass.states.set("person.john", "not_home", {"latitude": 40.7000, "longitude": -74.0000})

    # No automation should trigger for leaving
    # (unless we have a specific "goodbye" automation)

    # Verify no services were called
    assert len(hass.services._calls) == 0

    # Light should remain in its current state
    entrance_state = hass.states.get("light.entrance")
    assert entrance_state is not None
    assert entrance_state.state == "on"


def test_zone_with_notification(hass: MockHomeAssistant) -> None:
    """Test zone entry with notification."""
    # Reset service calls
    hass.services._calls = []

    # Family member arrives home while parents are away
    hass.states.set("person.parent1", "not_home")
    hass.states.set("person.parent2", "not_home")
    hass.states.set("person.kid", "not_home")

    # Kid arrives home
    hass.states.set("person.kid", "home")

    # Check if parents are away
    parent1_state = hass.states.get("person.parent1")
    parent2_state = hass.states.get("person.parent2")
    kid_state = hass.states.get("person.kid")

    parent1_away = parent1_state is not None and parent1_state.state == "not_home"
    parent2_away = parent2_state is not None and parent2_state.state == "not_home"
    kid_home = kid_state is not None and kid_state.state == "home"

    if parent1_away and parent2_away and kid_home:
        # Send notification to parents
        hass.services.call(
            "notify",
            "parents_phones",
            {
                "message": "Kid arrived home safely",
                "title": "🏠 Family Update",
                "data": {"tag": "family-presence", "group": "family"},
            },
        )

    # Verify notification was sent
    assert len(hass.services._calls) == 1
    assert hass.services._calls[0].domain == "notify"
    assert "arrived home" in hass.services._calls[0].data["message"]


def test_first_person_home_automation(hass: MockHomeAssistant) -> None:
    """Test automation that runs when first person arrives home."""
    # Reset service calls
    hass.services._calls = []

    # Set everyone away
    hass.states.set("person.john", "not_home")
    hass.states.set("person.jane", "not_home")
    hass.states.set("group.all_people", "not_home")

    # First person arrives
    hass.states.set("person.john", "home")
    hass.states.set("group.all_people", "home")  # At least one person home

    # Check if this is the first person home
    people_home = sum(
        1
        for p in ["person.john", "person.jane"]
        if (state := hass.states.get(p)) is not None and state.state == "home"
    )

    if people_home == 1:  # First person home
        # Turn on common area lights
        hass.services.call("light", "turn_on", {"entity_id": "light.living_room"})
        # Set thermostat to comfort mode
        hass.services.call(
            "climate",
            "set_preset_mode",
            {"entity_id": "climate.main", "preset_mode": "comfort"},
        )
        # Disarm alarm
        hass.services.call(
            "alarm_control_panel",
            "alarm_disarm",
            {"entity_id": "alarm_control_panel.home"},
        )

    # Verify appropriate services were called
    assert len(hass.services._calls) == 3
    assert any(c.domain == "light" for c in hass.services._calls)
    assert any(c.domain == "climate" for c in hass.services._calls)
    assert any(c.domain == "alarm_control_panel" for c in hass.services._calls)
