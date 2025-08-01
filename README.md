# Home Assistant Testing Framework

A comprehensive testing framework for Home Assistant configurations, integrations, and automations. This framework supports multiple testing levels from unit tests to full integration tests using Docker containers.

## Two Testing Approaches

### 1. Logic-First Testing (Recommended)

Test automation **logic** as pure Python functions without Home Assistant:

- ✅ Fast execution (milliseconds)
- ✅ No HA instance needed
- ✅ Test-driven development
- ✅ Easy to understand

See [Testing Strategy Documentation](docs/testing-strategy.md) for details.

### 2. Mock-Based Testing

Test automation behavior using mocked Home Assistant components:

- ✅ Tests service calls and state changes
- ✅ Simulates HA behavior
- ❌ Doesn't test actual automations
- ❌ Requires manual state updates

## Features

- 🧪 **Multi-level Testing**: Unit, Integration, UI, and API tests
- 🐳 **Docker-based**: Isolated Home Assistant instance with health monitoring
- ✅ **Configuration Validation**: Automatic validation before Home Assistant starts
- ⚡ **Fast Feedback**: Unit tests run in seconds, integration tests in minutes
- 🚀 **Parallel Execution**: Tests run across all CPU cores with pytest-xdist
- 📊 **Coverage Reports**: HTML coverage reports with detailed metrics
- 🔄 **CI/CD Ready**: JUnit XML output for CI integration
- 🎯 **Specific Scenarios**: Test time-based automations, notifications, and zone entry
- 📸 **UI Testing**: Playwright-based browser automation with screenshot support
- 📁 **Organized Output**: Timestamped directories for test artifacts and screenshots

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Just command runner (https://github.com/casey/just)
- Make (optional, for backward compatibility)
- UV package manager (for Python dependency management)

### Setup

1. Clone the repository and navigate to the project directory

1. Install dependencies based on your testing needs:

   ```bash
   # For unit tests only
   just python::setup

   # For unit + integration tests (includes Home Assistant)
   just python::setup-integration

   # For all test types (includes E2E and UI support)
   just python::setup-all
   ```

   This will:

   - Create Python 3.11 environment using UV
   - Install test dependencies from tests/requirements/
   - Set up bypass authentication for Docker

1. Build Docker containers:

   ```bash
   just docker::build
   ```

1. Start Home Assistant:

   ```bash
   just docker::start
   ```

   The system will automatically wait for Home Assistant to be healthy before proceeding. You can check the health status anytime with:

   ```bash
   just docker::healthcheck
   ```

1. Run all tests:

   ```bash
   just test
   # or
   make test
   ```

   **Note**: `just` and `make` commands are interchangeable throughout this project!

## Test Scenarios

This framework includes tests for three common Home Assistant automation patterns:

### 1. Time-Based Light Automation

- Turns on lights at specific times
- Includes sunset/sunrise conditions
- Tests brightness and transition settings

### 2. Notification System

- Sends mobile app notifications on events
- Tests priority levels and action buttons
- Validates notification content and delivery

### 3. Zone Entry Automation

- Triggers actions when person enters home zone
- Time-based conditions (evening only)
- Multiple actions: lights, climate, notifications

## UI Testing

The framework includes Playwright-based UI testing capabilities:

### Features

- **Browser Automation**: Test Home Assistant's web interface
- **Screenshot Support**: Automatic screenshots on test failure
- **Parallel Execution**: Run UI tests in parallel for faster feedback
- **Debug Mode**: Step through tests with visible browser and slow motion
- **Docker Container**: Pre-configured container with all Playwright dependencies

### Running UI Tests

```bash
# Run all UI tests (headless)
just test::ui

# Run with visible browser
just test::ui::headed

# Debug mode (slow motion, single thread)
just test::ui::debug

# Screenshots are saved to:
# reports/YYYY-MM-DD_HH-MM-SS_ui/
```

### Writing UI Tests

```python
@pytest.mark.ui
def test_home_assistant_navigation(page, ha_url, save_screenshot):
    """Test navigating Home Assistant UI."""
    # Navigate to Home Assistant
    page.goto(ha_url, wait_until="networkidle")

    # Take a screenshot
    save_screenshot(page, "main_page")

    # Interact with the UI
    page.click("text=Dashboard")

    # Verify navigation
    assert "Dashboard" in page.title()
```

The `save_screenshot` fixture automatically saves screenshots to the test run's directory. Failed tests automatically capture screenshots for debugging.

## Running Tests

### Using Just or Make

Just and Make are interchangeable - use whichever you prefer:

```bash
# Run all tests (both commands do the same thing)
just test
make test

# Run specific test types (just/make are interchangeable)
just test::unit             # Unit tests only (logic + mock)
make test::unit             # Same as above

just test::unit::logic      # Logic tests only
make test::unit::logic      # Same as above

just test::integration      # Integration tests (in-memory HA)
make test::integration      # Same as above

just test::e2e              # End-to-end tests (Docker)
make test::e2e              # Same as above

just test::ui               # UI tests with Playwright (Docker)
make test::ui               # Same as above

just test::ui::headed       # UI tests with visible browser
make test::ui::headed       # Same as above

# Watch mode for development
just test::watch
make test::watch

# Get help for any module (both work)
just test::help             # Help for all test commands
make test::help             # Same as above

just test::unit::help       # Help for unit test commands
make test::unit::help       # Same as above
```

### Test Output Organization

Test results are organized in timestamped directories for better tracking:

```
reports/
├── 2025-08-01_14-30-45_unit/      # Unit test run
│   └── results.xml
├── 2025-08-01_14-32-10_integration/ # Integration test run
│   └── results.xml
├── 2025-08-01_14-35-20_e2e/       # E2E test run
│   └── results.xml
├── 2025-08-01_14-40-15_ui/        # UI test run
│   ├── results.xml
│   ├── test_basic_navigation.png    # Screenshot from test
│   └── failure_test_example.png     # Automatic failure screenshot
└── last_report.txt                  # Points to most recent test run
```

Features:

- **Timestamped directories**: Each test run creates a unique directory
- **Format**: `YYYY-MM-DD_HH-MM-SS_testtype` for chronological sorting
- **Screenshots**: UI and E2E tests save screenshots in their run directory
- **Automatic failure screenshots**: Failed tests automatically capture screenshots
- **Last report tracking**: `last_report.txt` shows the most recent test directory

### Using Docker Compose

The Docker Compose setup includes automatic configuration validation:

```bash
# Start Home Assistant (validates configuration first)
docker-compose up -d

# If configuration is invalid, you'll see validation errors:
docker logs config-validator

# View Home Assistant logs
docker-compose logs -f home-assistant
```

**Configuration Validation Flow:**

1. `config-validator` service runs first to check `configuration.yaml`
1. If validation passes, Home Assistant starts
1. If validation fails, Home Assistant won't start and clear error messages are shown
1. Once Home Assistant is healthy, the onboarding service runs

This prevents Home Assistant from starting with invalid configurations, protecting against database corruption and startup failures.

### Using UV Python Environment

```bash
# Activate Python environment
source .venv/bin/activate

# Run unit tests
pytest tests/unit -v

# Run specific test
pytest -k "test_evening_lights" -v

# Update dependencies
just python::env-update

# Deactivate when done
deactivate
```

## CI/CD

This project uses GitHub Actions for continuous integration:

- **E2E Tests**: Automatically run on every pull request
- **Required Checks**: E2E tests must pass before merging
- **Test Reports**: Results are saved as artifacts in GitHub Actions

## Build System

This project uses **Just** as the primary build tool with modular organization:

### Just Module Structure

The build system is organized into modules for better maintainability:

```
justfile                    # Main entry point
├── just/
│   ├── common.just        # Shared variables and settings
│   ├── test.just          # Test module with submodules
│   │   ├── unit.just      # Unit test commands
│   │   ├── integration.just # Integration test commands
│   │   ├── e2e.just       # E2E test commands
│   │   └── ui.just        # UI test commands
│   ├── docker.just        # Docker management
│   ├── python.just        # Python environment management
│   ├── quality.just       # Code quality tools
│   └── dev.just           # Development utilities
```

### Module Navigation

- Use `::` to navigate modules: `just test::unit::logic`
- Each module has a default command that runs when called without a subcommand
- Get help for any module: `just test::help`, `just docker::help`

### Make and Just Interoperability

**Make and Just are now fully interchangeable!** The Makefile acts as a transparent proxy to Just:

```bash
# These commands are identical:
make test::unit         =  just test::unit
make docker::build      =  just docker::build
make quality::lint      =  just quality::lint
make test::ui::headed   =  just test::ui::headed
make python::setup      =  just python::setup
```

This means:

- Use whichever tool you prefer - they work identically
- No need to remember different syntaxes
- All new Just commands automatically work with Make
- Zero maintenance - the Makefile dynamically forwards everything

**Note**: The old single-colon syntax (`make test:unit`) is no longer supported. Use double-colons (`make test::unit`) for module commands.

## Project Structure

```
.
├── tests/
│   ├── requirements.txt        # Base test dependencies
│   ├── unit/
│   │   ├── logic/             # Pure logic tests (no HA needed)
│   │   └── mock/              # Mock-based HA tests
│   ├── integration/
│   │   └── requirements.txt   # Integration deps (includes base + HA)
│   ├── e2e/
│   │   └── requirements.txt   # E2E deps (includes base + browser tools)
│   ├── common.py              # HA-style test utilities
│   ├── conftest.py            # Pytest fixtures
│   ├── docker/                # Docker configuration for tests
│   ├── ui/                    # UI tests with Playwright
│   └── api/                   # API tests
├── scripts/                    # Utility scripts
├── reports/                    # Test reports and coverage (timestamped)
├── justfile                    # Primary build tool
├── Makefile                    # Legacy support
└── pyproject.toml               # Project config (includes pytest settings)
```

## Configuration

### Authentication Options

This framework supports two authentication modes:

#### 1. **Bypass Authentication (Recommended for Testing)**

The default and recommended approach - no tokens needed!

```bash
# Already configured during setup
just python::setup

# Or switch manually
just dev::auth-bypass
just docker::restart
```

With bypass auth:

- No token required for API calls
- Trusted networks: localhost and Docker networks
- Perfect for automated testing
- No manual setup needed

#### 2. **Token Authentication (Optional)**

For testing with real authentication:

```bash
# Switch to token mode
just dev::auth-token
just docker::restart

# Generate token
just dev::generate-token
# Follow the instructions to create a token

# Set in environment
export HA_TEST_TOKEN='your-token-here'
```

### Environment Variables

Set these environment variables if needed:

```bash
export HA_URL=http://localhost:8123
export HA_TEST_TOKEN=your_token_here  # Only needed if using token auth
export HA_USE_BYPASS_AUTH=true       # Set to false for token auth
```

## Writing Tests

### Unit Test Example

```python
@pytest.mark.asyncio
async def test_light_automation(hass):
    """Test light turns on at specific time."""
    # Setup
    hass.states.async_set("light.test", "off")

    # Configure automation
    await async_setup_component(
        hass,
        "automation",
        {
            "automation": {
                "trigger": {"platform": "time", "at": "18:00"},
                "action": {"service": "light.turn_on", "entity_id": "light.test"},
            }
        },
    )

    # Trigger and verify
    await hass.services.async_call("automation", "trigger", blocking=True)
    assert hass.states.get("light.test").state == "on"
```

### Integration Test Example

```python
@pytest.mark.integration
async def test_real_automation(ha_client):
    """Test automation in real HA instance."""
    # Set initial state
    await ha_client.set_state("light.test", "off")

    # Trigger automation
    await ha_client.call_service(
        "automation", "trigger", {"entity_id": "automation.test"}
    )

    # Wait and verify
    state = await ha_client.wait_for_state("light.test", "on")
    assert state is True
```

## Development

### Python Environment Management

This project uses **UV** for fast Python dependency management:

```bash
# All Python commands use the .venv created by UV
just test::unit      # Runs: .venv/bin/pytest tests/unit
just quality::lint   # Runs: .venv/bin/flake8
just quality::format # Runs: .venv/bin/black

# Work directly in the Python environment
source .venv/bin/activate
pytest tests/unit -v
deactivate  # Leave Python environment
```

Benefits of UV:

- Lightning-fast package installation (10-100x faster than pip)
- Built-in Python version management (no need for pyenv)
- Simple Python environment creation
- Compatible with standard requirements.txt files

### Code Quality

```bash
# Run linters
just quality::lint

# Format code
just quality::format

# Generate coverage report
just quality::coverage

# Open coverage report in browser
just quality::report

# Run pre-commit hooks
just quality::pre-commit
```

### Debugging

```bash
# View Home Assistant logs
just docker::logs

# Shell into test container
just docker::shell

# Shell into HA container
just docker::ha-shell

# Clean up containers and artifacts
just docker::clean
```

## CI/CD Integration

The framework generates JUnit XML reports suitable for CI systems:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    docker-compose up -d homeassistant
    docker-compose run test_runner

- name: Upload test results
  uses: actions/upload-artifact@v2
  with:
    name: test-results
    path: reports/
```

## Troubleshooting

### Common Issues

1. **Home Assistant not starting**:
   - Check configuration validation: `docker logs config-validator`
   - Check Home Assistant logs: `make logs` or `docker-compose logs home-assistant`
   - Common cause: Invalid configuration.yaml syntax or settings
1. **Tests timing out**: Increase timeout in `pyproject.toml` under `[tool.pytest.ini_options]`
1. **Permission errors**: Ensure Docker has necessary permissions
1. **Token issues**: Regenerate token and update environment variables

### Clean Environment

```bash
# Remove all containers and test artifacts
just docker::clean

# Clean specific components
just python::env-clean   # Remove Python environment
just quality::clean      # Remove coverage reports
```

## Contributing

1. Write tests for your automations
1. Ensure all tests pass: `make test`
1. Check code quality: `make lint`
1. Update documentation as needed

## License

This testing framework is provided as-is for testing Home Assistant configurations.
