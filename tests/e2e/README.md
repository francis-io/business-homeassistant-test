# End-to-End Tests

This directory contains end-to-end (E2E) tests that validate the complete Home Assistant stack using Docker Compose.

## Overview

E2E tests automatically:
1. Clean up any existing test containers for a fresh start
2. Validate the configuration
3. Start Home Assistant
4. Complete the onboarding process
5. Run tests against the fully configured instance
6. Generate timestamped test reports
7. Clean up all containers afterwards

## Running E2E Tests

### Using Make (recommended):
```bash
make test:e2e
```

### Running directly with docker-compose:
```bash
# Clean up any existing containers
docker-compose -f tests/e2e/docker/docker-compose.yml down

# Run E2E tests (will automatically start Home Assistant and wait for it to be healthy)
docker-compose -f tests/e2e/docker/docker-compose.yml run --rm home-assistant-test-runner-e2e

# Clean up
docker-compose -f tests/e2e/docker/docker-compose.yml down
```

## How It Works

The E2E tests run inside a Docker container to ensure consistency:

1. **Home Assistant starts**: The docker-compose setup validates config and starts HA
2. **Test container runs**: A Python container with pytest runs in the same network
3. **Tests execute**: Tests can access Home Assistant at `http://home-assistant:8123`
4. **Results saved**: JUnit XML results are saved to `reports/` with timestamps
5. **Cleanup**: All containers are stopped and removed

### Key Features:
- Tests run in isolated Docker container
- No local Python environment needed for E2E tests
- Consistent test environment across different machines
- Tests have network access to Home Assistant container
- Results are saved with timestamps in `reports/` directory
- Automatic container cleanup before and after tests
- Execution time tracking and reporting

## Writing E2E Tests

```python
def test_my_e2e_test(ha_url, ha_credentials):
    """Example E2E test."""
    # ha_url is automatically provided by the fixture
    response = requests.get(f"{ha_url}/api/")
    assert response.status_code in [200, 401]
```

## Available Fixtures

- `ha_url`: The URL of the running Home Assistant instance
- `ha_credentials`: Dict with username/password from onboarding
- `authenticated_session`: A requests session (auth not fully implemented yet)

## Requirements

- Docker and Docker Compose installed
- The project must be run from the root directory

## Configuration

The E2E tests use the docker-compose.yml in the docker subdirectory, which includes:
- Configuration validation before startup
- Automatic onboarding with default credentials (admin/admin) and readiness verification
- Health checks to ensure HA is ready
- A test-runner that executes the E2E test suite

## Test Reports

E2E test results are saved in the `reports/` directory at the project root:
- Report files are named: `e2e_YYYYMMDD_HHMMSS_results.xml`
- Each test run generates a new timestamped report
- The exact report filename is displayed after test completion
- Reports are in JUnit XML format for CI/CD integration

## Troubleshooting

If tests fail to start:
1. Check Docker logs: `docker-compose logs`
2. Ensure no other services are using port 8123
3. Verify docker-compose.yml syntax
4. Check that all required files exist in their directories:
   - `docker/config/configuration.yaml`
   - `docker/scripts/onboarding.py`
   - `docker/scripts/test_onboarding_complete.py`