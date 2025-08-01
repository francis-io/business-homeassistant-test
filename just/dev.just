# Development tools module - Cleanup, authentication, and utilities

# Import common variables
import 'common.just'

# Display available dev commands with descriptions
help:
    @echo "Development Module Commands:"
    @echo "═══════════════════════════════════════════════════════"
    @cd {{justfile_directory()}} && just --list --justfile just/dev.just --list-heading "" --list-prefix "  just dev::"

# Clean all containers, test artifacts, and cache files
clean:
    @echo "Cleaning up..."
    docker-compose -f {{docker_compose_e2e}} down -v
    rm -rf {{reports_dir}}/* {{project_root}}/.pytest_cache {{project_root}}/.coverage
    find {{project_root}} -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find {{project_root}} -type f -name "*.pyc" -delete
    # Clean container-generated files from config directory
    @just dev::clean-config
    @echo "✅ Cleanup complete!"

# Clean container-generated config files only
clean-config:
    @echo "Cleaning container-generated config files..."
    @if [ -d "{{project_root}}/tests/e2e/docker/config/.storage" ]; then \
        if rm -rf {{project_root}}/tests/e2e/docker/config/.storage 2>/dev/null; then \
            echo "Removed .storage directory"; \
        else \
            echo "Warning: Could not remove .storage directory (may need sudo)"; \
        fi; \
    fi
    @rm -rf {{project_root}}/tests/e2e/docker/config/deps 2>/dev/null || true
    @rm -rf {{project_root}}/tests/e2e/docker/config/tts 2>/dev/null || true
    @rm -f {{project_root}}/tests/e2e/docker/config/*.log {{project_root}}/tests/e2e/docker/config/*.log.* 2>/dev/null || true
    @rm -f {{project_root}}/tests/e2e/docker/config/*.txt 2>/dev/null || true
    @rm -f {{project_root}}/tests/e2e/docker/config/.HA_VERSION 2>/dev/null || true
    @rm -f {{project_root}}/tests/e2e/docker/config/home-assistant_v2.db* 2>/dev/null || true

# Switch to bypass auth mode (no tokens needed)
auth-bypass:
    @echo "Switching to bypass authentication (recommended for testing)..."
    {{project_root}}/scripts/switch_auth_mode.sh bypass
    @echo "Restart HA for changes to take effect: just docker::restart"

# Switch to token auth mode (requires HA_TEST_TOKEN)
auth-token:
    @echo "Switching to token authentication..."
    {{project_root}}/scripts/switch_auth_mode.sh token
    @echo "Restart HA for changes to take effect: just docker::restart"

# Show instructions for generating HA access token
generate-token:
    @echo "To generate a token (only needed if using token auth):"
    @echo "1. Switch to token auth: just dev::auth-token"
    @echo "2. Start Home Assistant: just docker::start"
    @echo "3. Visit {{ha_url}}"
    @echo "4. Create user account"
    @echo "5. Go to Profile -> Long-Lived Access Tokens"
    @echo "6. Create a new token"
    @echo "7. Export it: export HA_TEST_TOKEN='your-token-here'"

# Show comprehensive help for all available commands
help-all:
    @echo "Home Assistant Testing Framework - All Commands"
    @echo "============================================="
    @echo ""
    @echo "COMMANDS BY CATEGORY:"
    @echo "────────────────────"
    @echo ""
    @just --list --list-heading ""
    @echo ""
    @echo "📝 EXAMPLES:"
    @echo "────────────"
    @echo "  just setup                    # Initial setup"
    @echo "  just test                     # Run all tests"
    @echo "  just test::unit               # Run unit tests only"
    @echo "  just docker::start            # Start Home Assistant"
    @echo "  just docker::logs             # View HA logs"
    @echo "  just quality::lint            # Check code quality"
    @echo ""
    @echo "💡 TIPS:"
    @echo "────────"
    @echo "• Use 'just help' for a concise command list"
    @echo "• Commands support tab completion"
    @echo "• Make and Just are interchangeable (make test = just test)"
    @echo "• Run 'just --show <recipe>' to see command details"
    @echo "• Modules: test, docker, python, quality, dev"
