"""Unit tests for notification automation logic."""

import pytest
from tests.helpers.automation_logic import (
    should_send_water_leak_notification,
    get_notification_priority,
    should_send_door_open_reminder,
    should_send_motion_notification,
    should_send_arrival_notification
)


class TestWaterLeakNotification:
    """Test water leak notification logic."""
    
    def test_should_send_when_leak_detected(self):
        """Test notification sent when leak first detected."""
        assert should_send_water_leak_notification(
            sensor_state="on",
            previous_state="off",
            notification_sent_recently=False
        ) is True
    
    def test_should_not_send_if_already_leaking(self):
        """Test no duplicate notification for ongoing leak."""
        assert should_send_water_leak_notification(
            sensor_state="on",
            previous_state="on",
            notification_sent_recently=False
        ) is False
    
    def test_should_not_send_when_leak_stops(self):
        """Test no notification when leak stops."""
        assert should_send_water_leak_notification(
            sensor_state="off",
            previous_state="on",
            notification_sent_recently=False
        ) is False
    
    def test_should_not_send_if_recently_notified(self):
        """Test rate limiting of notifications."""
        assert should_send_water_leak_notification(
            sensor_state="on",
            previous_state="off",
            notification_sent_recently=True
        ) is False


class TestNotificationPriority:
    """Test notification priority logic."""
    
    def test_high_priority_alerts(self):
        """Test critical alerts get high priority."""
        assert get_notification_priority("water_leak") == "high"
        assert get_notification_priority("fire") == "high"
        assert get_notification_priority("security") == "high"
        assert get_notification_priority("gas_leak") == "high"
    
    def test_medium_priority_alerts(self):
        """Test moderate alerts get medium priority."""
        assert get_notification_priority("door_open") == "medium"
        assert get_notification_priority("window_open") == "medium"
        assert get_notification_priority("motion") == "medium"
    
    def test_low_priority_alerts(self):
        """Test routine alerts get low priority."""
        assert get_notification_priority("battery_low") == "low"
        assert get_notification_priority("update_available") == "low"
        assert get_notification_priority("reminder") == "low"


class TestDoorOpenReminder:
    """Test door open reminder logic."""
    
    def test_should_remind_after_threshold(self):
        """Test reminder sent after door open too long."""
        assert should_send_door_open_reminder(
            door_state="on",
            minutes_open=6,
            reminder_threshold=5
        ) is True
    
    def test_should_not_remind_before_threshold(self):
        """Test no reminder before threshold time."""
        assert should_send_door_open_reminder(
            door_state="on",
            minutes_open=3,
            reminder_threshold=5
        ) is False
    
    def test_should_not_remind_if_door_closed(self):
        """Test no reminder if door is closed."""
        assert should_send_door_open_reminder(
            door_state="off",
            minutes_open=10,
            reminder_threshold=5
        ) is False
    
    def test_custom_threshold(self):
        """Test custom reminder thresholds."""
        # Garage door - longer threshold
        assert should_send_door_open_reminder(
            door_state="on",
            minutes_open=20,
            reminder_threshold=30
        ) is False
        
        # Refrigerator door - shorter threshold
        assert should_send_door_open_reminder(
            door_state="on",
            minutes_open=2,
            reminder_threshold=1
        ) is True


class TestMotionNotification:
    """Test motion detection notification logic."""
    
    def test_should_notify_when_away_and_armed(self):
        """Test notification when motion detected while away."""
        assert should_send_motion_notification(
            motion_detected=True,
            person_home=False,
            armed_away=True
        ) is True
    
    def test_should_not_notify_when_home(self):
        """Test no notification when someone is home."""
        assert should_send_motion_notification(
            motion_detected=True,
            person_home=True,
            armed_away=True
        ) is False
    
    def test_should_not_notify_when_disarmed(self):
        """Test no notification when system disarmed."""
        assert should_send_motion_notification(
            motion_detected=True,
            person_home=False,
            armed_away=False
        ) is False
    
    def test_should_not_notify_without_motion(self):
        """Test no notification without motion."""
        assert should_send_motion_notification(
            motion_detected=False,
            person_home=False,
            armed_away=True
        ) is False


class TestArrivalNotification:
    """Test arrival notification logic."""
    
    def test_should_notify_tracked_person_arrival(self):
        """Test notification for tracked person arriving."""
        notify_list = ["kid", "elderly_parent"]
        
        assert should_send_arrival_notification(
            person="kid",
            arrived_home=True,
            notify_list=notify_list
        ) is True
    
    def test_should_not_notify_untracked_person(self):
        """Test no notification for untracked person."""
        notify_list = ["kid", "elderly_parent"]
        
        assert should_send_arrival_notification(
            person="adult",
            arrived_home=True,
            notify_list=notify_list
        ) is False
    
    def test_should_not_notify_if_not_arrived(self):
        """Test no notification if person hasn't arrived."""
        notify_list = ["kid", "elderly_parent"]
        
        assert should_send_arrival_notification(
            person="kid",
            arrived_home=False,
            notify_list=notify_list
        ) is False


class TestComplexNotificationScenarios:
    """Test complex real-world notification scenarios."""
    
    def test_smart_doorbell_notification_logic(self):
        """Test smart doorbell notification decisions."""
        scenarios = [
            # (motion, person_home, package_detected, expected_notify)
            (True, True, False, False),    # Someone home, regular motion
            (True, False, False, True),     # Nobody home, motion
            (True, False, True, True),      # Nobody home, package
            (False, False, True, True),     # Package detected (always notify)
        ]
        
        for motion, home, package, should_notify in scenarios:
            # Smart doorbell logic
            result = motion and not home or package
            assert result == should_notify
    
    def test_leak_notification_escalation(self):
        """Test notification escalation for persistent leaks."""
        # Initial leak - high priority
        assert get_notification_priority("water_leak") == "high"
        
        # Leak duration affects message urgency
        def get_leak_message(minutes_leaking):
            if minutes_leaking < 5:
                return "Water leak detected!"
            elif minutes_leaking < 15:
                return "URGENT: Water leak ongoing for {} minutes!".format(minutes_leaking)
            else:
                return "CRITICAL: Major water leak for {} minutes! Immediate action required!".format(minutes_leaking)
        
        assert "detected" in get_leak_message(2)
        assert "URGENT" in get_leak_message(10)
        assert "CRITICAL" in get_leak_message(20)
    
    def test_notification_grouping_logic(self):
        """Test logic for grouping related notifications."""
        def should_group_notifications(notif1_type, notif2_type, time_diff_seconds):
            # Group similar notifications within 30 seconds
            related_types = {
                "motion": ["motion", "person_detected", "doorbell"],
                "security": ["door_open", "window_open", "motion"],
                "climate": ["temperature", "humidity", "air_quality"]
            }
            
            for group, types in related_types.items():
                if notif1_type in types and notif2_type in types:
                    return time_diff_seconds <= 30
            
            return False
        
        # Same type within time window
        assert should_group_notifications("motion", "motion", 20) is True
        
        # Related types within time window
        assert should_group_notifications("motion", "doorbell", 15) is True
        
        # Same type but too far apart
        assert should_group_notifications("motion", "motion", 60) is False
        
        # Unrelated types
        assert should_group_notifications("motion", "temperature", 10) is False