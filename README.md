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

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Make (optional but recommended)
- UV package manager (for Python dependency management)

### Setup

1. Clone the repository and navigate to the project directory

2. Install dependencies based on your testing needs:
   ```bash
   # For unit tests only
   make setup
   
   # For unit + integration tests (includes Home Assistant)
   make setup-integration
   
   # For all test types (future E2E support)
   make setup-all
   ```
   
   This will:
   - Create Python 3.11 environment using UV
   - Install test dependencies from tests/requirements/
   - Set up bypass authentication for Docker

3. Build Docker containers:
   ```bash
   make build
   ```

4. Start Home Assistant:
   ```bash
   make start
   ```
   
   The system will automatically wait for Home Assistant to be healthy before proceeding. You can check the health status anytime with:
   ```bash
   make healthcheck
   ```

5. Run all tests:
   ```bash
   make test
   ```

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

## Running Tests

### Using Make (Recommended)

```bash
# Run all tests (unit, integration, e2e, ui)
make test

# Run specific test types
make test:unit          # Unit tests only (logic + mock)
make test:unit:logic    # Logic tests only
make test:unit:mock     # Mock tests only
make test:integration   # Integration tests (in-memory HA)
make test:e2e           # End-to-end tests (Docker)
make test:ui            # UI tests with Playwright (Docker)
make test:ui:headed     # UI tests with visible browser
make test:ui:debug      # UI tests in debug mode

# Watch mode for development
make test-watch
```

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
2. If validation passes, Home Assistant starts
3. If validation fails, Home Assistant won't start and clear error messages are shown
4. Once Home Assistant is healthy, the onboarding service runs

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
make env-update

# Deactivate when done
deactivate
```

## CI/CD

This project uses GitHub Actions for continuous integration:

- **E2E Tests**: Automatically run on every pull request
- **Required Checks**: E2E tests must pass before merging
- **Test Reports**: Results are saved as artifacts in GitHub Actions

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
│   ├── ui/                    # UI tests (future)
│   └── api/                   # API tests
├── scripts/                    # Utility scripts
├── reports/                    # Test reports and coverage
├── Makefile                    # Build automation
└── pyproject.toml               # Project config (includes pytest settings)
```

## Configuration

### Authentication Options

This framework supports two authentication modes:

#### 1. **Bypass Authentication (Recommended for Testing)**

The default and recommended approach - no tokens needed!

```bash
# Already configured during setup
make setup

# Or switch manually
make auth-bypass
make restart
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
make auth-token
make restart

# Generate token
make generate-token
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

Or create a `.env` file in the project root with the same variables.

## Writing Tests

### Unit Test Example

```python
@pytest.mark.asyncio
async def test_light_automation(hass):
    """Test light turns on at specific time."""
    # Setup
    hass.states.async_set("light.test", "off")
    
    # Configure automation
    await async_setup_component(hass, "automation", {
        "automation": {
            "trigger": {"platform": "time", "at": "18:00"},
            "action": {"service": "light.turn_on", "entity_id": "light.test"}
        }
    })
    
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
    await ha_client.call_service("automation", "trigger", 
                                {"entity_id": "automation.test"})
    
    # Wait and verify
    state = await ha_client.wait_for_state("light.test", "on")
    assert state is True
```

## Development

### Python Environment Management

This project uses **UV** for fast Python dependency management:

```bash
# All Python commands use the .venv created by UV
make test:unit      # Runs: .venv/bin/pytest tests/unit
make lint           # Runs: .venv/bin/flake8
make format         # Runs: .venv/bin/black

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
make lint

# Format code
make format

# Generate coverage report
make coverage

# Open coverage report in browser
make report
```

### Debugging

```bash
# View Home Assistant logs
make logs

# Shell into test container
make shell

# Shell into HA container
make ha-shell
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
2. **Tests timing out**: Increase timeout in `pyproject.toml` under `[tool.pytest.ini_options]`
3. **Permission errors**: Ensure Docker has necessary permissions
4. **Token issues**: Regenerate token and update `.env`

### Clean Environment

```bash
# Remove all containers and test artifacts
make clean
```

## Contributing

1. Write tests for your automations
2. Ensure all tests pass: `make test`
3. Check code quality: `make lint`
4. Update documentation as needed

## License

This testing framework is provided as-is for testing Home Assistant configurations.