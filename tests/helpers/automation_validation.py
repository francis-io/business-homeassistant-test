"""Automation validation helpers for Home Assistant tests.

This module provides reusable validation functions for automation configurations
before running tests, helping catch configuration errors early.
"""

from typing import Dict, List, Any, Optional, Tuple

# Valid trigger platforms
VALID_TRIGGER_PLATFORMS = {
    'event', 'homeassistant', 'mqtt', 'numeric_state', 'state',
    'sun', 'tag', 'template', 'time', 'time_pattern', 'webhook', 'zone'
}

# Valid condition types
VALID_CONDITION_TYPES = {
    'and', 'or', 'not', 'device', 'numeric_state', 'state',
    'sun', 'template', 'time', 'trigger', 'zone'
}

# Valid action types
VALID_ACTION_TYPES = {
    'service', 'delay', 'wait_template', 'wait_for_trigger',
    'repeat', 'choose', 'parallel', 'if', 'stop', 'variables', 'event'
}

# Valid automation modes
VALID_MODES = {'single', 'restart', 'queued', 'parallel'}


class ValidationError(Exception):
    """Raised when automation validation fails."""
    pass


def validate_automation_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a complete automation configuration.
    
    Args:
        config: The automation configuration dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    if 'trigger' not in config and 'id' not in config:
        errors.append("Automation must have either 'trigger' or 'id' field")
    
    # Validate ID if present
    if 'id' in config:
        if not isinstance(config['id'], str):
            errors.append(f"ID must be a string, got {type(config['id']).__name__}")
        elif not config['id']:
            errors.append("ID cannot be empty")
    
    # Validate alias
    if 'alias' in config:
        if not isinstance(config['alias'], str):
            errors.append(f"Alias must be a string, got {type(config['alias']).__name__}")
    
    # Validate mode
    if 'mode' in config:
        if config['mode'] not in VALID_MODES:
            errors.append(f"Invalid mode '{config['mode']}'. Must be one of: {', '.join(VALID_MODES)}")
    
    # Validate triggers
    if 'trigger' in config:
        trigger_errors = validate_triggers(config['trigger'])
        errors.extend(trigger_errors)
    
    # Validate conditions
    if 'condition' in config:
        condition_errors = validate_conditions(config['condition'])
        errors.extend(condition_errors)
    
    # Validate actions
    if 'action' in config:
        action_errors = validate_actions(config['action'])
        errors.extend(action_errors)
    else:
        errors.append("Automation must have 'action' field")
    
    return len(errors) == 0, errors


def validate_triggers(triggers: List[Dict[str, Any]]) -> List[str]:
    """Validate trigger configurations."""
    errors = []
    
    if not isinstance(triggers, list):
        return [f"Triggers must be a list, got {type(triggers).__name__}"]
    
    for i, trigger in enumerate(triggers):
        if not isinstance(trigger, dict):
            errors.append(f"Trigger {i} must be a dict, got {type(trigger).__name__}")
            continue
            
        if 'platform' not in trigger:
            errors.append(f"Trigger {i} missing required 'platform' field")
            continue
            
        platform = trigger['platform']
        if platform not in VALID_TRIGGER_PLATFORMS:
            errors.append(f"Trigger {i} has invalid platform '{platform}'")
            continue
        
        # Platform-specific validation
        if platform == 'time':
            if 'at' not in trigger:
                errors.append(f"Time trigger {i} missing required 'at' field")
            else:
                # Validate time format
                at_time = trigger['at']
                if not _is_valid_time_string(at_time):
                    errors.append(f"Time trigger {i} has invalid time format: {at_time}")
                    
        elif platform == 'state':
            if 'entity_id' not in trigger:
                errors.append(f"State trigger {i} missing required 'entity_id' field")
                
        elif platform == 'numeric_state':
            if 'entity_id' not in trigger:
                errors.append(f"Numeric state trigger {i} missing required 'entity_id' field")
            if 'above' not in trigger and 'below' not in trigger:
                errors.append(f"Numeric state trigger {i} must have 'above' or 'below'")
                
        elif platform == 'sun':
            if 'event' not in trigger:
                errors.append(f"Sun trigger {i} missing required 'event' field")
            elif trigger['event'] not in ['sunrise', 'sunset']:
                errors.append(f"Sun trigger {i} event must be 'sunrise' or 'sunset'")
    
    return errors


def validate_conditions(conditions: List[Dict[str, Any]]) -> List[str]:
    """Validate condition configurations."""
    errors = []
    
    if not isinstance(conditions, list):
        return [f"Conditions must be a list, got {type(conditions).__name__}"]
    
    for i, condition in enumerate(conditions):
        if not isinstance(condition, dict):
            errors.append(f"Condition {i} must be a dict, got {type(condition).__name__}")
            continue
            
        if 'condition' not in condition:
            errors.append(f"Condition {i} missing required 'condition' field")
            continue
            
        cond_type = condition['condition']
        if cond_type not in VALID_CONDITION_TYPES:
            errors.append(f"Condition {i} has invalid type '{cond_type}'")
            continue
        
        # Type-specific validation
        if cond_type == 'state':
            if 'entity_id' not in condition:
                errors.append(f"State condition {i} missing required 'entity_id' field")
            if 'state' not in condition:
                errors.append(f"State condition {i} missing required 'state' field")
                
        elif cond_type == 'numeric_state':
            if 'entity_id' not in condition:
                errors.append(f"Numeric state condition {i} missing required 'entity_id' field")
            if 'above' not in condition and 'below' not in condition:
                errors.append(f"Numeric state condition {i} must have 'above' or 'below'")
                
        elif cond_type == 'time':
            has_after = 'after' in condition
            has_before = 'before' in condition
            if not has_after and not has_before:
                errors.append(f"Time condition {i} must have 'after' or 'before'")
            if has_after and not _is_valid_time_string(condition['after']):
                errors.append(f"Time condition {i} has invalid 'after' time format")
            if has_before and not _is_valid_time_string(condition['before']):
                errors.append(f"Time condition {i} has invalid 'before' time format")
    
    return errors


def validate_actions(actions: List[Dict[str, Any]]) -> List[str]:
    """Validate action configurations."""
    errors = []
    
    if not isinstance(actions, list):
        return [f"Actions must be a list, got {type(actions).__name__}"]
    
    if not actions:
        return ["Automation must have at least one action"]
    
    for i, action in enumerate(actions):
        if not isinstance(action, dict):
            errors.append(f"Action {i} must be a dict, got {type(action).__name__}")
            continue
        
        # Determine action type
        action_type = None
        if 'service' in action:
            action_type = 'service'
        elif 'delay' in action:
            action_type = 'delay'
        elif 'wait_template' in action:
            action_type = 'wait_template'
        elif 'repeat' in action:
            action_type = 'repeat'
        elif 'choose' in action:
            action_type = 'choose'
        elif 'if' in action:
            action_type = 'if'
        elif 'stop' in action:
            action_type = 'stop'
        elif 'variables' in action:
            action_type = 'variables'
        elif 'parallel' in action:
            action_type = 'parallel'
        elif 'event' in action:
            action_type = 'event'
        else:
            errors.append(f"Action {i} has no recognized action type")
            continue
        
        # Type-specific validation
        if action_type == 'service':
            service = action['service']
            if not isinstance(service, str):
                errors.append(f"Action {i} service must be a string")
            elif '.' not in service:
                errors.append(f"Action {i} service '{service}' must be in format 'domain.service'")
            else:
                domain, service_name = service.split('.', 1)
                if not domain or not service_name:
                    errors.append(f"Action {i} has invalid service format: '{service}'")
                    
            # Validate target/entity_id
            if 'target' in action:
                target = action['target']
                if not isinstance(target, dict):
                    errors.append(f"Action {i} target must be a dict")
                elif 'entity_id' not in target and 'device_id' not in target and 'area_id' not in target:
                    errors.append(f"Action {i} target must have entity_id, device_id, or area_id")
                    
        elif action_type == 'delay':
            delay = action['delay']
            if not isinstance(delay, (dict, str)):
                errors.append(f"Action {i} delay must be a dict or string")
            elif isinstance(delay, dict):
                if not any(key in delay for key in ['hours', 'minutes', 'seconds', 'milliseconds']):
                    errors.append(f"Action {i} delay must have time units")
                    
        elif action_type == 'parallel':
            parallel = action['parallel']
            if not isinstance(parallel, list):
                errors.append(f"Action {i} parallel must be a list")
            else:
                # Recursively validate parallel actions
                parallel_errors = validate_actions(parallel)
                for error in parallel_errors:
                    errors.append(f"Action {i} parallel: {error}")
    
    return errors


def _is_valid_time_string(time_str: str) -> bool:
    """Check if a string is a valid time format (HH:MM or HH:MM:SS)."""
    if not isinstance(time_str, str):
        return False
    
    parts = time_str.split(':')
    if len(parts) not in (2, 3):
        return False
    
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2]) if len(parts) == 3 else 0
        
        if not (0 <= hours <= 23):
            return False
        if not (0 <= minutes <= 59):
            return False
        if not (0 <= seconds <= 59):
            return False
        
        return True
    except ValueError:
        return False


def validate_service_data(domain: str, service: str, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate service call data for common domains."""
    errors = []
    
    if domain == 'light':
        if service == 'turn_on':
            # Validate brightness
            if 'brightness' in data:
                brightness = data['brightness']
                if not isinstance(brightness, (int, float)) or not 0 <= brightness <= 255:
                    errors.append(f"brightness must be 0-255, got {brightness}")
                    
            if 'brightness_pct' in data:
                brightness_pct = data['brightness_pct']
                if not isinstance(brightness_pct, (int, float)) or not 0 <= brightness_pct <= 100:
                    errors.append(f"brightness_pct must be 0-100, got {brightness_pct}")
                    
            # Validate color temperature
            if 'color_temp' in data:
                color_temp = data['color_temp']
                if not isinstance(color_temp, (int, float)) or color_temp < 0:
                    errors.append(f"color_temp must be positive, got {color_temp}")
                    
            # Validate transition
            if 'transition' in data:
                transition = data['transition']
                if not isinstance(transition, (int, float)) or transition < 0:
                    errors.append(f"transition must be non-negative, got {transition}")
                    
    elif domain == 'climate':
        if service == 'set_temperature':
            if 'temperature' not in data:
                errors.append("climate.set_temperature requires 'temperature' field")
            else:
                temp = data['temperature']
                if not isinstance(temp, (int, float)) or not -50 <= temp <= 50:
                    errors.append(f"temperature seems unrealistic: {temp}")
                    
    elif domain == 'notify':
        if 'message' not in data:
            errors.append("notify services require 'message' field")
    
    return len(errors) == 0, errors


def assert_valid_automation(config: Dict[str, Any]) -> None:
    """Assert that an automation configuration is valid, raising on errors."""
    is_valid, errors = validate_automation_config(config)
    if not is_valid:
        raise ValidationError(f"Invalid automation configuration:\n" + "\n".join(f"  - {e}" for e in errors))


def get_automation_summary(config: Dict[str, Any]) -> str:
    """Get a human-readable summary of an automation."""
    parts = []
    
    # Basic info
    if 'id' in config:
        parts.append(f"ID: {config['id']}")
    if 'alias' in config:
        parts.append(f"Alias: {config['alias']}")
    if 'mode' in config:
        parts.append(f"Mode: {config['mode']}")
    
    # Triggers
    if 'trigger' in config:
        trigger_count = len(config['trigger'])
        trigger_types = {t.get('platform', 'unknown') for t in config['trigger']}
        parts.append(f"Triggers: {trigger_count} ({', '.join(trigger_types)})")
    
    # Conditions
    if 'condition' in config:
        condition_count = len(config['condition'])
        condition_types = {c.get('condition', 'unknown') for c in config['condition']}
        parts.append(f"Conditions: {condition_count} ({', '.join(condition_types)})")
    
    # Actions
    if 'action' in config:
        action_count = len(config['action'])
        services = [a.get('service', '') for a in config['action'] if 'service' in a]
        if services:
            parts.append(f"Actions: {action_count} (services: {', '.join(services)})")
        else:
            parts.append(f"Actions: {action_count}")
    
    return " | ".join(parts)