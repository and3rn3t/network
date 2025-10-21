"""
Create Fresh UniFi Database

Creates a new database with all UniFi tables.
"""

import os
import sqlite3
import sys
from pathlib import Path

# Change to project root directory
os.chdir(Path(__file__).parent.parent)

print("\n" + "=" * 80)
print("  Creating Fresh UniFi Database")
print("=" * 80 + "\n")

# Use a new database name to avoid locks
db_path = "unifi_network.db"
base_schema_file = Path("src/database/schema.sql")
unifi_schema_file = Path("src/database/schema_unifi_controller.sql")

print(f"Creating new database: {db_path}\n")

# Read base schema
if not base_schema_file.exists():
    print(f"❌ Base schema file not found: {base_schema_file}")
    sys.exit(1)

with open(base_schema_file, "r", encoding="utf-8") as f:
    base_schema_sql = f.read()

print(f"✅ Loaded base schema ({len(base_schema_sql)} bytes)")

# Read UniFi schema
if not unifi_schema_file.exists():
    print(f"❌ UniFi schema file not found: {unifi_schema_file}")
    sys.exit(1)

with open(unifi_schema_file, "r", encoding="utf-8") as f:
    unifi_schema_sql = f.read()

print(f"✅ Loaded UniFi schema ({len(unifi_schema_sql)} bytes)\n")

try:
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Step 1: Creating base tables...")
    cursor.executescript(base_schema_sql)
    conn.commit()
    print("✅ Base schema applied\n")

    print("Step 2: Creating UniFi tables and views...")
    cursor.executescript(unifi_schema_sql)
    conn.commit()
    print("✅ UniFi schema applied\n")

    # Verify tables
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'unifi_%' ORDER BY name"
    )
    tables = cursor.fetchall()

    print(f"✅ Created {len(tables)} tables:")
    for (table_name,) in tables:
        print(f"   • {table_name}")

    # Verify views
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'v_%unifi%' ORDER BY name"
    )
    views = cursor.fetchall()

    if views:
        print(f"\n✅ Created {len(views)} views:")
        for (view_name,) in views:
            print(f"   • {view_name}")

    conn.close()

    print("\n" + "=" * 80)
    print("✅ Fresh database created successfully!")
    print("=" * 80)
    print(f"\nDatabase location: {db_path}")
    print("\nTo use this database, update your config.py:")
    print("  # Or set DATABASE_PATH in your collection script")
    print("\nOr run collection with custom DB:")
    print(f"  python collect_unifi_data.py --config config.py")
    print("\nNote: You can also rename this file to network_monitor.db")
    print(f"  after closing any programs using the old database.")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
