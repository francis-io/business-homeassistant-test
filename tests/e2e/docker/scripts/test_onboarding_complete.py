"""Test to verify Home Assistant is accessible after onboarding."""
import os
import time
import requests
import pytest


HA_URL = os.getenv("HA_URL", "http://localhost:8123")


def wait_for_home_assistant(url, timeout=30):
    """Poll Home Assistant until it's accessible or timeout."""
    print(f"Waiting for Home Assistant at {url} to be accessible...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/api/", timeout=5)
            if response.status_code in [200, 401]:
                print(f"✓ Home Assistant is accessible after {time.time() - start_time:.1f} seconds")
                return True
        except requests.exceptions.RequestException:
            pass

    raise TimeoutError(f"Home Assistant at {url} was not accessible after {timeout} seconds")


def test_home_assistant_is_accessible():
    """Test that Home Assistant API is accessible after onboarding."""
    # Poll until HA is healthy
    wait_for_home_assistant(HA_URL)

    # Test the API endpoint
    response = requests.get(f"{HA_URL}/api/")

    # Should get 200 OK or 401 (auth required) - both indicate API is working
    assert response.status_code in [200, 401], f"Expected 200 or 401, got {response.status_code}"

    if response.status_code == 200:
        data = response.json()
        assert "message" in data
        assert data["message"] == "API running."

    print(f"✓ Home Assistant API is accessible at {HA_URL} (status: {response.status_code})")


def test_onboarding_is_complete():
    """Test that onboarding has been completed."""
    # Check onboarding status
    response = requests.get(f"{HA_URL}/api/onboarding")

    # Should get 200 OK
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Check all steps are done
    steps = response.json()
    for step in steps:
        assert step["done"] is True, f"Step '{step['step']}' is not complete"

    print("✓ All onboarding steps are complete")


def test_lovelace_is_accessible():
    """Test that the Lovelace UI is accessible."""
    # Test the frontend
    response = requests.get(f"{HA_URL}/lovelace")

    # Should get 200 OK
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"✓ Lovelace UI is accessible at {HA_URL}/lovelace")


if __name__ == "__main__":
    test_home_assistant_is_accessible()
    test_onboarding_is_complete()
    test_lovelace_is_accessible()
    print("\nAll tests passed! Home Assistant is ready for testing.")
