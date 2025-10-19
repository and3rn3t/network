from src.database.database import Database

print("=== network_monitor.db ===")
db = Database("network_monitor.db")
cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

print("\n=== network.db ===")
db2 = Database("network.db")
cursor2 = db2.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables2 = [row[0] for row in cursor2.fetchall()]
print("Tables:", tables2)

if "hosts" in tables2:
    cursor = db2.execute("PRAGMA table_info(hosts)")
    columns = cursor.fetchall()
    print("\nHosts table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

    cursor = db2.execute("SELECT COUNT(*) FROM hosts")
    count = cursor.fetchone()[0]
    print(f"\nTotal hosts: {count}")
