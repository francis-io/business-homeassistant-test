# Logic Tests

## Purpose

These tests validate **pure Python automation logic** without any Home Assistant dependencies.

## Does it use Home Assistant?

**No.** These tests do NOT use Home Assistant at all. They test business logic as pure Python functions.

## What's Being Tested

- **Business Rules**: Should the light turn on? What brightness should be set?
- **Calculations**: Time-based calculations, brightness levels, temperature settings
- **Decision Logic**: Conditions, thresholds, state transitions
- **Pure Functions**: Input → Output transformations with no side effects

## Example

```python
# Testing pure logic function
def test_should_turn_on_evening_lights():
    result = should_turn_on_evening_lights(
        current_time=time(18, 30),
        is_after_sunset=True,
        light_state="off"
    )
    assert result is True  # Light should turn on
```

## Benefits

- ✅ **Ultra-fast**: Run in milliseconds (no I/O or external dependencies)
- ✅ **Deterministic**: Same inputs always produce same outputs
- ✅ **Easy to Debug**: Simple Python functions with clear inputs/outputs
- ✅ **100% Coverage**: Easy to test all code paths and edge cases
- ✅ **No Setup Required**: No Home Assistant installation needed

## When to Use Logic Tests

- Testing automation conditions and decision-making
- Validating calculations and transformations
- Testing business rules and thresholds
- Ensuring edge cases are handled correctly

## Test Files

- `test_time_based_light_logic.py` - Time calculations, brightness logic, scene selection
- `test_notification_logic.py` - Priority determination, rate limiting, grouping logic
- `test_zone_entry_logic.py` - Presence detection, occupancy calculations, zone transitions

## Running Logic Tests

```bash
# Run all logic tests in parallel
make test-logic

# Run a specific test file
pytest tests/unit/logic/test_notification_logic.py -v

# Run with coverage
pytest tests/unit/logic --cov=tests.helpers.automation_logic
```

## Key Point

These tests prove your automation logic is correct without needing Home Assistant. They test the "brain" of your automations - the decision-making logic that determines what should happen and when.
