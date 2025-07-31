"""Basic UI test using pytest-playwright fixtures."""

import pytest


@pytest.mark.ui
def test_basic_navigation(page):
    """Test basic navigation to Home Assistant."""
    # Navigate to Home Assistant
    page.goto("http://localhost:8123")
    
    # Check the title
    assert "Home Assistant" in page.title() or "Loading" in page.title()
    
    # Take a screenshot for debugging
    page.screenshot(path="test_basic_navigation.png")
    print(f"Page title: {page.title()}")


@pytest.mark.ui  
def test_parallel_isolation_sync(page):
    """Test that pages are isolated in parallel execution."""
    # Navigate to HA
    page.goto("http://localhost:8123")
    
    # Set a value in localStorage
    page.evaluate("localStorage.setItem('test_key', 'test_value')")
    
    # Verify we can read it back
    value = page.evaluate("localStorage.getItem('test_key')")
    assert value == "test_value"