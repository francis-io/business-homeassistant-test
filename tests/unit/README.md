# Unit Tests Overview

This directory contains unit tests that run **without requiring Home Assistant** to be installed.

## Test Categories

### 📐 Logic Tests (`/logic`)

Pure Python functions testing automation logic with no dependencies.

### 🎭 Mock Tests (`/mock`)

Tests using mock objects to simulate Home Assistant behavior.

## Quick Comparison

| Aspect                        | Logic Tests                  | Mock Tests                   |
| ----------------------------- | ---------------------------- | ---------------------------- |
| **Uses Real Home Assistant?** | ❌ No                        | ❌ No                        |
| **Dependencies**              | None                         | Mock objects only            |
| **What's Tested**             | Business logic, calculations | Service calls, state changes |
| **Speed**                     | ~1ms per test                | ~10ms per test               |
| **Setup Required**            | None                         | None                         |
| **Best For**                  | Decision logic, algorithms   | Automation workflows         |

## Neither Uses Home Assistant!

**Important**: Both test types run completely without Home Assistant:

- **Logic tests** test pure Python functions (no HA at all)
- **Mock tests** use mock objects that simulate HA behavior

If you need to test with actual Home Assistant:

- Use **integration tests** (require HA installed or Docker)
- See `/tests/integration/` directory

## Running Tests

```bash
# Run ALL unit tests (logic + mock) in parallel
make test:unit

# Run only logic tests
make test:unit:logic

# Run only mock tests
make test:unit:mock
```

## When to Use Each

### Use Logic Tests When:

- Testing calculations or algorithms
- Validating business rules
- Testing conditions and thresholds
- You want the fastest possible tests

### Use Mock Tests When:

- Testing service call sequences
- Verifying state transitions
- Testing automation workflows
- Simulating component interactions

## Example Comparison

**Logic Test** (no HA involved):

```python
def test_brightness_calculation():
    brightness = calculate_brightness_for_time(hour=14)
    assert brightness == 204  # 80% at 2 PM
```

**Mock Test** (simulating HA):

```python
def test_light_automation(mock_hass):
    # Simulate state
    mock_hass.states.set("light.room", "off")

    # Simulate service call
    mock_hass.services.call("light", "turn_on")

    # Verify (manual update needed)
    assert mock_hass.states.get("light.room").state == "on"
```

## Coverage

Both test types contribute to overall test coverage:

- Logic tests: 100% coverage of automation logic
- Mock tests: 95%+ coverage of automation behavior
- Combined: Comprehensive testing without Home Assistant
