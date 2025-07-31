# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated testing.

## Workflows

### 1. All Tests (`all-tests.yml`)

- **Trigger**: On every PR and push to main/master branches
- **Purpose**: Runs the complete test suite
- **What it runs**: `make test` which includes:
  - Unit tests (logic + mock)
  - Integration tests
  - E2E tests (Docker)
  - UI tests (Playwright in Docker)
- **Timeout**: 20 minutes
- **Artifacts**: Test results and logs

### 2. E2E Tests Only (`e2e-tests.yml`)

- **Trigger**: Manual only (workflow_dispatch)
- **Purpose**: Run just the E2E tests for debugging
- **What it runs**: `make test:e2e`
- **Timeout**: 10 minutes
- **Artifacts**: E2E test results and logs

## Key Features

### Test Environment Setup

- Python 3.11 with UV package manager
- Docker Compose v2.39.1 for containerized tests
- Automatic dependency installation

### PR Comments

- Workflows automatically comment on PRs with test results
- Includes links to test reports and full workflow runs
- Works even if some tests fail

### Artifacts

- Test results are saved for 30 days
- Test logs are saved for 7 days (on failure)
- Reports include JUnit XML format for integration

## Running Workflows Manually

You can manually trigger workflows from the Actions tab:

1. Go to the Actions tab in GitHub
1. Select the workflow you want to run
1. Click "Run workflow"
1. Select the branch and click "Run workflow"

## Adding New Workflows

When adding new workflows:

1. Use the existing workflows as templates
1. Include proper permissions for PR comments
1. Add artifact upload for test results
1. Set appropriate timeouts
1. Use UV for fast Python dependency management
