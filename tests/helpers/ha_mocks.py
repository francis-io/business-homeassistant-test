"""Mock Home Assistant components for testing without HA installation."""

import asyncio
from typing import Any, Optional
from unittest.mock import Mock


class MockHomeAssistant:
    """Mock Home Assistant core."""

    def __init__(self) -> None:
        """Initialize MockHomeAssistant instance."""
        self.states = MockStates()
        self.services = MockServices()
        self.config_entries = Mock()
        self.data: dict[str, Any] = {}
        self.bus = Mock()
        self.components: set[str] = set()
        self.automations: list[dict[str, Any]] = []
        self.hass = self  # Self reference for compatibility

    async def async_block_till_done(self) -> None:
        """Mock waiting for async operations."""
        await asyncio.sleep(0)

    def async_create_task(self, coro: Any) -> asyncio.Task[Any]:
        """Mock task creation."""
        return asyncio.create_task(coro)

    async def add_automation(self, config: dict[str, Any]) -> None:
        """Add an automation."""
        self.automations.append(config)
        automation_id = config.get("id", config.get("alias", "unnamed"))
        entity_id = f"automation.{automation_id}"
        self.states.async_set(entity_id, STATE_ON)
        self.data[entity_id] = config

    async def trigger_automation(self, automation_id: str, skip_condition: bool = False) -> None:
        """Trigger an automation by ID."""
        # entity_id = f"automation.{automation_id}"  # Reserved for future use

        # Find the automation config
        config = None
        for auto in self.automations:
            if auto.get("id") == automation_id or auto.get("alias") == automation_id:
                config = auto
                break

        if config:
            # Execute actions
            action = config.get("action", [])
            if isinstance(action, dict):
                action = [action]

            for act in action:
                service = act.get("service", "")
                if "." in service:
                    domain, service_name = service.split(".", 1)

                    # Handle common services
                    if service == "light.turn_on":
                        entities = act.get("target", {}).get("entity_id", [])
                        if isinstance(entities, str):
                            entities = [entities]
                        for entity in entities:
                            self.states.async_set(entity, "on")
                    elif service == "light.turn_off":
                        entities = act.get("target", {}).get("entity_id", [])
                        if isinstance(entities, str):
                            entities = [entities]
                        for entity in entities:
                            self.states.async_set(entity, "off")

                    # Call the service
                    await self.services.async_call(
                        domain,
                        service_name,
                        act.get("data", {}),
                        blocking=True,
                    )

    async def set_state(
        self,
        entity_id: str,
        state: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Set entity state."""
        self.states.async_set(entity_id, state, attributes)
        await self.async_block_till_done()

    def get_state(self, entity_id: str) -> str | None:
        """Get entity state."""
        state = self.states.get(entity_id)
        return state.state if state else None

    async def wait_for_state(
        self, entity_id: str, expected_state: str, timeout: float = 5.0
    ) -> bool:
        """Wait for entity to reach expected state."""
        import time

        start = time.time()
        while time.time() - start < timeout:
            if self.get_state(entity_id) == expected_state:
                return True
            await asyncio.sleep(0.1)
        return False


class MockStates:
    """Mock state management."""

    def __init__(self) -> None:
        """Initialize MockStates instance."""
        self._states: dict[str, MockState] = {}

    def async_set(
        self,
        entity_id: str,
        state: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Set entity state."""
        self._states[entity_id] = MockState(entity_id, state, attributes or {})

    def set(
        self,
        entity_id: str,
        state: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Set entity state (synchronous version)."""
        self._states[entity_id] = MockState(entity_id, state, attributes or {})

    def get(self, entity_id: str) -> Optional["MockState"]:
        """Get entity state."""
        return self._states.get(entity_id)

    def async_remove(self, entity_id: str) -> None:
        """Remove entity."""
        self._states.pop(entity_id, None)


class MockState:
    """Mock entity state."""

    def __init__(self, entity_id: str, state: str, attributes: dict[str, Any]) -> None:
        """Initialize MockState with entity details."""
        from datetime import datetime

        self.entity_id = entity_id
        self.state = state
        self.attributes = attributes
        self.last_changed = datetime.now()
        self.last_updated = datetime.now()
        self.context = {
            "user_id": None,
            "parent_id": None,
            "id": "mock_context",
        }


class MockServices:
    """Mock service management."""

    def __init__(self) -> None:
        """Initialize MockServices instance."""
        self._services: dict[str, dict[str, Any]] = {}
        self._calls: list[MockServiceCall] = []

    def async_register(self, domain: str, service: str, handler: Any) -> None:
        """Register a service."""
        if domain not in self._services:
            self._services[domain] = {}
        self._services[domain][service] = handler

    async def async_call(
        self,
        domain: str,
        service: str,
        data: dict[str, Any] | None = None,
        blocking: bool = False,
    ) -> None:
        """Call a service."""
        call = MockServiceCall(domain, service, data or {})
        self._calls.append(call)

        # If blocking is True, we would normally wait for the service to complete
        # For mocking purposes, we just record the call immediately
        _ = blocking  # Acknowledge the parameter

        # Call the handler if registered
        if domain in self._services and service in self._services[domain]:
            handler = self._services[domain][service]
            if asyncio.iscoroutinefunction(handler):
                await handler(call)
            else:
                handler(call)

    def call(self, domain: str, service: str, data: dict[str, Any] | None = None) -> None:
        """Call a service (synchronous version)."""
        call = MockServiceCall(domain, service, data or {})
        self._calls.append(call)

        # Call the handler if registered
        if domain in self._services and service in self._services[domain]:
            handler = self._services[domain][service]
            if not asyncio.iscoroutinefunction(handler):
                handler(call)


class MockServiceCall:
    """Mock service call."""

    def __init__(self, domain: str, service: str, data: dict[str, Any]) -> None:
        """Initialize MockServiceCall with service details."""
        self.domain = domain
        self.service = service
        self.data = data


# Constants
STATE_ON = "on"
STATE_OFF = "off"
STATE_HOME = "home"
STATE_NOT_HOME = "not_home"
ATTR_ENTITY_ID = "entity_id"


# Mock setup function
async def async_setup_component(
    hass: MockHomeAssistant, domain: str, config: dict[str, Any]
) -> bool:
    """Mock component setup."""
    hass.components.add(domain)

    # Handle automation setup
    if domain == "automation":
        automation_config = config.get("automation", {})
        if isinstance(automation_config, dict):
            # Single automation
            await setup_automation(hass, automation_config)
        elif isinstance(automation_config, list):
            # Multiple automations
            for auto in automation_config:
                await setup_automation(hass, auto)

    return True


async def setup_automation(hass: MockHomeAssistant, config: dict[str, Any]) -> None:
    """Set up a mock automation."""
    automation_id = config.get("alias", "unnamed").lower().replace(" ", "_")
    entity_id = f"automation.{automation_id}"

    # Store automation config
    hass.data[entity_id] = config

    # Set automation state
    hass.states.async_set(entity_id, STATE_ON)

    # Register trigger service
    async def trigger_automation(call: MockServiceCall) -> None:
        """Trigger the automation."""
        target_entity = call.data.get(ATTR_ENTITY_ID)
        if target_entity and (target_entity == entity_id or entity_id in target_entity):
            # Execute actions
            action = config.get("action", {})
            if isinstance(action, dict):
                await execute_action(hass, action)
            elif isinstance(action, list):
                for act in action:
                    await execute_action(hass, act)

    hass.services.async_register("automation", "trigger", trigger_automation)


async def execute_action(hass: MockHomeAssistant, action: dict[str, Any]) -> None:
    """Execute an automation action."""
    service = action.get("service", "")
    if "." in service:
        domain, service_name = service.split(".", 1)
        data = action.get("data", {})
        target = action.get("target", {})

        # Merge target into data for compatibility
        if "entity_id" in target:
            data["entity_id"] = target["entity_id"]

        await hass.services.async_call(domain, service_name, data)


# Create a global hass fixture for imports
hass = MockHomeAssistant()

# Export HomeAssistant as an alias
HomeAssistant = MockHomeAssistant
