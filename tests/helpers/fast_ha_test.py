"""Fast Home Assistant test framework for integration tests."""

import asyncio
import tempfile
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

import pytest
import yaml

try:
    import homeassistant.util.dt as dt_util
    from homeassistant import bootstrap
    from homeassistant.const import EVENT_HOMEASSISTANT_START
    from homeassistant.core import HomeAssistant
    from homeassistant.setup import async_setup_component
    from homeassistant.util.dt import set_default_time_zone

    HAS_HA = True
except ImportError:
    HAS_HA = False

    # Mock classes for when HA is not available
    class HomeAssistant:  # type: ignore[no-redef]
        """Mock Home Assistant class when HA is not available."""

        pass


class FastHATest:
    """Fast Home Assistant test instance for integration testing."""

    def __init__(self, config_dir: str | None = None):
        """Initialize FastHATest instance."""
        self.hass: HomeAssistant | None = None
        self.config_dir = config_dir or tempfile.mkdtemp()
        self._automations: list[dict[str, Any]] = []
        self._started = False

    async def start(self) -> HomeAssistant:
        """Start a minimal Home Assistant instance."""
        if not HAS_HA:
            pytest.skip("Home Assistant not available")

        # Create basic config
        config_path = Path(self.config_dir)
        config_path.mkdir(exist_ok=True)

        # Write minimal configuration.yaml
        config = {
            "homeassistant": {
                "name": "Test Home",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "elevation": 10,
                "unit_system": "metric",
                "time_zone": "America/New_York",
                "auth_providers": [
                    {
                        "type": "bypass",
                        "trusted_users": {"127.0.0.1": "test_user"},
                    }
                ],
            },
            "logger": {"default": "warning"},
        }

        # Write config synchronously - acceptable in test setup
        config_file = config_path / "configuration.yaml"
        config_file.write_text(yaml.dump(config))

        # Create HA instance with config_dir
        self.hass = HomeAssistant(str(config_path))
        self.hass.config.config_dir = str(config_path)

        # Set timezone
        set_default_time_zone(dt_util.get_time_zone("America/New_York"))

        # Initialize the loader cache - this is required before bootstrap
        from homeassistant.loader import DATA_COMPONENTS, DATA_INTEGRATIONS, DATA_MISSING_PLATFORMS

        self.hass.data[DATA_INTEGRATIONS] = {}
        self.hass.data[DATA_COMPONENTS] = {}
        self.hass.data[DATA_MISSING_PLATFORMS] = {}

        # Bootstrap core
        await bootstrap.async_from_config_dict(config, self.hass)

        # Setup required components quickly
        await asyncio.gather(
            async_setup_component(self.hass, "persistent_notification", {}),
            async_setup_component(self.hass, "sun", {}),
            async_setup_component(self.hass, "light", {"light": {"platform": "demo"}}),
            async_setup_component(
                self.hass,
                "binary_sensor",
                {"binary_sensor": {"platform": "demo"}},
            ),
            async_setup_component(self.hass, "climate", {"climate": {"platform": "demo"}}),
            async_setup_component(self.hass, "person", {}),
            async_setup_component(
                self.hass,
                "zone",
                {
                    "zone": {
                        "name": "Home",
                        "latitude": 40.7128,
                        "longitude": -74.0060,
                        "radius": 100,
                    }
                },
            ),
            async_setup_component(
                self.hass,
                "notify",
                {"notify": [{"platform": "demo", "name": "test_notifier"}]},
            ),
        )

        # Start HA
        await self.hass.async_start()
        self.hass.bus.async_fire(EVENT_HOMEASSISTANT_START)
        await self.hass.async_block_till_done()

        self._started = True
        return self.hass

    async def stop(self) -> None:
        """Stop the Home Assistant instance."""
        if self.hass and self._started:
            await self.hass.async_stop()

    async def add_automation(self, automation_config: dict[str, Any]) -> None:
        """Add an automation to the test instance."""
        if not self._started:
            raise RuntimeError("HA instance not started")

        self._automations.append(automation_config)

        # Setup automation component with our automations
        if self.hass is None:
            raise RuntimeError("HA instance not initialized")
        await async_setup_component(self.hass, "automation", {"automation": self._automations})
        await self.hass.async_block_till_done()

    async def trigger_automation(self, automation_id: str, skip_condition: bool = False) -> None:
        """Trigger an automation by ID."""
        if self.hass is None:
            raise RuntimeError("HA instance not initialized")
        await self.hass.services.async_call(
            "automation",
            "trigger",
            {
                "entity_id": f"automation.{automation_id}",
                "skip_condition": skip_condition,
            },
            blocking=True,
        )
        await self.hass.async_block_till_done()

    async def set_state(
        self,
        entity_id: str,
        state: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Set entity state."""
        if self.hass is None:
            raise RuntimeError("HA instance not initialized")
        self.hass.states.async_set(entity_id, state, attributes or {})
        await self.hass.async_block_till_done()

    def get_state(self, entity_id: str) -> str | None:
        """Get entity state."""
        if self.hass is None:
            raise RuntimeError("HA instance not initialized")
        state = self.hass.states.get(entity_id)
        return state.state if state else None

    async def advance_time(self, seconds: int = 0, minutes: int = 0) -> None:
        """Advance time for testing time-based automations."""
        if self.hass is None:
            raise RuntimeError("HA instance not initialized")
        # Fire time changed event
        import datetime as dt

        next_time = dt_util.utcnow() + dt.timedelta(seconds=seconds, minutes=minutes)
        self.hass.bus.async_fire("time_changed", {"now": next_time})
        await self.hass.async_block_till_done()

    async def wait_for_state(
        self, entity_id: str, expected_state: str, timeout: float = 5.0
    ) -> bool:
        """Wait for entity to reach expected state."""
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < timeout:
            if self.get_state(entity_id) == expected_state:
                return True
            await asyncio.sleep(0.1)
        return False

    def get_service_calls(self, domain: str, service: str) -> list[dict[str, Any]]:
        """Get service calls made to a specific service."""
        if self.hass is None:
            raise RuntimeError("HA instance not initialized")
        calls = []
        for call in self.hass.services._services.get(domain, {}).get(service, {}).get("calls", []):
            calls.append(call.data)
        return calls


# Pytest fixtures for fast HA testing
@pytest.fixture
async def fast_hass() -> Any:
    """Create a fast Home Assistant test instance."""
    ha_test = FastHATest()
    await ha_test.start()
    yield ha_test
    await ha_test.stop()


@pytest.fixture
def mock_service_calls() -> (
    tuple[dict[str, list[dict[str, Any]]], Callable[[Any], Coroutine[Any, Any, None]]]
):
    """Track service calls made during tests."""
    calls: dict[str, list[dict[str, Any]]] = {}

    async def mock_service_handler(call: Any) -> None:
        domain = call.domain
        service = call.service
        key = f"{domain}.{service}"
        if key not in calls:
            calls[key] = []
        calls[key].append({"data": dict(call.data), "context": call.context})

    return calls, mock_service_handler
