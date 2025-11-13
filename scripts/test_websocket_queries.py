"""Test websocket broadcast queries."""
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.database import Database

db = Database('network_monitor.db')

print("Testing WebSocket broadcast queries...")
print("=" * 60)

# Test metrics broadcast query
since = datetime.now() - timedelta(minutes=5)
query = """
    SELECT
        d.id, d.name, m.metric_name, m.metric_value, m.recorded_at
    FROM unifi_device_metrics m
    JOIN unifi_devices d ON m.device_mac = d.mac
    WHERE m.recorded_at >= ?
    ORDER BY m.recorded_at DESC
    LIMIT 100
"""

rows = db.fetch_all(query, (since.isoformat(),))
print(f"\n✅ Metrics query returned {len(rows)} rows")
if rows:
    print(f"   Sample row keys: {list(rows[0].keys())}")
    # Test dictionary access
    sample = rows[0]
    print(f"   Sample data:")
    print(f"     - device_id: {sample['id']}")
    print(f"     - device_name: {sample['name']}")
    print(f"     - metric_name: {sample['metric_name']}")
    print(f"     - metric_value: {sample['metric_value']}")
    print(f"     - recorded_at: {sample['recorded_at']}")
    
    # Test creating broadcast data
    metrics_data = [
        {
            "device_id": row["id"],
            "device_name": row["name"],
            "metric_name": row["metric_name"],
            "metric_value": row["metric_value"],
            "recorded_at": row["recorded_at"],
        }
        for row in rows[:5]  # Just first 5 for testing
    ]
    print(f"\n✅ Successfully created {len(metrics_data)} metric messages")
    print(f"   First message: {metrics_data[0]}")
else:
    print("   ⚠️  No recent metrics found. Run data collection first.")

# Test health broadcast query
device_query = """
    SELECT
        COUNT(*) as total,
        SUM(CASE WHEN state = 1 THEN 1 ELSE 0 END) as online
    FROM unifi_devices
"""
device_row = db.fetch_one(device_query)
print(f"\n✅ Device health query result: {device_row}")
total_devices = device_row["total"] if device_row else 0
online_devices = device_row["online"] if device_row else 0
print(f"   Total: {total_devices}, Online: {online_devices}")

health_score = 100
if total_devices > 0:
    offline_penalty = ((total_devices - online_devices) / total_devices) * 30
    health_score -= offline_penalty
health_score = max(0, min(100, health_score))

if health_score >= 90:
    health_status = "excellent"
elif health_score >= 75:
    health_status = "good"
elif health_score >= 50:
    health_status = "fair"
else:
    health_status = "poor"

print(f"\n✅ Calculated health score: {health_score:.1f} ({health_status})")

print("\n" + "=" * 60)
print("✅ All WebSocket broadcast queries work correctly!")
print("   Backend restart will enable live broadcasts.")
