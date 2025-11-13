"""Quick test to check database fetch methods."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.database import Database

db = Database('network_monitor.db')

# Test fetch_one
row = db.fetch_one('SELECT COUNT(*) as total FROM unifi_devices')
print(f"fetch_one() returns type: {type(row)}")
print(f"Row content: {row}")

if row:
    print(f"\nAccess by key 'total': {row['total']}")
    try:
        print(f"Access by index [0]: {row[0]}")
    except Exception as e:
        print(f"Access by index [0] failed: {e}")

# Test fetch_all
rows = db.fetch_all('SELECT id, name FROM unifi_devices LIMIT 2')
print(f"\nfetch_all() returns type: {type(rows)}")
if rows:
    print(f"First row type: {type(rows[0])}")
    print(f"First row content: {rows[0]}")
