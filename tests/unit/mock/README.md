# Mock Tests

## Purpose

These tests validate Home Assistant automation **behavior** using mock objects that simulate Home Assistant components.

## Does it use Home Assistant?

**No.** These tests do NOT use actual Home Assistant. They use **mock objects** that simulate Home Assistant's behavior for testing purposes.

## What's Being Tested

- **Service Calls**: Verify the correct services are called with correct parameters
- **State Changes**: Ensure entities change state as expected
- **Automation Flow**: Test the sequence of actions in response to triggers
- **Integration Points**: Verify how different components interact

## How Mocks Work

```python
# We use a MockHomeAssistant object that simulates HA behavior
hass = MockHomeAssistant()

# Set a state (simulated)
hass.states.set('light.bedroom', 'off')

# Call a service (captured but not executed)
hass.services.call('light', 'turn_on', {'entity_id': 'light.bedroom'})

# Verify the state changed (manually updated in test)
assert hass.states.get('light.bedroom').state == 'on'
```

## Mock Components Used

- **MockHomeAssistant**: Simulates the core HA object
- **MockStates**: Tracks entity states in memory
- **MockServices**: Captures service calls without executing them
- **MockState**: Represents an entity's state and attributes

## Benefits

- ✅ **No HA Required**: Tests run without Home Assistant installed
- ✅ **Fast Execution**: No real devices or network calls
- ✅ **Predictable**: Mocks behave consistently every time
- ✅ **Easy Setup**: No configuration files or Docker needed
- ✅ **Isolated Testing**: Each test starts with a clean state

## Limitations

- ❌ **Not Real HA**: Mocks approximate but don't perfectly replicate HA behavior
- ❌ **Manual State Updates**: Must manually update states after service calls
- ❌ **No YAML Validation**: Doesn't validate actual automation YAML syntax
- ❌ **No Real Components**: Can't test actual device integrations

## When to Use Mock Tests

- Testing service call sequences
- Verifying state transitions
- Testing automation workflows
- Simulating entity interactions
- Testing without Home Assistant installed

## Test Files

- `test_time_based_light.py` - Mock light automations with time triggers
- `test_notification.py` - Mock notification service calls and conditions
- `test_zone_entry.py` - Mock zone entry/exit triggers and actions
- `test_simple_demo.py` - Basic examples of mock usage patterns

## Running Mock Tests

```bash
# Run all mock tests in parallel
make test:unit:mock

# Run a specific test file
pytest tests/unit/mock/test_notification.py -v

# Run with coverage
pytest tests/unit/mock --cov=tests.helpers.ha_mocks
```

## Key Differences from Real HA

1. **State Updates**: In real HA, calling `light.turn_on` automatically updates the light's state. In mocks, you must manually update it.

2. **Service Validation**: Real HA validates service parameters. Mocks accept any parameters.

3. **Async Behavior**: Real HA is fully async. Mocks simulate this but may not capture all timing nuances.

4. **Component Loading**: Real HA loads actual component code. Mocks just track calls.

## Summary

Mock tests let you verify your automation logic and service call patterns without needing Home Assistant installed. They're perfect for quick feedback during development and for testing on systems where Home Assistant can't be installed.
