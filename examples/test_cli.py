"""Test the alert CLI tool."""

import subprocess
import sys
from pathlib import Path


def run_cli(*args):
    """Run CLI command and return result."""
    cmd = [sys.executable, "-m", "src.alerts.cli"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def test_cli():
    """Test CLI commands."""
    print("Testing Alert CLI Tool")
    print("=" * 60)

    # Test help
    print("\n1. Testing help command...")
    code, stdout, stderr = run_cli("--help")
    if code == 0 and "UniFi Network Alert System CLI" in stdout:
        print("   ✓ Help command works")
    else:
        print(f"   ✗ Help command failed: {stderr}")
        return False

    # Test rule list
    print("\n2. Testing rule list...")
    code, stdout, stderr = run_cli("rule", "list")
    if code == 0:
        print(f"   ✓ Rule list works")
        print(f"   Output: {stdout.strip()[:100]}...")
    else:
        print(f"   ✗ Rule list failed: {stderr}")
        return False

    # Test alert list
    print("\n3. Testing alert list...")
    code, stdout, stderr = run_cli("alert", "list")
    if code == 0:
        print(f"   ✓ Alert list works")
        print(f"   Output: {stdout.strip()[:100]}...")
    else:
        print(f"   ✗ Alert list failed: {stderr}")
        return False

    # Test channel list
    print("\n4. Testing channel list...")
    code, stdout, stderr = run_cli("channel", "list")
    if code == 0:
        print(f"   ✓ Channel list works")
        print(f"   Output: {stdout.strip()[:100]}...")
    else:
        print(f"   ✗ Channel list failed: {stderr}")
        return False

    # Test mute list
    print("\n5. Testing mute list...")
    code, stdout, stderr = run_cli("mute", "list")
    if code == 0:
        print(f"   ✓ Mute list works")
        print(f"   Output: {stdout.strip()[:100]}...")
    else:
        print(f"   ✗ Mute list failed: {stderr}")
        return False

    # Test alert stats
    print("\n6. Testing alert stats...")
    code, stdout, stderr = run_cli("alert", "stats")
    if code == 0:
        print(f"   ✓ Alert stats works")
        print(f"   Output: {stdout.strip()[:100]}...")
    else:
        print(f"   ✗ Alert stats failed: {stderr}")
        return False

    # Test create rule (this will create a real rule)
    print("\n7. Testing rule creation...")
    code, stdout, stderr = run_cli(
        "rule",
        "create",
        "--name",
        "CLI Test Rule",
        "--type",
        "threshold",
        "--metric",
        "cpu_usage",
        "--condition",
        "gt",
        "--threshold",
        "90",
        "--severity",
        "warning",
        "--channels",
        "email-1",
        "--description",
        "Test rule created by CLI test",
    )
    if code == 0 and "Created rule" in stdout:
        print(f"   ✓ Rule creation works")
        print(f"   {stdout.strip()}")
    else:
        print(f"   ✗ Rule creation failed: {stderr}")
        return False

    print("\n" + "=" * 60)
    print("All CLI tests passed! ✓")
    print("\n💡 Try these commands:")
    print("   python -m src.alerts.cli rule list")
    print("   python -m src.alerts.cli alert list")
    print("   python -m src.alerts.cli channel list")
    print("   python -m src.alerts.cli alert stats")

    return True


if __name__ == "__main__":
    try:
        success = test_cli()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
