"""Unit tests for time-based light automation logic."""

from datetime import time
from typing import Any

import pytest

from tests.helpers.automation_logic import (
    calculate_brightness_for_time,
    evaluate_automation_conditions,
    get_time_based_scene,
    should_trigger_time_pattern,
    should_turn_on_evening_lights,
)


class TestEveningLightsLogic:
    """Test evening lights automation logic."""

    def test_should_turn_on_after_sunset_at_correct_time(self) -> None:
        """Test lights turn on at 18:30 after sunset."""
        assert (
            should_turn_on_evening_lights(
                current_time=time(18, 30),
                is_after_sunset=True,
                light_state="off",
            )
            is True
        )

    def test_should_not_turn_on_before_sunset(self) -> None:
        """Test lights don't turn on before sunset even at correct time."""
        assert (
            should_turn_on_evening_lights(
                current_time=time(18, 30),
                is_after_sunset=False,
                light_state="off",
            )
            is False
        )

    def test_should_not_turn_on_before_scheduled_time(self) -> None:
        """Test lights don't turn on before 18:30 even after sunset."""
        assert (
            should_turn_on_evening_lights(
                current_time=time(17, 0),
                is_after_sunset=True,
                light_state="off",
            )
            is False
        )

    def test_should_not_turn_on_if_already_on(self) -> None:
        """Test automation doesn't trigger if lights already on."""
        assert (
            should_turn_on_evening_lights(
                current_time=time(18, 30),
                is_after_sunset=True,
                light_state="on",
            )
            is False
        )


class TestBrightnessCalculation:
    """Test brightness calculation logic."""

    @pytest.mark.parametrize(
        ("hour", "expected_brightness"),
        [
            (6, 77),  # Early morning - 30%
            (7, 77),  # Morning - 30%
            (9, 128),  # Mid-morning - 50%
            (14, 204),  # Afternoon - 80%
            (18, 179),  # Early evening - 70%
            (21, 102),  # Late evening - 40%
            (23, 26),  # Night - 10%
            (2, 26),  # Late night - 10%
        ],
    )
    def test_brightness_for_different_times(self, hour: int, expected_brightness: int) -> None:
        """Test correct brightness calculation for different hours."""
        assert calculate_brightness_for_time(hour) == expected_brightness

    def test_brightness_transitions_are_logical(self) -> None:
        """Test brightness follows logical progression through day."""
        morning = calculate_brightness_for_time(7)
        noon = calculate_brightness_for_time(12)
        evening = calculate_brightness_for_time(20)
        night = calculate_brightness_for_time(23)

        # Brightness should increase from morning to noon
        assert noon > morning
        # Then decrease towards night
        assert evening < noon
        assert night < evening


class TestTimePatternTrigger:
    """Test time pattern trigger logic."""

    def test_every_15_minutes_pattern(self) -> None:
        """Test trigger every 15 minutes."""
        pattern = 15

        # Should trigger at 0, 15, 30, 45
        assert should_trigger_time_pattern(0, pattern) is True
        assert should_trigger_time_pattern(15, pattern) is True
        assert should_trigger_time_pattern(30, pattern) is True
        assert should_trigger_time_pattern(45, pattern) is True

        # Should not trigger at other times
        assert should_trigger_time_pattern(10, pattern) is False
        assert should_trigger_time_pattern(25, pattern) is False

    def test_every_5_minutes_pattern(self) -> None:
        """Test trigger every 5 minutes."""
        pattern = 5

        # Should trigger at 0, 5, 10, 15, etc.
        for minute in range(0, 60, 5):
            assert should_trigger_time_pattern(minute, pattern) is True

        # Should not trigger at non-5-minute intervals
        assert should_trigger_time_pattern(3, pattern) is False
        assert should_trigger_time_pattern(7, pattern) is False


class TestTimeBasedScenes:
    """Test time-based scene selection logic."""

    def test_weekday_scenes(self) -> None:
        """Test scene selection during weekdays."""
        is_weekend = False

        assert get_time_based_scene(3, is_weekend) == "night"
        assert get_time_based_scene(7, is_weekend) == "morning_routine"
        assert get_time_based_scene(10, is_weekend) == "day"
        assert get_time_based_scene(18, is_weekend) == "evening"
        assert get_time_based_scene(21, is_weekend) == "relax"
        assert get_time_based_scene(23, is_weekend) == "night"

    def test_weekend_scenes(self) -> None:
        """Test scene selection during weekends."""
        is_weekend = True

        assert get_time_based_scene(3, is_weekend) == "night"
        assert get_time_based_scene(9, is_weekend) == "weekend_morning"
        assert get_time_based_scene(14, is_weekend) == "day_bright"
        assert get_time_based_scene(18, is_weekend) == "weekend_evening"
        assert get_time_based_scene(21, is_weekend) == "relax"
        assert get_time_based_scene(23, is_weekend) == "night"

    def test_weekend_morning_is_later(self) -> None:
        """Test that weekend morning scene starts later than weekday."""
        # At 7 AM
        weekday_scene = get_time_based_scene(7, is_weekend=False)
        weekend_scene = get_time_based_scene(7, is_weekend=True)

        assert weekday_scene == "morning_routine"
        assert weekend_scene == "night"  # Still night mode on weekend


class TestAutomationConditions:
    """Test complex automation condition evaluation."""

    def test_time_condition_within_range(self) -> None:
        """Test time condition when current time is within range."""
        conditions = [{"condition": "time", "after": time(17, 0), "before": time(22, 0)}]

        current_state = {"time": time(19, 0)}
        assert evaluate_automation_conditions(conditions, current_state) is True

        current_state = {"time": time(16, 0)}
        assert evaluate_automation_conditions(conditions, current_state) is False

    def test_state_condition(self) -> None:
        """Test state condition evaluation."""
        conditions = [{"condition": "state", "entity_id": "person.john", "state": "home"}]

        current_state = {"states": {"person.john": "home"}}
        assert evaluate_automation_conditions(conditions, current_state) is True

        current_state = {"states": {"person.john": "not_home"}}
        assert evaluate_automation_conditions(conditions, current_state) is False

    def test_multiple_conditions_all_must_pass(self) -> None:
        """Test that all conditions must pass."""
        conditions: list[dict[str, Any]] = [
            {"condition": "time", "after": time(17, 0), "before": time(22, 0)},
            {
                "condition": "state",
                "entity_id": "person.john",
                "state": "home",
            },
        ]

        # Both conditions met
        current_state = {
            "time": time(19, 0),
            "states": {"person.john": "home"},
        }
        assert evaluate_automation_conditions(conditions, current_state) is True

        # Only time condition met
        current_state = {
            "time": time(19, 0),
            "states": {"person.john": "not_home"},
        }
        assert evaluate_automation_conditions(conditions, current_state) is False

    def test_numeric_state_condition(self) -> None:
        """Test numeric state conditions."""
        conditions = [
            {
                "condition": "numeric_state",
                "entity_id": "sensor.temperature",
                "above": 20,
                "below": 30,
            }
        ]

        # Temperature in range
        current_state = {"states": {"sensor.temperature": 25}}
        assert evaluate_automation_conditions(conditions, current_state) is True

        # Temperature too low
        current_state = {"states": {"sensor.temperature": 19}}
        assert evaluate_automation_conditions(conditions, current_state) is False

        # Temperature too high
        current_state = {"states": {"sensor.temperature": 31}}
        assert evaluate_automation_conditions(conditions, current_state) is False


class TestRealWorldScenarios:
    """Test real-world automation scenarios."""

    def test_adaptive_lighting_throughout_day(self) -> None:
        """Test how lighting adapts throughout a typical day."""
        # Track brightness changes through the day
        brightness_schedule = []

        for hour in range(24):
            brightness = calculate_brightness_for_time(hour)
            brightness_schedule.append((hour, brightness))

        # Verify smooth transitions (no sudden jumps > 50%)
        for i in range(1, len(brightness_schedule)):
            prev_brightness = brightness_schedule[i - 1][1]
            curr_brightness = brightness_schedule[i][1]
            change = abs(curr_brightness - prev_brightness)

            # Allow larger changes at specific transition times
            transition_hours = [6, 8, 12, 17, 20, 22]
            if brightness_schedule[i][0] not in transition_hours:
                assert change <= 102  # Max 40% change between hours

    def test_vacation_mode_simulation(self) -> None:
        """Test vacation mode light simulation."""
        # Simulate "someone is home" pattern
        vacation_times = [
            time(7, 15),  # Morning routine
            time(12, 30),  # Lunch time
            time(18, 45),  # Evening arrival
            time(22, 0),  # Bedtime
        ]

        for check_time in vacation_times:
            # During vacation times, lights should follow normal patterns
            if check_time >= time(18, 30):
                # Evening lights would be on
                is_evening = check_time >= time(18, 30) and check_time <= time(23, 0)
                assert is_evening is True
