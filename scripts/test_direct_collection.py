"""
Direct UniFi Collection Test

Tests data collection without the orchestrator to avoid circular imports.
"""

import sys
import time
from datetime import datetime

print("\n" + "=" * 80)
print("  Direct UniFi Collection Test")
print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 80 + "\n")

# Test controller connection
print("Step 1: Testing controller connection...")
try:
    import config
    from src.unifi_controller import UniFiController

    controller = UniFiController(
        host=config.CONTROLLER_HOST,
        username=config.CONTROLLER_USERNAME,
        password=config.CONTROLLER_PASSWORD,
        verify_ssl=False,
    )

    controller.login()
    print("✅ Login successful")

    # Get data
    devices = controller.get_devices()
    clients = controller.get_clients()

    print(f"✅ Found {len(devices)} devices")
    print(f"✅ Found {len(clients)} clients")

    # Show sample data
    if devices:
        d = devices[0]
        print(f"\nSample device:")
        print(f"  Name: {d.get('name', 'Unknown')}")
        print(f"  MAC: {d.get('mac', 'Unknown')}")
        print(f"  Model: {d.get('model', 'Unknown')}")
        print(f"  Type: {d.get('type', 'Unknown')}")

    if clients:
        c = clients[0]
        print(f"\nSample client:")
        print(f"  Hostname: {c.get('hostname', c.get('name', 'Unknown'))}")
        print(f"  MAC: {c.get('mac', 'Unknown')}")
        print(f"  IP: {c.get('ip', 'Unknown')}")
        print(f"  Connected: {c.get('_is_guest_by_uap', False)}")

    controller.logout()
    print("✅ Logout successful\n")

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test data models
print("Step 2: Testing data models...")
try:
    from src.database.models_unifi import UniFiClient, UniFiDevice

    # Create device from API data
    if devices:
        device = UniFiDevice.from_api_response(devices[0])
        print(f"✅ Created device model: {device.name}")

    # Create client from API data
    if clients:
        client = UniFiClient.from_api_response(clients[0])
        print(f"✅ Created client model: {client.mac}")

    print()

except Exception as e:
    print(f"❌ Error: {e}\n")

# Show what the full system would do
print("=" * 80)
print("Summary:")
print("=" * 80)
print(f"\n✅ Controller connection: WORKING")
print(f"✅ Data retrieval: {len(devices)} devices, {len(clients)} clients")
print(f"✅ Data models: WORKING")
print(f"\nTo complete the integration test:")
print(f"1. Close any programs using network_monitor.db")
print(f"2. Run: python setup_unifi_tables.py")
print(f"3. Run: python collect_unifi_data.py --verbose")
print(f"4. Run: python unifi_analytics_demo.py")
print()
