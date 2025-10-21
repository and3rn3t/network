"""
Safe Database Setup for UniFi Tables

Handles database locks gracefully and sets up UniFi tables.
"""

import sqlite3
import sys
import time
from pathlib import Path

print("\n" + "=" * 80)
print("  UniFi Database Setup")
print("=" * 80 + "\n")

db_path = "network_monitor.db"
schema_file = Path("src/database/schema_unifi_controller.sql")

# Check schema file
if not schema_file.exists():
    print(f"❌ Schema file not found: {schema_file}")
    sys.exit(1)

print(f"✅ Found schema file: {schema_file}")

# Read schema
with open(schema_file, "r", encoding="utf-8") as f:
    schema_sql = f.read()

print(f"✅ Loaded schema ({len(schema_sql)} bytes)\n")

# Try to connect with retry
max_retries = 3
retry_delay = 2

for attempt in range(max_retries):
    try:
        print(f"Attempt {attempt + 1}/{max_retries}: Connecting to {db_path}...")

        # Connect with a timeout
        conn = sqlite3.connect(db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")  # Use WAL mode to reduce locks

        print("✅ Connected successfully\n")

        # Check if tables already exist
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name LIKE 'unifi_%'"
        )
        existing_count = cursor.fetchone()[0]

        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing UniFi tables")
            response = input("Do you want to recreate them? (y/N): ").strip().lower()

            if response != "y":
                print("\n✅ Keeping existing tables")
                conn.close()
                sys.exit(0)

            # Drop existing tables
            print("\nDropping existing UniFi tables...")
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'unifi_%'"
            )
            tables = cursor.fetchall()
            for (table_name,) in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                print(f"  Dropped: {table_name}")

            # Drop existing views
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'v_%unifi%'"
            )
            views = cursor.fetchall()
            for (view_name,) in views:
                cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
                print(f"  Dropped: {view_name}")

            conn.commit()

        # Create tables
        print("\nCreating UniFi tables and views...")
        cursor.executescript(schema_sql)
        conn.commit()

        print("✅ Schema applied successfully\n")

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

        # Close connection
        conn.close()

        print("\n" + "=" * 80)
        print("✅ Database setup complete!")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Run collection: python collect_unifi_data.py --verbose")
        print("  2. Start daemon: python collect_unifi_data.py --daemon --interval 300")
        print("  3. View analytics: python unifi_analytics_demo.py")
        print()

        sys.exit(0)

    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            print(f"❌ Database is locked (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                print(f"   Waiting {retry_delay} seconds before retry...\n")
                time.sleep(retry_delay)
            else:
                print("\n" + "=" * 80)
                print("❌ Could not access database after multiple attempts")
                print("=" * 80)
                print("\nPossible solutions:")
                print("  1. Close any SQLite browser/viewer extensions in VS Code")
                print("  2. Close any other programs accessing the database")
                print("  3. Restart VS Code")
                print("  4. Run this script again")
                print()
                sys.exit(1)
        else:
            print(f"❌ Database error: {e}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
