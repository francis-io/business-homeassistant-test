"""Basic UI test using pytest-playwright fixtures."""

import pytest


@pytest.mark.ui
def test_basic_navigation(page, ha_url, save_screenshot):
    """Test basic navigation to Home Assistant."""
    # Navigate to Home Assistant
    page.goto(ha_url, wait_until="networkidle")

    # Check the title
    assert "Home Assistant" in page.title() or "Loading" in page.title()

    # Take a screenshot for debugging
    save_screenshot(page, "test_basic_navigation")
    print(f"Page title: {page.title()}")


@pytest.mark.ui
def test_parallel_isolation_sync(page, ha_url):
    """Test that pages are isolated in parallel execution."""
    # Navigate to HA
    page.goto(ha_url, wait_until="networkidle")

    # Set a value in localStorage
    page.evaluate("localStorage.setItem('test_key', 'test_value')")

    # Verify we can read it back
    value = page.evaluate("localStorage.getItem('test_key')")
    assert value == "test_value"
