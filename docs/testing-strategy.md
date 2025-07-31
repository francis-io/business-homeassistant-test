# Home Assistant Automation Testing Strategy

## Overview

This testing framework demonstrates a logic-first approach to testing Home Assistant automations. Instead of testing the YAML configuration or actual automation execution, we test the **business logic** that drives automation decisions.

## Testing Philosophy

### What We Test (Unit Tests)
- **Decision Logic**: "Should the light turn on?"
- **Calculations**: "What brightness should be set?"
- **Conditions**: "Are all requirements met?"
- **State Transitions**: "What happens when someone arrives home?"

### What We Don't Test (in Unit Tests)
- YAML configuration syntax
- Actual Home Assistant automation triggers
- Real device interactions
- Service handler execution

## Architecture

### 1. Logic Functions (`automation_logic.py`)
Pure Python functions that encapsulate automation logic:

```python
def should_turn_on_evening_lights(
    current_time: time,
    is_after_sunset: bool,
    light_state: str = "off"
) -> bool:
    """Determine if evening lights should turn on."""
    return (
        light_state == "off" and
        current_time >= time(18, 30) and
        is_after_sunset
    )
```

### 2. Logic Tests
Test the business rules without Home Assistant:

```python
def test_should_turn_on_after_sunset_at_correct_time():
    assert should_turn_on_evening_lights(
        current_time=time(18, 30),
        is_after_sunset=True,
        light_state="off"
    ) is True
```

### 3. Mock Framework
For testing service calls and state management:

```python
# MockHomeAssistant provides:
- states.set() / states.get()
- services.call()
- Basic state tracking
```

## Test Categories

### 1. Time-Based Automations
- Evening light schedules
- Brightness calculations throughout the day
- Time pattern triggers (every 15 minutes, etc.)
- Scene selection based on time and day
- Complex time conditions

### 2. Notification Logic
- Priority determination (high/medium/low)
- Rate limiting and deduplication
- Conditional notifications
- Escalation strategies
- Smart grouping logic

### 3. Zone/Presence Automations
- Arrival/departure actions
- First person home logic
- Occupancy calculations
- Climate mode selection
- Vacation simulation

## Benefits

### 1. **Fast Feedback**
- Tests run in milliseconds
- No Home Assistant instance needed
- Instant validation during development

### 2. **Test-Driven Development**
- Write logic tests first
- Implement logic functions
- Then create Home Assistant automations

### 3. **Regression Prevention**
- Catch logic errors before deployment
- Document expected behavior
- Ensure consistency across changes

### 4. **Maintainability**
- Logic separated from configuration
- Easy to understand and modify
- Reusable across different automations

## Real-World Examples

### Example 1: Adaptive Brightness
```python
def calculate_brightness_for_time(current_hour: int) -> int:
    if 6 <= current_hour < 8:
        return 77  # 30% - Gentle morning light
    elif 8 <= current_hour < 12:
        return 128  # 50% - Productive morning
    elif 12 <= current_hour < 17:
        return 204  # 80% - Bright afternoon
    # ... etc
```

### Example 2: Smart Notifications
```python
def should_send_water_leak_notification(
    sensor_state: str,
    previous_state: str,
    notification_sent_recently: bool
) -> bool:
    return (
        sensor_state == "on" and
        previous_state == "off" and
        not notification_sent_recently
    )
```

### Example 3: Zone Entry Actions
```python
def get_zone_entry_actions(
    person_state: str,
    previous_state: str,
    current_time: time,
    people_home_count: int
) -> Dict[str, List[Dict]]:
    # Returns specific actions for lights, climate, security, etc.
```

## Testing Strategy Layers

### Layer 1: Logic Tests (What we built)
- Pure Python functions
- Business rule validation
- Edge case handling
- ~100ms execution

### Layer 2: Integration Tests (Future)
- Real Home Assistant instance
- Actual automation loading
- Service execution verification
- ~10s execution

### Layer 3: End-to-End Tests (Future)
- Full scenario simulation
- Device state verification
- User journey validation
- ~60s execution

## Best Practices

1. **Keep Logic Pure**: No side effects in logic functions
2. **Test Edge Cases**: Midnight, transitions, boundaries
3. **Use Parametrized Tests**: Test multiple scenarios efficiently
4. **Document Intent**: Clear test names and docstrings
5. **Real-World Scenarios**: Test actual use cases

## Getting Started

### Running Logic Tests
```bash
# Run all logic tests (in parallel by default)
make test-logic

# Run specific category
pytest tests/unit/logic/test_notification_logic.py -v

# Run with coverage
pytest tests/unit/logic --cov=tests.helpers.automation_logic
```

### Adding New Logic
1. Add function to `automation_logic.py`
2. Write tests in `test_*_logic.py`
3. Implement Home Assistant automation using the logic

## Automation Validation

### Always Validate YAML Before Testing

**Important**: All YAML automations must be validated before being loaded in tests. This catches configuration errors early with clear, actionable error messages.

```python
# In your test fixtures or setup:
from tests.helpers.automation_validation import assert_valid_automation
import yaml

with open('automation.yaml') as f:
    config = yaml.safe_load(f)
    
# This will raise ValidationError with detailed errors if invalid
assert_valid_automation(config)
```

### What Gets Validated

- **Structure**: Required fields (trigger, action), correct data types
- **Triggers**: Valid platforms, required fields, time formats
- **Conditions**: Valid types, logical operators, required parameters
- **Actions**: Service format (domain.service), delay formats
- **Service Data**: Domain-specific validation (brightness 0-100, temperature ranges)

### Using Validation in Tests

```python
# Option 1: Manual validation
@pytest.fixture
def automation_config():
    with open('my_automation.yaml') as f:
        config = yaml.safe_load(f)
    assert_valid_automation(config)  # Validate before use
    return config

# Option 2: Use the base class (recommended)
from tests.helpers.automation_test_base import AutomationTestBase

class TestMyAutomation(AutomationTestBase):
    AUTOMATION_FILE = "path/to/automation.yaml"
    # Validation happens automatically!
```

### Example Validation Output

```python
# Invalid automation example:
config = {
    'trigger': [{'platform': 'time', 'at': '25:00'}],  # Bad time
    'action': [{'service': 'turn_on'}]  # Missing domain
}

is_valid, errors = validate_automation_config(config)
# errors = [
#     "Time trigger 0 has invalid time format: 25:00",
#     "Action 0 service 'turn_on' must be in format 'domain.service'"
# ]
```

## Conclusion

This approach separates "what should happen" (logic) from "how it happens" (Home Assistant configuration), making automations more testable, maintainable, and reliable. The validation layer ensures that all YAML configurations are correct before testing begins.