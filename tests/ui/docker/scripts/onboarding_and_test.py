#!/usr/bin/env python3
"""Perform Home Assistant onboarding and then verify it's ready for testing.

This combines the onboarding.py and test_onboarding_complete.py scripts.
"""
import os
import subprocess
import sys


def main() -> None:
    # First, run the onboarding script
    print("=== Running onboarding ===")
    onboarding_result = subprocess.run(
        [
            sys.executable,
            "/scripts/onboarding.py",
            "--base-url",
            os.getenv("HA_URL", "http://home-assistant-test-server:8123"),
        ],
        capture_output=True,
        text=True,
    )

    print(onboarding_result.stdout)
    if onboarding_result.stderr:
        print(onboarding_result.stderr, file=sys.stderr)

    if onboarding_result.returncode != 0:
        print("Onboarding failed!")
        sys.exit(1)

    # Now run the readiness tests
    print("\n=== Running readiness tests ===")
    test_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "/scripts/test_onboarding_complete.py",
            "-v",
        ],
        env={
            **os.environ,
            "HA_URL": os.getenv("HA_URL", "http://home-assistant-test-server:8123"),
        },
    )

    # Exit with the test result code
    sys.exit(test_result.returncode)


if __name__ == "__main__":
    main()
