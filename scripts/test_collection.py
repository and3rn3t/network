#!/usr/bin/env python3
"""Quick test of metrics collection."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.database import Database
from src.unifi_client import UniFiClient

try:
    import config
except ImportError:
    print("❌ Error: config.py not found")
    sys.exit(1)

print("🧪 Testing Metrics Collection Setup\n")
print("=" * 70)

# Test 1: Database connection
print("\n1️⃣ Testing Database Connection...")
try:
    db = Database()
    print(f"   ✅ Database: {db.db_path}")

    # Check hosts
    cursor = db.execute("SELECT COUNT(*) FROM hosts")
    host_count = cursor.fetchone()[0]
    print(f"   ✅ Hosts in database: {host_count}")

    # Check existing metrics
    cursor = db.execute("SELECT COUNT(*) FROM metrics")
    metrics_count = cursor.fetchone()[0]
    print(f"   ✅ Existing metrics: {metrics_count:,}")

except Exception as e:
    print(f"   ❌ Database error: {e}")
    sys.exit(1)

# Test 2: UniFi API connection
print("\n2️⃣ Testing UniFi API Connection...")
try:
    api_key = config.API_KEY
    base_url = getattr(config, "BASE_URL", "https://api.ui.com/v1")

    client = UniFiClient(api_key=api_key, base_url=base_url)
    print(f"   ✅ API Client created")
    print(f"   ✅ Base URL: {base_url}")

    # Try to fetch hosts
    hosts = client.get_hosts()
    print(f"   ✅ API accessible: {len(hosts)} host(s) found")

except Exception as e:
    print(f"   ❌ API error: {e}")
    sys.exit(1)

# Test 3: Check host MAC addresses match
print("\n3️⃣ Checking Host MAC Address Matching...")
try:
    # Get hosts from database
    cursor = db.execute("SELECT id, mac_address, name FROM hosts")
    db_hosts = cursor.fetchall()

    for db_host in db_hosts:
        host_id, mac, name = db_host
        print(f"\n   Database: {name or 'Unknown'}")
        print(f"   MAC: {mac}")

        # Try to find in API
        mac_normalized = mac.replace(":", "").lower() if mac else ""
        found = False

        for api_host in hosts:
            api_mac = api_host.get("mac", "").replace(":", "").lower()
            if api_mac == mac_normalized:
                found = True
                print(f"   ✅ Found in API!")
                print(f"   API Name: {api_host.get('name', 'N/A')}")
                break

        if not found:
            print(f"   ⚠️  Not found in API (MAC mismatch or offline)")
            print(f"   Expected MAC: {mac_normalized}")
            print(f"   API hosts MACs: {[h.get('mac', 'N/A') for h in hosts[:3]]}")

except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Collection readiness
print("\n4️⃣ Collection System Readiness...")
print("   ✅ Database connection: Working")
print("   ✅ UniFi API connection: Working")
print(f"   ✅ Devices to monitor: {host_count}")
print(f"   ✅ API devices available: {len(hosts)}")

print("\n" + "=" * 70)
print("✅ System is ready for metrics collection!")
print("\nNext steps:")
print("   1. Run: python collect_real_metrics.py")
print("   2. Choose option 3 for current + historical data")
print("   3. Or start continuous collection:")
print("      python start_metrics_collection.py")
print()

# Cleanup
db.close()
