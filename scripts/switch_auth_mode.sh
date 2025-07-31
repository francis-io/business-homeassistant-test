#!/bin/bash
# Switch between authentication modes for Home Assistant testing

set -e

MODE=${1:-bypass}
CONFIG_DIR="tests/e2e/docker/config"

echo "🔐 Switching Home Assistant auth mode to: $MODE"

case $MODE in
    bypass)
        echo "Setting up bypass authentication (no token needed)..."
        # Use the test configuration with bypass auth
        cp "${CONFIG_DIR}/configuration_test.yaml" "${CONFIG_DIR}/configuration.yaml"
        echo "✅ Bypass auth enabled - no token required for testing"
        echo "   Trusted networks: 127.0.0.1, Docker networks (172.x.x.x)"
        ;;

    token)
        echo "Setting up token authentication..."
        # Restore original configuration
        if [ -f "${CONFIG_DIR}/configuration_original.yaml" ]; then
            cp "${CONFIG_DIR}/configuration_original.yaml" "${CONFIG_DIR}/configuration.yaml"
        fi
        echo "⚠️  Token authentication enabled"
        echo "   You'll need to:"
        echo "   1. Create a user account in Home Assistant"
        echo "   2. Generate a long-lived access token"
        echo "   3. Set HA_TEST_TOKEN environment variable"
        ;;

    *)
        echo "❌ Unknown mode: $MODE"
        echo "Usage: $0 [bypass|token]"
        exit 1
        ;;
esac

echo ""
echo "🔄 Restart Home Assistant for changes to take effect:"
echo "   make restart"
