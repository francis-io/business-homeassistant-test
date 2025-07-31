# How Integration Tests Work

## Overview

Integration tests work by using **Home Assistant's actual core components** but in a minimal, optimized configuration. This provides the benefits of testing with real HA components while maintaining fast execution speeds.

## Architecture

```
┌─────────────────────────────────────────────┐
│          Integration Test                    │
├─────────────────────────────────────────────┤
│  1. Load Minimal HA Components              │
│     - Core, State Machine, Service Registry │
│     - Event Bus, Automation Component        │
│     - Time/Sun components as needed         │
│                                             │
│  2. Load Automation YAML                    │
│     - Real YAML parsing                     │
│     - Real validation                       │
│     - Real automation setup                 │
│                                             │
│  3. Execute Test                            │
│     - Set states                            │
│     - Execute automation actions            │
│     - Verify results                        │
└─────────────────────────────────────────────┘
```

## Key Components Used

### 1. **State Machine** (Real)

```python
# This is the ACTUAL Home Assistant state machine
hass.states.async_set("light.test", "on", {"brightness": 255})
state = hass.states.get("light.test")
assert state.state == "on"
assert state.attributes["brightness"] == 255
```

### 2. **Service Registry** (Real)

```python
# Real service validation and execution
await hass.services.async_call(
    "light", "turn_on", {"entity_id": "light.test", "brightness": 128}, blocking=True
)
```

### 3. **Event Bus** (Real)

```python
# Real event system
events = []
hass.bus.async_listen("state_changed", lambda event: events.append(event))
```

### 4. **Automation Engine** (Real)

```python
# Real automation loading and validation
await async_setup_component(hass, "automation", {"automation": yaml_config})
```

## What's Different from Production HA

| Feature           | Production HA       | Integration Tests |
| ----------------- | ------------------- | ----------------- |
| State Machine     | ✅ Full             | ✅ Full           |
| Service Registry  | ✅ Full             | ✅ Full           |
| Event Bus         | ✅ Full             | ✅ Full           |
| Automation Engine | ✅ Full             | ✅ Full           |
| Entity Creation   | ✅ Creates entities | ❌ No entities    |
| Network I/O       | ✅ Yes              | ❌ No             |
| Database          | ✅ Yes              | ❌ No             |
| Web Server        | ✅ Yes              | ❌ No             |
| Integrations      | ✅ All available    | ❌ Core only      |

## Example: How Automations Work

### In Production:

```python
# Automation creates an entity: automation.sunset_lights
# Can be triggered via service call:
await hass.services.async_call(
    "automation", "trigger", {"entity_id": "automation.sunset_lights"}
)
```

### In Integration Tests:

```python
# Load automation configuration
config = yaml.safe_load(open("sunset_automation.yaml"))

# Automation is validated but no entity created
# Execute actions directly:
for action in config["action"]:
    await hass.services.async_call(
        action["service"].split(".")[0],
        action["service"].split(".")[1],
        action.get("data", {}),
        blocking=True,
    )
```

## Real Examples from Tests

### 1. Valid Automation (Works)

```python
await async_setup_component(
    hass,
    "automation",
    {
        "automation": {
            "id": "test_automation",
            "alias": "Test",
            "trigger": {"platform": "state", "entity_id": "sensor.test"},
            "action": {"service": "light.turn_on", "entity_id": "light.test"},
        }
    },
)
# ✅ Automation loads successfully
# ✅ YAML is validated
# ✅ Can execute actions
# ❌ No automation.test_automation entity
```

### 2. Invalid Automation (Fails)

```python
# This would fail in integration tests (HA rejects it)
await async_setup_component(
    hass,
    "automation",
    {
        "automation": {
            "trigger": {"platform": "invalid_platform"},  # ❌ Invalid
            "action": {"service": "turn_on"},  # ❌ Missing domain
        }
    },
)
# Real HA validation catches these errors!
```

## Benefits

1. **Real Validation**: Catches YAML errors, invalid service calls, bad configurations
1. **Fast Execution**: ~500ms per test vs 10+ seconds for Docker tests
1. **Accurate Behavior**: Uses actual HA components, not mocks
1. **Easy Debugging**: Direct access to HA internals
1. **CI/CD Friendly**: No Docker required, runs anywhere

## Performance: Why It's Fast

### 1. **Minimal Components**

```python
# Production HA: ~100+ components loaded
# Integration Tests: ~10 essential components only
```

### 2. **No I/O Operations**

- No network calls
- No database writes
- No file system operations (except loading YAML)

### 3. **In-Memory Only**

- Everything runs in RAM
- No persistence layer
- No external dependencies

## Comparison

| Feature         | Unit Test | Integration Test | Docker Test |
| --------------- | --------- | ---------------- | ----------- |
| Uses Real HA    | ❌        | ✅               | ✅          |
| YAML Validation | ❌        | ✅               | ✅          |
| Speed           | ~1ms      | ~500ms           | ~10s        |
| Dependencies    | None      | Python/HA        | Docker      |
| Debugging       | Easy      | Easy             | Hard        |
| Entity Creation | N/A       | ❌               | ✅          |

## Writing Effective Integration Tests

```python
class TestMyAutomation(AutomationTestBase):
    AUTOMATION_FILE = "my_automation.yaml"

    async def test_behavior(self, hass, automation_config, service_tracker):
        # 1. Set initial state
        hass.states.async_set("sensor.temperature", "25")

        # 2. Execute automation actions
        for action in automation_config["action"]:
            await hass.services.async_call(
                action["service"].split(".")[0],
                action["service"].split(".")[1],
                action.get("data", {}),
                blocking=True,
            )

        # 3. Verify results
        assert service_tracker.has_calls("climate", "set_temperature")
        assert hass.states.get("climate.room").attributes["temperature"] == 22
```

## When Integration Tests Are Sufficient

Integration tests are perfect for:

- ✅ Automation logic testing
- ✅ Service call validation
- ✅ State machine interactions
- ✅ YAML configuration validation
- ✅ Component interaction testing

Consider Docker tests only for:

- Device-specific integrations
- Network-dependent features
- Database persistence testing
- Full UI interaction testing

## Summary

Integration tests provide **high confidence** that your automations will work in production because they use Home Assistant's actual core components. The only difference is they skip the slow parts (network, database, external services) that aren't needed for testing automation logic.
