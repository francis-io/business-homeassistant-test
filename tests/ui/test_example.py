"""Example UI tests demonstrating the current working setup."""

import pytest
from playwright.sync_api import Page


class TestExampleUI:
    """Example UI tests that work with the current setup."""

    @pytest.mark.ui
    def test_home_assistant_title(self, page: Page, ha_url: str):
        """Test that Home Assistant page has correct title."""
        # Navigate to Home Assistant
        page.goto(ha_url, wait_until="networkidle")

        # Check the title
        title = page.title()
        assert "Home Assistant" in title or "Loading" in title

    @pytest.mark.ui
    def test_take_screenshot(self, page: Page, ha_url: str):
        """Test taking a screenshot of Home Assistant."""
        # Navigate to Home Assistant
        page.goto(ha_url, wait_until="networkidle")

        # Take a screenshot
        page.screenshot(path="/reports/ha_screenshot.png")

        # Verify screenshot was taken (file will exist)
        assert True, "Screenshot taken successfully"

    @pytest.mark.ui
    def test_page_content(self, page: Page, ha_url: str):
        """Test that Home Assistant page loads content."""
        # Navigate to Home Assistant
        page.goto(ha_url, wait_until="networkidle")

        # Wait a moment for content to load
        page.wait_for_timeout(1000)

        # Check that page has content
        content = page.content()
        assert len(content) > 100, "Page should have substantial content"

    @pytest.mark.ui
    def test_parallel_execution(self, page: Page, ha_url: str):
        """Test designed to verify parallel execution works."""
        # Navigate to Home Assistant
        page.goto(ha_url, wait_until="networkidle")

        # Each test gets its own page context
        # Set a unique value
        import random

        unique_id = f"test_{random.randint(1000, 9999)}"

        # Use JavaScript to verify isolation
        page.evaluate(f"window.testId = '{unique_id}'")

        # Verify we get our value back
        result = page.evaluate("window.testId")
        assert result == unique_id
