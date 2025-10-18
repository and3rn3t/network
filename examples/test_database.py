"""
Test the database setup.

Simple script to initialize the database and verify it works.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import Database


def main():
    print("🚀 Testing Database Setup...")
    print()

    # Create database
    db = Database("data/unifi_network.db")

    print("📁 Database path:", db.db_path)
    print()

    # Initialize schema
    print("📝 Initializing schema...")
    db.initialize()
    print("✅ Schema initialized successfully!")
    print()

    # Get schema version
    version = db.get_schema_version()
    print(f"📊 Schema version: {version}")
    print()

    # Get database stats
    print("📈 Database Statistics:")
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()

    # Test a simple query
    print("🔍 Testing query...")
    result = db.fetch_one("SELECT datetime('now') as current_time")
    print(f"   Current database time: {result['current_time']}")
    print()

    # List all tables
    print("📋 Database Tables:")
    tables = db.fetch_all(
        """
        SELECT name FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """
    )
    for table in tables:
        print(f"   ✓ {table['name']}")
    print()

    # List all views
    print("👁️  Database Views:")
    views = db.fetch_all(
        """
        SELECT name FROM sqlite_master
        WHERE type='view'
        ORDER BY name
    """
    )
    for view in views:
        print(f"   ✓ {view['name']}")
    print()

    print("🎉 Database setup test completed successfully!")
    print()
    print("Next steps:")
    print("  1. Create data models (Host, HostStatus, Event, Metric)")
    print("  2. Create repository classes (CRUD operations)")
    print("  3. Create data collector service")
    print("  4. Write comprehensive tests")

    db.close()


if __name__ == "__main__":
    main()
