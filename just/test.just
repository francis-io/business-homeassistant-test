# Test module - Main testing commands and orchestration

# Import submodules
mod unit 'test/unit.just'
mod integration 'test/integration.just'
mod e2e 'test/e2e.just'
mod ui 'test/ui.just'

# Variables for this module
project_root := justfile_directory()
venv_path := project_root + "/.venv"
pytest := venv_path + "/bin/pytest"
reports_dir := project_root + "/reports"

# Run all tests - unit, integration, e2e, and ui tests in sequence
all:
    @echo "Running all tests (unit, integration, e2e, ui)..."
    @echo "Note: UI and E2E tests run separately due to Docker requirements"
    @echo ""
    @just test::unit
    @echo ""
    @just test::integration
    @echo ""
    @just test::e2e
    @echo ""
    @just test::ui
    @echo ""
    @echo "All tests completed!"

# Display available test commands with descriptions
help:
    @echo "Test Module Commands:"
    @echo "═══════════════════════════════════════════════════════"
    @cd {{justfile_directory()}} && just --list --justfile just/test.just --list-heading "" --list-prefix "  just test::"

# Generate test coverage report for unit tests
coverage:
    @echo "Generating coverage report..."
    {{pytest}} tests/unit --cov=tests/helpers --cov-report=html:{{reports_dir}}/unit_coverage --cov-report=term
    @echo "Coverage report generated in: {{reports_dir}}/unit_coverage/index.html"

# Open coverage report in browser
report:
    @echo "Opening coverage report..."
    @if [ -f "{{reports_dir}}/unit_coverage/index.html" ]; then \
        if command -v xdg-open &> /dev/null; then \
            xdg-open "{{reports_dir}}/unit_coverage/index.html"; \
        elif command -v open &> /dev/null; then \
            open "{{reports_dir}}/unit_coverage/index.html"; \
        else \
            echo "Please open manually: {{reports_dir}}/unit_coverage/index.html"; \
        fi; \
    else \
        echo "Coverage report not found. Run 'just test::coverage' first."; \
    fi

# Run quick tests only (unit + integration, no Docker required)
quick:
    @echo "Running quick tests (unit + integration)..."
    @just test::unit
    @echo ""
    @just test::integration
    @echo ""
    @echo "Quick tests completed!"

# Run Docker-based tests only (e2e + ui)
docker:
    @echo "Running Docker-based tests (e2e + ui)..."
    @just test::e2e
    @echo ""
    @just test::ui
    @echo ""
    @echo "Docker-based tests completed!"

# Watch tests and rerun on file changes
watch:
    @echo "Watching for file changes..."
    {{pytest}} tests/unit --watch
