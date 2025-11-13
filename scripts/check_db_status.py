"""Quick script to check database status."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.database import Database

db_path = Path(__file__).parent.parent / "data" / "unifi_network.db"
db = Database(str(db_path))

print("Database Tables:")
tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for table in tables:
    print(f"  - {table[0]}")

print("\nDevice Count:")
try:
    count = db.execute("SELECT COUNT(*) FROM unifi_devices").fetchone()[0]
    print(f"  {count} devices")

    if count > 0:
        # Show sample device
        device = db.execute(
            "SELECT id, name, mac, model FROM unifi_devices LIMIT 1"
        ).fetchone()
        print(f"  Sample: {device}")
except Exception as e:
    print(f"  Error: {e}")

db.close()
