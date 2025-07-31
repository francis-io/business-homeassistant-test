"""Test to verify persons.yaml configuration is valid."""

import pytest
import yaml
from pathlib import Path


def test_persons_yaml_is_valid():
    """Test that persons.yaml is valid YAML and contains expected persons."""
    yaml_path = Path(__file__).parent.parent / "e2e/docker/config/persons.yaml"
    
    # Load the persons config
    with open(yaml_path, 'r') as f:
        persons_config = yaml.safe_load(f)
    
    # Should be a list
    assert isinstance(persons_config, list), "persons.yaml should contain a list"
    
    # Should have exactly 2 persons
    assert len(persons_config) == 2, f"Expected 2 persons, found {len(persons_config)}"
    
    # Check John
    john = next((p for p in persons_config if p.get('id') == 'john'), None)
    assert john is not None, "Person 'john' not found"
    assert john['name'] == 'John'
    assert john['user_id'] == 'test_user_john'
    assert john['device_trackers'] == ['device_tracker.johns_phone']
    
    # Check Test User
    test_user = next((p for p in persons_config if p.get('id') == 'test_user'), None)
    assert test_user is not None, "Person 'test_user' not found"
    assert test_user['name'] == 'Test User'
    assert test_user['user_id'] == 'test_user_id'
    assert test_user['device_trackers'] == ['device_tracker.test_phone']


def test_persons_config_structure():
    """Test that persons config has valid structure for Home Assistant."""
    yaml_path = Path(__file__).parent.parent / "e2e/docker/config/persons.yaml"
    
    with open(yaml_path, 'r') as f:
        persons_config = yaml.safe_load(f)
    
    # Check that it's a list of dicts
    assert isinstance(persons_config, list), "persons config should be a list"
    
    for person in persons_config:
        assert isinstance(person, dict), f"Each person should be a dict, got {type(person)}"
        
        # Check that name and id are strings
        assert isinstance(person.get('name'), str), f"name should be a string"
        assert isinstance(person.get('id'), str), f"id should be a string"


def test_all_required_fields_present():
    """Test that all persons have required fields."""
    yaml_path = Path(__file__).parent.parent / "e2e/docker/config/persons.yaml"
    
    with open(yaml_path, 'r') as f:
        persons_config = yaml.safe_load(f)
    
    required_fields = ['name', 'id']
    optional_fields = ['device_trackers', 'user_id']
    
    for person in persons_config:
        # Check required fields
        for field in required_fields:
            assert field in person, f"Person missing required field '{field}': {person}"
        
        # Check that optional fields, if present, have correct types
        if 'device_trackers' in person:
            assert isinstance(person['device_trackers'], list), \
                f"device_trackers should be a list for person {person['id']}"
        
        if 'user_id' in person:
            assert isinstance(person['user_id'], str), \
                f"user_id should be a string for person {person['id']}"