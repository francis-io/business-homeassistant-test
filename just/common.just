# Common settings and variables shared across all modules

# Python version
python_version := "3.11"

# Project paths
project_root := justfile_directory()
venv_path := project_root + "/.venv"
reports_dir := project_root + "/reports"

# Docker compose files
docker_compose_e2e := project_root + "/tests/e2e/docker/docker-compose.yml"
docker_compose_ui := project_root + "/tests/ui/docker/docker-compose.yml"

# Python commands (using venv)
python := venv_path + "/bin/python"
pip := venv_path + "/bin/pip"
pytest := venv_path + "/bin/pytest"
black := venv_path + "/bin/black"
flake8 := venv_path + "/bin/flake8"
mypy := venv_path + "/bin/mypy"
isort := venv_path + "/bin/isort"
pre_commit := venv_path + "/bin/pre-commit"
playwright := venv_path + "/bin/playwright"

# UV package manager
uv := "uv"

# Home Assistant URLs
ha_url := "http://localhost:8123"

# Test parallelization settings
# Note: For ~90 tests, -n 2 is optimal (faster than -n auto)
test_workers := "2"

# ANSI color codes for pretty output
bold := '\e[1m'
green := '\e[32m'
yellow := '\e[33m'
red := '\e[31m'
blue := '\e[34m'
reset := '\e[0m'

# Helper functions for output (use as {{function_name()}} in recipes)
echo_info := blue + "ℹ" + reset
echo_success := green + "✅" + reset
echo_warning := yellow + "⚠️" + reset
echo_error := red + "❌" + reset
