"""Base class for automation tests with built-in validation.

This provides a reusable base class that handles common automation testing
patterns including validation, service mocking, and state management.
"""

import pytest
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from .automation_validation import (
    assert_valid_automation,
    validate_service_data,
    get_automation_summary,
    ValidationError
)


class AutomationTestBase:
    """Base class for automation tests with validation and helpers."""
    
    # Override these in subclasses
    AUTOMATION_FILE: Optional[str] = None  # Path to YAML file
    AUTOMATION_CONFIG: Optional[Dict[str, Any]] = None  # Or provide config directly
    
    @pytest.fixture
    def automation_config(self):
        """Load and validate automation configuration."""
        if self.AUTOMATION_CONFIG:
            config = self.AUTOMATION_CONFIG
        elif self.AUTOMATION_FILE:
            # AUTOMATION_FILE should be an absolute path or Path object
            yaml_path = Path(self.AUTOMATION_FILE)
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)
        else:
            raise ValueError("Must set either AUTOMATION_FILE or AUTOMATION_CONFIG")
        
        # Validate before testing
        try:
            assert_valid_automation(config)
        except ValidationError as e:
            pytest.fail(f"Invalid automation configuration: {e}")
        
        # Log summary for debugging
        print(f"\nTesting automation: {get_automation_summary(config)}")
        
        return config
    
    @pytest.fixture
    def service_tracker(self, hass: HomeAssistant):
        """Track service calls with validation."""
        tracked_calls = {}
        
        async def create_tracker(domain: str, service: str, validate: bool = True):
            """Create a service handler that tracks and validates calls."""
            calls = []
            tracked_calls[f"{domain}.{service}"] = calls
            
            async def handler(call):
                # Validate service data if requested
                if validate:
                    is_valid, errors = validate_service_data(
                        domain, service, dict(call.data)
                    )
                    if not is_valid:
                        pytest.fail(f"Invalid service data for {domain}.{service}: {errors}")
                
                calls.append({
                    'domain': domain,
                    'service': service,
                    'data': dict(call.data),
                    'context': call.context
                })
            
            hass.services.async_register(domain, service, handler)
            return calls
        
        # Return both the creator function and the tracked calls
        return create_tracker, tracked_calls
    
    @pytest.fixture
    async def setup_automation(self, hass: HomeAssistant, automation_config):
        """Set up the automation in Home Assistant."""
        assert await async_setup_component(hass, 'automation', {
            'automation': [automation_config]
        })
        await hass.async_block_till_done()
        return automation_config
    
    async def execute_automation_actions(
        self, 
        hass: HomeAssistant, 
        automation_config: Dict[str, Any],
        skip_delays: bool = True
    ):
        """Execute all actions from an automation."""
        for action in automation_config.get('action', []):
            if skip_delays and 'delay' in action:
                continue
                
            if 'service' in action:
                await hass.services.async_call(
                    action['service'].split('.')[0],
                    action['service'].split('.')[1],
                    action.get('data', {}) | action.get('target', {}),
                    blocking=True
                )
    
    def assert_service_called(
        self,
        calls: List[Dict[str, Any]],
        expected_domain: str,
        expected_service: str,
        expected_data: Optional[Dict[str, Any]] = None,
        call_index: int = 0
    ):
        """Assert a specific service was called with expected data."""
        assert len(calls) > call_index, (
            f"Expected at least {call_index + 1} calls to "
            f"{expected_domain}.{expected_service}, got {len(calls)}"
        )
        
        call = calls[call_index]
        assert call['domain'] == expected_domain
        assert call['service'] == expected_service
        
        if expected_data:
            for key, value in expected_data.items():
                assert key in call['data'], f"Missing key '{key}' in service data"
                assert call['data'][key] == value, (
                    f"Expected {key}={value}, got {key}={call['data'][key]}"
                )
    
    def assert_services_called_in_order(
        self,
        tracked_calls: Dict[str, List[Dict[str, Any]]],
        expected_order: List[str]
    ):
        """Assert services were called in a specific order."""
        all_calls = []
        for service_name, calls in tracked_calls.items():
            for call in calls:
                all_calls.append((service_name, call))
        
        # Sort by context (which preserves order in HA)
        all_calls.sort(key=lambda x: str(x[1]['context']))
        
        actual_order = [call[0] for call in all_calls]
        
        # Check that expected order is a subsequence of actual order
        actual_idx = 0
        for expected_service in expected_order:
            found = False
            while actual_idx < len(actual_order):
                if actual_order[actual_idx] == expected_service:
                    found = True
                    actual_idx += 1
                    break
                actual_idx += 1
            
            assert found, (
                f"Expected service '{expected_service}' not found in order. "
                f"Actual order: {actual_order}"
            )