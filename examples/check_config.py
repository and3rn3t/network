"""
Interactive Configuration Helper

This script helps you gather and verify your UniFi API configuration.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_loader import get_base_url, load_api_key
from src.unifi_client import UniFiClient


def check_api_connection(client):
    """Test the API connection."""
    print("\n🔍 Testing API connection...")
    try:
        # Try a simple request
        result = client.test_connection()
        if result:
            print("✅ API connection successful!")
            return True
        else:
            print("❌ API connection failed")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def gather_configuration():
    """Interactive configuration gathering."""
    print("=" * 60)
    print("UniFi API Configuration Helper")
    print("=" * 60)

    # Check API key
    print("\n📋 Checking current configuration...")
    api_key = load_api_key()
    base_url = get_base_url()

    if not api_key:
        print("\n❌ No API key found!")
        print("\nPlease configure your API key first:")
        print("1. Copy config.example.py to config.py")
        print("2. Add your API key")
        return

    print(f"✅ API Key: {'*' * 20}{api_key[-4:]}")
    print(f"✅ Base URL: {base_url}")

    # Test connection
    client = UniFiClient(api_key, base_url)
    connected = check_api_connection(client)

    if not connected:
        print("\n⚠️  Cannot gather additional info - API not responding")
        print("\nPossible issues:")
        print("- Invalid API key")
        print("- Network connectivity issues")
        print("- API endpoint not accessible")
        return

    # Gather additional info
    print("\n" + "=" * 60)
    print("Current Configuration Summary")
    print("=" * 60)

    config_items = {
        "API Key": "Configured ✅",
        "Base URL": base_url,
        "Connection": "Working ✅",
    }

    for key, value in config_items.items():
        print(f"{key:.<25} {value}")

    print("\n" + "=" * 60)
    print("Optional Configuration Recommendations")
    print("=" * 60)

    recommendations = [
        ("Timeout Settings", "Add REQUEST_TIMEOUT to config.py", "Optional"),
        ("SSL Verification", "Set VERIFY_SSL in config.py", "Recommended"),
        ("Retry Logic", "Add MAX_RETRIES to config.py", "Recommended"),
        ("Logging Level", "Already configured (INFO)", "✅"),
        ("Rate Limiting", "Add REQUESTS_PER_SECOND", "For high volume"),
    ]

    print(f"\n{'Setting':<25} {'Action':<35} {'Priority':<15}")
    print("-" * 75)
    for setting, action, priority in recommendations:
        print(f"{setting:<25} {action:<35} {priority:<15}")

    print("\n" + "=" * 60)
    print("Next Steps")
    print("=" * 60)
    print("\n1. 📖 Read docs/CONFIGURATION.md for detailed options")
    print("2. 🧪 Try examples/list_hosts.py to test API calls")
    print("3. 🔍 Use api_explorer.http for interactive testing")
    print("4. 📚 Check docs/API_REFERENCE.md for available endpoints")

    print("\n✨ You're ready to explore the UniFi API!\n")


if __name__ == "__main__":
    try:
        gather_configuration()
    except KeyboardInterrupt:
        print("\n\n👋 Configuration check cancelled")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
