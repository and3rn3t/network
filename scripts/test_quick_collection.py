"""
Quick test of data collection to fresh database
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import shutil

# Change to parent directory so relative paths work
os.chdir(Path(__file__).parent.parent)

# First rename the database
if os.path.exists("unifi_network.db"):
    # Use the fresh database
    if os.path.exists("network_monitor.db.locked"):
        os.remove("network_monitor.db.locked")
    shutil.copy("unifi_network.db", "network_monitor.db")
    print("✅ Using fresh database as network_monitor.db\n")

# Now run collection
from src.collector.orchestrator import create_orchestrator_from_config_file

print("=" * 80)
print("  Testing Data Collection")
print("=" * 80)
print()

try:
    # Create orchestrator
    orchestrator = create_orchestrator_from_config_file("config.py")
    print("✅ Orchestrator created\n")

    # Run collection
    print("Running collection...")
    stats = orchestrator.collect_all()

    print("\n" + "=" * 80)
    print("  Collection Results")
    print("=" * 80)

    if stats.get("unifi_stats"):
        unifi = stats["unifi_stats"]
        print(f"\n🌐 UniFi Controller:")
        print(f"   Devices processed: {unifi.get('devices_processed', 0)}")
        print(f"   Devices created: {unifi.get('devices_created', 0)}")
        print(f"   Devices updated: {unifi.get('devices_updated', 0)}")
        print(f"   Clients processed: {unifi.get('clients_processed', 0)}")
        print(f"   Clients created: {unifi.get('clients_created', 0)}")
        print(f"   Clients updated: {unifi.get('clients_updated', 0)}")
        print(f"   Status records: {unifi.get('status_records', 0)}")
        print(f"   Events created: {unifi.get('events_created', 0)}")
        print(f"   Metrics created: {unifi.get('metrics_created', 0)}")

    print(f"\n⏱️  Duration: {stats.get('duration_seconds', 0):.2f}s")
    print(f"❌ Errors: {stats.get('total_errors', 0)}")

    orchestrator.close()

    print("\n" + "=" * 80)
    print("✅ Collection test completed successfully!")
    print("=" * 80)
    print("\nDatabase: network_monitor.db")
    print("\nNext steps:")
    print('  1. View data: sqlite3 network_monitor.db "SELECT * FROM unifi_devices;"')
    print("  2. Run analytics: python unifi_analytics_demo.py")
    print("  3. Start daemon: python collect_unifi_data.py --daemon")
    print()

except Exception as e:
    print(f"\n❌ Collection failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
