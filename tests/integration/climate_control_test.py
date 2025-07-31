"""Test smart climate control automation."""

import pytest
from pathlib import Path
import yaml

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from tests.helpers.automation_validation import assert_valid_automation, get_automation_summary


class TestClimateControl:
    """Test the smart climate control automation."""
    
    @pytest.fixture
    def automation_config(self):
        """Load the climate control automation from YAML file."""
        yaml_path = Path(__file__).parent / "climate_control.yaml"
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate the automation before using it in tests
        assert_valid_automation(config)
        print(f"\nAutomation summary: {get_automation_summary(config)}")
        
        return config
    
    @pytest.mark.asyncio
    async def test_heating_mode_activation(self, hass: HomeAssistant, automation_config):
        """Test that heating activates when temperature is low and occupied."""
        # Track service calls
        service_calls = {}
        
        async def track_call(domain, service):
            calls = []
            service_calls[f"{domain}.{service}"] = calls
            async def handler(call):
                calls.append(dict(call.data))
            hass.services.async_register(domain, service, handler)
            return calls
        
        # Register services
        climate_calls = await track_call('climate', 'set_temperature')
        notify_calls = await track_call('notify', 'mobile_app')
        
        # Set up states
        hass.states.async_set('sensor.average_indoor_temperature', '18')  # Cold
        hass.states.async_set('binary_sensor.occupancy', 'on')
        hass.states.async_set('input_boolean.climate_automation_enabled', 'on')
        
        # Setup automation
        assert await async_setup_component(hass, 'automation', {
            'automation': [automation_config]
        })
        await hass.async_block_till_done()
        
        # Execute the heating sequence from the choose action
        heating_sequence = automation_config['action'][0]['choose'][0]['sequence']
        
        for action in heating_sequence:
            await hass.services.async_call(
                action['service'].split('.')[0],
                action['service'].split('.')[1],
                action.get('data', {}) | action.get('target', {}),
                blocking=True
            )
        
        # Verify heating was activated
        assert len(climate_calls) == 1
        assert climate_calls[0]['temperature'] == 21
        assert climate_calls[0]['hvac_mode'] == 'heat'
        assert climate_calls[0]['entity_id'] == 'climate.main_thermostat'
        
        # Verify notification was sent
        assert len(notify_calls) == 1
        assert 'Heating activated' in notify_calls[0]['message']
    
    @pytest.mark.asyncio
    async def test_cooling_mode_activation(self, hass: HomeAssistant, automation_config):
        """Test that cooling activates when temperature is high."""
        service_calls = {}
        
        async def track_call(domain, service):
            calls = []
            service_calls[f"{domain}.{service}"] = calls
            async def handler(call):
                calls.append(dict(call.data))
            hass.services.async_register(domain, service, handler)
            return calls
        
        climate_calls = await track_call('climate', 'set_temperature')
        fan_calls = await track_call('fan', 'turn_on')
        
        # Set up hot conditions
        hass.states.async_set('sensor.average_indoor_temperature', '27')  # Hot
        hass.states.async_set('binary_sensor.occupancy', 'on')
        
        # Execute cooling sequence
        cooling_sequence = automation_config['action'][0]['choose'][1]['sequence']
        
        for action in cooling_sequence:
            await hass.services.async_call(
                action['service'].split('.')[0],
                action['service'].split('.')[1],
                action.get('data', {}) | action.get('target', {}),
                blocking=True
            )
        
        # Verify cooling was activated
        assert len(climate_calls) == 1
        assert climate_calls[0]['temperature'] == 24
        assert climate_calls[0]['hvac_mode'] == 'cool'
        
        # Verify fan was turned on
        assert len(fan_calls) == 1
        assert fan_calls[0]['entity_id'] == 'fan.ceiling_fan'
        assert fan_calls[0]['percentage'] == 66
    
    @pytest.mark.asyncio
    async def test_away_mode_activation(self, hass: HomeAssistant, automation_config):
        """Test that away mode activates when unoccupied."""
        service_calls = {}
        
        async def track_call(domain, service):
            calls = []
            service_calls[f"{domain}.{service}"] = calls
            async def handler(call):
                calls.append(dict(call.data))
            hass.services.async_register(domain, service, handler)
            return calls
        
        preset_calls = await track_call('climate', 'set_preset_mode')
        fan_calls = await track_call('fan', 'turn_off')
        
        # Execute away sequence
        away_sequence = automation_config['action'][0]['choose'][2]['sequence']
        
        for action in away_sequence:
            await hass.services.async_call(
                action['service'].split('.')[0],
                action['service'].split('.')[1],
                action.get('data', {}) | action.get('target', {}),
                blocking=True
            )
        
        # Verify away mode was set
        assert len(preset_calls) == 1
        assert preset_calls[0]['preset_mode'] == 'away'
        assert preset_calls[0]['entity_id'] == 'climate.main_thermostat'
        
        # Verify fan was turned off
        assert len(fan_calls) == 1
        assert fan_calls[0]['entity_id'] == 'fan.ceiling_fan'
    
    @pytest.mark.asyncio
    async def test_triggers_configuration(self, hass: HomeAssistant, automation_config):
        """Test that all triggers are properly configured."""
        triggers = automation_config['trigger']
        assert len(triggers) == 3
        
        # Time pattern trigger
        time_trigger = next(t for t in triggers if t['platform'] == 'time_pattern')
        assert time_trigger['minutes'] == '/15'
        
        # Temperature sensor triggers
        temp_triggers = [t for t in triggers if t['platform'] == 'state' and 'temperature' in str(t.get('entity_id', ''))]
        assert len(temp_triggers) == 1
        assert 'sensor.living_room_temperature' in temp_triggers[0]['entity_id']
        assert 'sensor.bedroom_temperature' in temp_triggers[0]['entity_id']
        
        # Occupancy trigger
        occupancy_triggers = [t for t in triggers if t.get('entity_id') == 'binary_sensor.occupancy']
        assert len(occupancy_triggers) == 1
        assert occupancy_triggers[0]['to'] == 'on'
        assert occupancy_triggers[0]['for']['minutes'] == 5
    
    @pytest.mark.asyncio
    async def test_choose_action_structure(self, hass: HomeAssistant, automation_config):
        """Test that the choose action has all necessary branches."""
        choose_action = automation_config['action'][0]
        assert 'choose' in choose_action
        
        choices = choose_action['choose']
        assert len(choices) == 3  # Heating, cooling, away
        
        # Verify each choice has conditions and sequence
        for choice in choices:
            assert 'conditions' in choice
            assert 'sequence' in choice
            assert len(choice['conditions']) > 0
            assert len(choice['sequence']) > 0
        
        # Verify default action exists
        assert 'default' in choose_action
        assert len(choose_action['default']) > 0