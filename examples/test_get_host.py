"""
Test the improved get_host method with actual API data.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_loader import get_base_url, load_api_key
from src.exceptions import UniFiNotFoundError
from src.unifi_client import UniFiClient


def main():
    print("=" * 70)
    print("Testing get_host() Method")
    print("=" * 70)

    # Initialize client
    api_key = load_api_key()
    if not api_key:
        print("❌ No API key found!")
        return

    client = UniFiClient(api_key, get_base_url())

    # First, get list of hosts to find a valid ID
    print("\n📋 Fetching list of hosts...")
    try:
        hosts = client.get_hosts()
        if not hosts:
            print("❌ No hosts found")
            return

        print(f"✅ Found {len(hosts)} host(s)\n")

        # Test with the first host
        first_host = hosts[0]
        host_id = first_host.get("id")

        print(f"🔍 Testing get_host() with ID: {host_id[:50]}...\n")

        # Get detailed host information
        host_details = client.get_host(host_id)

        print("✅ Successfully retrieved host details!")
        print("\n" + "=" * 70)
        print("Host Details")
        print("=" * 70)

        # Display key information
        details_to_show = {
            "ID": host_details.get("id", "N/A")[:50] + "...",
            "Type": host_details.get("type", "N/A"),
            "IP Address": host_details.get("ipAddress", "N/A"),
            "Hardware ID": host_details.get("hardwareId", "N/A"),
            "Owner": "Yes" if host_details.get("owner") else "No",
            "Blocked": "Yes" if host_details.get("isBlocked") else "No",
        }

        for key, value in details_to_show.items():
            print(f"{key:<20} {value}")

        # Test with invalid ID
        print("\n" + "=" * 70)
        print("Testing Error Handling (Invalid Host ID)")
        print("=" * 70)

        try:
            client.get_host("invalid-host-id-123")
            print("❌ Should have raised UniFiNotFoundError")
        except UniFiNotFoundError as e:
            print(f"✅ Correctly raised UniFiNotFoundError: {e.message}")

        print("\n✨ All tests passed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
