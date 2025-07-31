# UI Testing with Playwright

This directory contains browser-based UI tests for Home Assistant using Playwright.

## Current Status

✅ **Working**: 
- Basic navigation tests (`test_basic.py`)
- Playwright browser automation
- Parallel test execution framework

⚠️ **In Progress**:
- Complex UI interaction tests (automation and entity pages)
- Custom fixtures for authenticated pages

The UI testing framework is set up and functional. Basic tests pass successfully. More complex tests that navigate to specific Home Assistant pages are being refined.

## Overview

UI tests verify the user interface functionality of Home Assistant, including:
- Navigation and page rendering
- Entity and automation interactions
- Form submissions and validations
- Visual elements and responsiveness
- Real user workflows

## Key Features

### Parallel Execution
- Tests run in parallel using pytest-xdist (2 workers by default)
- Each worker gets its own browser instance for isolation
- Browser contexts provide test isolation within workers
- No shared state between tests ensures reliable parallel execution

### Worker-Scoped Fixtures
- `browser`: One browser instance per pytest-xdist worker
- `context`: Fresh browser context for each test
- `page`: New page/tab for each test
- `worker_id`: Identifies which parallel worker is running

### Test Organization
```
tests/ui/
├── conftest.py           # Parallel-safe fixtures and helpers
├── requirements.txt      # UI-specific dependencies
├── test_automation_ui.py # Automation interface tests
├── test_entity_ui.py     # Entity interface tests
└── README.md            # This file
```

## Running UI Tests

### Automatic Container Management
All UI test commands automatically:
- Stop any existing Home Assistant containers
- Start a fresh Home Assistant instance
- Wait for it to be healthy
- Run the tests
- Stop and remove containers (even if tests fail)

This ensures tests always run against a clean Home Assistant instance.

### Basic Commands
```bash
# Run all UI tests in parallel (headless)
make test:ui

# Run with visible browser (headed mode)
make test:ui:headed

# Run in debug mode (single worker, slow motion)
make test:ui:debug

# Run specific test file
.venv/bin/pytest tests/ui/test_automation_ui.py -n 2

# Run specific test
.venv/bin/pytest tests/ui/test_automation_ui.py::TestAutomationUI::test_view_automations_list
```

### Command Line Options
- `-n 2`: Run with 2 parallel workers (default)
- `-n 0`: Disable parallel execution (useful for debugging)
- `--headed`: Show browser window
- `--slowmo=1000`: Slow down actions by 1000ms
- `-v`: Verbose output
- `-s`: Show print statements

## Writing UI Tests

### Basic Test Structure
```python
import pytest
from playwright.sync_api import Page, expect

class TestMyFeature:
    @pytest.mark.ui
    def test_feature_interaction(self, page: Page):
        """Test description."""
        # Navigate to Home Assistant
        page.goto("http://localhost:8123")
        
        # Wait for app to load
        page.wait_for_selector("home-assistant", state="visible")
        
        # Navigate to feature
        page.click("a[href='/config/feature']")
        
        # Wait for element
        expect(page.locator("ha-feature")).to_be_visible()
        
        # Interact with UI
        page.fill("input[name='value']", "test")
        page.click("mwc-button[raised]")
        
        # Assert results
        expect(page.locator(".success")).to_contain_text("Saved")
```

### Available Fixtures

#### Core Fixtures (from pytest-playwright)
- `page`: Browser page for interaction (automatically provided)
- `context`: Browser context with fresh state (automatically provided)
- `browser`: Browser instance (automatically provided)

#### Custom Fixtures
- `ha_url`: Home Assistant URL (default: http://localhost:8123)

### Best Practices

#### 1. Use Proper Selectors
```python
# Good - Specific selectors
await page.click("mwc-button[raised]")
await page.locator("ha-card[header='Triggers']")

# Avoid - Generic selectors
await page.click("button")
await page.locator("div.card")
```

#### 2. Wait for Elements
```python
# Wait for element to be visible
await expect(page.locator("ha-automation-picker")).to_be_visible()

# Wait for specific state
await page.wait_for_selector("hui-view", state="visible")

# Wait for network idle
await page.wait_for_load_state("networkidle")
```

#### 3. Handle Dynamic Content
```python
# Wait for content to load
await page.wait_for_timeout(500)  # Small delay for animations

# Check element count before interaction
if await page.locator("ha-card").count() > 0:
    await page.locator("ha-card").first.click()
```

#### 4. Test Isolation
```python
# Each test gets fresh browser context
# No need to clean up state between tests
async def test_isolated_1(self, page: Page):
    await page.evaluate("localStorage.setItem('key', 'value1')")
    
async def test_isolated_2(self, page: Page):
    # This test won't see localStorage from test_isolated_1
    value = await page.evaluate("localStorage.getItem('key')")
    assert value is None
```

## Parallel Execution Details

### How It Works
1. pytest-xdist creates multiple worker processes
2. Each worker gets its own browser instance via worker-scoped fixture
3. Tests are distributed across workers automatically
4. Each test gets a fresh browser context for isolation

### Benefits
- 2-4x faster test execution
- True isolation between tests
- No test interdependencies
- Reliable and reproducible results

### Debugging Parallel Issues
```bash
# Run without parallelization to isolate issues
.venv/bin/pytest tests/ui -n 0 -v

# Run with specific number of workers
.venv/bin/pytest tests/ui -n 1  # Single worker
.venv/bin/pytest tests/ui -n 4  # Four workers

# Check worker ID in tests
async def test_worker_info(self, worker_id: str):
    print(f"Running on worker: {worker_id}")
```

## Visual Testing

### Screenshots on Failure
Tests automatically capture screenshots when they fail:
```
reports/ui_screenshots/
└── test_name_worker01.png
```

### Manual Screenshots
```python
# Capture screenshot during test
await page.screenshot(path="debug_screenshot.png")

# Full page screenshot
await page.screenshot(path="full_page.png", full_page=True)
```

### Visual Regression Testing
```python
# Compare against baseline
await expect(page).to_have_screenshot("baseline.png")

# With tolerance
await expect(page).to_have_screenshot("baseline.png", max_diff_pixels=100)
```

## Common Patterns

### Testing Forms
```python
# Fill form fields
await page.fill("input[name='username']", "test_user")
await page.fill("input[name='password']", "test_pass")
await page.check("input[type='checkbox']")
await page.select_option("select[name='option']", "value1")

# Submit form
await page.click("button[type='submit']")

# Wait for response
await expect(page.locator(".success-message")).to_be_visible()
```

### Testing Dialogs
```python
# Open dialog
await page.click("mwc-button[icon='add']")

# Interact with dialog content
dialog = page.locator("ha-dialog")
await dialog.locator("input").fill("New Item")
await dialog.locator("mwc-button[slot='primaryAction']").click()

# Verify dialog closed
await expect(dialog).not_to_be_visible()
```

### Testing Dynamic Lists
```python
# Wait for list to load
await page.wait_for_selector("mwc-list-item", state="visible")

# Count items
items = page.locator("mwc-list-item")
count = await items.count()

# Interact with specific item
if count > 2:
    await items.nth(2).click()
```

## Troubleshooting

### Browser Not Found
```bash
# Install Playwright browsers
.venv/bin/playwright install chromium firefox webkit
```

### Timeout Errors
```python
# Increase timeout for slow operations
await page.click("button", timeout=60000)  # 60 seconds

# Set default timeout for page
page.set_default_timeout(60000)
```

### Element Not Found
```python
# Debug selector
await page.screenshot(path="debug.png")
print(await page.content())  # Print HTML

# Wait for JavaScript to load
await page.wait_for_load_state("domcontentloaded")
await page.wait_for_load_state("networkidle")
```

### Flaky Tests
1. Add explicit waits instead of arbitrary timeouts
2. Use `wait_for_selector` with specific state
3. Check element count before interaction
4. Use `expect` assertions with built-in retries

## Environment Variables

- `HA_URL`: Home Assistant URL (default: http://localhost:8123)
- `HA_USERNAME`: Username for login (if not using bypass auth)
- `HA_PASSWORD`: Password for login (if not using bypass auth)

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Install Playwright
  run: |
    pip install -r tests/ui/requirements.txt
    playwright install chromium

- name: Run UI Tests
  run: |
    make start  # Start Home Assistant
    sleep 30    # Wait for HA to initialize
    make test:ui
```

### Artifacts on Failure
```yaml
- name: Upload Screenshots
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: ui-test-screenshots
    path: reports/ui_screenshots/
```