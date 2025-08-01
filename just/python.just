# Python environment module - UV package management and setup

# Import common variables
import 'common.just'

# Display available python commands with descriptions
help:
    @echo "Python Module Commands:"
    @echo "═══════════════════════════════════════════════════════"
    @cd {{justfile_directory()}} && just --list --justfile just/python.just --list-heading "" --list-prefix "  just python::"

# Check if UV is installed
_check-uv:
    @which {{uv}} &> /dev/null || (echo "Please install uv: https://github.com/astral-sh/uv" && exit 1)

# Create Python env and install base test dependencies
setup: _check-uv
    @echo "Creating Python {{python_version}} environment with UV..."
    {{uv}} venv --python {{python_version}}
    @echo "Installing base test dependencies..."
    {{uv}} pip install -r {{project_root}}/tests/requirements.txt
    @echo "Creating necessary directories..."
    mkdir -p {{reports_dir}} {{project_root}}/tests/e2e/docker/config/.storage
    @echo "Setting up bypass authentication..."
    {{project_root}}/scripts/switch_auth_mode.sh bypass
    @echo "✅ Setup complete!"

# Setup with integration test dependencies added
setup-integration: setup
    @echo "Installing integration test dependencies..."
    {{uv}} pip install -r {{project_root}}/tests/integration/requirements.txt
    @echo "✅ Integration setup complete!"

# Setup with UI test deps and Playwright browsers
setup-ui: setup
    @echo "Installing UI test dependencies..."
    {{uv}} pip install -r {{project_root}}/tests/ui/requirements.txt
    @echo "Installing Playwright browsers..."
    {{playwright}} install chromium firefox webkit
    @echo "✅ UI setup complete!"

# Setup with end-to-end test dependencies
setup-e2e: setup
    @echo "Installing E2E test dependencies..."
    {{uv}} pip install -r {{project_root}}/tests/e2e/requirements.txt
    @echo "✅ E2E setup complete!"

# Setup with all test dependencies (integration, UI, E2E)
setup-all: setup
    @echo "Installing all test dependencies..."
    {{uv}} pip install -r {{project_root}}/tests/integration/requirements.txt
    {{uv}} pip install -r {{project_root}}/tests/ui/requirements.txt
    {{uv}} pip install -r {{project_root}}/tests/e2e/requirements.txt
    @echo "Installing Playwright browsers..."
    {{playwright}} install chromium firefox webkit
    @echo "✅ All dependencies installed!"

# Show how to activate the Python environment
env-shell:
    @echo "To activate the Python environment, run:"
    @echo "source {{venv_path}}/bin/activate"

# Update all dependencies to latest compatible versions
env-update:
    @echo "Updating all dependencies with UV..."
    {{uv}} pip install -r {{project_root}}/tests/requirements.txt --upgrade
    @echo "✅ Dependencies updated!"

# Remove Python virtual environment completely
env-clean:
    @echo "Removing Python environment..."
    rm -rf {{venv_path}}
    @echo "✅ Environment removed!"

# Show path to Python virtual environment
env-where:
    @echo "Python environment location:"
    @echo "{{venv_path}}"

# Check for outdated Python packages
check-deps:
    @echo "Checking for outdated dependencies..."
    @{{pip}} list --outdated

# Update dependencies interactively with diff preview
update-deps:
    @echo "Updating all dependencies to latest versions..."
    @{{uv}} pip compile --upgrade {{project_root}}/pyproject.toml -o {{project_root}}/requirements-new.txt
    @echo ""
    @echo "Dependency changes:"
    @diff -u {{project_root}}/tests/requirements.txt {{project_root}}/requirements-new.txt || true
    @echo ""
    @read -p "Apply these updates? [y/N] " -n 1 -r; \
    echo ""; \
    if [[ $REPLY =~ ^[Yy]$ ]]; then \
        mv {{project_root}}/requirements-new.txt {{project_root}}/tests/requirements.txt; \
        {{uv}} pip sync {{project_root}}/tests/requirements.txt; \
        echo "Dependencies updated! Run 'make test' to verify."; \
    else \
        rm {{project_root}}/requirements-new.txt; \
        echo "Update cancelled."; \
    fi

# Update all dependencies automatically (no prompts)
update-deps-auto:
    @echo "Updating all dependencies (non-interactive)..."
    @{{uv}} pip compile --upgrade {{project_root}}/pyproject.toml -o {{project_root}}/tests/requirements.txt
    @{{uv}} pip sync {{project_root}}/tests/requirements.txt
    @echo "Dependencies updated!"

# Update dependencies and run all tests
update-and-test: update-deps-auto
    @just test::all
    @echo "Update and test completed!"

# Run security vulnerability scan on dependencies
audit-deps:
    @echo "Running security audit on dependencies..."
    @{{pip}} install pip-audit --quiet
    @{{venv_path}}/bin/pip-audit || (echo "Found vulnerabilities! Run 'make env::update-deps' to update." && exit 1)
