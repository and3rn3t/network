"""Diagnostic script to test database and user repository."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.src.database.user_repository import UserRepository
from src.database.database import Database


def test_database_connection():
    """Test database connection."""
    print("\n" + "=" * 60)
    print("🔍 Testing Database Connection")
    print("=" * 60)

    try:
        db = Database("../network_monitor.db")
        print("✅ Database instance created")

        conn = db.get_connection()
        print("✅ Database connection established")

        # Test a simple query
        cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tables in database")
        for table in tables[:5]:
            print(f"   - {table[0]}")

        return db
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback

        traceback.print_exc()
        return None


def test_user_repository(db):
    """Test user repository."""
    print("\n" + "=" * 60)
    print("🔍 Testing User Repository")
    print("=" * 60)

    try:
        repo = UserRepository(db)
        print("✅ UserRepository created")

        # Test getting admin user
        print("\n📝 Looking for admin user...")
        user = repo.get_by_username("admin")

        if user:
            print("✅ Found admin user!")
            print(f"   ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Is Superuser: {user.is_superuser}")
            print(f"   Is Active: {user.is_active}")
            return user
        else:
            print("❌ Admin user not found in database")
            print("\n📝 Listing all users...")
            users = repo.list_users()
            print(f"   Found {len(users)} user(s)")
            for u in users:
                print(f"   - {u.username} (ID: {u.id})")
            return None

    except Exception as e:
        print(f"❌ Repository error: {e}")
        import traceback

        traceback.print_exc()
        return None


def test_password_verification(user):
    """Test password verification."""
    print("\n" + "=" * 60)
    print("🔍 Testing Password Verification")
    print("=" * 60)

    try:
        from backend.src.services.auth_service import verify_password

        # Test with correct password
        correct = verify_password("admin123!", user.hashed_password)
        print(f"✅ Correct password: {correct}")

        # Test with wrong password
        wrong = verify_password("wrongpass", user.hashed_password)
        print(f"✅ Wrong password: {wrong}")

        return correct
    except Exception as e:
        print(f"❌ Password verification error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all diagnostic tests."""
    print("\n" + "=" * 60)
    print("🧪 Authentication Diagnostic Test")
    print("=" * 60)

    # Test database
    db = test_database_connection()
    if not db:
        print("\n❌ Cannot continue without database")
        return

    # Test user repository
    user = test_user_repository(db)
    if not user:
        print("\n❌ Cannot continue without admin user")
        return

    # Test password verification
    if test_password_verification(user):
        print("\n" + "=" * 60)
        print("✅ All diagnostic tests passed!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Password verification failed")
        print("=" * 60)


if __name__ == "__main__":
    main()
