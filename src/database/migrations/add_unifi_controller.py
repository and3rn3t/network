"""
Database migration: Add UniFi Controller integration tables

This migration adds tables for UniFi local controller integration:
- unifi_devices: Network devices (switches, APs, gateways)
- unifi_device_status: Historical device status
- unifi_clients: Connected network clients
- unifi_client_status: Historical client status
- unifi_events: Events from controller
- unifi_device_metrics: Time-series metrics for devices
- unifi_client_metrics: Time-series metrics for clients
- unifi_collection_runs: Collection execution tracking
- Views for common queries

Version: 1.0
Created: October 20, 2025
"""

import sqlite3
from pathlib import Path
from typing import Optional


def apply_migration(db_path: Optional[Path] = None) -> None:
    """
    Apply UniFi Controller schema migration to database.
    
    Args:
        db_path: Path to database file (default: data/network_monitor.db)
    """
    if db_path is None:
        db_path = Path(__file__).parent.parent.parent.parent / "network_monitor.db"
    
    print(f"Applying UniFi Controller migration to: {db_path}")
    
    # Read schema SQL
    schema_path = Path(__file__).parent.parent / "schema_unifi_controller.sql"
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Execute schema
        print("Creating UniFi Controller tables...")
        cursor.executescript(schema_sql)
        conn.commit()
        print("✅ Migration applied successfully!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'unifi_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        print(f"\n📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Verify views were created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' AND name LIKE 'v_unifi_%'
            ORDER BY name
        """)
        views = cursor.fetchall()
        
        print(f"\n👁️ Created {len(views)} views:")
        for view in views:
            print(f"  - {view[0]}")
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def rollback_migration(db_path: Optional[Path] = None) -> None:
    """
    Rollback UniFi Controller schema migration.
    
    WARNING: This will delete all UniFi Controller data!
    
    Args:
        db_path: Path to database file (default: data/network_monitor.db)
    """
    if db_path is None:
        db_path = Path(__file__).parent.parent.parent.parent / "network_monitor.db"
    
    print(f"⚠️  Rolling back UniFi Controller migration from: {db_path}")
    print("⚠️  This will DELETE all UniFi Controller data!")
    
    response = input("Are you sure? Type 'yes' to confirm: ")
    if response.lower() != 'yes':
        print("Rollback cancelled.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Drop tables in reverse order (respecting foreign keys)
        tables = [
            'unifi_client_metrics',
            'unifi_device_metrics',
            'unifi_events',
            'unifi_client_status',
            'unifi_clients',
            'unifi_device_status',
            'unifi_devices',
            'unifi_collection_runs'
        ]
        
        views = [
            'v_unifi_network_topology',
            'v_unifi_recent_events',
            'v_unifi_client_connections',
            'v_unifi_device_uptime_stats',
            'v_unifi_latest_client_status',
            'v_unifi_latest_device_status'
        ]
        
        print("\nDropping views...")
        for view in views:
            cursor.execute(f"DROP VIEW IF EXISTS {view}")
            print(f"  - Dropped {view}")
        
        print("\nDropping tables...")
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"  - Dropped {table}")
        
        # Remove metadata
        cursor.execute("""
            DELETE FROM database_metadata 
            WHERE key IN ('unifi_controller_schema_version', 'unifi_controller_schema_added')
        """)
        
        conn.commit()
        print("\n✅ Rollback completed successfully!")
        
    except sqlite3.Error as e:
        print(f"❌ Rollback failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def check_migration_status(db_path: Optional[Path] = None) -> bool:
    """
    Check if UniFi Controller migration has been applied.
    
    Args:
        db_path: Path to database file (default: data/network_monitor.db)
        
    Returns:
        True if migration is applied, False otherwise
    """
    if db_path is None:
        db_path = Path(__file__).parent.parent.parent.parent / "network_monitor.db"
    
    if not db_path.exists():
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if unifi_devices table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='unifi_devices'
        """)
        result = cursor.fetchone()
        return result is not None
    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback_migration()
    elif len(sys.argv) > 1 and sys.argv[1] == 'status':
        status = check_migration_status()
        if status:
            print("✅ UniFi Controller migration is applied")
        else:
            print("❌ UniFi Controller migration is NOT applied")
    else:
        # Check status first
        if check_migration_status():
            print("ℹ️  UniFi Controller migration already applied")
            print("   Run with 'rollback' to remove it")
        else:
            apply_migration()
