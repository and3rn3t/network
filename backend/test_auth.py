"""Test authentication endpoints."""

import json

import requests

BASE_URL = "http://localhost:8000"


def test_login():
    """Test login with default admin credentials."""
    print("\n" + "=" * 70)
    print("🔐 Testing Login")
    print("=" * 70)

    # Default credentials
    login_data = {"username": "admin", "password": "admin123!"}

    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)

    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"   Username: {data['user']['username']}")
        print(f"   Email: {data['user']['email']}")
        print(f"   Is Superuser: {data['user']['is_superuser']}")
        print(f"   Token: {data['access_token'][:50]}...")
        print(f"   Expires in: {data['expires_in']} seconds")
        return data["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   {response.json()}")
        return None


def test_get_current_user(token):
    """Test getting current user info."""
    print("\n" + "=" * 70)
    print("👤 Testing Get Current User")
    print("=" * 70)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("✅ Got user info!")
        print(f"   ID: {data['id']}")
        print(f"   Username: {data['username']}")
        print(f"   Email: {data['email']}")
        print(f"   Full Name: {data['full_name']}")
        print(f"   Is Active: {data['is_active']}")
        print(f"   Created: {data['created_at']}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   {response.json()}")


def test_list_users(token):
    """Test listing all users (superuser only)."""
    print("\n" + "=" * 70)
    print("📋 Testing List Users")
    print("=" * 70)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/users", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data)} user(s)!")
        for user in data:
            print(f"   - {user['username']} ({user['email']})")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   {response.json()}")


def test_create_user(token):
    """Test creating a new user (superuser only)."""
    print("\n" + "=" * 70)
    print("➕ Testing Create User")
    print("=" * 70)

    headers = {"Authorization": f"Bearer {token}"}
    new_user = {
        "username": "testuser",
        "password": "testpass123!",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False,
    }

    response = requests.post(
        f"{BASE_URL}/api/auth/users", headers=headers, json=new_user
    )

    if response.status_code == 200:
        data = response.json()
        print("✅ User created successfully!")
        print(f"   ID: {data['id']}")
        print(f"   Username: {data['username']}")
        print(f"   Email: {data['email']}")
        return data["username"]
    elif response.status_code == 400:
        print("ℹ️  User already exists (expected on re-run)")
        return "testuser"
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   {response.json()}")
        return None


def test_login_new_user():
    """Test login with newly created user."""
    print("\n" + "=" * 70)
    print("🔐 Testing Login with New User")
    print("=" * 70)

    login_data = {"username": "testuser", "password": "testpass123!"}

    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)

    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"   Username: {data['user']['username']}")
        print(f"   Is Superuser: {data['user']['is_superuser']}")
        return data["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   {response.json()}")
        return None


def test_unauthorized_access():
    """Test accessing protected endpoint without token."""
    print("\n" + "=" * 70)
    print("🚫 Testing Unauthorized Access")
    print("=" * 70)

    response = requests.get(f"{BASE_URL}/api/auth/me")

    if response.status_code == 401:
        print("✅ Correctly rejected unauthorized request!")
        print(f"   Status: {response.status_code}")
    else:
        print(f"❌ Unexpected status: {response.status_code}")


def test_logout(token):
    """Test logout."""
    print("\n" + "=" * 70)
    print("👋 Testing Logout")
    print("=" * 70)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("✅ Logout successful!")
        print(f"   Message: {data['message']}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   {response.json()}")


def main():
    """Run all authentication tests."""
    print("\n" + "=" * 70)
    print("🧪 Authentication System Test Suite")
    print("=" * 70)

    # Test unauthorized access
    test_unauthorized_access()

    # Test admin login
    admin_token = test_login()
    if not admin_token:
        print("\n❌ Cannot continue without admin token")
        return

    # Test getting current user
    test_get_current_user(admin_token)

    # Test listing users
    test_list_users(admin_token)

    # Test creating new user
    test_create_user(admin_token)

    # Test logging in with new user
    user_token = test_login_new_user()

    # Test logout
    if user_token:
        test_logout(user_token)

    print("\n" + "=" * 70)
    print("✅ Authentication Test Suite Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("   Make sure the server is running: python backend/src/main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
