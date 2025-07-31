# Requirements Restructure Documentation

## Overview

We've restructured the project's dependency management to follow Home Assistant's pattern while adapting it for a test-only project. All test dependencies are now organized under `tests/requirements/`.

## Changes Made

### 1. Consolidated Requirements Files

**Before:**

- `/requirements.txt` - Mixed base and test dependencies
- `/requirements-test.txt` - Duplicate test dependencies with versions
- `/tests/integration/requirements-integration.txt` - Integration deps

**After:**

- `/tests/requirements.txt` - Core test dependencies (base for all tests)
- `/tests/integration/requirements.txt` - Integration test deps (includes base + HA)
- `/tests/e2e/requirements.txt` - E2E test deps placeholder (includes base + browser tools)

### 2. Removed pytest-homeassistant-custom-component

Instead of relying on the external `pytest-homeassistant-custom-component` package, we've created our own lightweight test utilities:

- `/tests/common.py` - Home Assistant-style test utilities
- Updated `/tests/conftest.py` - Added `hass` and `mock_service` fixtures

### 3. Updated Makefile

New setup commands:

- `make setup` - Install base test dependencies only
- `make setup-integration` - Base + Home Assistant for integration tests
- `make setup-e2e` - Base + browser automation (future)
- `make setup-all` - Install all test dependencies

### 4. Maintained Test Structure

The three-level test structure remains unchanged:

- **Unit tests** - No Home Assistant needed, millisecond execution
- **Integration tests** - Uses Home Assistant, second-level execution
- **E2E tests** - Browser automation, minute-level execution (future)

## Benefits

1. **Cleaner Organization**: All test dependencies in one logical location
1. **Progressive Installation**: Install only what you need for your test level
1. **No External Dependencies**: Our own test utilities instead of third-party packages
1. **Follows HA Patterns**: Uses similar structure to Home Assistant core
1. **Faster Installation**: UV package manager is 10-100x faster than pip

## Migration Notes

For existing users:

1. Delete old Python environment: `rm -rf .venv`
1. Run appropriate setup: `make setup-integration` (for most users)
1. All commands work the same, just faster!

## Home Assistant Testing Approach

Home Assistant separates dependencies because they have:

- Runtime code that needs production dependencies
- Test code that needs test dependencies
- Component-specific dependencies for integrations

Since this project is test-only, we simplified:

- All dependencies are test dependencies
- Organized by test level (base/integration/e2e)
- No production code means no runtime dependencies
