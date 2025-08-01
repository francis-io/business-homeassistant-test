#!/usr/bin/env python3
"""Generate Just files with dynamic group attributes based on module name.

This is an example of how to achieve dynamic grouping.
"""

import re
from pathlib import Path


def add_group_to_recipe(content: str, group_name: str) -> str:
    """Add group attribute to all recipes in content."""
    # Pattern to match recipe definitions (excluding private ones starting with _)
    recipe_pattern = r"^([a-zA-Z][a-zA-Z0-9_-]*(?:\s+[*+]?[a-zA-Z0-9_-]+)*\s*:)"

    lines = content.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a recipe definition
        if re.match(recipe_pattern, line) and not line.strip().startswith("_"):
            # Check if there's already a group attribute
            if i > 0 and lines[i - 1].strip().startswith("[group("):
                result.append(line)
            else:
                # Add group attribute before the recipe
                result.append(f"[group('{group_name}')]")
                result.append(line)
        else:
            result.append(line)

        i += 1

    return "\n".join(result)


def process_just_file(filepath: Path):
    """Process a single Just file to add dynamic group attributes."""
    # Extract module name from filename (e.g., "python.just" -> "python")
    module_name = filepath.stem

    # Skip common.just as it doesn't need grouping
    if module_name == "common":
        return

    print(f"Processing {filepath.name} with group '{module_name}'...")

    # Read the file
    content = filepath.read_text()

    # Add group attributes
    new_content = add_group_to_recipe(content, module_name)

    # Write back if changed
    if new_content != content:
        filepath.write_text(new_content)
        print(f"  ✓ Updated {filepath.name}")
    else:
        print(f"  - No changes needed for {filepath.name}")


def main():
    """Process all Just files."""
    just_dir = Path(__file__).parent.parent / "just"

    if not just_dir.exists():
        print(f"Error: {just_dir} directory not found")
        return 1

    # Process all .just files
    for just_file in just_dir.glob("*.just"):
        process_just_file(just_file)

    print("\nDone! All Just files have been updated with dynamic group attributes.")
    return 0


if __name__ == "__main__":
    exit(main())
