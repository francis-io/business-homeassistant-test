# UI Testing with Playwright

This directory contains browser-based UI tests for Home Assistant using Playwright.

## Overview

UI tests run in Docker containers, ensuring consistent environments across different machines. The tests use Playwright for browser automation and run against a containerized Home Assistant instance.

## Running UI Tests

All UI tests run in Docker containers with the following workflow:
1. Clean up any existing test containers
2. Validate Home Assistant configuration
3. Start fresh Home Assistant instance
4. Complete onboarding automatically
5. Run UI tests with Playwright
6. Generate timestamped test reports
7. Clean up all containers

### Basic Commands

```bash
# Run all UI tests (headless mode)
make test:ui

# Run with visible browser (headed mode)
make test:ui:headed

# Run in debug mode (single worker, slow motion, visible browser)
make test:ui:debug
```

### What Happens Behind the Scenes

The `make test:ui` commands:
- Build a custom Docker image with Python 3.11 and Playwright browsers
- Start Home Assistant with a clean configuration
- Automatically complete the onboarding process
- Run UI tests inside the container
- Save test reports with timestamps to `reports/` directory
- Clean up all containers after completion

## Docker Architecture

### Container Services

1. **config-validator**: Validates Home Assistant configuration before starting
2. **home-assistant-server**: Runs Home Assistant with health checks
3. **onboarding**: Completes Home Assistant setup automatically
4. **runner-ui**: Executes UI tests with Playwright browsers installed

### File Structure
```
tests/ui/docker/
├── docker-compose.yml    # Orchestrates all services
├── Dockerfile           # Custom image with Playwright
├── .env                 # Environment variables
├── config/              # Home Assistant configuration
│   └── configuration.yaml
└── scripts/             # Onboarding automation scripts
    ├── onboarding.py
    └── onboarding_and_test.py
```

## Writing UI Tests

### Basic Test Structure
```python
import pytest
from playwright.sync_api import Page

@pytest.mark.ui
def test_home_assistant_loads(page: Page, ha_url: str):
    """Test that Home Assistant loads successfully."""
    # Navigate to Home Assistant
    page.goto(ha_url, wait_until="networkidle")
    
    # Check the title
    assert "Home Assistant" in page.title()
    
    # Take a screenshot
    page.screenshot(path="/reports/test_screenshot.png")
```

### Available Fixtures

- `page`: Playwright page object for browser interaction
- `ha_url`: URL of the Home Assistant instance (from environment)
- `context`: Browser context (automatically provided)
- `browser`: Browser instance (automatically provided)

### Best Practices

1. **Wait for Page Load**
   ```python
   page.goto(ha_url, wait_until="networkidle")
   ```

2. **Use Proper Selectors**
   ```python
   # Good - Specific selectors
   page.click("mwc-button[raised]")
   page.locator("ha-card[header='Automations']")
   
   # Avoid - Generic selectors
   page.click("button")
   ```

3. **Handle Dynamic Content**
   ```python
   # Wait for elements
   page.wait_for_selector("home-assistant", state="visible")
   
   # Use expect for auto-retry
   from playwright.sync_api import expect
   expect(page.locator("ha-card")).to_be_visible()
   ```

4. **Screenshots in Reports Directory**
   ```python
   # Screenshots must go to /reports/ which is mounted
   page.screenshot(path="/reports/my_screenshot.png")
   ```

## Test Reports

Test results are saved in the `reports/` directory:
- Report files are named: `ui_YYYYMMDD_HHMMSS_results.xml`
- Each test run generates a new timestamped report
- Screenshots are saved alongside reports
- Reports are in JUnit XML format for CI/CD integration

## Parallel Execution

Tests run in parallel by default (2 workers):
- Each worker gets its own browser instance
- Tests are isolated with fresh browser contexts
- No shared state between tests

To control parallelization:
```bash
# Default: 2 parallel workers
make test:ui

# Debug mode: Single worker
make test:ui:debug

# Custom: Set workers via environment
docker-compose -f tests/ui/docker/docker-compose.yml run \
  -e "DEBUG=false" \
  -e "PYTEST_WORKERS=4" \
  home-assistant-test-runner-ui
```

## Environment Variables

The following environment variables are available:
- `HA_URL`: Home Assistant URL (default: http://home-assistant-test-server:8123)
- `HEADED`: Run in headed mode (default: false)
- `DEBUG`: Run in debug mode with single worker (default: false)
- `SLOWMO`: Milliseconds to slow down actions in debug mode (default: 0)

## Troubleshooting

### Container Issues
```bash
# View logs
docker-compose -f tests/ui/docker/docker-compose.yml logs

# Clean up stuck containers
docker ps -a --filter "name=home-assistant-test-" --format "{{.Names}}" | xargs -r docker rm -f
```

### Test Failures
1. Check if Home Assistant started correctly
2. Verify onboarding completed successfully
3. Look at screenshots in reports directory
4. Run in debug mode to see browser interactions

### Common Errors

**"Read-only file system"**: Ensure screenshots are saved to `/reports/` not relative paths

**"Connection refused"**: Home Assistant may not be ready. The tests wait for health checks.

**"Element not found"**: Home Assistant UI may have changed. Update selectors.

## CI/CD Integration

The containerized approach makes CI/CD integration simple:

```yaml
# Example GitHub Actions
- name: Run UI Tests
  run: make test:ui

- name: Upload Test Results
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: ui-test-results
    path: reports/
```

## Development Tips

1. **Local Development**: You can still run tests locally without Docker if you have Home Assistant running on localhost:8123

2. **Browser Choice**: Tests run on Chromium by default. Firefox and WebKit are also installed.

3. **Debugging**: Use `make test:ui:debug` to see the browser and slow down actions

4. **Custom Configuration**: Modify `tests/ui/docker/config/configuration.yaml` to test specific HA setups