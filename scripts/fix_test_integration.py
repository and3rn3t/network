"""
Fix test_integration.py to use NotificationChannel dataclass.

This script updates all create_channel() calls to use the NotificationChannel
dataclass instead of passing individual parameters.
"""

import re
from pathlib import Path


def fix_create_channel_calls(content: str) -> str:
    """Fix create_channel method calls to use NotificationChannel."""

    # Pattern to match create_channel calls with named parameters
    # This is a complex pattern that captures the entire method call
    pattern = r'(\s+)(\w+\s*=\s*)?alert_manager\.create_channel\(\s*\n\s*name\s*=\s*"([^"]+)",\s*\n\s*channel_type\s*=\s*"([^"]+)",\s*\n\s*config\s*=\s*({[^}]+}|\n\s*{[^}]+}),\s*\n?(?:\s*enabled\s*=\s*(\w+),\s*)?\n?(?:\s*min_severity\s*=\s*"([^"]+)",\s*)?\n?\s*\)'

    def replace_call(match):
        indent = match.group(1)
        var_assign = match.group(2) or ""
        name = match.group(3)
        channel_type = match.group(4)
        config = match.group(5).strip()
        enabled = match.group(6) if match.group(6) else "True"
        min_severity = match.group(7)

        # Generate unique ID from name
        channel_id = name.lower().replace(" ", "_").replace("+", "_plus")

        # Add min_severity to config if present
        if min_severity:
            # Remove trailing }
            config = config.rstrip("}").rstrip()
            config += f',\n{indent}    "min_severity": "{min_severity}",\n{indent}}}'

        # Build the replacement
        result = f"""{indent}{var_assign}alert_manager.create_channel(
{indent}    NotificationChannel(
{indent}        id="{channel_id}",
{indent}        name="{name}",
{indent}        channel_type="{channel_type}",
{indent}        config={config},
{indent}        enabled={enabled},
{indent}    )
{indent})"""
        return result

    # Apply the pattern
    fixed_content = re.sub(
        pattern, replace_call, content, flags=re.MULTILINE | re.DOTALL
    )

    return fixed_content


def main():
    test_file = (
        Path(__file__).parent.parent / "tests" / "alerts" / "test_integration.py"
    )

    print(f"Fixing {test_file}...")

    # Read the file
    content = test_file.read_text()

    # Fix the calls
    fixed_content = fix_create_channel_calls(content)

    # Write back
    test_file.write_text(fixed_content)

    print("✅ Fixed create_channel() calls")


if __name__ == "__main__":
    main()
