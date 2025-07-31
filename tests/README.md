# Home Assistant Testing Framework

## Overview

This testing framework provides multiple levels of testing for Home Assistant automations, from pure logic tests to integration tests.

## Does Each Test Type Use Home Assistant?

| Test Type       | Uses Real HA? | What It Uses                    | Requirements             |
| --------------- | ------------- | ------------------------------- | ------------------------ |
| **Unit/Logic**  | ❌ No         | Pure Python functions           | None                     |
| **Unit/Mock**   | ❌ No         | Mock objects simulating HA      | None                     |
| **Integration** | ✅ Yes        | Real HA core components         | Python 3.11+ & HA        |
| **UI**          | ✅ Yes        | Real HA with browser automation | HA + Playwright browsers |

## Directory Structure

```
tests/
├── unit/                    # No Home Assistant needed
│   ├── logic/              # Pure Python logic tests
│   │   └── README.md       # ❌ No HA - tests pure functions
│   └── mock/               # Mock-based behavior tests
│       └── README.md       # ❌ No HA - uses mock objects
│
├── integration/            # Real Home Assistant required
│   ├── test_*.py          # ✅ Uses real HA (in-memory)
│   └── README.md          # ✅ Requires actual Home Assistant
│
├── ui/                    # Browser-based UI tests
│   ├── test_*.py         # ✅ Uses real HA + Playwright
│   └── README.md         # ✅ Requires HA + browsers
│
├── helpers/               # Test utilities and fixtures
│   ├── automation_logic.py    # Pure Python logic functions
│   ├── ha_mocks.py           # Mock HA components
│   ├── fast_ha_test.py       # Minimal HA instance helper
│   ├── automation_validation.py  # YAML automation validation
│   └── automation_test_base.py   # Base class with validation
│
└── README.md              # This file
```

## Quick Start Guide

### 1. Run Tests WITHOUT Home Assistant

These work on any system with Python:

```bash
# Run all unit tests (no HA needed)
make test:unit          # Runs both logic and mock tests

# Run specific types
make test:unit:logic    # Pure Python logic tests
make test:unit:mock     # Mock-based behavior tests
```

### 2. Run Tests WITH Home Assistant

These require Home Assistant or Docker:

```bash
# Integration tests (needs Python 3.11+ and HA installed)
make test:integration    # Run all integration tests

# UI tests (needs HA running + Playwright browsers)
make test:ui            # Run UI tests in parallel (headless)
make test:ui:headed     # Run with visible browser
make test:ui:debug      # Run in debug mode (slow, single worker)
```

## Choosing the Right Test Type

### Use Logic Tests When:

- Testing business rules and calculations
- Validating decision logic
- You want the fastest tests
- No Home Assistant available

### Use Mock Tests When:

- Testing service call patterns
- Verifying state transitions
- Testing automation workflows
- No Home Assistant available

### Use Integration Tests When:

- Testing real YAML configurations
- Validating actual HA behavior
- Testing component interactions
- Home Assistant is available

### Use UI Tests When:

- Testing user interface interactions
- Validating visual elements
- Testing user workflows
- Verifying browser compatibility
- Home Assistant + browsers available

## Test Execution Speed

| Test Type   | Speed  | Parallel | Isolation       |
| ----------- | ------ | -------- | --------------- |
| Logic       | ~1ms   | ✅ Yes   | Complete        |
| Mock        | ~10ms  | ✅ Yes   | Complete        |
| Integration | ~500ms | ✅ Yes   | Process-level   |
| UI          | ~2-5s  | ✅ Yes   | Browser context |

## Current Testing Status

✅ **Working Tests** (90 tests):

- 63 logic tests - Pure Python automation logic
- 27 mock tests - Simulated HA behavior

⚠️ **Skipped Tests** (15 tests):

- Integration tests - Require Python 3.11+ for Home Assistant

## Running All Tests

```bash
# All available tests in parallel
make test

# Unit tests only
make test:unit
```

## Automation Validation Helpers

### Why Validate?

**Always validate YAML automations before testing!** This catches configuration errors early and provides better error messages than Home Assistant's generic "invalid config" errors.

### Using the Validation Helpers

```python
from tests.helpers.automation_validation import (
    validate_automation_config,  # Returns (is_valid, errors)
    assert_valid_automation,  # Raises ValidationError if invalid
    get_automation_summary,  # Human-readable description
)

# Load your automation
with open("automation.yaml") as f:
    config = yaml.safe_load(f)

# Method 1: Check and handle errors
is_valid, errors = validate_automation_config(config)
if not is_valid:
    for error in errors:
        print(f"Error: {error}")

# Method 2: Assert valid (for tests)
assert_valid_automation(config)  # Raises if invalid

# Get a summary
print(get_automation_summary(config))
# Output: "ID: sunset | Alias: Sunset Lights | Triggers: 1 (sun) | Actions: 1"
```

### What Gets Validated?

- ✅ **Structure**: Required fields (trigger/action), correct data types
- ✅ **IDs**: Automation ID format and uniqueness within config
- ✅ **Triggers**: Valid platforms, required fields, time formats
- ✅ **Conditions**: Valid types, logical operators, required fields
- ✅ **Actions**: Service format (domain.service), delay formats
- ✅ **Service Data**: Domain-specific validation (brightness 0-100, etc.)
- ✅ **Time Formats**: HH:MM or HH:MM:SS validation
- ✅ **Numeric Ranges**: Temperature limits, brightness percentages

### Example Validation Errors

```yaml
# This automation has several errors:
alias: Bad Automation
trigger:
  - platform: invalid_platform  # ❌ Invalid platform
    at: "25:00"                # ❌ Invalid time
condition:
  - condition: state
    entity_id: sensor.test     # ❌ Missing 'state' field
action:
  - service: turn_on           # ❌ Missing domain
  - delay:                     # ❌ Missing time units
```

Validation output:

```
- Trigger 0 has invalid platform 'invalid_platform'
- Time trigger 0 has invalid time format: 25:00
- State condition 0 missing required 'state' field
- Action 0 service 'turn_on' must be in format 'domain.service'
- Action 1 delay must have time units
```

### Using the Test Base Class

For the easiest testing experience, use `AutomationTestBase`:

```python
from tests.helpers.automation_test_base import AutomationTestBase

class TestMyAutomation(AutomationTestBase):
    AUTOMATION_FILE = "path/to/automation.yaml"

    async def test_automation(self, hass, automation_config, service_tracker):
        # automation_config is pre-validated ✅
        # Validation errors fail the test with clear messages
        # Use built-in helpers for common assertions
```

### Best Practices

1. **Always validate** YAML automations in tests
1. **Validate early** - In fixtures or setup methods
1. **Use clear messages** - The validation errors are descriptive
1. **Test invalid configs** - Write tests for validation itself
1. **Share validation** - Use the base class for consistency

### Bulk Validation Script

Validate all automations in a directory:

```bash
# Validate all YAML files in tests/
python scripts/validate_automations.py

# Validate specific directory
python scripts/validate_automations.py tests/integration

# Returns exit code 1 if any automations are invalid
```

## Key Takeaway

**You don't need Home Assistant installed to test your automation logic!**

- Logic tests validate your business rules
- Mock tests verify automation behavior
- Integration tests confirm everything works in real HA
- **Validation helpers ensure your automations are correct before testing**

This layered approach lets you develop and test automations even without Home Assistant installed, while still having the option for full integration testing when needed.
