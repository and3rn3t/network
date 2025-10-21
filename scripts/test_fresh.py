"""Test collection with custom database"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Temporarily override database path
import src.database.database as db_module
from src.collector.orchestrator import create_orchestrator_from_config_file

original_db_path = "network_monitor.db"
db_module.DEFAULT_DB_PATH = "test_fresh.db"

print("Testing collection with test_fresh.db\n")

orch = create_orchestrator_from_config_file("config.py")
print(f"Collectors: {orch.get_stats()['collectors_configured']}\n")

stats = orch.collect_all()

print("\n=== RESULTS ===")
if stats.get("unifi_stats"):
    u = stats["unifi_stats"]
    print(
        f"Devices: {u.get('devices_processed', 0)} processed, {u.get('devices_created', 0)} created"
    )
    print(
        f"Clients: {u.get('clients_processed', 0)} processed, {u.get('clients_created', 0)} created"
    )
    print(f"Duration: {stats['duration_seconds']:.2f}s")
else:
    print(f"No UniFi stats - errors: {stats['total_errors']}")

orch.close()
