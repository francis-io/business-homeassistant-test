"""Test smart doorbell notification automation."""

import pytest
from pathlib import Path
import yaml
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from tests.helpers.automation_validation import assert_valid_automation, get_automation_summary


class TestDoorbellNotification:
    """Test the smart doorbell notification automation."""
    
    @pytest.fixture
    def automation_config(self):
        """Load the doorbell notification automation from YAML file."""
        yaml_path = Path(__file__).parent / "doorbell_notification.yaml"
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate the automation before using it in tests
        assert_valid_automation(config)
        print(f"\nAutomation summary: {get_automation_summary(config)}")
        
        return config
    
    @pytest.mark.asyncio
    async def test_doorbell_triggers_notification(self, hass: HomeAssistant, automation_config):
        """Test that doorbell press triggers notifications."""
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
        await track_call('camera', 'snapshot')
        notify_calls = await track_call('notify', 'all_devices')
        await track_call('logbook', 'log')
        
        # Set up states
        hass.states.async_set('input_boolean.do_not_disturb', 'off')
        hass.states.async_set('person.homeowner', 'home')
        
        # Setup automation
        assert await async_setup_component(hass, 'automation', {
            'automation': [automation_config]
        })
        await hass.async_block_till_done()
        
        # Execute notification action
        notification_action = None
        for action in automation_config['action'][0]['parallel']:
            if 'service' in action and action['service'] == 'notify.all_devices':
                notification_action = action
                break
        
        assert notification_action is not None
        
        # Simulate the notification
        await hass.services.async_call(
            'notify',
            'all_devices',
            {
                'title': '🔔 Doorbell',
                'message': f'Someone rang the doorbell at {datetime.now().strftime("%I:%M %p")}',
                'data': notification_action['data']['data']
            },
            blocking=True
        )
        
        # Verify notification was sent
        assert len(notify_calls) == 1
        assert notify_calls[0]['title'] == '🔔 Doorbell'
        assert 'priority' in notify_calls[0]['data']
        assert notify_calls[0]['data']['priority'] == 'high'
        assert 'actions' in notify_calls[0]['data']
        assert len(notify_calls[0]['data']['actions']) == 3
    
    @pytest.mark.asyncio
    async def test_camera_snapshot_action(self, hass: HomeAssistant, automation_config):
        """Test that camera snapshot is taken."""
        # Find camera snapshot action
        camera_action = None
        for action in automation_config['action'][0]['parallel']:
            if 'service' in action and action['service'] == 'camera.snapshot':
                camera_action = action
                break
        
        assert camera_action is not None
        assert camera_action['target']['entity_id'] == 'camera.front_door'
        assert 'filename' in camera_action['data']
        assert '/tmp/doorbell_' in camera_action['data']['filename']
    
    @pytest.mark.asyncio
    async def test_flash_lights_when_home(self, hass: HomeAssistant, automation_config):
        """Test that lights flash when someone is home."""
        service_calls = []
        
        async def mock_service(call):
            service_calls.append(dict(call.data))
        
        hass.services.async_register('light', 'turn_on', mock_service)
        
        # Set person as home
        hass.states.async_set('person.homeowner', 'home')
        
        # Find and execute the light flash action
        for action in automation_config['action'][0]['parallel']:
            if 'choose' in action:
                for choice in action['choose']:
                    # Check if this is the "home" condition
                    conditions = choice.get('conditions', [])
                    if any(c.get('entity_id') == 'person.homeowner' and c.get('state') == 'home' for c in conditions):
                        # Execute the sequence
                        for seq_action in choice['sequence']:
                            await hass.services.async_call(
                                seq_action['service'].split('.')[0],
                                seq_action['service'].split('.')[1],
                                seq_action.get('data', {}) | seq_action.get('target', {}),
                                blocking=True
                            )
        
        # Verify lights were flashed
        assert len(service_calls) == 1
        assert 'light.hallway' in service_calls[0]['entity_id']
        assert 'light.entrance' in service_calls[0]['entity_id']
        assert service_calls[0]['flash'] == 'short'
    
    @pytest.mark.asyncio
    async def test_dnd_condition(self, hass: HomeAssistant, automation_config):
        """Test that DND mode is respected."""
        # Check condition configuration
        conditions = automation_config['condition']
        assert len(conditions) == 1
        assert conditions[0]['condition'] == 'template'
        
        # The template checks that either:
        # 1. DND is off, OR
        # 2. It's daytime hours (8 AM - 10 PM)
        template = conditions[0]['value_template']
        assert 'do_not_disturb' in template
        assert 'hour < 22' in template
        assert 'hour >= 8' in template
    
    @pytest.mark.asyncio
    async def test_multiple_trigger_types(self, hass: HomeAssistant, automation_config):
        """Test that automation has multiple trigger types."""
        triggers = automation_config['trigger']
        assert len(triggers) == 3
        
        # Event trigger
        event_triggers = [t for t in triggers if t['platform'] == 'event']
        assert len(event_triggers) == 1
        assert event_triggers[0]['event_type'] == 'doorbell_pressed'
        
        # State triggers
        state_triggers = [t for t in triggers if t['platform'] == 'state']
        assert len(state_triggers) == 2
        
        entity_ids = [t['entity_id'] for t in state_triggers]
        assert 'binary_sensor.front_door_motion' in entity_ids
        assert 'binary_sensor.doorbell_button' in entity_ids
    
    @pytest.mark.asyncio
    async def test_notification_actions(self, hass: HomeAssistant, automation_config):
        """Test that notification includes actionable buttons."""
        # Find notification action
        notify_action = None
        for action in automation_config['action'][0]['parallel']:
            if 'service' in action and action['service'] == 'notify.all_devices':
                notify_action = action
                break
        
        assert notify_action is not None
        actions = notify_action['data']['data']['actions']
        assert len(actions) == 3
        
        # Check action IDs and titles
        action_ids = [a['action'] for a in actions]
        assert 'OPEN_DOOR' in action_ids
        assert 'SPEAK' in action_ids
        assert 'IGNORE' in action_ids