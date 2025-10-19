"""Simple login test to verify authentication works."""

import requests

BASE_URL = "http://localhost:8000"

print("\n🔐 Testing Login...")
print("=" * 50)

# Test login
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": "admin", "password": "admin123!"}
)

if response.status_code == 200:
    data = response.json()
    print("✅ LOGIN SUCCESSFUL!")
    print(f"   Username: {data['user']['username']}")
    print(f"   Email: {data['user']['email']}")
    print(f"   Is Superuser: {data['user']['is_superuser']}")
    print(f"   Token (first 50 chars): {data['access_token'][:50]}...")
    print("\n🎉 Authentication system is working!")
else:
    print(f"❌ Login failed: {response.status_code}")
    print(f"   Response: {response.json()}")

print("=" * 50 + "\n")
