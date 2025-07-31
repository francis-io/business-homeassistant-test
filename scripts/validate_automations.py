#!/usr/bin/env python3
"""Validate all YAML automation files in a directory.

Usage:
    python scripts/validate_automations.py [directory]

If no directory is specified, validates all .yaml files in tests/
"""

import sys
from pathlib import Path

import yaml

# Add project root to path before local imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Local imports after path setup
from tests.helpers.automation_validation import (  # noqa: E402
    get_automation_summary,
    validate_automation_config,
)


def validate_file(yaml_path: Path) -> bool:
    """Validate a single YAML file."""
    print(f"\n📄 Validating: {yaml_path}")

    try:
        with open(yaml_path) as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"   ❌ Failed to load YAML: {e}")
        return False

    # Skip if not an automation (no trigger/action)
    if not isinstance(config, dict) or ("trigger" not in config and "id" not in config):
        print("   ⏩ Skipping - not an automation file")
        return True

    # Validate
    is_valid, errors = validate_automation_config(config)

    if is_valid:
        summary = get_automation_summary(config)
        print(f"   ✅ Valid - {summary}")
        return True
    else:
        print(f"   ❌ Invalid - {len(errors)} error(s):")
        for error in errors:
            print(f"      - {error}")
        return False


def main():
    """Run the main validation process."""
    # Determine directory to scan
    if len(sys.argv) > 1:
        search_dir = Path(sys.argv[1])
    else:
        search_dir = project_root / "tests"

    if not search_dir.exists():
        print(f"❌ Directory not found: {search_dir}")
        sys.exit(1)

    print(f"🔍 Searching for YAML files in: {search_dir}")

    # Find all YAML files
    yaml_files = list(search_dir.rglob("*.yaml")) + list(search_dir.rglob("*.yml"))

    if not yaml_files:
        print("⚠️  No YAML files found")
        sys.exit(0)

    print(f"📊 Found {len(yaml_files)} YAML file(s)")

    # Validate each file
    valid_count = 0
    invalid_count = 0
    skipped_count = 0

    for yaml_file in sorted(yaml_files):
        result = validate_file(yaml_file)
        if result is None:
            skipped_count += 1
        elif result:
            valid_count += 1
        else:
            invalid_count += 1

    # Summary
    print("\n📈 Summary:")
    print(f"   ✅ Valid automations: {valid_count}")
    print(f"   ❌ Invalid automations: {invalid_count}")
    print(f"   ⏩ Skipped (not automations): {skipped_count}")

    # Exit code based on results
    sys.exit(1 if invalid_count > 0 else 0)


if __name__ == "__main__":
    main()
