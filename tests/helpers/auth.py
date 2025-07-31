"""Authentication helpers for testing."""

import os
from typing import Optional


class TestAuth:
    """Handle authentication for tests."""

    @staticmethod
    def get_token() -> Optional[str]:
        """Get authentication token with fallback strategies."""
        # 1. Try environment variable
        token = os.getenv("HA_TEST_TOKEN")
        if token and token != "test_token":
            return token

        # 2. For bypass auth, return None (no token needed)
        if os.getenv("HA_USE_BYPASS_AUTH", "true").lower() == "true":
            return None

        # 3. Default test token for CI/CD
        if os.getenv("CI"):
            return "ci_test_token"

        # 4. No auth needed for unit tests
        return None

    @staticmethod
    def get_headers(token: Optional[str] = None) -> dict:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}

        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    @staticmethod
    def is_auth_required() -> bool:
        """Check if authentication is required."""
        # No auth needed if using bypass
        if os.getenv("HA_USE_BYPASS_AUTH", "true").lower() == "true":
            return False

        # Check if token is available
        return bool(os.getenv("HA_TEST_TOKEN"))


class MockHAClient:
    """Mock Home Assistant client that doesn't require authentication."""

    def __init__(self, base_url: str = "http://localhost:8123"):
        self.base_url = base_url
        self.states = {}
        self.service_calls = []

    async def get_state(self, entity_id: str):
        """Get mocked state."""
        return self.states.get(entity_id, {"state": "unknown"})

    async def set_state(self, entity_id: str, state: str, attributes=None):
        """Set mocked state."""
        self.states[entity_id] = {
            "entity_id": entity_id,
            "state": state,
            "attributes": attributes or {},
        }
        return True

    async def call_service(self, domain: str, service: str, data=None):
        """Record service call."""
        self.service_calls.append(
            {"domain": domain, "service": service, "data": data or {}}
        )
        return True

    async def wait_for_state(self, entity_id: str, expected_state: str, timeout=10):
        """Mock wait for state."""
        # In mock, immediately return true if state matches
        current = self.states.get(entity_id, {})
        return current.get("state") == expected_state
