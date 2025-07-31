# Integration Tests

## Overview

Integration tests use real Home Assistant core components to test automations in a realistic environment. These tests create an in-memory Home Assistant instance for fast, reliable testing without Docker.

## Does it use Home Assistant?

**Yes!** Integration tests use actual Home Assistant core components:
- Real YAML parsing and validation
- Actual automation engine execution
- Real state machine and event system
- Actual service registry and calls

**Note**: Currently SKIPPED because Home Assistant requires Python 3.11+ (we have 3.10)

## What's Different from Unit Tests

| Aspect | Unit Tests (Logic/Mock) | Integration Tests |
|--------|------------------------|-------------------|
| **Real Home Assistant** | ❌ Never | ✅ Always |
| **YAML Validation** | ❌ No | ✅ Yes |
| **Real State Machine** | ❌ Simulated | ✅ Actual |
| **Real Services** | ❌ Mocked | ✅ Actual |
| **Dependencies** | None | Home Assistant |
| **Speed** | Milliseconds | ~500ms |

## Test Structure

Each integration test follows this pattern:

1. **Create HA instance** - In-memory Home Assistant with minimal setup
2. **Load automation** - Parse and validate YAML configuration
3. **Setup states** - Configure initial entity states
4. **Execute action** - Run automation actions directly
5. **Verify results** - Check service calls and state changes

## Running Integration Tests

```bash
# Run all integration tests (requires Python 3.11+)
make test:integration

# Or directly with pytest
pytest tests/integration -v
```

## Current Status

⚠️ **Integration Tests are SKIPPED** because:
- Home Assistant requires Python 3.11+
- We're using Python 3.10
- Tests skip with: "Home Assistant not available"

To enable these tests:
```bash
# Install Python 3.11+ and update dependencies
uv venv --python 3.11
uv pip install -r tests/integration/requirements.txt
```

## Key Testing Insights

### Test Environment vs Production
The Home Assistant test environment behaves differently from a running instance:
- **Automation entities** are not automatically created in tests
- **Service calls** need to be mocked and tracked manually
- **State changes** must be simulated explicitly

### Best Practices
1. **Always include an `id` field** in automation YAML for proper identification
2. **Focus on behavior, not entities** - Test service calls and state changes
3. **Mock services appropriately** - Register mock handlers to track calls
4. **Execute actions directly** when automation entities aren't available
5. **Use validation helpers** - Always validate YAML before testing

### Common Pitfalls
- ❌ Expecting `automation.*` entities to exist in tests
- ❌ Trying to trigger automations via entity IDs
- ❌ Assuming entity attributes are available

### Recommended Approach
- ✅ Load automation config and verify structure
- ✅ Mock services and track their calls
- ✅ Execute automation actions directly
- ✅ Verify expected service calls and state changes
- ✅ Use `AutomationTestBase` for consistent validation

## Example Test

```python
from tests.helpers.automation_test_base import AutomationTestBase

class TestMyAutomation(AutomationTestBase):
    AUTOMATION_FILE = "tests/integration/my_automation.yaml"
    
    async def test_automation_behavior(self, hass, automation_config, service_tracker):
        # automation_config is pre-validated ✅
        # Set initial state
        hass.states.async_set("light.test", "off")
        
        # Execute automation actions
        for action in automation_config['action']:
            await hass.services.async_call(
                action['service'].split('.')[0],
                action['service'].split('.')[1],
                action.get('data', {}),
                blocking=True
            )
        
        # Verify results
        assert hass.states.get("light.test").state == "on"
```

## Summary

Integration tests use **real Home Assistant** to validate that automations work correctly in the actual system. While unit tests (logic/mock) are fast and don't need HA, integration tests provide confidence that your automations will work in production.

Understanding how the test environment differs from production HA is crucial for writing effective integration tests. Focus on testing the behavior and effects of your automations rather than expecting the same entity structure as in a running instance.