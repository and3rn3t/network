"""
Quick test script for UniFi Controller API integration.
Tests basic connectivity and listing operations without any destructive actions.

Usage:
    python quick_test_unifi.py
"""

import sys
from datetime import datetime

try:
    import config
    from src.unifi_controller import UniFiController
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure config.py exists and src/unifi_controller.py is present")
    sys.exit(1)


def main():
    print("\n" + "=" * 80)
    print("  Quick UniFi Controller Connection Test")
    print("=" * 80)
    print(f"\n  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(
        f"  Controller: {config.CONTROLLER_HOST}:{getattr(config, 'CONTROLLER_PORT', 8443)}"
    )
    print(f"  Site: {getattr(config, 'CONTROLLER_SITE', 'default')}")

    try:
        # Initialize controller
        print("\n📡 Initializing controller connection...")
        controller = UniFiController(
            host=config.CONTROLLER_HOST,
            username=config.CONTROLLER_USERNAME,
            password=config.CONTROLLER_PASSWORD,
            port=getattr(config, "CONTROLLER_PORT", 8443),
            site=getattr(config, "CONTROLLER_SITE", "default"),
            verify_ssl=getattr(config, "CONTROLLER_VERIFY_SSL", False),
            timeout=30,
        )

        # Test connection
        print("🔐 Testing connection...")
        if controller.test_connection():
            print("✅ Connection successful!")
        else:
            print("❌ Connection failed!")
            return 1

        # Login
        print("🔑 Authenticating...")
        controller.login()
        print("✅ Authentication successful!")

        # Get sites
        print("\n📍 Fetching sites...")
        sites = controller.get_sites()
        print(f"✅ Found {len(sites)} site(s)")
        for site in sites:
            name = site.get("name", "unknown")
            desc = site.get("desc", "No description")
            print(f"   • {name}: {desc}")

        # Get devices
        print("\n🖥️  Fetching devices...")
        devices = controller.get_devices()
        print(f"✅ Found {len(devices)} device(s)")
        for i, device in enumerate(devices[:5], 1):
            name = device.get("name", "Unnamed")
            model = device.get("model", "Unknown")
            mac = device.get("mac", "unknown")
            state = device.get("state", 0)
            status = "🟢 Online" if state == 1 else "🔴 Offline"
            print(f"   {i}. {name} ({model}) - {mac} - {status}")
        if len(devices) > 5:
            print(f"   ... and {len(devices) - 5} more")

        # Get clients
        print("\n👥 Fetching clients...")
        clients = controller.get_clients()
        print(f"✅ Found {len(clients)} active client(s)")
        for i, client in enumerate(clients[:5], 1):
            hostname = client.get("hostname", client.get("name", "Unknown"))
            mac = client.get("mac", "unknown")
            ip = client.get("ip", "No IP")
            print(f"   {i}. {hostname} - {mac} - {ip}")
        if len(clients) > 5:
            print(f"   ... and {len(clients) - 5} more")

        # Logout
        print("\n🚪 Logging out...")
        controller.logout()
        print("✅ Logged out successfully")

        print("\n" + "=" * 80)
        print("  ✅ All basic tests passed!")
        print("=" * 80)
        print("\nNext steps:")
        print("  • Run 'python test_unifi_integration.py' for comprehensive testing")
        print("  • Start backend: 'cd backend && python src/main.py'")
        print("  • Test API endpoints via Swagger UI: http://localhost:8000/docs")
        print()

        return 0

    except AttributeError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("\nRequired settings in config.py:")
        print("  - CONTROLLER_HOST")
        print("  - CONTROLLER_USERNAME")
        print("  - CONTROLLER_PASSWORD")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
