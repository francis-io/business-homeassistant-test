"""Unit tests for zone entry automation logic."""

import pytest
from datetime import time
from tests.helpers.automation_logic import (
    get_zone_entry_actions,
    should_send_arrival_notification,
    calculate_home_occupancy,
    is_everyone_away,
    get_presence_based_climate_mode
)


class TestZoneEntryActions:
    """Test zone entry action determination."""
    
    def test_evening_arrival_actions(self):
        """Test actions when arriving home in evening."""
        actions = get_zone_entry_actions(
            person_state="home",
            previous_state="not_home",
            current_time=time(19, 0),
            people_home_count=2
        )
        
        # Should turn on entrance and hallway lights
        assert len(actions["lights"]) == 2
        assert any(a["entity"] == "light.entrance" for a in actions["lights"])
        assert any(a["entity"] == "light.hallway" for a in actions["lights"])
        
        # Should set climate
        assert len(actions["climate"]) == 1
        assert actions["climate"][0]["temperature"] == 22
    
    def test_daytime_arrival_no_lights(self):
        """Test no lights turn on during daytime arrival."""
        actions = get_zone_entry_actions(
            person_state="home",
            previous_state="not_home",
            current_time=time(14, 0),
            people_home_count=2
        )
        
        # No lights during daytime
        assert len(actions["lights"]) == 0
        assert len(actions["climate"]) == 0
    
    def test_first_person_home_actions(self):
        """Test special actions for first person arriving."""
        actions = get_zone_entry_actions(
            person_state="home",
            previous_state="not_home",
            current_time=time(19, 0),
            people_home_count=1
        )
        
        # Should have entrance, hallway, and living room lights
        assert len(actions["lights"]) == 3
        living_room_action = next(
            (a for a in actions["lights"] if a["entity"] == "light.living_room"),
            None
        )
        assert living_room_action is not None
        
        # Should disarm security
        assert len(actions["security"]) == 1
        assert actions["security"][0]["action"] == "disarm"
    
    def test_already_home_no_actions(self):
        """Test no actions if person was already home."""
        actions = get_zone_entry_actions(
            person_state="home",
            previous_state="home",
            current_time=time(19, 0),
            people_home_count=2
        )
        
        # No actions if already home
        assert all(len(actions[key]) == 0 for key in actions)


class TestHomeOccupancy:
    """Test home occupancy calculations."""
    
    def test_calculate_occupancy_count(self):
        """Test counting people at home."""
        people_states = {
            "person.john": "home",
            "person.jane": "not_home",
            "person.kid": "home"
        }
        
        count, people_home = calculate_home_occupancy(people_states)
        
        assert count == 2
        assert "person.john" in people_home
        assert "person.kid" in people_home
        assert "person.jane" not in people_home
    
    def test_nobody_home(self):
        """Test when nobody is home."""
        people_states = {
            "person.john": "not_home",
            "person.jane": "away",
            "person.kid": "not_home"
        }
        
        count, people_home = calculate_home_occupancy(people_states)
        
        assert count == 0
        assert len(people_home) == 0
    
    def test_everyone_home(self):
        """Test when everyone is home."""
        people_states = {
            "person.john": "home",
            "person.jane": "home",
            "person.kid": "home"
        }
        
        count, people_home = calculate_home_occupancy(people_states)
        
        assert count == 3
        assert len(people_home) == 3


class TestEveryoneAway:
    """Test everyone away detection."""
    
    def test_everyone_is_away(self):
        """Test detection when everyone is away."""
        people_states = {
            "person.john": "not_home",
            "person.jane": "away",
            "person.kid": "not_home"
        }
        
        assert is_everyone_away(people_states) is True
    
    def test_someone_is_home(self):
        """Test detection when someone is home."""
        people_states = {
            "person.john": "home",
            "person.jane": "not_home",
            "person.kid": "not_home"
        }
        
        assert is_everyone_away(people_states) is False
    
    def test_different_away_states(self):
        """Test various away state values."""
        # All different ways of being "away"
        people_states = {
            "person.john": "not_home",
            "person.jane": "away",
            "person.kid": "work",
            "person.guest": "unknown"
        }
        
        assert is_everyone_away(people_states) is True


class TestPresenceBasedClimate:
    """Test climate mode based on presence."""
    
    def test_away_mode_when_empty(self):
        """Test away mode when nobody home."""
        assert get_presence_based_climate_mode(
            people_home=0,
            current_hour=14
        ) == "away"
    
    def test_sleep_mode_at_night(self):
        """Test sleep mode during night hours."""
        # Late night
        assert get_presence_based_climate_mode(
            people_home=2,
            current_hour=23
        ) == "sleep"
        
        # Early morning
        assert get_presence_based_climate_mode(
            people_home=2,
            current_hour=3
        ) == "sleep"
    
    def test_morning_mode(self):
        """Test morning mode during wake up time."""
        assert get_presence_based_climate_mode(
            people_home=2,
            current_hour=7
        ) == "morning"
    
    def test_comfort_mode_during_day(self):
        """Test comfort mode during regular hours."""
        assert get_presence_based_climate_mode(
            people_home=1,
            current_hour=14
        ) == "comfort"
        
        assert get_presence_based_climate_mode(
            people_home=3,
            current_hour=19
        ) == "comfort"


class TestComplexZoneScenarios:
    """Test complex zone-based scenarios."""
    
    def test_guest_mode_activation(self):
        """Test special handling for guests."""
        def should_activate_guest_mode(people_states, known_residents):
            home_people = [p for p, state in people_states.items() if state == "home"]
            unknown_people = [p for p in home_people if p not in known_residents]
            return len(unknown_people) > 0
        
        known_residents = ["person.john", "person.jane", "person.kid"]
        
        # No guests
        people_states = {
            "person.john": "home",
            "person.jane": "home"
        }
        assert should_activate_guest_mode(people_states, known_residents) is False
        
        # Guest present
        people_states = {
            "person.john": "home",
            "person.guest1": "home"
        }
        assert should_activate_guest_mode(people_states, known_residents) is True
    
    def test_pet_mode_logic(self):
        """Test automation adjustments for pets home alone."""
        def get_pet_mode_settings(people_home, pets_home):
            if people_home == 0 and pets_home > 0:
                return {
                    "climate_mode": "pet_comfort",
                    "temperature": 20,  # Slightly cooler
                    "lights": ["light.living_room"],  # Minimal lighting
                    "music": True  # Calming music
                }
            return None
        
        # Pets home alone
        settings = get_pet_mode_settings(people_home=0, pets_home=2)
        assert settings is not None
        assert settings["climate_mode"] == "pet_comfort"
        assert settings["music"] is True
        
        # People home with pets
        settings = get_pet_mode_settings(people_home=1, pets_home=2)
        assert settings is None
    
    def test_multi_zone_tracking(self):
        """Test tracking across multiple zones."""
        def get_zone_transition_actions(from_zone, to_zone, person):
            transitions = {
                ("not_home", "home"): "arrival",
                ("home", "not_home"): "departure",
                ("not_home", "work"): "arrived_work",
                ("work", "not_home"): "left_work",
                ("home", "garage"): "in_garage",
                ("garage", "home"): "from_garage"
            }
            
            return transitions.get((from_zone, to_zone), "unknown")
        
        # Test various transitions
        assert get_zone_transition_actions("not_home", "home", "john") == "arrival"
        assert get_zone_transition_actions("home", "garage", "john") == "in_garage"
        assert get_zone_transition_actions("work", "not_home", "john") == "left_work"
    
    def test_presence_simulation_vacation_mode(self):
        """Test presence simulation when on vacation."""
        def get_vacation_simulation_schedule(current_hour):
            schedule = {
                7: ["light.bedroom", "light.bathroom"],
                8: ["light.kitchen"],
                12: ["light.living_room"],
                18: ["light.kitchen", "light.dining"],
                20: ["light.living_room"],
                22: ["light.bedroom"],
                23: []  # All off
            }
            
            return schedule.get(current_hour, None)
        
        # Morning routine
        assert "light.bedroom" in get_vacation_simulation_schedule(7)
        
        # Evening routine  
        assert "light.kitchen" in get_vacation_simulation_schedule(18)
        
        # Bedtime
        assert get_vacation_simulation_schedule(23) == []