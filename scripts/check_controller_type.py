"""
Final diagnostic - checks if there are alternative login methods or admin panel access.
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
    print("  UniFi Controller Alternative Login Check")
    print("=" * 80)

    base_url = f"https://{config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}"

    session = requests.Session()
    session.verify = False

    print(f"\n  Testing: {base_url}\n")

    # Check what type of UniFi device this is
    endpoints_to_check = [
        ("/api/login", "Standard login"),
        ("/api/auth/login", "Alternative auth login"),
        ("/manage", "Management interface"),
        ("/proxy/network/api/login", "Proxy network login (UDM)"),
        ("/api/s/default/stat/device", "Device stats (requires auth)"),
    ]

    print("🔍 Checking available endpoints:\n")

    for endpoint, description in endpoints_to_check:
        try:
            url = f"{base_url}{endpoint}"
            response = session.get(url, timeout=5)

            status_icon = "✅" if response.status_code in [200, 302, 400, 401] else "❌"
            print(f"  {status_icon} {endpoint}")
            print(f"     {description}")
            print(f"     Status: {response.status_code}")

            if response.status_code == 302:
                location = response.headers.get("Location", "N/A")
                print(f"     Redirects to: {location}")

            if response.text and len(response.text) < 200:
                print(f"     Response: {response.text}")

            print()

        except Exception as e:
            print(f"  ❌ {endpoint}")
            print(f"     Error: {str(e)[:80]}")
            print()

    print("=" * 80)
    print("  IMPORTANT QUESTIONS:")
    print("=" * 80)
    print()
    print("  1. When you log into the web UI, do you:")
    print("     a) Enter username and password directly")
    print("     b) Click 'Sign in with Ubiquiti Account'")
    print("     c) Use Single Sign-On (SSO)")
    print()
    print("  2. Is this device a:")
    print("     a) UDM (UniFi Dream Machine)")
    print("     b) UDM-Pro")
    print("     c) Cloud Key")
    print("     d) Self-hosted controller on Windows/Linux/Mac")
    print()
    print("  3. In the web UI, go to Settings → Admins:")
    print("     - Is there an admin account with username 'and3rn3t'?")
    print("     - Does it show 'Local' or 'Ubiquiti Account'?")
    print("     - Does it have 'Super Administrator' role?")
    print()
    print("  4. Try this test:")
    print("     - Create a simple local admin: username='apitest', password='test123'")
    print("     - Give it Super Administrator role")
    print("     - Update config.py with these credentials")
    print("     - Run this test again")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
