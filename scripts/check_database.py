"""Check database status and available data."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.database import Database

# Try main database path
db_path = Path(__file__).parent.parent / "network_monitor.db"
if not db_path.exists():
    db_path = Path(__file__).parent.parent / "network.db"

if not db_path.exists():
    print("❌ Database not found!")
    print(f"   Looked for: {db_path}")
    print("\n💡 Run data collection first:")
    print("   python collect_unifi_data.py")
    sys.exit(1)

print(f"✅ Found database: {db_path}")
db = Database(str(db_path))

# Check tables
print("\n📊 Database Tables:")
tables = db.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()
for table in tables:
    count = db.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
    print(f"   • {table[0]}: {count} rows")

# Check hosts
print("\n🖥️  Devices (hosts):")
hosts = db.execute(
    "SELECT id, mac_address, name, model, ip_address FROM hosts LIMIT 5"
).fetchall()
if hosts:
    for host in hosts:
        print(f"   • {host[2] or 'Unknown'} ({host[3]}) - {host[4]}")
else:
    print("   ⚠️  No devices found - run data collection")

# Check clients
print("\n📱 Clients:")
clients_count = db.execute("SELECT COUNT(*) FROM unifi_clients").fetchone()[0]
print(f"   Total: {clients_count}")
if clients_count > 0:
    sample_clients = db.execute(
        "SELECT hostname, name, ip, signal_strength FROM unifi_clients LIMIT 3"
    ).fetchall()
    for client in sample_clients:
        print(
            f"   • {client[0] or client[1] or 'Unknown'} - {client[2]} ({client[3]} dBm)"
        )

# Check metrics
print("\n📈 Metrics:")
metrics_count = db.execute("SELECT COUNT(*) FROM unifi_metrics").fetchone()[0]
print(f"   Total metric records: {metrics_count}")

if metrics_count == 0:
    print("\n⚠️  No data found!")
    print("\n🔧 To populate the database with real UniFi data:")
    print("   1. Edit config.py with your UniFi controller credentials")
    print("   2. Run: python collect_unifi_data.py")
    print("   3. Backend will then serve real data to frontend")
else:
    print("\n✅ Database has data! Frontend should display real information.")

db.close()
