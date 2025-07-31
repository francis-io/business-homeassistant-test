"""Pure automation logic functions for testing."""

from datetime import time
from typing import Any


# Time-based Light Automation Logic
def should_turn_on_evening_lights(
    current_time: time, is_after_sunset: bool, light_state: str = "off"
) -> bool:
    """Determine if evening lights should turn on."""
    return light_state == "off" and current_time >= time(18, 30) and is_after_sunset


def calculate_brightness_for_time(current_hour: int) -> int:
    """Calculate brightness based on time of day."""
    if 6 <= current_hour < 8:
        return 77  # 30% of 255
    elif 8 <= current_hour < 12:
        return 128  # 50% of 255
    elif 12 <= current_hour < 17:
        return 204  # 80% of 255
    elif 17 <= current_hour < 20:
        return 179  # 70% of 255
    elif 20 <= current_hour < 22:
        return 102  # 40% of 255
    else:
        return 26  # 10% of 255 (night light)


def should_trigger_time_pattern(current_minute: int, pattern_minutes: int) -> bool:
    """Check if current time matches a time pattern trigger."""
    return current_minute % pattern_minutes == 0


# Notification Automation Logic
def should_send_water_leak_notification(
    sensor_state: str,
    previous_state: str,
    notification_sent_recently: bool = False,
) -> bool:
    """Determine if water leak notification should be sent."""
    return sensor_state == "on" and previous_state == "off" and not notification_sent_recently


def get_notification_priority(alert_type: str) -> str:
    """Get notification priority based on alert type."""
    high_priority_alerts = ["water_leak", "fire", "security", "gas_leak"]
    medium_priority_alerts = ["door_open", "window_open", "motion"]

    if alert_type in high_priority_alerts:
        return "high"
    elif alert_type in medium_priority_alerts:
        return "medium"
    else:
        return "low"


def should_send_door_open_reminder(
    door_state: str, minutes_open: int, reminder_threshold: int = 5
) -> bool:
    """Determine if door open reminder should be sent."""
    return door_state == "on" and minutes_open >= reminder_threshold


def should_send_motion_notification(
    motion_detected: bool, person_home: bool, armed_away: bool
) -> bool:
    """Determine if motion notification should be sent."""
    return motion_detected and not person_home and armed_away


# Zone Entry Automation Logic
def get_zone_entry_actions(
    person_state: str,
    previous_state: str,
    current_time: time,
    people_home_count: int,
) -> dict[str, list[dict[str, Any]]]:
    """Determine what actions to take when someone enters a zone."""
    actions: dict[str, list[dict[str, Any]]] = {
        "lights": [],
        "climate": [],
        "notifications": [],
        "security": [],
    }

    # Check if person just arrived home
    if person_state == "home" and previous_state != "home":
        # Evening arrival actions
        if time(17, 0) <= current_time <= time(22, 0):
            actions["lights"].extend(
                [
                    {
                        "entity": "light.entrance",
                        "action": "turn_on",
                        "brightness": 80,
                    },
                    {
                        "entity": "light.hallway",
                        "action": "turn_on",
                        "brightness": 60,
                    },
                ]
            )
            actions["climate"].append(
                {
                    "entity": "climate.living_room",
                    "action": "set_temperature",
                    "temperature": 22,
                }
            )

        # First person home actions
        if people_home_count == 1:
            actions["lights"].append({"entity": "light.living_room", "action": "turn_on"})
            actions["security"].append({"entity": "alarm_control_panel.home", "action": "disarm"})

    return actions


def should_send_arrival_notification(
    person: str, arrived_home: bool, notify_list: list[str]
) -> bool:
    """Determine if arrival notification should be sent."""
    return arrived_home and person in notify_list


def calculate_home_occupancy(
    people_states: dict[str, str],
) -> tuple[int, list[str]]:
    """Calculate how many people are home and who they are."""
    people_home = [person for person, state in people_states.items() if state == "home"]
    return len(people_home), people_home


def is_everyone_away(people_states: dict[str, str]) -> bool:
    """Check if everyone is away from home."""
    return all(state != "home" for state in people_states.values())


def get_presence_based_climate_mode(people_home: int, current_hour: int) -> str | None:
    """Determine climate mode based on presence and time."""
    if people_home == 0:
        return "away"
    elif 22 <= current_hour or current_hour < 6:
        return "sleep"
    elif 6 <= current_hour < 8:
        return "morning"
    else:
        return "comfort"


# Combined Logic Functions
def evaluate_automation_conditions(
    conditions: list[dict[str, Any]], current_state: dict[str, Any]
) -> bool:
    """Evaluate a list of automation conditions."""
    for condition in conditions:
        condition_type = condition.get("condition")

        if condition_type == "time":
            current_time = current_state.get("time")
            after = condition.get("after")
            before = condition.get("before")

            if after and current_time < after:
                return False
            if before and current_time > before:
                return False

        elif condition_type == "state":
            entity = condition.get("entity_id")
            expected_state = condition.get("state")
            actual_state = current_state.get("states", {}).get(entity)

            if actual_state != expected_state:
                return False

        elif condition_type == "numeric_state":
            entity = condition.get("entity_id")
            value = current_state.get("states", {}).get(entity, 0)
            above = condition.get("above")
            below = condition.get("below")

            if above is not None and value <= above:
                return False
            if below is not None and value >= below:
                return False

    return True


def get_time_based_scene(current_hour: int, is_weekend: bool) -> str:
    """Determine which scene to activate based on time and day."""
    if is_weekend:
        if 0 <= current_hour < 8:
            return "night"
        elif 8 <= current_hour < 10:
            return "weekend_morning"
        elif 10 <= current_hour < 17:
            return "day_bright"
        elif 17 <= current_hour < 20:
            return "weekend_evening"
        elif 20 <= current_hour < 22:
            return "relax"
        else:
            return "night"
    else:
        if 0 <= current_hour < 6:
            return "night"
        elif 6 <= current_hour < 8:
            return "morning_routine"
        elif 8 <= current_hour < 17:
            return "day"
        elif 17 <= current_hour < 20:
            return "evening"
        elif 20 <= current_hour < 22:
            return "relax"
        else:
            return "night"
