#!/usr/bin/env python3
"""Validate test files are in the correct directory structure."""
import ast
import sys
from pathlib import Path


def check_test_structure():
    """Ensure tests follow the logic/mock/integration structure."""
    errors = []
    test_root = Path("tests")

    # Define what imports are allowed in each test type
    logic_forbidden = {"homeassistant", "pytest_homeassistant_custom", "ha_mocks"}
    mock_required = {"ha_mocks"}
    integration_required = {"fast_ha_test"}

    for test_file in test_root.rglob("test_*.py"):
        if test_file.parent.name == "helpers":
            continue

        content = test_file.read_text()
        tree = ast.parse(content)
        imports = set()

        # Extract all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Check if importing from ha_mocks or fast_ha_test
                    if "ha_mocks" in node.module:
                        imports.add("ha_mocks")
                    elif "fast_ha_test" in node.module:
                        imports.add("fast_ha_test")
                    else:
                        imports.add(node.module.split(".")[0])

        # Check based on test type
        if "logic" in str(test_file):
            forbidden = imports & logic_forbidden
            if forbidden:
                errors.append(
                    f"{test_file}: Logic tests cannot import {forbidden}. "
                    "Extract logic to automation_logic.py"
                )

        elif "mock" in str(test_file):
            if not any(req in imports for req in mock_required):
                errors.append(f"{test_file}: Mock tests must use ha_mocks for proper isolation")

        elif "integration" in str(test_file):
            # Only check if the test seems to be using HA functionality
            ha_indicators = {"hass", "MockHomeAssistant", "homeassistant", "async"}
            if any(indicator in content for indicator in ha_indicators):
                if not any(req in imports for req in integration_required):
                    errors.append(f"{test_file}: Integration tests should use fast_ha_test helper")

    if errors:
        print("Test structure validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(check_test_structure())
