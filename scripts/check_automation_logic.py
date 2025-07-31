#!/usr/bin/env python3
"""Ensure business logic is properly extracted to automation_logic.py."""
import ast
import sys
from pathlib import Path


def check_automation_logic():
    """Verify that complex logic is in helpers, not in test files."""
    errors = []
    test_files = list(Path("tests").rglob("test_*.py"))

    # Patterns that indicate business logic
    logic_indicators = {
        "complex conditions": lambda node: (
            isinstance(node, ast.If) and count_conditions(node.test) > 3
        ),
        "time calculations": lambda node: (
            isinstance(node, ast.Call)
            and hasattr(node.func, "attr")
            and node.func.attr in ["sunset", "sunrise"]
            and
            # Exclude simple time mocking in tests
            not (
                hasattr(node.func, "value")
                and hasattr(node.func.value, "id")
                and node.func.value.id in ["datetime", "freezegun", "freeze_time"]
            )
        ),
        "state calculations": lambda node: (
            isinstance(node, ast.FunctionDef)
            and any(word in node.name.lower() for word in ["calculate", "determine"])
            and not node.name.startswith("test_")
            and not node.name.startswith("_")
        ),
    }

    for test_file in test_files:
        if test_file.parent.name == "helpers":
            continue

        content = test_file.read_text()
        tree = ast.parse(content)

        for node in ast.walk(tree):
            for pattern_name, checker in logic_indicators.items():
                if checker(node):
                    if isinstance(node, ast.FunctionDef):
                        # Skip test functions
                        if node.name.startswith("test_"):
                            continue

                    errors.append(
                        f"{test_file}: Found {pattern_name} - "
                        "consider extracting to automation_logic.py"
                    )

    if errors:
        print("Automation logic validation failed:")
        for error in errors[:10]:  # Limit output
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more issues")
        return 1

    return 0


def count_conditions(node):
    """Count logical operators in a condition."""
    if isinstance(node, (ast.And, ast.Or)):
        return 1 + sum(count_conditions(child) for child in ast.walk(node))
    return 0


if __name__ == "__main__":
    sys.exit(check_automation_logic())
