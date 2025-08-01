# UI test module - Browser-based UI testing with Playwright

# Variables for this module
project_root := justfile_directory()
docker_compose_ui := project_root + "/tests/ui/docker/docker-compose.yml"
reports_dir := project_root + "/reports"

# Run UI tests in headless mode (first recipe = default for 'just test::ui')
@all *args='':
    echo "Running UI tests in Docker (headless)..."
    @start_time=$(date +%s); \
    echo "Cleaning up any existing test containers..."; \
    docker ps -a --filter "name=home-assistant-test-" --format "{{{{.Names}}}}" | xargs -r docker rm -f 2>/dev/null || true; \
    docker-compose -f {{docker_compose_ui}} down --volumes --remove-orphans; \
    echo "Starting fresh UI test run..."; \
    docker-compose -f {{docker_compose_ui}} run --rm home-assistant-test-runner-ui {{args}} || exit_code=$?; \
    echo "Cleaning up test containers..."; \
    docker ps -a --filter "name=home-assistant-test-" --format "{{{{.Names}}}}" | xargs -r docker rm -f 2>/dev/null || true; \
    docker-compose -f {{docker_compose_ui}} down --volumes --remove-orphans; \
    end_time=$(date +%s); \
    duration=$((end_time - start_time)); \
    echo ""; \
    echo "=========================================="; \
    echo "UI tests completed in $duration seconds"; \
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

# Show help for UI test module
@help:
    echo "UI Test Module Commands:"
    echo "═══════════════════════════════════════════════════════"
    echo "  just test::ui         - Run UI tests (headless)"
    echo "  just test::ui::headed - Run UI tests with visible browser"
    echo "  just test::ui::debug  - Run UI tests in debug mode"
    echo ""
    echo "UI tests use Playwright to test the Home Assistant"
    echo "web interface in real browsers."
    echo ""
    echo "Requirements:"
    echo "  - Docker and docker-compose installed"
    echo "  - Playwright browsers installed"

# Run UI tests with visible browser
@headed:
    echo "Running UI tests with visible browser..."
    @start_time=$(date +%s); \
    echo "Cleaning up any existing test containers..."; \
    docker ps -a --filter "name=home-assistant-test-" --format "{{{{.Names}}}}" | xargs -r docker rm -f 2>/dev/null || true; \
    docker-compose -f {{docker_compose_ui}} down --volumes --remove-orphans; \
    echo "Starting fresh UI test run with headed mode..."; \
    HEADED=true docker-compose -f {{docker_compose_ui}} run --rm home-assistant-test-runner-ui || exit_code=$?; \
    echo "Cleaning up test containers..."; \
    docker ps -a --filter "name=home-assistant-test-" --format "{{{{.Names}}}}" | xargs -r docker rm -f 2>/dev/null || true; \
    docker-compose -f {{docker_compose_ui}} down --volumes --remove-orphans; \
    end_time=$(date +%s); \
    duration=$((end_time - start_time)); \
    echo ""; \
    echo "=========================================="; \
    echo "UI tests (headed) completed in $duration seconds"; \
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

# Run UI tests in debug mode (slow, visible browser)
@debug:
    echo "Running UI tests in debug mode..."
    @start_time=$(date +%s); \
    echo "Cleaning up any existing test containers..."; \
    docker ps -a --filter "name=home-assistant-test-" --format "{{{{.Names}}}}" | xargs -r docker rm -f 2>/dev/null || true; \
    docker-compose -f {{docker_compose_ui}} down --volumes --remove-orphans; \
    echo "Starting fresh UI test run in debug mode..."; \
    HEADED=true DEBUG=true SLOWMO=1000 docker-compose -f {{docker_compose_ui}} run --rm home-assistant-test-runner-ui || exit_code=$?; \
    echo "Cleaning up test containers..."; \
    docker ps -a --filter "name=home-assistant-test-" --format "{{{{.Names}}}}" | xargs -r docker rm -f 2>/dev/null || true; \
    docker-compose -f {{docker_compose_ui}} down --volumes --remove-orphans; \
    end_time=$(date +%s); \
    duration=$((end_time - start_time)); \
    echo ""; \
    echo "=========================================="; \
    echo "UI tests (debug) completed in $duration seconds"; \
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

# Clean up UI test containers
@clean:
    echo "Cleaning up UI test containers..."
    docker ps -a --filter "name=home-assistant-test-" --format "{{{{.Names}}}}" | xargs -r docker rm -f 2>/dev/null || true
    docker-compose -f {{docker_compose_ui}} down --volumes --remove-orphans
    echo "Cleanup complete!"

# Show UI container status
@status:
    echo "UI test container status:"
    docker-compose -f {{docker_compose_ui}} ps

# Rebuild UI test container
@rebuild:
    echo "Rebuilding UI test container with updated dependencies..."
    docker-compose -f {{docker_compose_ui}} build --no-cache home-assistant-test-runner-ui
    echo "UI test container rebuilt successfully!"
