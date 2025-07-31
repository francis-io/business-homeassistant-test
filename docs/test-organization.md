# Test Organization Guide

## Overview

Tests are organized into clear categories based on their dependencies and testing approach:

```
tests/
├── unit/
│   ├── logic/      # Pure Python logic tests (no HA dependencies)
│   └── mock/       # Mock-based HA behavior tests
├── integration/    # Tests requiring actual HA or Docker
├── ui/            # Browser-based UI tests
└── api/           # API endpoint tests
```

## Unit Tests

### Logic Tests (`tests/unit/logic/`)

**Purpose**: Test automation logic as pure Python functions without any Home Assistant dependencies.

**Characteristics**:
- No imports from Home Assistant
- Test business logic directly
- Execute in milliseconds
- 100% deterministic
- Easy to debug

**Examples**:
- `test_time_based_light_logic.py` - Time calculations, brightness logic
- `test_notification_logic.py` - Priority determination, rate limiting
- `test_zone_entry_logic.py` - Presence detection, occupancy calculations

**Running**:
```bash
make test-logic              # Run all logic tests in parallel
make test-unit-sequential    # Run sequentially for debugging
```

### Mock Tests (`tests/unit/mock/`)

**Purpose**: Test Home Assistant automation behavior using mock components.

**Characteristics**:
- Use mock Home Assistant objects
- Test service calls and state changes
- Verify automation workflows
- No real HA instance needed

**Examples**:
- `test_time_based_light.py` - Mock light automation behavior
- `test_notification.py` - Mock notification service calls
- `test_zone_entry.py` - Mock zone entry triggers

**Running**:
```bash
make test-mock    # Run all mock tests in parallel
```

## Integration Tests

### Integration Tests (`test_*.py`)

**Purpose**: Test actual YAML automations with real HA core components in an in-memory instance.

**Characteristics**:
- Use real HA core components
- Validate YAML syntax and execution
- Real state machine and service registry
- Skip gracefully if HA not available
- Run in ~500ms without Docker

**Status**: Currently skipped due to Python version requirements (need Python 3.11+).

**Running**:
```bash
make test:integration    # Run all integration tests
```

## Test Execution

### Parallel by Default

All test commands use pytest-xdist for parallel execution:

```bash
make test-unit    # All unit tests in parallel (logic + mock)
make test-all     # ALL tests in parallel
make test-logic   # Just logic tests in parallel
make test-mock    # Just mock tests in parallel
```

### Test by Scenario

Run specific automation scenarios:

```bash
make test-lights          # Time-based light tests
make test-notifications   # Notification tests  
make test-zones          # Zone entry tests
```

### Sequential Debugging

When debugging failures:

```bash
make test-unit-sequential    # Run tests one at a time
pytest tests/unit/logic -v -n 0    # Disable parallelism
```

## Best Practices

### 1. Choose the Right Test Type

**Use Logic Tests When**:
- Testing business rules
- Validating calculations
- Checking conditions
- Testing pure functions

**Use Mock Tests When**:
- Testing service calls
- Verifying state changes
- Testing automation flow
- Simulating HA behavior

**Use Integration Tests When**:
- Testing real YAML configs
- Validating component interactions
- Testing external integrations
- End-to-end scenarios

### 2. Test Organization

Each test file should:
- Have a clear focus (one automation type)
- Use descriptive test names
- Group related tests in classes
- Include docstrings

### 3. Parallel Safety

Ensure tests are parallel-safe:
- No shared state between tests
- Unique entity names
- Independent fixtures
- No file system conflicts

## Coverage Goals

- **Logic Tests**: 100% coverage (pure functions)
- **Mock Tests**: >95% coverage (behavior verification)
- **Integration Tests**: Critical paths covered
- **Overall**: >80% coverage

## Adding New Tests

### 1. New Logic Test

```python
# tests/unit/logic/test_new_automation_logic.py
from tests.helpers.automation_logic import my_logic_function

def test_my_logic():
    result = my_logic_function(input1, input2)
    assert result == expected_value
```

### 2. New Mock Test

```python
# tests/unit/mock/test_new_automation.py
async def test_my_automation(hass):
    # Setup
    hass.states.set('sensor.test', 'value')
    
    # Action
    await hass.services.call('automation', 'trigger')
    
    # Assert
    assert hass.states.get('light.test').state == 'on'
```

### 3. New Integration Test

```python
# tests/integration/test_new_integration.py
@pytest.mark.integration
async def test_real_automation(ha_client):
    await ha_client.set_state('sensor.test', 'value')
    result = await ha_client.trigger_automation('my_automation')
    assert result is True
```