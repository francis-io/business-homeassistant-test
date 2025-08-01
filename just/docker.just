# Docker module - Container management and operations

# Import common variables
import 'common.just'

# Display available docker commands with descriptions
help:
    @echo "Docker Module Commands:"
    @echo "═══════════════════════════════════════════════════════"
    @cd {{justfile_directory()}} && just --list --justfile just/docker.just --list-heading "" --list-prefix "  just docker::"

# Build Docker containers for testing
build:
    @echo "Building Docker containers..."
    docker-compose -f {{docker_compose_e2e}} build

# Start Home Assistant container at http://localhost:8123
start:
    @echo "Starting Home Assistant..."
    docker-compose -f {{docker_compose_e2e}} up -d homeassistant
    @echo "Waiting for Home Assistant to be healthy..."
    @timeout=60; \
    while [ $timeout -gt 0 ]; do \
        if docker-compose -f {{docker_compose_e2e}} ps homeassistant | grep -q "healthy"; then \
            echo "✅ Home Assistant is healthy and running at {{ha_url}}"; \
            exit 0; \
        fi; \
        echo "⏳ Waiting for Home Assistant to become healthy... ($timeout seconds remaining)"; \
        sleep 5; \
        timeout=$((timeout - 5)); \
    done; \
    echo "❌ Error: Home Assistant failed to become healthy within 60 seconds"; \
    docker-compose -f {{docker_compose_e2e}} logs --tail=50 homeassistant; \
    exit 1

# Stop and remove all Docker containers
stop:
    @echo "Stopping and removing all containers..."
    docker-compose -f {{docker_compose_e2e}} down --remove-orphans

# Restart Home Assistant and test containers
restart: stop start

# Start with fresh HA instance (removes all data)
start-clean: stop
    @echo "Removing Home Assistant volumes..."
    docker-compose -f {{docker_compose_e2e}} down -v
    @just docker::start

# Check Home Assistant health status
healthcheck:
    @if docker-compose -f {{docker_compose_e2e}} ps homeassistant 2>/dev/null | grep -q "healthy"; then \
        echo "✅ Home Assistant is healthy"; \
    else \
        echo "❌ Home Assistant is not healthy"; \
        docker-compose -f {{docker_compose_e2e}} ps homeassistant; \
        exit 1; \
    fi

# Show Home Assistant logs (follow mode)
logs:
    @echo "Showing Home Assistant logs..."
    docker-compose -f {{docker_compose_e2e}} logs -f homeassistant

# Open bash shell in test runner container
shell:
    @echo "Opening shell in test runner container..."
    docker-compose -f {{docker_compose_e2e}} run --rm test_runner /bin/bash

# Open bash shell in Home Assistant container
ha-shell:
    @echo "Opening shell in Home Assistant container..."
    docker-compose -f {{docker_compose_e2e}} exec homeassistant /bin/bash

# Validate Home Assistant YAML configuration
validate-config:
    @echo "Validating Home Assistant configuration files..."
    @if ! docker-compose -f {{docker_compose_e2e}} ps homeassistant 2>/dev/null | grep -q "Up"; then \
        echo "Starting temporary Home Assistant container for validation..."; \
        docker run --rm \
            -v {{project_root}}/tests/e2e/docker/config:/config:ro \
            homeassistant/home-assistant:stable \
            python -m homeassistant --config /config --script check_config; \
    else \
        echo "Using running Home Assistant container for validation..."; \
        docker-compose -f {{docker_compose_e2e}} exec -T homeassistant \
            python -m homeassistant --config /config --script check_config; \
    fi

# Show container status
status:
    @echo "Container status:"
    docker-compose -f {{docker_compose_e2e}} ps

# Clean up containers and artifacts
clean:
    @echo "Cleaning up Docker containers and volumes..."
    docker-compose -f {{docker_compose_e2e}} down -v --remove-orphans
    docker-compose -f {{docker_compose_ui}} down -v --remove-orphans
    @echo "Docker cleanup complete!"

# Start all containers in detached mode
dc-up:
    docker-compose -f {{docker_compose_e2e}} up -d

# Stop all containers
dc-down:
    docker-compose -f {{docker_compose_e2e}} down

# Show all container logs (follow mode)
dc-logs:
    docker-compose -f {{docker_compose_e2e}} logs -f

# Show container status
dc-ps:
    docker-compose -f {{docker_compose_e2e}} ps
