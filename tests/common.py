"""Common test utilities for Home Assistant testing.

Based on Home Assistant's test utilities but simplified for our needs.
This provides lightweight fixtures without external dependencies.
"""

import asyncio
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch
import tempfile
from pathlib import Path

from homeassistant.core import HomeAssistant
from homeassistant import bootstrap, loader
from homeassistant.helpers import aiohttp_client
from homeassistant.loader import DATA_INTEGRATIONS, DATA_COMPONENTS, DATA_MISSING_PLATFORMS
from homeassistant.util import dt as dt_util


async def async_test_home_assistant(config_dir: Optional[str] = None) -> HomeAssistant:
    """Create a test instance of Home Assistant."""
    if config_dir is None:
        config_dir = tempfile.mkdtemp()
    
    config_path = Path(config_dir)
    config_path.mkdir(exist_ok=True)
    
    # Create a minimal Home Assistant instance
    hass = HomeAssistant(str(config_path))
    hass.config.config_dir = str(config_path)
    
    # Initialize required data structures
    hass.data[DATA_INTEGRATIONS] = {}
    hass.data[DATA_COMPONENTS] = {}
    hass.data[DATA_MISSING_PLATFORMS] = {}
    
    # Set timezone
    dt_util.set_default_time_zone(dt_util.get_time_zone("UTC"))
    
    # Basic configuration
    config = {
        'homeassistant': {
            'name': 'Test Home',
            'latitude': 40.0,
            'longitude': -74.0,
            'elevation': 0,
            'unit_system': 'metric',
            'time_zone': 'UTC',
            'internal_url': 'http://127.0.0.1:8123',
            'external_url': 'http://127.0.0.1:8123',
        }
    }
    
    # Bootstrap the instance
    await bootstrap.async_from_config_dict(config, hass)
    await hass.async_block_till_done()
    await hass.async_start()
    await hass.async_block_till_done()
    
    return hass


async def async_mock_service(
    hass: HomeAssistant,
    domain: str,
    service: str,
    return_value: Any = None
) -> List[Dict[str, Any]]:
    """Mock a service and return a list to track calls."""
    calls = []
    
    async def mock_service_handler(call):
        calls.append({
            'domain': call.domain,
            'service': call.service,
            'data': dict(call.data),
            'context': call.context,
        })
        return return_value
    
    hass.services.async_register(domain, service, mock_service_handler)
    return calls


async def async_fire_time_changed(hass: HomeAssistant, datetime_: Any) -> None:
    """Fire a time changed event."""
    hass.bus.async_fire('time_changed', {'now': datetime_})
    await hass.async_block_till_done()


def mock_restore_cache(hass: HomeAssistant, states: List[Dict[str, Any]]) -> None:
    """Mock the restore state cache."""
    from homeassistant.helpers.restore_state import DATA as RESTORE_DATA
    from homeassistant.helpers.restore_state import RestoreEntity
    
    data = []
    for state in states:
        restored_state = Mock(spec=RestoreEntity)
        restored_state.state = state.get('state')
        restored_state.attributes = state.get('attributes', {})
        data.append(restored_state)
    
    hass.data[RESTORE_DATA] = {
        'restore_state_data': data
    }


async def async_setup_component(
    hass: HomeAssistant,
    domain: str,
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """Set up a component and its dependencies."""
    from homeassistant.setup import async_setup_component as _async_setup_component
    
    if config is None:
        config = {}
    
    return await _async_setup_component(hass, domain, config)


def assert_setup_component(count: int, domain: str) -> Any:
    """Ensure a component is set up successfully."""
    config = {}
    
    async def mock_setup(hass, config_input):
        """Mock setup function."""
        config[domain] = config_input.get(domain)
        return True
    
    with patch(f'homeassistant.components.{domain}.async_setup', mock_setup):
        yield config
    
    assert len(config) == count


class MockConfigEntry:
    """Mock a config entry."""
    
    def __init__(
        self,
        *,
        domain: str = "test",
        data: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
        entry_id: str = "mock_entry_id",
        state: str = "loaded",
        title: str = "Mock Entry",
    ):
        """Initialize a mock config entry."""
        self.domain = domain
        self.data = data or {}
        self.options = options or {}
        self.entry_id = entry_id
        self.state = state
        self.title = title
        self.unique_id = None




async def async_capture_events(hass: HomeAssistant, event_type: str) -> List[Any]:
    """Capture all events of a specific type."""
    events = []
    
    def capture_event(event):
        events.append(event)
    
    hass.bus.async_listen(event_type, capture_event)
    return events