# Integration Testing Guide

## Overview

This framework provides integration testing for Home Assistant automations using real HA core components in an in-memory instance. These tests validate actual YAML configurations and automation behavior without requiring Docker.

## Features

- ✅ Test actual YAML automation configurations
- ✅ Use real Home Assistant core components
- ✅ Run in ~500ms without Docker
- ✅ Support parallel execution with pytest-xdist
- ✅ Validate automation logic and service calls

## Running Integration Tests

```bash
# Install dependencies (includes Home Assistant)
make setup-integration

# Run integration tests
make test:integration

# Run with verbose output
pytest tests/integration -v

# Run specific test file
pytest tests/integration/sunset_automation_test.py -v

# Run with specific number of workers
pytest tests/integration -n 2
```

## Writing Integration Tests

### Using the Base Class (Recommended)

```python
from tests.helpers.automation_test_base import AutomationTestBase

class TestMyAutomation(AutomationTestBase):
    AUTOMATION_FILE = "tests/integration/my_automation.yaml"
    
    async def test_automation_behavior(self, hass, automation_config, service_tracker):
        """Test actual YAML automation with validation."""
        # automation_config is pre-validated ✅
        
        # Set initial state
        hass.states.async_set('sensor.temperature', '25')
        
        # Execute automation actions
        for action in automation_config['action']:
            await hass.services.async_call(
                action['service'].split('.')[0],
                action['service'].split('.')[1],
                action.get('data', {}),
                blocking=True
            )
        
        # Verify service calls
        assert service_tracker.has_calls('climate', 'set_temperature')
        
        # Verify state changes
        assert hass.states.get('climate.room').attributes['temperature'] == 22
```

### Manual Test Structure

```python
import pytest
import yaml
from homeassistant.setup import async_setup_component

@pytest.mark.asyncio
async def test_automation(hass, service_tracker):
    """Test automation without base class."""
    # Load and validate automation
    with open('automation.yaml') as f:
        config = yaml.safe_load(f)
    
    # Setup automation component
    await async_setup_component(hass, 'automation', {
        'automation': config
    })
    
    # Set states
    hass.states.async_set('light.test', 'off')
    
    # Execute actions
    for action in config['action']:
        await hass.services.async_call(
            action['service'].split('.')[0],
            action['service'].split('.')[1],
            action.get('data', {}),
            blocking=True
        )
    
    # Verify results
    assert hass.states.get('light.test').state == 'on'
```

## Key Concepts

### Test Environment vs Production

| Aspect | Production HA | Test Environment |
|--------|--------------|------------------|
| Automation Entities | Created as `automation.*` | Not created |
| Service Calls | Via entity triggers | Direct execution |
| YAML Validation | On startup | During test |
| State Machine | Full persistence | In-memory only |
| External I/O | Network, Database | None |

### Best Practices

1. **Always validate YAML** - Use validation helpers before testing
2. **Include ID field** - Required for proper automation identification
3. **Focus on behavior** - Test service calls and state changes
4. **Execute directly** - Don't expect automation entities
5. **Mock services** - Register handlers to track calls

### Common Patterns

#### Time-Based Automation
```python
async def test_sunset_lights(self, hass, automation_config, service_tracker):
    # Test automation that triggers at sunset
    for action in automation_config['action']:
        await hass.services.async_call(
            action['service'].split('.')[0],
            action['service'].split('.')[1],
            action.get('data', {}),
            blocking=True
        )
    
    # Verify lights turned on
    assert service_tracker.has_calls('light', 'turn_on')
```

#### Conditional Automation
```python
async def test_conditional_action(self, hass, automation_config):
    # Set condition state
    hass.states.async_set('sensor.temperature', '30')
    
    # Execute with conditions
    for action in automation_config['action']:
        # Check conditions if present
        if 'condition' in automation_config:
            # Evaluate conditions here
            pass
        
        await hass.services.async_call(
            action['service'].split('.')[0],
            action['service'].split('.')[1],
            action.get('data', {}),
            blocking=True
        )
```

## Service Tracking

The `service_tracker` fixture helps verify service calls:

```python
# Check if service was called
assert service_tracker.has_calls('light', 'turn_on')

# Get all calls for a service
calls = service_tracker.get_calls('notify', 'mobile_app')
assert len(calls) == 1
assert calls[0]['message'] == 'Water leak detected!'

# Verify call data
call = service_tracker.get_last_call('climate', 'set_temperature')
assert call['temperature'] == 22
```

## Test Organization

### Directory Structure
```
tests/integration/
├── climate_control_test.py        # Climate automation
├── doorbell_notification_test.py  # Doorbell tests  
├── energy_saving_test.py          # Energy optimization
├── motion_security_light_test.py  # Motion sensor tests
├── sunset_automation_test.py       # Time-based automation
├── *.yaml                         # Automation configurations
└── README.md                      # This guide
```

### Test Categories

| Category | Examples | Key Testing Points |
|----------|----------|-------------------|
| Time-Based | Sunset, Schedule | Time triggers, conditions |
| Sensor-Based | Motion, Temperature | State changes, thresholds |
| Zone-Based | Entry, Exit | Location triggers |
| Notification | Alerts, Messages | Service data, priorities |
| Complex | Multi-action, Choose | Logic flow, conditions |

## Troubleshooting

### Python Version Issues
```
ModuleNotFoundError: No module named 'homeassistant'
```
**Solution**: Upgrade to Python 3.11+ (HA requirement)

### Service Not Found
```
Service light.turn_on not found
```
**Solution**: Mock the service in your fixture

### Automation Not Loading
```
Invalid config for [automation]
```
**Solution**: Validate YAML with validation helpers

## Performance Tips

1. **Use parallel execution** - Tests are isolated and thread-safe
2. **Minimize setup** - Share fixtures when possible
3. **Batch similar tests** - Group by automation type
4. **Skip when appropriate** - Use pytest marks for conditional tests

## CI/CD Integration

```yaml
# GitHub Actions example
test:
  runs-on: ubuntu-latest
  strategy:
    matrix:
      python-version: [3.11, 3.12]
  
  steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install uv
        make setup-integration
    
    - name: Run integration tests
      run: make test:integration
```

## Summary

Integration tests provide confidence that your automations work correctly with real Home Assistant components. They catch YAML errors, validate service calls, and ensure proper state management - all without the overhead of Docker or a full HA instance.