# Unit test module - Logic and mock testing

# Variables for this module
project_root := justfile_directory()
venv_path := project_root + "/.venv"
pytest := venv_path + "/bin/pytest"
test_workers := "2"

# Run all unit tests (first recipe = default for 'just test::unit')
@all:
    echo "Running all unit tests (logic + mock)..."
    {{pytest}} {{project_root}}/tests/unit -n {{test_workers}} -q

# Show help for unit test module
@help:
    echo "Unit Test Module Commands:"
    echo "═══════════════════════════════════════════════════════"
    echo "  just test::unit        - Run all unit tests"
    echo "  just test::unit::logic - Run logic tests only (pure Python)"
    echo "  just test::unit::mock  - Run mock tests only (HA components)"
    echo ""
    echo "Unit tests are fast and don't require Docker or Home Assistant."
    echo "They test business logic and component behavior in isolation."

# Run logic unit tests only (pure Python business logic)
@logic:
    echo "Running logic unit tests..."
    {{pytest}} {{project_root}}/tests/unit/logic -n {{test_workers}} -q

# Run mock unit tests only (mocked HA components)
@mock:
    echo "Running mock unit tests..."
    {{pytest}} {{project_root}}/tests/unit/mock -n {{test_workers}} -q

# Run specific unit test pattern
@run pattern:
    echo "Running unit tests matching '{{pattern}}'..."
    {{pytest}} {{project_root}}/tests/unit -k "{{pattern}}" -v

# Run unit tests with verbose output
@verbose:
    echo "Running all unit tests (verbose)..."
    {{pytest}} {{project_root}}/tests/unit -n {{test_workers}} -v

# Run unit tests with debugging enabled
@debug:
    echo "Running unit tests with debugging..."
    {{pytest}} {{project_root}}/tests/unit -s -vv --capture=no
