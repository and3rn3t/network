"""Initialize authentication database tables."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.database import Database


def initialize_auth_tables():
    """Initialize authentication tables."""
    print("\n" + "=" * 60)
    print("🔧 Initializing Authentication Tables")
    print("=" * 60)

    db = Database("../network_monitor.db")
    schema_file = Path(__file__).parent / "src" / "database" / "auth_schema.sql"

    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        return False

    print(f"📄 Reading schema from: {schema_file}")

    with open(schema_file, "r") as f:
        schema = f.read()

    print(f"📝 Schema length: {len(schema)} characters")

    try:
        print("⚙️  Executing schema...")
        conn = db.get_connection()
        conn.executescript(schema)
        conn.commit()
        print("✅ Schema executed successfully!")

        # Verify tables were created
        cursor = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        result = cursor.fetchone()

        if result:
            print(f"✅ Users table created: {result[0]}")

            # Check if admin user exists
            cursor = db.execute("SELECT username FROM users WHERE username='admin'")
            admin = cursor.fetchone()

            if admin:
                print(f"✅ Admin user exists: {admin[0]}")
            else:
                print("⚠️  Admin user not found (will be created on first use)")

            return True
        else:
            print("❌ Users table was not created")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    if initialize_auth_tables():
        print("\n" + "=" * 60)
        print("✅ Authentication database initialized!")
        print("=" * 60 + "\n")
    else:
        print("\n" + "=" * 60)
        print("❌ Failed to initialize authentication database")
        print("=" * 60 + "\n")
