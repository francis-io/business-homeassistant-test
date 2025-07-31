#!/usr/bin/env python3
"""Validate that HA mocks match expected interfaces."""
import sys
from pathlib import Path
import ast


def validate_ha_mocks():
    """Check mock objects implement required HA interfaces."""
    errors = []
    
    # Expected methods for common mocks
    expected_interfaces = {
        "MockHass": {
            "states", "services", "async_block_till_done", 
            "bus", "data", "config"
        },
        "MockState": {
            "state", "attributes", "entity_id", "last_changed",
            "last_updated", "context"
        },
        "MockService": {
            "call", "async_call", "has_service", "services"
        },
    }
    
    # Find mock definitions
    mock_files = [
        Path("tests/helpers/ha_mocks.py"),
        *Path("tests/unit/mock").rglob("*.py")
    ]
    
    for mock_file in mock_files:
        if not mock_file.exists():
            continue
            
        content = mock_file.read_text()
        tree = ast.parse(content)
        
        # Find class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name in expected_interfaces:
                    # Get all methods/attributes
                    defined = set()
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            defined.add(item.name)
                        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            defined.add(item.target.id)
                    
                    # Check for missing interfaces
                    missing = expected_interfaces[node.name] - defined
                    if missing:
                        errors.append(
                            f"{mock_file}: {node.name} missing interfaces: {missing}"
                        )
    
    # Check mock usage patterns
    for test_file in Path("tests/unit/mock").rglob("test_*.py"):
        content = test_file.read_text()
        
        # Look for direct HA imports in mock tests
        if "from homeassistant" in content and "ha_mocks" not in content:
            errors.append(
                f"{test_file}: Mock tests should use ha_mocks instead of direct HA imports"
            )
    
    if errors:
        print("HA mock validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(validate_ha_mocks())