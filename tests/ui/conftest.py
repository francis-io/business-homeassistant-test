"""UI test configuration for pytest-playwright."""

import os

import pytest
from playwright.sync_api import Page


@pytest.fixture
def ha_url() -> str:
    """Get Home Assistant URL from environment or default."""
    return os.getenv("HA_URL", "http://localhost:8123")


@pytest.fixture
def screenshot_dir():
    """Get the screenshot directory from environment or default."""
    return os.environ.get("PYTEST_SCREENSHOT_DIR", "/reports")


@pytest.fixture
def save_screenshot(screenshot_dir):
    """Provide helper function to save screenshots in the correct directory."""

    def _save(page: Page, name: str):
        """Save a screenshot with the given name."""
        if not name.endswith(".png"):
            name += ".png"
        path = os.path.join(screenshot_dir, name)
        page.screenshot(path=path)
        return path

    return _save


# Hook to automatically take screenshots on test failure
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Take a screenshot if a UI test fails."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Check if this is a UI test with a page fixture
        if "page" in item.fixturenames:
            page = item.funcargs.get("page")
            screenshot_dir = os.environ.get("PYTEST_SCREENSHOT_DIR", "/reports")

            if page:
                screenshot_name = f"failure_{item.name}.png"
                screenshot_path = os.path.join(screenshot_dir, screenshot_name)
                try:
                    page.screenshot(path=screenshot_path)
                    print(f"\nScreenshot saved: {screenshot_path}")
                except Exception as e:
                    print(f"\nFailed to save screenshot: {e}")


# Let pytest-playwright handle browser, context, and page fixtures automatically
