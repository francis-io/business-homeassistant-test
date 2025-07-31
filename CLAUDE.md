# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude Code MCP Servers

This project recommends using these MCP (Model Context Protocol) servers for enhanced assistance:

- **context7**: Use for accessing up-to-date documentation and best practices for libraries and frameworks used in this project
- **sequential-thinking**: Use for breaking down complex testing scenarios and thinking through automation logic step-by-step

## Development Commands

### Setup and Environment

```bash
# Create Python environment and install dependencies
make setup                   # Base test dependencies
make setup-integration      # + integration test dependencies
make setup-all              # All dependencies including E2E

# Python environment management
source .venv/bin/activate    # Activate environment (uses UV package manager)
make env-update             # Update dependencies
make env-clean              # Remove Python environment
```

### Testing Commands

```bash
# Primary test commands (all use parallel execution)
make test                   # Run all available tests
make test:unit              # Unit tests (logic + mock)
make test:unit:logic        # Pure Python logic tests only
make test:unit:mock         # Mock-based behavior tests only
make test:integration        # Integration tests (no Docker needed)

# Direct pytest usage
.venv/bin/pytest tests/unit -n 2 -q
.venv/bin/pytest tests/unit/logic -k "test_evening_lights" -v
```

### Docker and Home Assistant

```bash
make build                  # Build Docker containers
make start                  # Start Home Assistant at http://localhost:8123
make stop                   # Stop containers
make restart                # Restart containers

# Docker debugging
make logs                   # Show HA logs
make shell                  # Shell into test container
make ha-shell              # Shell into HA container
```

### Code Quality

```bash
make lint                   # Run flake8, mypy, black --check
make format                 # Format with black and isort
make coverage               # Generate coverage report
make clean                  # Clean containers and artifacts

# Pre-commit hooks (enforced on all commits)
make pre-commit-install     # Setup pre-commit (first time only)
make pre-commit-run         # Run all checks manually
make pre-commit-update      # Update hooks to latest versions
```

### Pre-commit Requirements

This project uses pre-commit hooks to enforce code quality. Key checks include:

- **Security**: detect-secrets, gitleaks, bandit
- **Type Safety**: mypy --strict for HA compatibility
- **Code Quality**: black, isort, flake8 with pytest/async plugins
- **Test Integrity**: pytest collection validation
- **Custom Validators**: Test structure, automation logic, HA mock consistency

**Important for AI-generated code**:

- Business logic must go in `tests/helpers/automation_logic.py`, not test files
- Logic tests cannot import Home Assistant components
- Mock tests must use `ha_mocks` helpers
- All code must pass strict type checking for HA compatibility

## Architecture Overview

### Multi-Level Testing Strategy

This framework implements a unique **logic-first** testing approach with three distinct levels:

1. **Logic Tests** (`tests/unit/logic/`) - Test pure Python business logic functions without Home Assistant
1. **Mock Tests** (`tests/unit/mock/`) - Test automation behavior using mocked HA components
1. **Integration Tests** (`tests/integration/`) - Test real Home Assistant automations in containers

### Core Components

**Pure Logic Functions** (`tests/helpers/automation_logic.py`):

- `should_turn_on_evening_lights()` - Time/sunset-based light logic
- `calculate_brightness_for_time()` - Brightness calculations by hour
- `should_send_water_leak_notification()` - Leak detection logic
- `should_trigger_zone_entry_actions()` - Zone entry automation logic

**Test Helpers**:

- `tests/helpers/ha_mocks.py` - Mock Home Assistant components and services
- `tests/helpers/fast_ha_test.py` - Minimal HA instance for integration tests
- `tests/helpers/auth.py` - Authentication utilities for API testing

**Automation Scenarios** (all have logic, mock, and integration test variants):

- **Time-Based Lights**: Sunset/sunrise lighting with brightness control
- **Notification System**: Water leak alerts, mobile notifications
- **Zone Entry**: Location-based automations (lights, climate, notifications)

### Project Structure Philosophy

- Tests are organized by **testing approach** (unit/logic, unit/mock, integration) rather than by feature
- Pure business logic is extracted into testable functions in `automation_logic.py`
- Each automation scenario has corresponding test files across all test levels
- Configuration files are in `tests/e2e/docker/config/` for containerized HA testing

### Key Technical Details

**Python Environment**: Uses UV package manager for fast dependency management with Python 3.11

**Parallel Testing**: Optimized for 2-4 workers (`-n 2`) rather than auto-detection for ~90 test suite

**Authentication**: Defaults to bypass authentication for testing (no tokens needed), with token auth available via `make auth-token`

**Coverage**: HTML reports generated in `reports/unit_coverage/`

**Docker Configuration**: Uses `tests/e2e/docker/docker-compose.yml` with Home Assistant 2024.1.0

## Testing Best Practices

### Writing New Tests

1. **Extract Logic First**: Create pure Python functions in `automation_logic.py`
1. **Test Logic**: Write fast unit tests for the extracted functions
1. **Test Behavior**: Add mock tests to verify HA service calls and state changes
1. **Test Integration**: Add integration tests for end-to-end validation

### Running Specific Tests

```bash
# Test specific automation logic
pytest tests/unit/logic/test_time_based_light_logic.py -v

# Test specific scenario across all levels
pytest -k "evening_lights" -v

# Debug single test
pytest tests/unit/logic/test_time_based_light_logic.py::test_brightness_calculation -vs
```

### Development Workflow

1. Use `make setup` for initial environment
1. Develop and test logic functions first (`make test:unit:logic`)
1. Add mock tests for HA integration behavior (`make test:unit:mock`)
1. Use `make start` and integration tests for end-to-end validation
1. Run `make lint` and `make format` before commits
