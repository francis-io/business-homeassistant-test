#!/bin/bash
# Setup script for pre-commit hooks

set -e

echo "Setting up pre-commit hooks for HA Test Framework..."

# Check if in virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: Not in a virtual environment. Activating .venv..."
    source .venv/bin/activate || {
        echo "❌ Failed to activate virtual environment. Run 'make setup' first."
        exit 1
    }
fi

# Install pre-commit
echo "📦 Installing pre-commit..."
pip install pre-commit

# Install the pre-commit hooks
echo "🔗 Installing git hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Install additional dependencies for hooks
echo "📚 Installing additional dependencies..."
pip install detect-secrets bandit vulture pydocstyle commitizen

# Run against all files to check current status
echo "🔍 Checking current code status (this may take a minute)..."
pre-commit run --all-files || {
    echo "⚠️  Some checks failed. This is normal for initial setup."
    echo "📋 Review the output above and fix issues as needed."
}

# Generate initial secrets baseline
echo "🔐 Generating secrets baseline..."
detect-secrets scan --baseline .secrets.baseline

echo "✅ Pre-commit setup complete!"
echo ""
echo "Next steps:"
echo "1. Review and fix any issues from the initial run"
echo "2. Commit the .pre-commit-config.yaml and .secrets.baseline"
echo "3. Team members should run: ./scripts/setup-pre-commit.sh"
echo ""
echo "To skip hooks temporarily: git commit --no-verify"
echo "To update hooks: pre-commit autoupdate"
