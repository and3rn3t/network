"""
Try to mimic browser login behavior - get cookies first, then login.
"""

import sys

import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
    import config
except ImportError:
    print("❌ Error: config.py not found")
    sys.exit(1)


def main():
    print("\n" + "=" * 80)
    print("  Browser-Style Login Test")
    print("=" * 80)

    base_url = f"https://{config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}"

    session = requests.Session()
    session.verify = False

    print(f"\n  Controller: {base_url}")
    print(f"  Username: {config.CONTROLLER_USERNAME}")

    # Step 1: Visit the main page to get cookies
    print("\n📍 Step 1: Visiting main page to get cookies...")
    try:
        response = session.get(f"{base_url}/manage", timeout=30)
        print(f"  Status: {response.status_code}")
        print(f"  Cookies received: {list(session.cookies.keys())}")
    except Exception as e:
        print(f"  Error: {str(e)[:100]}")

    # Step 2: Try login with cookies
    print("\n🔐 Step 2: Attempting login with session cookies...")
    session.headers.update(
        {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Referer": f"{base_url}/manage",
        }
    )

    payload = {
        "username": config.CONTROLLER_USERNAME,
        "password": config.CONTROLLER_PASSWORD,
    }

    try:
        response = session.post(f"{base_url}/api/login", json=payload, timeout=30)

        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        print(f"  Cookies after login: {dict(session.cookies)}")

        if response.status_code == 200:
            print("\n✅ SUCCESS!")

            # Try to get devices to confirm we're logged in
            print("\n📱 Step 3: Testing authenticated request (get devices)...")
            response = session.get(f"{base_url}/api/s/default/stat/device", timeout=30)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                devices = data.get("data", [])
                print(f"  ✅ Got {len(devices)} devices!")

            return True
        else:
            print("\n❌ Login still failed")

    except Exception as e:
        print(f"  Error: {str(e)[:100]}")

    # Try one more thing - check if this needs the csrf token
    print("\n🔐 Step 3: Checking for CSRF token requirement...")

    # Get the manage page and look for CSRF token
    try:
        response = session.get(f"{base_url}/manage", timeout=30)
        if "csrf" in response.text.lower() or "x-csrf-token" in response.headers:
            print("  ⚠️  Controller might require CSRF token")
            print("  This is more complex and might need browser automation")
        else:
            print("  No CSRF token detected in response")
    except Exception as e:
        print(f"  Error: {str(e)[:100]}")

    return False


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
