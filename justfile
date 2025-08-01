# Home Assistant Testing Framework - Justfile
# This is the main entry point for the Just build system

# Import common variables globally
import 'just/common.just'

# Import modules
mod test 'just/test.just'
mod docker 'just/docker.just'
mod python 'just/python.just'
mod quality 'just/quality.just'
mod dev 'just/dev.just'

# Show all available commands organized by module
default:
    @echo "Home Assistant Testing Framework"
    @echo "================================"
    @echo ""
    @echo "🧪 TEST COMMANDS"
    @echo "────────────────"
    @echo "  just test                    # Run all tests"
    @echo "  just test::unit              # Run unit tests (logic + mock)"
    @echo "  just test::integration       # Run integration tests"
    @echo "  just test::e2e               # Run end-to-end tests in Docker"
    @echo "  just test::ui                # Run UI tests with Playwright"
    @echo "  just test::coverage          # Generate test coverage report"
    @echo "  just test::help              # Show all test commands"
    @echo ""
    @echo "🐳 DOCKER COMMANDS"
    @echo "──────────────────"
    @echo "  just docker::build           # Build Docker containers"
    @echo "  just docker::start           # Start Home Assistant"
    @echo "  just docker::stop            # Stop all containers"
    @echo "  just docker::logs            # Show Home Assistant logs"
    @echo "  just docker::shell           # Open shell in container"
    @echo "  just docker::help            # Show all docker commands"
    @echo ""
    @echo "🐍 PYTHON COMMANDS"
    @echo "──────────────────"
    @echo "  just python::setup           # Create environment and install deps"
    @echo "  just python::setup-all       # Setup with all test dependencies"
    @echo "  just python::env-update      # Update dependencies"
    @echo "  just python::env-clean       # Remove Python environment"
    @echo "  just python::help            # Show all python commands"
    @echo ""
    @echo "✨ QUALITY COMMANDS"
    @echo "───────────────────"
    @echo "  just quality::lint           # Run linters (flake8, mypy, black)"
    @echo "  just quality::format         # Format code with black and isort"
    @echo "  just quality::pre-commit     # Run pre-commit checks"
    @echo "  just quality::help           # Show all quality commands"
    @echo ""
    @echo "🔧 DEV COMMANDS"
    @echo "───────────────"
    @echo "  just dev::clean              # Clean all artifacts"
    @echo "  just dev::auth-bypass        # Use bypass auth (no tokens)"
    @echo "  just dev::generate-token     # Show token generation help"
    @echo "  just dev::help               # Show all dev commands"
    @echo ""
    @echo "💡 TIPS:"
    @echo "────────"
    @echo "• Run 'just <module>::help' for detailed help on any module"
    @echo "• Example: 'just test::help' shows all test commands"
    @echo "• Make and Just are interchangeable: 'make test' = 'just test'"
    @echo "• Use tab completion for commands"
    @echo ""
    @echo "📚 For all commands in detail: 'just help-all'"

# Show detailed help with all commands from all modules
help-all:
    @echo "Home Assistant Testing Framework - All Commands"
    @echo "=============================================="
    @echo ""
    @echo "🧪 TEST MODULE"
    @echo "──────────────"
    @cd {{justfile_directory()}} && just --list --justfile just/test.just --list-heading "" --list-prefix "  just test::"
    @echo ""
    @echo "    📁 Unit Test Submodule:"
    @echo "      just test::unit::all         # Run all unit tests"
    @echo "      just test::unit::logic       # Run logic tests only"
    @echo "      just test::unit::mock        # Run mock tests only"
    @echo "      just test::unit::help        # Show unit test commands"
    @echo ""
    @echo "    📁 Integration Test Submodule:"
    @echo "      just test::integration::all  # Run integration tests"
    @echo "      just test::integration::help # Show integration commands"
    @echo ""
    @echo "    📁 E2E Test Submodule:"
    @echo "      just test::e2e::all          # Run E2E tests"
    @echo "      just test::e2e::help         # Show E2E commands"
    @echo ""
    @echo "    📁 UI Test Submodule:"
    @echo "      just test::ui::all           # Run UI tests (headless)"
    @echo "      just test::ui::headed        # Run with visible browser"
    @echo "      just test::ui::debug         # Run in debug mode"
    @echo "      just test::ui::help          # Show UI commands"
    @echo ""
    @echo "🐳 DOCKER MODULE"
    @echo "────────────────"
    @cd {{justfile_directory()}} && just --list --justfile just/docker.just --list-heading "" --list-prefix "  just docker::"
    @echo ""
    @echo "🐍 PYTHON MODULE"
    @echo "────────────────"
    @cd {{justfile_directory()}} && just --list --justfile just/python.just --list-heading "" --list-prefix "  just python::"
    @echo ""
    @echo "✨ QUALITY MODULE"
    @echo "─────────────────"
    @cd {{justfile_directory()}} && just --list --justfile just/quality.just --list-heading "" --list-prefix "  just quality::"
    @echo ""
    @echo "🔧 DEV MODULE"
    @echo "─────────────"
    @cd {{justfile_directory()}} && just --list --justfile just/dev.just --list-heading "" --list-prefix "  just dev::"
    @echo ""
    @echo "💡 Remember: All commands work with both 'just' and 'make'!"

# Show detailed help with categories (legacy format)
help-detailed:
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
    @echo "Pre-commit Hooks:"
    @echo "  make pre-commit         - Run ALL pre-commit checks manually (verbose)"
    @echo "  make pre-commit-install - Setup pre-commit hooks (first time)"
    @echo "  make pre-commit-run     - Run pre-commit on all files"
    @echo "  make pre-commit-update  - Update hooks to latest versions"
    @echo "  make pre-commit-status  - Show pre-commit configuration status"
    @echo ""
    @echo "Pre-commit Hook Groups (run specific checks):"
    @echo "  make pre-commit-security - Run security checks only"
    @echo "  make pre-commit-format   - Run formatting checks only"
    @echo "  make pre-commit-lint     - Run linting checks only"
    @echo "  make pre-commit-yaml     - Run YAML validation only"
    @echo "  make pre-commit-custom   - Run custom validators only"
    @echo "  make pre-commit-fix      - Run with auto-fix enabled"
    @echo ""
    @echo "Python Environment Management (UV):"
    @echo "  make env-update     - Update all dependencies"
    @echo "  make env-clean      - Remove Python environment"
    @echo "  make env-where      - Show environment location"
    @echo ""
    @echo "Reports:"
    @echo "  make coverage       - Generate coverage report"
    @echo "  make report         - Open HTML coverage report"
    @echo ""
    @echo "For all available commands: make help-all"

# ==== TOP-LEVEL ALIASES FOR COMMON COMMANDS ====
# These provide shortcuts for the most common operations

# Run all tests (unit, integration, e2e, ui)
test-all:
    @just test::all

# Create Python environment and install base test dependencies
setup:
    @just python::setup

# Start Home Assistant in Docker containers
start:
    @just docker::start

# Clean up all containers, test artifacts, and generated files
clean:
    @just dev::clean

# Run code quality checks (flake8, mypy, black --check)
lint:
    @just quality::lint

# Show this help message with available commands
help: default

# Show all available commands including submodules
list-all:
    @just --list --list-submodules
