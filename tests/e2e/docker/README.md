# E2E Docker Compose Setup

This directory contains the Docker Compose configuration for running end-to-end tests against Home Assistant.

## Overview

The docker-compose.yml orchestrates a complete Home Assistant testing environment with automatic setup and validation. The services start in a specific order to ensure everything is properly configured before tests run.

## Service Architecture

### 1. Configuration Validator (`home-assistant-config-validator`)
- **Purpose**: Validates configuration.yaml before Home Assistant starts
- **Runs**: Once at startup, exits after validation
- **Prevents**: Home Assistant from starting with invalid configuration

### 2. Home Assistant (`home-assistant`)
- **Purpose**: The main Home Assistant instance
- **Depends on**: Configuration validator must complete successfully
- **Port**: 8123 (exposed to host)
- **Health check**: Polls http://localhost:8123 every second
- **State**: Considered healthy when HTTP endpoint responds

### 3. Onboarding and Readiness (`home-assistant-test-onboarding-and-ready`)
- **Purpose**: Automatically completes onboarding and validates system readiness
- **Depends on**: Home Assistant must be healthy
- **Creates**: Default admin user (admin/admin)
- **Scripts**: 
  - `onboarding.py` handles the onboarding flow
  - `test_onboarding_complete.py` validates system is ready
  - `onboarding_and_test.py` orchestrates both scripts

### 4. E2E Test Runner (`home-assistant-test-runner-e2e`)
- **Purpose**: Runs pytest E2E tests in isolated container
- **Depends on**: Onboarding and readiness must complete successfully
- **Environment**: 
  - `HA_URL=http://home-assistant:8123` - Internal Docker network URL
  - Tests access Home Assistant via Docker networking
- **Output**: JUnit XML results saved to test-results/

## Service Startup Flow

```
1. Configuration Validator
   ↓ (validates config)
2. Home Assistant 
   ↓ (waits for healthy)
3. Onboarding and Readiness
   ↓ (creates admin user + verifies system)
4. E2E Test Runner
   (executes tests)
```

## Key Features

### Dependency Management
- Uses `depends_on` with conditions:
  - `service_completed_successfully` - Previous service must exit with code 0
  - `service_healthy` - Service must pass health checks
- Ensures proper startup order without manual orchestration

### Network Isolation
- All services run on the same Docker network
- Services communicate using container names (e.g., `http://home-assistant:8123`)
- No need for localhost or external IPs

### Volume Mounts
- `./config:/config:ro` - Configuration directory with configuration.yaml
- `./scripts:/scripts:ro` - Scripts directory containing:
  - `onboarding.py` - Automatic setup script
  - `test_onboarding_complete.py` - Validation tests
  - `onboarding_and_test.py` - Combined orchestration script
- `../../..:/workspace:ro` - Project root for test access
- `../../../test-results` - Test output directory

### Test Execution
The E2E test runner:
1. Installs pytest (already in the HA image)
2. Changes to /workspace directory
3. Runs: `python -m pytest tests/e2e -v --tb=short --junit-xml=/test-results/e2e-results.xml`
4. Saves results for CI/CD integration

## Usage

### Run E2E Tests
```bash
# From project root
make test:e2e

# Or directly with docker-compose
docker-compose -f tests/e2e/docker/docker-compose.yml run --rm home-assistant-test-runner-e2e
```

### Debugging

View logs for any service:
```bash
docker-compose -f tests/e2e/docker/docker-compose.yml logs [service-name]
```

Check service status:
```bash
docker-compose -f tests/e2e/docker/docker-compose.yml ps
```

## Directory Structure

```
docker/
├── docker-compose.yml      # Main orchestration file
├── .env                    # Environment variables
├── config/                 # Configuration directory
│   └── configuration.yaml  # Home Assistant configuration
└── scripts/                # Onboarding and test scripts
    ├── onboarding.py                # Automated onboarding script
    ├── test_onboarding_complete.py  # System validation tests
    └── onboarding_and_test.py       # Combined orchestration script
```

## Notes

- All services use the same Home Assistant image for consistency
- The test runner doesn't need a custom Dockerfile since pytest is included
- Configuration validation prevents common startup failures
- Automatic onboarding eliminates manual setup steps