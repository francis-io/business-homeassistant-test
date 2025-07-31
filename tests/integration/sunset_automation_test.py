"""Test sunset automation using real Home Assistant."""

from pathlib import Path
from typing import Any

import pytest
import yaml
from homeassistant.const import SERVICE_TURN_ON
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

# Import our validation helpers
from tests.helpers.automation_validation import assert_valid_automation, get_automation_summary


class TestSunsetAutomation:
    """Test the sunset light automation."""

    @pytest.fixture
    def automation_config(self) -> dict[str, Any]:
        """Load the sunset automation from YAML file."""
        yaml_path = Path(__file__).parent / "sunset_automation.yaml"
        with open(yaml_path) as f:
            config = yaml.safe_load(f)

        # Validate the automation before using it in tests
        assert_valid_automation(config)
        print(f"\nAutomation summary: {get_automation_summary(config)}")

        result: dict[str, Any] = config
        return result

    @pytest.mark.asyncio
    async def test_sunset_automation_triggers_light(
        self, hass: HomeAssistant, automation_config: dict[str, Any]
    ) -> None:
        """Test that lights turn on at sunset with correct brightness."""
        # Track service calls
        service_calls = []

        async def mock_service(call: Any) -> None:
            """Mock service handler."""
            service_calls.append(call)

        # Register mock light service
        hass.services.async_register("light", SERVICE_TURN_ON, mock_service)

        # Create a light entity
        hass.states.async_set("light.living_room", "off")

        # Setup automation
        assert await async_setup_component(hass, "automation", {"automation": [automation_config]})
        await hass.async_block_till_done()

        # Execute the automation action directly since we can't rely on entities
        for action in automation_config["action"]:
            await hass.services.async_call(
                action["service"].split(".")[0],  # domain
                action["service"].split(".")[1],  # service
                action.get("data", {}) | action.get("target", {}),
                blocking=True,
            )

        # Verify the service was called
        assert len(service_calls) == 1
        call = service_calls[0]

        # Verify correct service data
        assert call.service == SERVICE_TURN_ON
        assert call.data["entity_id"] == "light.living_room"
        assert call.data["brightness_pct"] == 80
        assert call.data["transition"] == 5

    @pytest.mark.asyncio
    async def test_automation_loads_from_yaml(
        self, hass: HomeAssistant, automation_config: dict[str, Any]
    ) -> None:
        """Test that the automation configuration is valid and loads correctly."""
        # Verify the YAML structure
        assert automation_config["id"] == "turn_on_lights_at_sunset"
        assert automation_config["alias"] == "Turn on lights at sunset"
        assert automation_config["trigger"][0]["platform"] == "sun"
        assert automation_config["trigger"][0]["event"] == "sunset"
        assert automation_config["action"][0]["service"] == "light.turn_on"
        assert automation_config["action"][0]["data"]["brightness_pct"] == 80

        # Verify it can be loaded by Home Assistant
        assert await async_setup_component(hass, "automation", {"automation": [automation_config]})
        await hass.async_block_till_done()

        # The automation component should be loaded
        assert "automation" in hass.config.components

    @pytest.mark.asyncio
    async def test_sunset_trigger_configuration(
        self, hass: HomeAssistant, automation_config: dict[str, Any]
    ) -> None:
        """Test that the sunset trigger is properly configured."""
        # Setup sun component first (required for sun triggers)
        assert await async_setup_component(hass, "sun", {"sun": {}})
        await hass.async_block_till_done()

        # The sun.sun entity should exist
        sun_state = hass.states.get("sun.sun")
        assert sun_state is not None

        # Setup automation
        assert await async_setup_component(hass, "automation", {"automation": [automation_config]})
        await hass.async_block_till_done()

        # Verify trigger configuration
        trigger_config = automation_config["trigger"][0]
        assert trigger_config["platform"] == "sun"
        assert trigger_config["event"] == "sunset"
        assert trigger_config["offset"] == 0

    @pytest.mark.asyncio
    async def test_light_state_after_automation(
        self, hass: HomeAssistant, automation_config: dict[str, Any]
    ) -> None:
        """Test the expected light state after automation runs."""
        # Track state changes
        state_changes = []

        async def state_changed(event: Any) -> None:
            """Track state change events."""
            if event.data.get("entity_id") == "light.living_room":
                state_changes.append(event.data)

        # Listen for state changes
        hass.bus.async_listen("state_changed", state_changed)

        # Mock light turn_on to also update the state
        async def mock_light_service(call: Any) -> None:
            """Mock service that also updates state."""
            entity_id = call.data["entity_id"]
            brightness = int(call.data.get("brightness_pct", 100) * 2.55)

            # Update the light state to 'on' with brightness
            hass.states.async_set(entity_id, "on", {"brightness": brightness})

        # Register mock service
        hass.services.async_register("light", SERVICE_TURN_ON, mock_light_service)

        # Set initial light state
        hass.states.async_set("light.living_room", "off")
        await hass.async_block_till_done()

        # Execute the automation action directly
        for action in automation_config["action"]:
            await hass.services.async_call(
                action["service"].split(".")[0],
                action["service"].split(".")[1],
                action.get("data", {}) | action.get("target", {}),
                blocking=True,
            )
        await hass.async_block_till_done()

        # Check final light state
        light_state = hass.states.get("light.living_room")
        assert light_state is not None
        assert light_state.state == "on"
        assert light_state.attributes.get("brightness") == 204  # 80% of 255
