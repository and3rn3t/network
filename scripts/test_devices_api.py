"""Test the devices API endpoint directly."""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.database import Database

# Test the query that the API uses
db = Database("network_monitor.db")

query = """
    SELECT
        d.id,
        d.mac,
        d.name,
        d.model,
        d.type,
        d.ip,
        COALESCE(ds.state, 'unknown') as status,
        d.version,
        COALESCE(ds.uptime, 0) as uptime,
        d.last_seen,
        d.site_name
    FROM unifi_devices d
    LEFT JOIN unifi_device_status ds ON d.mac = ds.device_mac
        AND ds.recorded_at = (
            SELECT MAX(recorded_at) FROM unifi_device_status WHERE device_mac = d.mac
        )
    WHERE 1=1
    LIMIT 100 OFFSET 0
"""

print("Executing query...")
try:
    cursor = db.execute(query)
    rows = cursor.fetchall()
    print(f"\n✅ Query successful! Found {len(rows)} devices\n")

    if rows:
        print("First device:")
        row = rows[0]
        device = {
            "id": row[0],
            "mac": row[1],
            "name": row[2] or "Unknown",
            "model": row[3],
            "type": row[4],
            "ip": row[5],
            "status": row[6] if row[6] in ["online", "offline"] else "online",
            "version": row[7],
            "uptime": row[8],
            "last_seen": row[9],
            "site_name": row[10],
        }
        for key, value in device.items():
            print(f"  {key}: {value}")
    else:
        print("⚠️ No devices found in database")

except Exception as e:
    print(f"❌ Query failed: {e}")
    import traceback

    traceback.print_exc()
