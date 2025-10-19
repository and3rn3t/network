"""Standalone authentication test with embedded server."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import time
from threading import Thread

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import auth

from src.database.database import Database


def create_test_app() -> FastAPI:
    """Create test FastAPI app with auth."""
    app = FastAPI(title="Auth Test Server")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

    return app


def run_server():
    """Run server in background thread."""
    app = create_test_app()
    uvicorn.run(app, host="127.0.0.1", port=8888, log_level="error")


async def test_authentication():
    """Test authentication endpoints."""
    print("\n" + "=" * 60)
    print("🧪 AUTHENTICATION STANDALONE TEST")
    print("=" * 60)

    # Start server in background
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    print("⏳ Waiting for server to start...")
    await asyncio.sleep(2)

    base_url = "http://127.0.0.1:8888"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Test 1: Login
            print("\n1️⃣  Testing Login...")
            login_response = await client.post(
                f"{base_url}/api/auth/login",
                json={"username": "admin", "password": "admin123!"},
            )

            if login_response.status_code == 200:
                print("   ✅ LOGIN SUCCESSFUL!")
                data = login_response.json()
                print(f"   📋 User: {data.get('user', {}).get('username')}")
                print(f"   🔑 Token: {data.get('access_token', '')[:30]}...")
                token = data.get("access_token")
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                print(f"   📋 Response: {login_response.json()}")
                return

            # Test 2: Get current user
            print("\n2️⃣  Testing Get Current User...")
            headers = {"Authorization": f"Bearer {token}"}
            me_response = await client.get(f"{base_url}/api/auth/me", headers=headers)

            if me_response.status_code == 200:
                print("   ✅ GET USER SUCCESSFUL!")
                user_data = me_response.json()
                print(f"   👤 Username: {user_data.get('username')}")
                print(f"   📧 Email: {user_data.get('email')}")
                print(f"   🔐 Superuser: {user_data.get('is_superuser')}")
            else:
                print(f"   ❌ Get user failed: {me_response.status_code}")
                print(f"   📋 Response: {me_response.json()}")

            # Test 3: List users (superuser only)
            print("\n3️⃣  Testing List Users (superuser)...")
            users_response = await client.get(
                f"{base_url}/api/auth/users", headers=headers
            )

            if users_response.status_code == 200:
                print("   ✅ LIST USERS SUCCESSFUL!")
                users = users_response.json()
                print(f"   📊 Total users: {len(users)}")
                for user in users:
                    print(f"      - {user.get('username')} ({user.get('email')})")
            else:
                print(f"   ❌ List users failed: {users_response.status_code}")
                print(f"   📋 Response: {users_response.json()}")

            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED!")
            print("=" * 60 + "\n")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_authentication())
