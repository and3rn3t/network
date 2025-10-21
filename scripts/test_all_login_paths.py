"""
Check if UDM/UDM-Pro has a different authentication mechanism.
Based on community reports, UDM might use different paths.
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


def test_endpoints():
    print("\n" + "=" * 80)
    print("  UDM/UDM-Pro Alternative Authentication Paths")
    print("=" * 80)

    base_url = f"https://{config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}"

    # Different possible login endpoints for UDM
    endpoints = [
        "/api/login",
        "/api/auth/login",
        "/proxy/network/api/login",
        "/api/s/default/cmd/login",
        "/auth/login",
    ]

    payload = {
        "username": config.CONTROLLER_USERNAME,
        "password": config.CONTROLLER_PASSWORD,
    }

    print(f"\n  Controller: {base_url}")
    print(f"  Username: {config.CONTROLLER_USERNAME}\n")

    for endpoint in endpoints:
        print(f"Testing: {endpoint}")

        session = requests.Session()
        session.verify = False
        session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        try:
            response = session.post(f"{base_url}{endpoint}", json=payload, timeout=30)

            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                print(f"  ✅ SUCCESS!")
                print(f"  Response: {response.text[:200]}")
                print(f"  Cookies: {dict(session.cookies)}")

                # Try to verify by getting devices
                print(f"\n  Verifying authentication with device list...")
                test_response = session.get(
                    f"{base_url}/api/s/default/stat/device", timeout=30
                )
                print(f"  Device list status: {test_response.status_code}")
                if test_response.status_code == 200:
                    print(f"  ✅ Authentication verified!")
                    return True
            else:
                print(f"  Response: {response.text[:100]}")

        except Exception as e:
            print(f"  Error: {str(e)[:80]}")

        print()

    print("=" * 80)
    print("  All endpoints failed")
    print("=" * 80)
    print("\n  This suggests the UDM might have:")
    print("  1. A different authentication mechanism")
    print("  2. API access disabled in settings")
    print("  3. Requires authentication via UI first (session-based)")
    print("\n  Please check:")
    print("  1. Settings → System → Advanced → Device Authentication")
    print("  2. Look for 'API' or 'Remote Access' settings")
    print("  3. Check if there's an 'API Key' option instead of user/pass")

    return False


if __name__ == "__main__":
    result = test_endpoints()
    sys.exit(0 if result else 1)
