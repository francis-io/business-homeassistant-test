#!/usr/bin/env python3
"""Automated setup for Home Assistant test authentication."""
import os
import sys
import time
from pathlib import Path

import requests


def wait_for_ha(base_url, timeout=60):
    """Wait for Home Assistant to be ready."""
    print(f"Waiting for Home Assistant at {base_url}...")
    start = time.time()

    while time.time() - start < timeout:
        try:
            response = requests.get(f"{base_url}/api/", timeout=2)
            if response.status_code in [200, 401]:  # 401 means HA is up but needs auth
                print("✅ Home Assistant is ready!")
                return True
        except Exception:
            pass
        time.sleep(2)

    print("❌ Home Assistant did not start in time")
    return False


def setup_test_user(base_url):
    """Set up a test user using onboarding API."""
    # This only works on fresh HA instances during onboarding
    onboarding_url = f"{base_url}/api/onboarding/users"

    user_data = {
        "name": "Test User",
        "username": "test_user",
        "password": "test_password_123",
        "language": "en",
    }

    try:
        response = requests.post(onboarding_url, json=user_data)
        if response.status_code == 200:
            print("✅ Test user created successfully")
            return True
        else:
            print(f"❌ Could not create user: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False


def create_auth_token(base_url, username, password):
    """Create a long-lived access token."""
    # First, get a regular auth token
    auth_url = f"{base_url}/auth/login_flow"

    # Start login flow
    response = requests.post(auth_url, json={"client_id": "test_client"})
    if response.status_code != 200:
        print("❌ Could not start login flow")
        return None

    flow_id = response.json()["flow_id"]

    # Submit credentials
    login_data = {
        "username": username,
        "password": password,
        "client_id": "test_client",
    }

    response = requests.post(f"{base_url}/auth/login_flow/{flow_id}", json=login_data)

    if response.status_code == 200:
        auth_code = response.json().get("result")
        print("✅ Authentication successful")
        # In a real implementation, you'd exchange this for a long-lived token
        return auth_code
    else:
        print("❌ Authentication failed")
        return None


def save_token_to_env(token):
    """Save token to .env file."""
    env_file = Path(".env")

    # Read existing .env or create from example
    if env_file.exists():
        content = env_file.read_text()
    else:
        example_file = Path(".env.example")
        if example_file.exists():
            content = example_file.read_text()
        else:
            content = ""

    # Update or add token
    lines = content.split("\n")
    token_found = False

    for i, line in enumerate(lines):
        if line.startswith("HA_TEST_TOKEN="):
            lines[i] = f"HA_TEST_TOKEN={token}"
            token_found = True
            break

    if not token_found:
        lines.append(f"HA_TEST_TOKEN={token}")

    # Write back
    env_file.write_text("\n".join(lines))
    print(f"✅ Token saved to {env_file}")


def main():
    """Execute main setup function."""
    # base_url = os.getenv("HA_URL", "http://localhost:8123")

    # Option 1: Use existing token from environment
    existing_token = os.getenv("HA_TEST_TOKEN")
    if existing_token and existing_token != "test_token":
        print("✅ Using existing token from environment")
        return 0

    # Option 2: Use bypass auth for testing (recommended)
    print("\n🔧 Recommended: Use bypass auth for testing")
    print("Add this to your tests/e2e/docker/config/configuration.yaml:")
    print("\nhomeassistant:")
    print("  auth_providers:")
    print("    - type: bypass")
    print("      trusted_users:")
    print("        127.0.0.1: test_user")
    print("\nThis allows authentication without tokens for testing.")

    # Option 3: Manual token creation
    print("\n📝 Alternative: Create token manually")
    print("1. Start Home Assistant: make start")
    print("2. Visit http://localhost:8123")
    print("3. Create user account")
    print("4. Go to Profile -> Long-Lived Access Tokens")
    print("5. Create token and run:")
    print("   export HA_TEST_TOKEN='your-token-here'")
    print("   # Or add to .env file")

    return 0


if __name__ == "__main__":
    sys.exit(main())
