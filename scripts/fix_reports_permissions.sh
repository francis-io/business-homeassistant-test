#!/bin/bash
# Fix permissions for the reports directory to allow containers to write

REPORTS_DIR="$(dirname "$0")/../reports"

# Create reports directory if it doesn't exist
mkdir -p "$REPORTS_DIR"

# Make reports directory writable by everyone (containers run with different UIDs)
chmod 777 "$REPORTS_DIR"

echo "✅ Fixed permissions for reports directory"
echo "   Reports directory is now writable by containers"
