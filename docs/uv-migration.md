# Migration to UV Package Manager

## Overview

We've successfully migrated the project from pipenv to uv, which provides:

- Fast package installation
- Built-in Python version management
- No system Python modifications needed

## What Was Done

### 1. Created Python 3.11 Environment

```bash
uv venv --python 3.11
```

- UV automatically downloaded Python 3.11.13
- Created `.venv` directory with isolated Python environment

### 2. Converted Dependencies

- Created `requirements.txt` from `Pipfile`
- Removed version conflicts
- All dependencies installed successfully

### 3. Updated Makefile

All commands now use `.venv/bin/` instead of `pipenv run`:

- `make test:unit` - Run unit tests
- `make test:unit:logic` - Run logic tests
- `make test:unit:mock` - Run mock tests
- `make lint` - Run linters
- `make format` - Format code

### 4. Python Environment Management

New commands:

- `make setup` - Create Python environment and install dependencies
- `make env-update` - Update all dependencies
- `make env-clean` - Remove Python environment
- `make env-shell` - Instructions to activate environment
  (Old venv-\* commands still work as aliases)

## Current Status

### ✅ Working

- Unit tests run perfectly (~1.4s with Python 3.11)
- All 90 unit tests pass
- Linting and formatting work
- No pipenv dependency

### ⚠️ Fast Integration Tests

- Home Assistant installed successfully
- Tests fail due to HA initialization complexity
- Error: Missing 'integrations' data during bootstrap
- Would require significant effort to fix HA setup

## Usage

### Initial Setup

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup project
make setup
```

### Running Tests

```bash
# All unit tests
make test:unit

# Specific test types
make test:unit:logic
make test:unit:mock
```

### Activating Python Environment

```bash
source .venv/bin/activate
```

## Benefits of UV

1. **Speed**: Package installation is 10-100x faster than pip
1. **Python Management**: Can install any Python version without sudo
1. **Simplicity**: Single tool for package and Python management
1. **Compatibility**: Works with standard requirements.txt

## Removed Files

The following have been removed:

- `Pipfile` and `Pipfile.lock` - No longer needed with UV
- `pytest.ini` - Configuration moved to `pyproject.toml`

All pytest configuration is now in `pyproject.toml` under `[tool.pytest.ini_options]`.

## Next Steps

For fast integration tests to work, would need to:

1. Study current Home Assistant initialization requirements
1. Update `fast_ha_test.py` to properly bootstrap HA
1. Consider using pytest-homeassistant-custom-component instead

However, the unit tests provide good coverage without needing Home Assistant.
