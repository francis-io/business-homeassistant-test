"""Example showing how to validate YAML automations before testing.

This demonstrates the recommended pattern for validating automation
configurations before they are used in tests.
"""

import pytest
import yaml
from pathlib import Path

# Import validation helpers
from tests.helpers.automation_validation import (
    validate_automation_config,
    assert_valid_automation,
    get_automation_summary,
    ValidationError
)


def load_and_validate_automation(yaml_path: str):
    """Load and validate an automation from a YAML file.
    
    This is the recommended pattern for loading automations in tests.
    """
    # Load the YAML
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Validate it (raises ValidationError if invalid)
    assert_valid_automation(config)
    
    # Log what we're testing
    print(f"Loaded automation: {get_automation_summary(config)}")
    
    return config


# Example 1: Using in a pytest fixture
@pytest.fixture
def my_automation():
    """Load and validate an automation for testing."""
    yaml_path = Path(__file__).parent / "my_automation.yaml"
    return load_and_validate_automation(yaml_path)


# Example 2: Handling validation errors gracefully
def test_automation_validation():
    """Test that an automation is valid."""
    # Create an example automation
    automation = {
        'id': 'example_automation',
        'alias': 'Example Automation',
        'trigger': [
            {'platform': 'time', 'at': '10:00:00'}
        ],
        'action': [
            {
                'service': 'light.turn_on',
                'target': {'entity_id': 'light.living_room'},
                'data': {'brightness_pct': 100}
            }
        ]
    }
    
    # Validate it
    is_valid, errors = validate_automation_config(automation)
    
    if is_valid:
        print("✅ Automation is valid!")
        print(f"Summary: {get_automation_summary(automation)}")
    else:
        print("❌ Automation has errors:")
        for error in errors:
            print(f"  - {error}")
    
    assert is_valid, f"Automation validation failed: {errors}"


# Example 3: Testing invalid automations
def test_invalid_automation_detection():
    """Test that validation catches common errors."""
    # Automation with multiple errors
    bad_automation = {
        'trigger': [
            {'platform': 'time', 'at': '25:00'},  # Invalid time
            {'platform': 'invalid_platform'},      # Invalid platform
        ],
        'action': [
            {'service': 'turn_on'},  # Missing domain
            {'delay': {}}           # Missing time units
        ]
    }
    
    # This should fail validation
    is_valid, errors = validate_automation_config(bad_automation)
    
    assert not is_valid
    assert len(errors) >= 4  # At least 4 errors
    
    # Check specific errors are caught
    assert any('invalid time format' in e for e in errors)
    assert any('invalid platform' in e for e in errors)
    assert any('domain.service' in e for e in errors)
    assert any('time units' in e for e in errors)


# Example 4: Using the assert helper
def test_with_assert_helper():
    """Test using the assert_valid_automation helper."""
    good_automation = {
        'id': 'test',
        'trigger': [{'platform': 'time', 'at': '10:00'}],
        'action': [{'service': 'light.turn_on'}]
    }
    
    # This passes silently if valid
    assert_valid_automation(good_automation)
    
    bad_automation = {
        'action': [{'service': 'invalid'}]  # Missing trigger and bad service
    }
    
    # This raises ValidationError
    with pytest.raises(ValidationError) as exc:
        assert_valid_automation(bad_automation)
    
    # The error message contains all validation errors
    assert "Invalid automation configuration" in str(exc.value)


if __name__ == "__main__":
    # Run the examples
    print("Example 1: Valid automation")
    test_automation_validation()
    
    print("\nExample 2: Invalid automation detection")
    test_invalid_automation_detection()
    print("✅ Invalid automation correctly detected")
    
    print("\nExample 3: Using assert helper")
    test_with_assert_helper()
    print("✅ Assert helper working correctly")