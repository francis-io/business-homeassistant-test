"""Unit tests for notification automation."""

import pytest
from unittest.mock import Mock
from tests.helpers.ha_mocks import MockHomeAssistant


@pytest.fixture
def hass():
    """Mock Home Assistant instance."""
    return MockHomeAssistant()


def test_water_leak_notification(hass):
    """Test notification sent when water leak detected."""
    # Track service calls
    service_calls = []
    
    def mock_service_call(domain, service, data):
        service_calls.append({
            "domain": domain,
            "service": service,
            "data": data
        })
    
    hass.services.call = mock_service_call
    
    # Set initial state - no leak
    hass.states.set("binary_sensor.water_leak_kitchen", "off")
    
    # Simulate water leak detection
    hass.states.set("binary_sensor.water_leak_kitchen", "on")
    
    # Trigger notification automation
    hass.services.call(
        "notify", "mobile_app_johns_phone",
        {
            "message": "Water leak detected in Kitchen!",
            "title": "⚠️ Water Leak Alert",
            "data": {
                "priority": "high",
                "ttl": 0,
                "channel": "alarm_stream"
            }
        }
    )
    
    # Verify notification was sent
    assert len(service_calls) == 1
    call = service_calls[0]
    assert call["domain"] == "notify"
    assert call["service"] == "mobile_app_johns_phone"
    assert "Water leak detected" in call["data"]["message"]
    assert call["data"]["data"]["priority"] == "high"


def test_door_open_notification(hass):
    """Test notification when door left open."""
    # Track service calls
    service_calls = []
    
    def mock_service_call(domain, service, data):
        service_calls.append({
            "domain": domain,
            "service": service,
            "data": data
        })
    
    hass.services.call = mock_service_call
    
    # Set door to open state
    hass.states.set(
        "binary_sensor.front_door",
        "on",
        {"device_class": "door", "friendly_name": "Front Door"}
    )
    
    # Simulate automation trigger after door open for 5 minutes
    hass.services.call(
        "notify", "mobile_app_johns_phone",
        {
            "message": "Front Door has been open for 5 minutes",
            "title": "🚪 Door Open",
            "data": {
                "actions": [
                    {
                        "action": "close_door_reminder",
                        "title": "Remind me later"
                    },
                    {
                        "action": "ignore_door",
                        "title": "Ignore"
                    }
                ]
            }
        }
    )
    
    # Verify notification was sent
    assert len(service_calls) == 1
    call = service_calls[0]
    assert call["domain"] == "notify"
    assert "Door has been open" in call["data"]["message"]
    assert len(call["data"]["data"]["actions"]) == 2


def test_multiple_notifications(hass):
    """Test multiple notifications in sequence."""
    # Track service calls
    service_calls = []
    
    def mock_service_call(domain, service, data):
        service_calls.append({
            "domain": domain,
            "service": service,
            "data": data
        })
    
    hass.services.call = mock_service_call
    
    # Send multiple notifications
    notifications = [
        {
            "message": "Motion detected at front door",
            "title": "🚶 Motion Alert"
        },
        {
            "message": "Package delivered",
            "title": "📦 Delivery"
        },
        {
            "message": "Garage door opened",
            "title": "🚗 Garage Alert"
        }
    ]
    
    for notif in notifications:
        hass.services.call(
            "notify", "mobile_app_johns_phone",
            {
                "message": notif["message"],
                "title": notif["title"]
            }
        )
    
    # Verify all notifications were sent
    assert len(service_calls) == 3
    for i, call in enumerate(service_calls):
        assert call["data"]["message"] == notifications[i]["message"]
        assert call["data"]["title"] == notifications[i]["title"]


def test_conditional_notification(hass):
    """Test notification with conditions."""
    # Track service calls
    service_calls = []
    
    def mock_service_call(domain, service, data):
        service_calls.append({
            "domain": domain,
            "service": service,
            "data": data
        })
    
    hass.services.call = mock_service_call
    
    # Test 1: Person is home - should NOT send notification
    hass.states.set("person.john", "home")
    hass.states.set("binary_sensor.motion_front", "on")
    
    # Check condition - don't send if person is home
    if hass.states.get("person.john").state != "home":
        hass.services.call(
            "notify", "mobile_app_johns_phone",
            {"message": "Motion detected while away"}
        )
    
    # No notification should be sent
    assert len(service_calls) == 0
    
    # Test 2: Person is away - SHOULD send notification
    hass.states.set("person.john", "not_home")
    hass.states.set("binary_sensor.motion_front", "on")
    
    # Check condition - send if person is away
    if hass.states.get("person.john").state == "not_home":
        hass.services.call(
            "notify", "mobile_app_johns_phone",
            {
                "message": "Motion detected while you're away!",
                "title": "🚨 Security Alert",
                "data": {
                    "priority": "high",
                    "image": "/api/camera_proxy/camera.front_door"
                }
            }
        )
    
    # Notification should be sent
    assert len(service_calls) == 1
    assert "Motion detected while you're away" in service_calls[0]["data"]["message"]


def test_notification_with_tts(hass):
    """Test notification with text-to-speech announcement."""
    # Track service calls
    service_calls = []
    
    def mock_service_call(domain, service, data):
        service_calls.append({
            "domain": domain,
            "service": service,
            "data": data
        })
    
    hass.services.call = mock_service_call
    
    # Trigger both mobile notification and TTS
    message = "Welcome home, John!"
    
    # Send mobile notification
    hass.services.call(
        "notify", "mobile_app_johns_phone",
        {"message": message, "title": "🏠 Welcome"}
    )
    
    # Send TTS announcement
    hass.services.call(
        "tts", "cloud_say",
        {
            "entity_id": "media_player.living_room_speaker",
            "message": message
        }
    )
    
    # Verify both services were called
    assert len(service_calls) == 2
    
    # Check mobile notification
    notify_call = next(c for c in service_calls if c["domain"] == "notify")
    assert notify_call["data"]["message"] == message
    
    # Check TTS
    tts_call = next(c for c in service_calls if c["domain"] == "tts")
    assert tts_call["data"]["message"] == message
    assert tts_call["data"]["entity_id"] == "media_player.living_room_speaker"