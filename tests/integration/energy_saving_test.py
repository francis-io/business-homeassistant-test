"""Test smart energy saving automation."""

import pytest
from pathlib import Path
import yaml

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from tests.helpers.automation_validation import assert_valid_automation, get_automation_summary


class TestEnergySaving:
    """Test the smart energy saving automation."""
    
    @pytest.fixture
    def automation_config(self):
        """Load the energy saving automation from YAML file."""
        yaml_path = Path(__file__).parent / "energy_saving.yaml"
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate the automation before using it in tests
        assert_valid_automation(config)
        print(f"\nAutomation summary: {get_automation_summary(config)}")
        
        return config
    
    @pytest.mark.asyncio
    async def test_away_mode_energy_saving(self, hass: HomeAssistant, automation_config):
        """Test that away mode turns off devices."""
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
        light_calls = await track_call('light', 'turn_off')
        switch_calls = await track_call('switch', 'turn_off')
        climate_calls = await track_call('climate', 'set_preset_mode')
        notify_calls = await track_call('notify', 'mobile_app')
        
        # Set up states
        hass.states.async_set('person.homeowner', 'not_home')
        hass.states.async_set('input_boolean.energy_saving_mode', 'on')
        
        # Setup automation
        assert await async_setup_component(hass, 'automation', {
            'automation': [automation_config]
        })
        await hass.async_block_till_done()
        
        # Execute away mode sequence
        away_sequence = automation_config['action'][1]['choose'][0]['sequence']
        
        for action in away_sequence:
            if action['service'] != 'notify.mobile_app':  # Skip notify for now
                await hass.services.async_call(
                    action['service'].split('.')[0],
                    action['service'].split('.')[1],
                    action.get('data', {}) | action.get('target', {}),
                    blocking=True
                )
        
        # Verify lights were turned off
        assert len(light_calls) == 1
        assert light_calls[0]['entity_id'] == 'all'
        assert light_calls[0]['transition'] == 2
        
        # Verify switches were turned off
        assert len(switch_calls) == 1
        expected_switches = ['switch.tv_power', 'switch.game_console', 'switch.computer_power']
        for switch in expected_switches:
            assert switch in switch_calls[0]['entity_id']
        
        # Verify climate set to eco mode
        assert len(climate_calls) == 1
        assert climate_calls[0]['preset_mode'] == 'eco'
    
    @pytest.mark.asyncio
    async def test_high_power_usage_reduction(self, hass: HomeAssistant, automation_config):
        """Test that high power usage triggers load reduction."""
        service_calls = {}
        
        async def track_call(domain, service):
            calls = []
            service_calls[f"{domain}.{service}"] = calls
            async def handler(call):
                calls.append(dict(call.data))
            hass.services.async_register(domain, service, handler)
            return calls
        
        switch_calls = await track_call('switch', 'turn_off')
        climate_calls = await track_call('climate', 'set_temperature')
        
        # Set high power usage
        hass.states.async_set('sensor.current_power_usage', '5500')  # 5.5kW
        hass.states.async_set('climate.main_thermostat', 'heat', 
                              attributes={'temperature': 22})
        
        # Execute high usage sequence
        high_usage_sequence = automation_config['action'][1]['choose'][1]['sequence']
        
        # Execute non-template actions
        for action in high_usage_sequence:
            if action['service'] == 'switch.turn_off':
                await hass.services.async_call(
                    'switch',
                    'turn_off',
                    action.get('data', {}) | action.get('target', {}),
                    blocking=True
                )
        
        # Verify high-power devices were turned off
        assert len(switch_calls) == 1
        assert 'switch.electric_water_heater' in switch_calls[0]['entity_id']
        assert 'switch.pool_pump' in switch_calls[0]['entity_id']
    
    @pytest.mark.asyncio
    async def test_night_mode_energy_saving(self, hass: HomeAssistant, automation_config):
        """Test that night mode turns off outdoor devices."""
        service_calls = {}
        
        async def track_call(domain, service):
            calls = []
            service_calls[f"{domain}.{service}"] = calls
            async def handler(call):
                calls.append(dict(call.data))
            hass.services.async_register(domain, service, handler)
            return calls
        
        light_calls = await track_call('light', 'turn_off')
        media_calls = await track_call('media_player', 'turn_off')
        fan_calls = await track_call('fan', 'turn_off')
        
        # Execute night mode sequence
        night_sequence = automation_config['action'][1]['choose'][2]['sequence']
        
        for action in night_sequence:
            await hass.services.async_call(
                action['service'].split('.')[0],
                action['service'].split('.')[1],
                action.get('data', {}) | action.get('target', {}),
                blocking=True
            )
        
        # Verify outdoor lights were turned off
        assert len(light_calls) == 1
        outdoor_lights = light_calls[0]['entity_id']
        assert 'light.outdoor_lights' in outdoor_lights
        assert 'light.decorative_lights' in outdoor_lights
        assert 'light.landscape_lights' in outdoor_lights
        
        # Verify media players turned off
        assert len(media_calls) == 1
        assert media_calls[0]['entity_id'] == 'all'
        
        # Verify fans turned off
        assert len(fan_calls) == 1
        assert 'fan.garage_fan' in fan_calls[0]['entity_id']
        assert 'fan.attic_fan' in fan_calls[0]['entity_id']
    
    @pytest.mark.asyncio
    async def test_trigger_configuration(self, hass: HomeAssistant, automation_config):
        """Test that all triggers are properly configured."""
        triggers = automation_config['trigger']
        assert len(triggers) == 4
        
        # Person away trigger
        away_triggers = [t for t in triggers if t['platform'] == 'state' and t.get('entity_id') == 'person.homeowner']
        assert len(away_triggers) == 1
        assert away_triggers[0]['from'] == 'home'
        assert away_triggers[0]['to'] == 'not_home'
        assert away_triggers[0]['for']['minutes'] == 10
        
        # Time trigger
        time_triggers = [t for t in triggers if t['platform'] == 'time']
        assert len(time_triggers) == 1
        assert time_triggers[0]['at'] == '23:00:00'
        
        # Power usage trigger
        power_triggers = [t for t in triggers if t['platform'] == 'numeric_state']
        assert len(power_triggers) == 1
        assert power_triggers[0]['entity_id'] == 'sensor.current_power_usage'
        assert power_triggers[0]['above'] == 5000
        
        # Sun trigger
        sun_triggers = [t for t in triggers if t['platform'] == 'sun']
        assert len(sun_triggers) == 1
        assert sun_triggers[0]['event'] == 'sunrise'
        assert sun_triggers[0]['offset'] == '01:00:00'
    
    @pytest.mark.asyncio
    async def test_queued_mode(self, hass: HomeAssistant, automation_config):
        """Test that automation uses queued mode."""
        assert automation_config['mode'] == 'queued'
        assert automation_config['max'] == 2
        
        # This allows multiple energy saving actions to queue up
        # but limits to 2 to prevent excessive queuing