# Code quality module - Linting, formatting, and pre-commit hooks

# Import common variables
import 'common.just'

# Display available quality commands with descriptions
help:
    @echo "Quality Module Commands:"
    @echo "═══════════════════════════════════════════════════════"
    @cd {{justfile_directory()}} && just --list --justfile just/quality.just --list-heading "" --list-prefix "  just quality::"

# Run all linters (flake8, mypy, black --check)
lint:
    @echo "Running linters..."
    {{flake8}} {{project_root}}/tests/
    {{mypy}} {{project_root}}/tests/ --ignore-missing-imports
    {{black}} --check {{project_root}}/tests/
    @echo "✅ All linters passed!"

# Format code with black and isort
format:
    @echo "Formatting code..."
    {{black}} {{project_root}}/tests/
    {{isort}} {{project_root}}/tests/ \
        --skip {{project_root}}/tests/unit/test_time_based_light.py \
        --skip {{project_root}}/tests/unit/test_notification.py \
        --skip {{project_root}}/tests/unit/test_zone_entry.py
    @echo "✅ Code formatted!"

# Install git pre-commit hooks for code quality
pre-commit-install:
    @echo "Setting up pre-commit hooks..."
    {{project_root}}/scripts/setup-pre-commit.sh
    @echo "✅ Pre-commit hooks installed!"

# Run all pre-commit hooks on all files
pre-commit-run:
    @echo "Running pre-commit on all files..."
    {{pre_commit}} run --all-files

# Update pre-commit hooks to latest versions
pre-commit-update:
    @echo "Updating pre-commit hooks to latest versions..."
    {{pre_commit}} autoupdate

# Run ALL pre-commit checks manually (verbose)
pre-commit-all:
    @echo "=========================================="
    @echo "Running ALL pre-commit checks manually"
    @echo "=========================================="
    @echo ""
    @echo "This runs all configured pre-commit hooks:"
    @echo "- Security checks (detect-secrets, gitleaks, bandit)"
    @echo "- Test integrity (pytest collection)"
    @echo "- Type checking (mypy)"
    @echo "- Code formatting (black, isort)"
    @echo "- Linting (flake8, vulture, pydocstyle)"
    @echo "- Custom validators (test structure, HA mocks)"
    @echo ""
    {{pre_commit}} run --all-files --verbose || echo ""
    @echo ""
    @echo "=========================================="
    @echo "Pre-commit checks completed"
    @echo "=========================================="

# Alias for pre-commit-all
pre-commit: pre-commit-all

# Show pre-commit configuration status
pre-commit-status:
    @echo "Pre-commit configuration status:"
    @echo "================================"
    @if [ -f {{project_root}}/.git/hooks/pre-commit ]; then \
        echo "✅ Pre-commit hooks are installed"; \
    else \
        echo "❌ Pre-commit hooks are NOT installed"; \
        echo "   Run 'just quality::pre-commit-install' to set them up"; \
    fi
    @echo ""
    @echo "Configured hooks (.pre-commit-config.yaml):"
    @{{pre_commit}} validate-config && echo "✅ Configuration is valid"
    @echo ""
    @echo "To see all configured hooks:"
    @echo "  cat {{project_root}}/.pre-commit-config.yaml"

# Run security-related pre-commit checks only
pre-commit-security:
    @echo "Running security checks..."
    {{pre_commit}} run detect-secrets --all-files
    {{pre_commit}} run gitleaks --all-files
    {{pre_commit}} run bandit --all-files
    @echo "✅ Security checks passed!"

# Run formatting-related pre-commit checks only
pre-commit-format:
    @echo "Running formatting checks..."
    {{pre_commit}} run black --all-files
    {{pre_commit}} run isort --all-files
    {{pre_commit}} run end-of-file-fixer --all-files
    {{pre_commit}} run trailing-whitespace --all-files
    @echo "✅ Formatting checks passed!"

# Run linting-related pre-commit checks only
pre-commit-lint:
    @echo "Running linting checks..."
    {{pre_commit}} run flake8 --all-files
    {{pre_commit}} run mypy --all-files
    {{pre_commit}} run vulture --all-files
    {{pre_commit}} run pydocstyle --all-files
    @echo "✅ Linting checks passed!"

# Run YAML validation pre-commit checks only
pre-commit-yaml:
    @echo "Running YAML validation..."
    {{pre_commit}} run check-yaml --all-files
    {{pre_commit}} run yamllint --all-files
    @echo "✅ YAML validation passed!"

# Run custom validator pre-commit checks only
pre-commit-custom:
    @echo "Running custom validators..."
    {{pre_commit}} run validate-test-structure --all-files
    {{pre_commit}} run validate-automation-logic --all-files
    {{pre_commit}} run validate-ha-mocks --all-files
    {{pre_commit}} run pytest-collection --all-files
    @echo "✅ Custom validators passed!"

# Run pre-commit with auto-fix enabled
pre-commit-fix:
    @echo "Running pre-commit with auto-fix..."
    {{pre_commit}} run --all-files --show-diff-on-failure || true
    @echo ""
    @echo "Files have been auto-fixed where possible."
    @echo "Review changes with 'git diff' before committing."

# Generate test coverage report
coverage:
    @just test::coverage

# Open coverage report in browser
report:
    @just test::report

# Clean coverage and quality artifacts
clean:
    @echo "Cleaning quality artifacts..."
    rm -rf {{reports_dir}}/unit_coverage
    rm -rf {{reports_dir}}/.coverage
    rm -rf {{project_root}}/.mypy_cache
    rm -rf {{project_root}}/.pytest_cache
    find {{project_root}} -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @echo "✅ Quality artifacts cleaned!"
