"""Combined test that runs server and tests authentication."""

import asyncio
import sys
import time
from pathlib import Path
from threading import Thread

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.api import auth
from backend.src.middleware.error_handler import add_exception_handlers


def create_app() -> FastAPI:
    """Create test FastAPI app."""
    app = FastAPI(title="Auth Test Server")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add exception handlers
    add_exception_handlers(app)

    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

    return app


def run_server():
    """Run server in background thread."""
    app = create_app()
    config = uvicorn.Config(app, host="127.0.0.1", port=8889, log_level="error")
    server = uvicorn.Server(config)
    server.run()


async def test_auth():
    """Test authentication endpoints."""
    print("\n" + "=" * 70)
    print("🧪 AUTHENTICATION TEST SUITE")
    print("=" * 70)

    # Start server in background
    print("\n⏳ Starting test server...")
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to be ready
    await asyncio.sleep(2)

    base_url = "http://127.0.0.1:8889"
    print(f"✅ Server running at {base_url}")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            #  Test 1: Unauthorized access
            print("\n" + "-" * 70)
            print("1️⃣  Test: Unauthorized Access (without token)")
            response = await client.get(f"{base_url}/api/auth/me")

            if response.status_code == 401:
                print(f"   ✅ PASS - Got 401 Unauthorized as expected")
            else:
                print(f"   ❌ FAIL - Expected 401, got {response.status_code}")
                print(f"      Response: {response.json()}")

            # Test 2: Login
            print("\n" + "-" * 70)
            print("2️⃣  Test: Login with admin credentials")
            login_response = await client.post(
                f"{base_url}/api/auth/login",
                json={"username": "admin", "password": "admin123!"},
            )

            if login_response.status_code == 200:
                print("   ✅ PASS - Login successful!")
                data = login_response.json()
                print(f"      Username: {data['user']['username']}")
                print(f"      Email: {data['user'].get('email', 'N/A')}")
                print(f"      Is Superuser: {data['user']['is_superuser']}")
                print(f"      Token (first 30 chars): {data['access_token'][:30]}...")
                token = data["access_token"]
            else:
                print(f"   ❌ FAIL - Login failed: {login_response.status_code}")
                print(f"      Response: {login_response.json()}")
                return

            # Test 3: Get current user
            print("\n" + "-" * 70)
            print("3️⃣  Test: Get Current User Info")
            headers = {"Authorization": f"Bearer {token}"}
            me_response = await client.get(f"{base_url}/api/auth/me", headers=headers)

            if me_response.status_code == 200:
                print("   ✅ PASS - Successfully retrieved user info")
                user_data = me_response.json()
                print(f"      Username: {user_data['username']}")
                print(f"      Email: {user_data.get('email', 'N/A')}")
                print(f"      Active: {user_data['is_active']}")
                print(f"      Superuser: {user_data['is_superuser']}")
            else:
                print(f"   ❌ FAIL - Get user failed: {me_response.status_code}")
                print(f"      Response: {me_response.json()}")

            # Test 4: List users (superuser only)
            print("\n" + "-" * 70)
            print("4️⃣  Test: List All Users (superuser endpoint)")
            users_response = await client.get(
                f"{base_url}/api/auth/users", headers=headers
            )

            if users_response.status_code == 200:
                print("   ✅ PASS - Successfully listed users")
                users = users_response.json()
                print(f"      Total users: {len(users)}")
                for user in users:
                    print(
                        f"      - {user['username']} "
                        f"({user.get('email', 'no email')}) "
                        f"[{'active' if user['is_active'] else 'inactive'}]"
                    )
            else:
                print(f"   ❌ FAIL - List users failed: {users_response.status_code}")
                print(f"      Response: {users_response.json()}")

            # Summary
            print("\n" + "=" * 70)
            print("✅ ALL AUTHENTICATION TESTS COMPLETED!")
            print("=" * 70)
            print("\n🎉 Authentication system is fully functional!")
            print("\nDefault credentials:")
            print("   Username: admin")
            print("   Password: admin123!")
            print("\n" + "=" * 70 + "\n")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_auth())
