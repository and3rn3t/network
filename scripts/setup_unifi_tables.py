"""
Setup UniFi tables in database.

This script safely creates the UniFi Controller tables.
"""

import sys
from pathlib import Path

print("Setting up UniFi Controller database tables...")
print("=" * 80)

# Read the schema file
schema_file = Path("src/database/schema_unifi_controller.sql")

if not schema_file.exists():
    print(f"❌ Schema file not found: {schema_file}")
    sys.exit(1)

with open(schema_file, "r") as f:
    schema_sql = f.read()

print(f"✅ Loaded schema file ({len(schema_sql)} bytes)")

# Create database connection
import sqlite3

db_path = "network_monitor.db"
print(f"\nConnecting to database: {db_path}")

try:
    conn = sqlite3.connect(db_path, timeout=30.0)
    cursor = conn.cursor()

    print("✅ Connected to database")

    # Execute schema
    print("\nCreating UniFi tables...")
    cursor.executescript(schema_sql)
    conn.commit()

    print("✅ Tables created successfully")

    # Verify tables
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'unifi_%' ORDER BY name"
    )
    tables = cursor.fetchall()

    print(f"\n✅ Verified {len(tables)} UniFi tables:")
    for (table_name,) in tables:
        print(f"   • {table_name}")

    # Verify views
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'v_%unifi%' ORDER BY name"
    )
    views = cursor.fetchall()

    if views:
        print(f"\n✅ Verified {len(views)} UniFi views:")
        for (view_name,) in views:
            print(f"   • {view_name}")

    conn.close()

    print("\n" + "=" * 80)
    print("✅ Setup complete! UniFi Controller tables are ready.")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
