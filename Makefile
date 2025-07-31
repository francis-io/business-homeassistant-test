.PHONY: help setup build start stop test test\:unit test\:unit\:logic test\:unit\:mock test\:integration\:fast test\:integration\:full clean logs shell lint format

# Default target
help:
	@echo "Home Assistant Testing Framework"
	@echo "==============================="
	@echo ""
	@echo "Setup & Management:"
	@echo "  make setup          - Create Python environment with UV and install base test dependencies"
	@echo "  make setup-integration - Setup + install integration test dependencies"
	@echo "  make setup-ui       - Setup + install UI test dependencies"
	@echo "  make setup-e2e      - Setup + install E2E test dependencies"
	@echo "  make setup-all      - Setup + install all test dependencies"
	@echo "  make build          - Build Docker containers"
	@echo "  make start          - Start Home Assistant container"
	@echo "  make start-clean    - Start with fresh Home Assistant (removes data)"
	@echo "  make stop           - Stop and remove all containers"
	@echo "  make restart        - Restart all containers"
	@echo "  make healthcheck    - Check if Home Assistant is healthy"
	@echo "  make clean          - Clean up containers and test artifacts"
	@echo "  make clean-config   - Clean only container-generated config files"
	@echo ""
	@echo "Testing:"
	@echo "  make test                - Run all tests (unit, integration, e2e, ui)"
	@echo "  make test:unit           - Run all unit tests (logic + mock) in parallel"
	@echo "  make test:unit:logic     - Run logic unit tests only"
	@echo "  make test:unit:mock      - Run mock unit tests only"
	@echo "  make test:integration    - Run integration tests"
	@echo "  make test:ui             - Run UI tests in parallel"
	@echo "  make test:ui:headed      - Run UI tests with visible browser"
	@echo "  make test:ui:debug       - Run UI tests in debug mode"
	@echo "  make test:e2e            - Run E2E tests"
	@echo ""
	@echo "Development:"
	@echo "  make logs           - Show Home Assistant logs"
	@echo "  make shell          - Shell into test runner container"
	@echo "  make ha-shell       - Shell into Home Assistant container"
	@echo "  make env-shell      - Show how to activate Python environment"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo "  make validate-config - Validate Home Assistant YAML configuration"
	@echo ""
	@echo "Python Environment Management (UV):"
	@echo "  make env-update     - Update all dependencies"
	@echo "  make env-clean      - Remove Python environment"
	@echo "  make env-where      - Show environment location"
	@echo ""
	@echo "Reports:"
	@echo "  make coverage       - Generate coverage report"
	@echo "  make report         - Open HTML coverage report"

# Setup
setup:
	@which uv || (echo "Please install uv: https://github.com/astral-sh/uv" && exit 1)
	@echo "Creating Python 3.11 environment with UV..."
	uv venv --python 3.11
	@echo "Installing base test dependencies..."
	uv pip install -r tests/requirements.txt
	@echo "Creating necessary directories..."
	# TODO: why this?
	mkdir -p reports tests/e2e/docker/config/.storage
	@echo "Setting up bypass authentication..."
	# TODO: why this?
	./scripts/switch_auth_mode.sh bypass

setup-integration: setup
	@echo "Installing integration test dependencies..."
	uv pip install -r tests/integration/requirements.txt

setup-ui: setup
	@echo "Installing UI test dependencies..."
	uv pip install -r tests/ui/requirements.txt
	@echo "Installing Playwright browsers..."
	.venv/bin/playwright install chromium firefox webkit

setup-e2e: setup
	@echo "Installing E2E test dependencies..."
	uv pip install -r tests/e2e/requirements.txt

setup-all: setup
	@echo "Installing all test dependencies..."
	uv pip install -r tests/integration/requirements.txt
	uv pip install -r tests/ui/requirements.txt
	uv pip install -r tests/e2e/requirements.txt
	@echo "Installing Playwright browsers..."
	.venv/bin/playwright install chromium firefox webkit

# Docker commands
build:
	@echo "Building Docker containers..."
	docker-compose -f tests/e2e/docker/docker-compose.yml build

start:
	@echo "Starting Home Assistant..."
	docker-compose -f tests/e2e/docker/docker-compose.yml up -d homeassistant
	@echo "Waiting for Home Assistant to be healthy..."
	@timeout=60; \
	while [ $$timeout -gt 0 ]; do \
		if docker-compose -f tests/e2e/docker/docker-compose.yml ps homeassistant | grep -q "healthy"; then \
			echo "✅ Home Assistant is healthy and running at http://localhost:8123"; \
			exit 0; \
		fi; \
		echo "⏳ Waiting for Home Assistant to become healthy... ($$timeout seconds remaining)"; \
		sleep 5; \
		timeout=$$((timeout - 5)); \
	done; \
	echo "❌ Error: Home Assistant failed to become healthy within 60 seconds"; \
	docker-compose -f tests/e2e/docker/docker-compose.yml logs --tail=50 homeassistant; \
	exit 1

stop:
	@echo "Stopping and removing all containers..."
	docker-compose -f tests/e2e/docker/docker-compose.yml down --remove-orphans

restart: stop start

# Start with clean volumes (removes all HA data)
start-clean: stop
	@echo "Removing Home Assistant volumes..."
	docker-compose -f tests/e2e/docker/docker-compose.yml down -v
	@$(MAKE) start

# Check if Home Assistant is healthy
healthcheck:
	@if docker-compose -f tests/e2e/docker/docker-compose.yml ps homeassistant 2>/dev/null | grep -q "healthy"; then \
		echo "✅ Home Assistant is healthy"; \
	else \
		echo "❌ Home Assistant is not healthy"; \
		docker-compose -f tests/e2e/docker/docker-compose.yml ps homeassistant; \
		exit 1; \
	fi

# Testing commands
test:
	@echo "Running all tests (unit, integration, e2e, ui)..."
	@echo "Note: UI tests run separately due to Docker requirements"
	.venv/bin/pytest tests/unit tests/integration -n auto -q --ignore=tests/e2e/docker
	@echo ""
	@echo "Running e2e tests in Docker..."
	@$(MAKE) test:e2e
	@echo "Running UI tests in Docker..."
	@$(MAKE) test:ui

test\:unit:
	@echo "Running all unit tests in parallel..."
	.venv/bin/pytest tests/unit -n 2 -q

test\:unit\:logic:
	@echo "Running logic unit tests in parallel..."
	.venv/bin/pytest tests/unit/logic -n 2 -q

test\:unit\:mock:
	@echo "Running mock unit tests in parallel..."
	.venv/bin/pytest tests/unit/mock -n 2 -q

test\:integration:
	@echo "Running integration tests..."
	.venv/bin/pytest tests/integration -n 2 -q

# UI tests (Docker-based)
test\:ui:
	@echo "Running UI tests in Docker..."
	@START_TIME=$$(date +%s); \
	echo "Cleaning up any existing test containers..."; \
	docker ps -a --filter "name=home-assistant-test-" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true; \
	docker-compose -f tests/ui/docker/docker-compose.yml down --volumes --remove-orphans; \
	echo "Starting fresh UI test run..."; \
	docker-compose -f tests/ui/docker/docker-compose.yml run --rm home-assistant-test-runner-ui || EXIT_CODE=$$?; \
	echo "Cleaning up test containers..."; \
	docker ps -a --filter "name=home-assistant-test-" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true; \
	docker-compose -f tests/ui/docker/docker-compose.yml down --volumes --remove-orphans; \
	END_TIME=$$(date +%s); \
	DURATION=$$((END_TIME - START_TIME)); \
	echo ""; \
	echo "=========================================="; \
	echo "UI tests completed in $$DURATION seconds"; \
	if [ -f reports/.last_report ]; then \
		REPORT_FILE=$$(cat reports/.last_report | grep "REPORT_FILE=" | cut -d'=' -f2); \
		echo "Test report saved: reports/$$REPORT_FILE"; \
	else \
		echo "Test reports saved in: reports/"; \
	fi; \
	echo "=========================================="; \
	exit $$EXIT_CODE

test\:ui\:headed:
	@echo "Running UI tests with visible browser in Docker..."
	@START_TIME=$$(date +%s); \
	echo "Cleaning up any existing test containers..."; \
	docker ps -a --filter "name=home-assistant-test-" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true; \
	docker-compose -f tests/ui/docker/docker-compose.yml down --volumes --remove-orphans; \
	echo "Starting fresh UI test run with headed mode..."; \
	HEADED=true docker-compose -f tests/ui/docker/docker-compose.yml run --rm home-assistant-test-runner-ui || EXIT_CODE=$$?; \
	echo "Cleaning up test containers..."; \
	docker ps -a --filter "name=home-assistant-test-" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true; \
	docker-compose -f tests/ui/docker/docker-compose.yml down --volumes --remove-orphans; \
	END_TIME=$$(date +%s); \
	DURATION=$$((END_TIME - START_TIME)); \
	echo ""; \
	echo "=========================================="; \
	echo "UI tests (headed) completed in $$DURATION seconds"; \
	if [ -f reports/.last_report ]; then \
		REPORT_FILE=$$(cat reports/.last_report | grep "REPORT_FILE=" | cut -d'=' -f2); \
		echo "Test report saved: reports/$$REPORT_FILE"; \
	else \
		echo "Test reports saved in: reports/"; \
	fi; \
	echo "=========================================="; \
	exit $$EXIT_CODE

test\:ui\:debug:
	@echo "Running UI tests in debug mode with visible browser in Docker..."
	@START_TIME=$$(date +%s); \
	echo "Cleaning up any existing test containers..."; \
	docker ps -a --filter "name=home-assistant-test-" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true; \
	docker-compose -f tests/ui/docker/docker-compose.yml down --volumes --remove-orphans; \
	echo "Starting fresh UI test run in debug mode..."; \
	HEADED=true DEBUG=true SLOWMO=1000 docker-compose -f tests/ui/docker/docker-compose.yml run --rm home-assistant-test-runner-ui || EXIT_CODE=$$?; \
	echo "Cleaning up test containers..."; \
	docker ps -a --filter "name=home-assistant-test-" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true; \
	docker-compose -f tests/ui/docker/docker-compose.yml down --volumes --remove-orphans; \
	END_TIME=$$(date +%s); \
	DURATION=$$((END_TIME - START_TIME)); \
	echo ""; \
	echo "=========================================="; \
	echo "UI tests (debug) completed in $$DURATION seconds"; \
	if [ -f reports/.last_report ]; then \
		REPORT_FILE=$$(cat reports/.last_report | grep "REPORT_FILE=" | cut -d'=' -f2); \
		echo "Test report saved: reports/$$REPORT_FILE"; \
	else \
		echo "Test reports saved in: reports/"; \
	fi; \
	echo "=========================================="; \
	exit $$EXIT_CODE

# E2E tests
test\:e2e:
	@echo "Running E2E tests..."
	@START_TIME=$$(date +%s); \
	echo "Cleaning up any existing test containers..."; \
	docker ps -a --filter "name=home-assistant-test-" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true; \
	docker-compose -f tests/e2e/docker/docker-compose.yml down --volumes --remove-orphans; \
	echo "Starting fresh E2E test run..."; \
	docker-compose -f tests/e2e/docker/docker-compose.yml run --rm home-assistant-test-runner-e2e || EXIT_CODE=$$?; \
	echo "Cleaning up test containers..."; \
	docker ps -a --filter "name=home-assistant-test-" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true; \
	docker-compose -f tests/e2e/docker/docker-compose.yml down --volumes --remove-orphans; \
	END_TIME=$$(date +%s); \
	DURATION=$$((END_TIME - START_TIME)); \
	echo ""; \
	echo "=========================================="; \
	echo "E2E tests completed in $$DURATION seconds"; \
	if [ -f reports/.last_report ]; then \
		REPORT_FILE=$$(cat reports/.last_report | grep "REPORT_FILE=" | cut -d'=' -f2); \
		echo "Test report saved: reports/$$REPORT_FILE"; \
	else \
		echo "Test reports saved in: reports/"; \
	fi; \
	echo "=========================================="; \
	exit $$EXIT_CODE

# Development tools
logs:
	@echo "Showing Home Assistant logs..."
	docker-compose -f tests/e2e/docker/docker-compose.yml logs -f homeassistant

shell:
	@echo "Opening shell in test runner container..."
	docker-compose -f tests/e2e/docker/docker-compose.yml run --rm test_runner /bin/bash

ha-shell:
	@echo "Opening shell in Home Assistant container..."
	docker-compose -f tests/e2e/docker/docker-compose.yml exec homeassistant /bin/bash

# Python environment commands (UV managed)
env-shell:
	@echo "To activate the Python environment, run:"
	@echo "source .venv/bin/activate"

env-update:
	@echo "Updating all dependencies with UV..."
	uv pip install -r tests/requirements.txt --upgrade

env-clean:
	@echo "Removing Python environment..."
	rm -rf .venv

env-where:
	@echo "Python environment location:"
	@echo "$${PWD}/.venv"

# Backward compatibility aliases
venv-shell: env-shell
venv-update: env-update
venv-clean: env-clean
venv-where: env-where

# Dependency management
check-deps:
	@echo "Checking for outdated dependencies..."
	@.venv/bin/pip list --outdated

update-deps:
	@echo "Updating all dependencies to latest versions..."
	@uv pip compile --upgrade pyproject.toml -o requirements-new.txt
	@echo ""
	@echo "Dependency changes:"
	@diff -u tests/requirements.txt requirements-new.txt || true
	@echo ""
	@read -p "Apply these updates? [y/N] " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		mv requirements-new.txt tests/requirements.txt; \
		uv pip sync tests/requirements.txt; \
		echo "Dependencies updated! Run 'make test' to verify."; \
	else \
		rm requirements-new.txt; \
		echo "Update cancelled."; \
	fi

update-deps-auto:
	@echo "Updating all dependencies (non-interactive)..."
	@uv pip compile --upgrade pyproject.toml -o tests/requirements.txt
	@uv pip sync tests/requirements.txt
	@echo "Dependencies updated!"

update-and-test: update-deps-auto test
	@echo "Update and test completed!"

audit-deps:
	@echo "Running security audit on dependencies..."
	@.venv/bin/pip-audit || (echo "Found vulnerabilities! Run 'make update-deps' to update." && exit 1)

# Code quality
lint:
	@echo "Running linters..."
	.venv/bin/flake8 tests/
	.venv/bin/mypy tests/ --ignore-missing-imports
	.venv/bin/black --check tests/

format:
	@echo "Formatting code..."
	.venv/bin/black tests/
	.venv/bin/isort tests/ --skip tests/unit/test_time_based_light.py --skip tests/unit/test_notification.py --skip tests/unit/test_zone_entry.py

# Validate Home Assistant configuration
validate-config:
	@echo "Validating Home Assistant configuration files..."
	@if ! docker-compose -f tests/e2e/docker/docker-compose.yml ps homeassistant 2>/dev/null | grep -q "Up"; then \
		echo "Starting temporary Home Assistant container for validation..."; \
		docker run --rm \
			-v $$(pwd)/tests/e2e/docker/config:/config:ro \
			homeassistant/home-assistant:stable \
			python -m homeassistant --config /config --script check_config; \
	else \
		echo "Using running Home Assistant container for validation..."; \
		docker-compose -f tests/e2e/docker/docker-compose.yml exec -T homeassistant \
			python -m homeassistant --config /config --script check_config; \
	fi


# Cleanup
clean:
	@echo "Cleaning up..."
	docker-compose -f tests/e2e/docker/docker-compose.yml down -v
	rm -rf reports/* .pytest_cache .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	# Clean container-generated files from config directory
	@$(MAKE) clean-config

# Clean only config directory (keep containers)
clean-config:
	@echo "Cleaning container-generated config files..."
	@if [ -d "tests/e2e/docker/config/.storage" ]; then \
		if rm -rf tests/e2e/docker/config/.storage 2>/dev/null; then \
			echo "Removed .storage directory"; \
		else \
			echo "Warning: Could not remove .storage directory (may need sudo)"; \
		fi; \
	fi
	@rm -rf tests/e2e/docker/config/deps 2>/dev/null || true
	@rm -rf tests/e2e/docker/config/tts 2>/dev/null || true
	@rm -f tests/e2e/docker/config/*.log tests/e2e/docker/config/*.log.* 2>/dev/null || true
	@rm -f tests/e2e/docker/config/*.txt 2>/dev/null || true
	@rm -f tests/e2e/docker/config/.HA_VERSION 2>/dev/null || true
	@rm -f tests/e2e/docker/config/home-assistant_v2.db* 2>/dev/null || true


# Docker compose shortcuts
dc-up:
	docker-compose -f tests/e2e/docker/docker-compose.yml up -d

dc-down:
	docker-compose -f tests/e2e/docker/docker-compose.yml down

dc-logs:
	docker-compose -f tests/e2e/docker/docker-compose.yml logs -f

dc-ps:
	docker-compose -f tests/e2e/docker/docker-compose.yml ps

# Authentication management
auth-bypass:
	@echo "Switching to bypass authentication (recommended for testing)..."
	./scripts/switch_auth_mode.sh bypass
	@echo "Restart HA for changes to take effect: make restart"

auth-token:
	@echo "Switching to token authentication..."
	./scripts/switch_auth_mode.sh token
	@echo "Restart HA for changes to take effect: make restart"

generate-token:
	@echo "To generate a token (only needed if using token auth):"
	@echo "1. Switch to token auth: make auth-token"
	@echo "2. Start Home Assistant: make start"
	@echo "3. Visit http://localhost:8123"
	@echo "4. Create user account"
	@echo "5. Go to Profile -> Long-Lived Access Tokens"
	@echo "6. Create a new token"
	@echo "7. Export it: export HA_TEST_TOKEN='your-token-here'"
