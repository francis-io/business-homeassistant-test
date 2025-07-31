"""Basic E2E tests to verify Home Assistant is working."""
import pytest
import requests
import json


class TestHomeAssistantE2E:
    """End-to-end tests for Home Assistant."""

    def test_api_is_accessible(self, ha_url):
        """Test that the API is accessible."""
        response = requests.get(f"{ha_url}/api/")
        # API requires auth, so 401 is expected
        assert response.status_code in [200, 401]

    def test_frontend_is_accessible(self, ha_url):
        """Test that the frontend is accessible."""
        response = requests.get(ha_url)
        assert response.status_code == 200
        assert "Home Assistant" in response.text or "home-assistant" in response.text

    def test_onboarding_status(self, ha_url):
        """Test that we can check onboarding status."""
        # Note: The /api/onboarding endpoint may not be available in all HA versions
        # or after onboarding is complete
        response = requests.get(f"{ha_url}/api/onboarding")

        # The endpoint might return 404 if onboarding is already complete
        if response.status_code == 404:
            pytest.skip("Onboarding endpoint not available (likely already completed)")

        assert response.status_code == 200
        steps = response.json()
        assert isinstance(steps, list)
        assert len(steps) == 4  # user, core_config, analytics, integration

        # Just verify the structure, not completion status
        # since test environment may not have onboarding completed
        step_names = [step["step"] for step in steps]
        assert "user" in step_names
        assert "core_config" in step_names
        assert "analytics" in step_names
        assert "integration" in step_names

        print(f"Onboarding status: {[(s['step'], s['done']) for s in steps]}")

    def test_system_health(self, ha_url):
        """Test that the system health endpoint is accessible."""
        # This endpoint typically doesn't require auth
        response = requests.get(f"{ha_url}/api/system_health/info")

        # System health might require auth or not be available in test setup
        if response.status_code in [401, 404]:
            pytest.skip("System health endpoint not available in test environment")

        assert response.status_code == 200

    def test_manifest_json(self, ha_url):
        """Test that the manifest.json is accessible."""
        response = requests.get(f"{ha_url}/manifest.json")
        assert response.status_code == 200

        manifest = response.json()
        assert "name" in manifest
        assert "short_name" in manifest
        assert manifest["name"] == "Home Assistant"

    def test_websocket_api_info(self, ha_url):
        """Test that we can get websocket API info."""
        response = requests.get(f"{ha_url}/api/websocket")

        # WebSocket endpoint typically returns 400 Bad Request when accessed via HTTP
        # This is expected behavior as it requires a WebSocket upgrade
        assert response.status_code in [200, 400, 426]

        # Some setups return upgrade required message
        if response.status_code == 426:
            assert "Upgrade Required" in response.text or "upgrade" in response.text.lower()

    def test_static_resources(self, ha_url):
        """Test that static resources are accessible."""
        # Test favicon
        response = requests.get(f"{ha_url}/static/icons/favicon.ico")
        assert response.status_code == 200
        assert response.headers.get("content-type", "").startswith("image/")
