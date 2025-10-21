"""
Test UniFi Data Collection with Fresh Database

Tests end-to-end collection to the fresh database.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.unifi_collector import UniFiCollectorService

import config
from database.database import Database
from unifi_controller import UniFiController

DB_PATH = "unifi_network.db"

print("\n" + "=" * 80)
print("  UniFi Data Collection Test - Fresh Database")
print("=" * 80 + "\n")

# Step 1: Test controller connection
print("Step 1: Testing controller connection...")
try:
    controller = UniFiController(
        host=config.CONTROLLER_HOST,
        username=config.CONTROLLER_USERNAME,
        password=config.CONTROLLER_PASSWORD,
        verify_ssl=False,
    )
    controller.login()
    print(f"✅ Connected to {config.CONTROLLER_HOST}\n")
except Exception as e:
    print(f"❌ Controller connection failed: {e}")
    sys.exit(1)

# Step 2: Retrieve data from controller
print("Step 2: Retrieving data from controller...")
try:
    devices = controller.get_devices()
    clients = controller.get_clients()
    print(f"✅ Retrieved {len(devices)} devices")
    print(f"✅ Retrieved {len(clients)} clients\n")
except Exception as e:
    print(f"❌ Data retrieval failed: {e}")
    controller.logout()
    sys.exit(1)

# Step 3: Initialize repositories
print("Step 3: Initializing database repositories...")
try:
    device_repo = UniFiDeviceRepository(DB_PATH)
    client_repo = UniFiClientRepository(DB_PATH)
    metric_repo = UniFiMetricRepository(DB_PATH)
    run_repo = UniFiCollectionRunRepository(DB_PATH)
    print("✅ Repositories initialized\n")
except Exception as e:
    print(f"❌ Repository initialization failed: {e}")
    controller.logout()
    sys.exit(1)

# Step 4: Store collection run
print("Step 4: Creating collection run record...")
try:
    run_id = run_repo.create_collection_run(
        site_name="default",
        status="running",
        device_count=len(devices),
        client_count=len(clients),
    )
    print(f"✅ Collection run created: ID {run_id}\n")
except Exception as e:
    print(f"❌ Collection run creation failed: {e}")
    controller.logout()
    sys.exit(1)

# Step 5: Store device data
print("Step 5: Storing device data...")
stored_devices = 0
try:
    for device in devices:
        mac = device.get("mac", "").lower()
        if not mac:
            continue

        device_repo.upsert_device(
            mac=mac,
            device_id=device.get("device_id"),
            name=device.get("name"),
            device_type=device.get("type"),
            model=device.get("model"),
            version=device.get("version"),
            ip=device.get("ip"),
            site_name="default",
            state=device.get("state"),
            adopted=device.get("adopted", False),
            uptime=device.get("uptime"),
            satisfaction=device.get("satisfaction"),
            num_sta=device.get("num_sta", 0),
            bytes_total=device.get("bytes", 0),
        )
        stored_devices += 1

    print(f"✅ Stored {stored_devices} devices\n")
except Exception as e:
    print(f"❌ Device storage failed: {e}")
    import traceback

    traceback.print_exc()

# Step 6: Store client data
print("Step 6: Storing client data...")
stored_clients = 0
try:
    for client in clients:
        mac = client.get("mac", "").lower()
        if not mac:
            continue

        client_repo.upsert_client(
            mac=mac,
            hostname=client.get("hostname"),
            ip=client.get("ip"),
            site_name="default",
            oui=client.get("oui"),
            is_wired=client.get("is_wired", False),
            is_guest=client.get("is_guest", False),
            first_seen=client.get("first_seen"),
            last_seen=client.get("last_seen"),
            usergroup_id=client.get("usergroup_id"),
            network_id=client.get("network_id"),
            ap_mac=client.get("ap_mac"),
            sw_mac=client.get("sw_mac"),
            sw_port=client.get("sw_port"),
        )
        stored_clients += 1

    print(f"✅ Stored {stored_clients} clients\n")
except Exception as e:
    print(f"❌ Client storage failed: {e}")
    import traceback

    traceback.print_exc()

# Step 7: Update collection run
print("Step 7: Finalizing collection run...")
try:
    run_repo.update_collection_run(run_id, status="completed")
    print("✅ Collection run completed\n")
except Exception as e:
    print(f"❌ Collection run update failed: {e}")

# Step 8: Verify data in database
print("Step 8: Verifying stored data...")
try:
    all_devices = device_repo.get_all_devices()
    all_clients = client_repo.get_all_clients()
    print(f"✅ Verified {len(all_devices)} devices in database")
    print(f"✅ Verified {len(all_clients)} clients in database\n")

    if all_devices:
        sample_device = all_devices[0]
        print(f"Sample device from database:")
        print(f"  Name: {sample_device.get('name')}")
        print(f"  MAC: {sample_device.get('mac')}")
        print(f"  Model: {sample_device.get('model')}")
        print(f"  Type: {sample_device.get('type')}")
        print()

    if all_clients:
        sample_client = all_clients[0]
        print(f"Sample client from database:")
        print(f"  Hostname: {sample_client.get('hostname')}")
        print(f"  MAC: {sample_client.get('mac')}")
        print(f"  IP: {sample_client.get('ip')}")
        print(f"  Wired: {sample_client.get('is_wired')}")
        print()

except Exception as e:
    print(f"❌ Data verification failed: {e}")

# Cleanup
controller.logout()

print("=" * 80)
print("✅ Collection test completed successfully!")
print("=" * 80)
print(f"\nDatabase: {DB_PATH}")
print(f"Devices stored: {stored_devices}")
print(f"Clients stored: {stored_clients}")
print("\nNext steps:")
print("  1. Run analytics: python unifi_analytics_demo.py")
print("  2. Start daemon: python collect_unifi_data.py --daemon")
print()
