# E2E test module - End-to-end testing in Docker containers

# Variables for this module
project_root := justfile_directory()
docker_compose_e2e := project_root + "/tests/e2e/docker/docker-compose.yml"
reports_dir := project_root + "/reports"

# Run all E2E tests (first recipe = default for 'just test::e2e')
@all:
    echo "Running E2E tests in Docker containers..."
    @start_time=$(date +%s); \
    echo "Cleaning up any existing test containers..."; \
    docker ps -a --filter "name=home-assistant-test-" --format "{{{{.Names}}}}" | xargs -r docker rm -f 2>/dev/null || true; \
    docker-compose -f {{docker_compose_e2e}} down --volumes --remove-orphans 2>/dev/null || true; \
    echo "Starting fresh E2E test run..."; \
    docker-compose -f {{docker_compose_e2e}} run --rm home-assistant-test-runner-e2e || exit_code=$?; \
    echo "Cleaning up test containers..."; \
    docker ps -a --filter "name=home-assistant-test-" --format "{{{{.Names}}}}" | xargs -r docker rm -f 2>/dev/null || true; \
    docker-compose -f {{docker_compose_e2e}} down --volumes --remove-orphans 2>/dev/null || true; \
    end_time=$(date +%s); \
    duration=$((end_time - start_time)); \
    echo ""; \
    echo "=========================================="; \
    echo "E2E tests completed in $duration seconds"; \
    if [ -f {{reports_dir}}/last_report.txt ]; then \
        run_dir=$(cat {{reports_dir}}/last_report.txt | grep "RUN_DIR=" | cut -d'=' -f2); \
        echo "Test artifacts saved in: {{reports_dir}}/$run_dir/"; \
        echo "  - Test report: {{reports_dir}}/$run_dir/results.xml"; \
        if ls {{reports_dir}}/$run_dir/*.png 2>/dev/null | grep -q .; then \
            echo "  - Screenshots: $(ls {{reports_dir}}/$run_dir/*.png | wc -l) files in {{reports_dir}}/$run_dir/"; \
        fi; \
    else \
        echo "Test reports saved in: {{reports_dir}}/"; \
    fi; \
    echo "=========================================="; \
    exit ${exit_code:-0}

# Show help for E2E test module
@help:
    echo "E2E Test Module Commands:"
    echo "═══════════════════════════════════════════════════════"
    echo "  just test::e2e - Run all E2E tests in Docker"
    echo ""
    echo "E2E tests run in Docker containers and test the full"
    echo "Home Assistant system end-to-end."
    echo ""
    echo "Requirements:"
    echo "  - Docker and docker-compose installed"
    echo "  - Port 8123 available"

# Clean up E2E test containers
@clean:
    echo "Cleaning up E2E test containers..."
    docker ps -a --filter "name=home-assistant-test-" --format "{{{{.Names}}}}" | xargs -r docker rm -f 2>/dev/null || true
    docker-compose -f {{docker_compose_e2e}} down --volumes --remove-orphans 2>/dev/null || true
    echo "Cleanup complete!"

# Show E2E container status
@status:
    echo "E2E test container status:"
    docker-compose -f {{docker_compose_e2e}} ps
