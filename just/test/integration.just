# Integration test module - Testing with real Home Assistant instance

# Variables for this module
project_root := justfile_directory()
venv_path := project_root + "/.venv"
pytest := venv_path + "/bin/pytest"
test_workers := "2"

# Run all integration tests (first recipe = default for 'just test::integration')
@all:
    echo "Running integration tests with real HA instance..."
    {{pytest}} {{project_root}}/tests/integration -n {{test_workers}} -q

# Show help for integration test module
@help:
    echo "Integration Test Module Commands:"
    echo "═══════════════════════════════════════════════════════"
    echo "  just test::integration - Run all integration tests"
    echo ""
    echo "Integration tests use a real Home Assistant instance"
    echo "but don't require Docker containers."

# Run integration tests with verbose output
@verbose:
    echo "Running integration tests (verbose)..."
    {{pytest}} {{project_root}}/tests/integration -n {{test_workers}} -v

# Run specific integration test pattern
@run pattern:
    echo "Running integration tests matching '{{pattern}}'..."
    {{pytest}} {{project_root}}/tests/integration -k "{{pattern}}" -v

# Run integration tests with debugging
@debug:
    echo "Running integration tests with debugging..."
    {{pytest}} {{project_root}}/tests/integration -s -vv --capture=no
