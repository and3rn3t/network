"""
Enhanced UniFi login diagnostic - tries different authentication methods.
"""

import json
import sys

import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
    import config
except ImportError:
    print("❌ Error: config.py not found")
    sys.exit(1)


def test_login_method(session, base_url, username, password, method_name, payload):
    """Test a specific login method."""
    print(f"\n  Method {method_name}:")
    print(f"    Payload: {json.dumps(payload, indent=6)}")

    try:
        response = session.post(f"{base_url}/api/login", json=payload, timeout=30)

        print(f"    Status: {response.status_code}")

        if response.status_code == 200:
            print(f"    ✅ SUCCESS!")
            return True
        else:
            print(f"    ❌ Failed")
            if response.text:
                print(f"    Response: {response.text[:200]}")

        return False

    except Exception as e:
        print(f"    ❌ Error: {str(e)[:100]}")
        return False


def main():
    print("\n" + "=" * 80)
    print("  UniFi Controller Enhanced Login Test")
    print("=" * 80)

    base_url = f"https://{config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}"
    print(f"\n  Controller: {base_url}")
    print(f"  Username: {config.CONTROLLER_USERNAME}")
    print(f"  Password: {'*' * len(config.CONTROLLER_PASSWORD)}")

    session = requests.Session()
    session.verify = False
    session.headers.update(
        {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )

    print("\n🔐 Testing different login methods...\n")

    # Method 1: Standard username/password
    if test_login_method(
        session,
        base_url,
        config.CONTROLLER_USERNAME,
        config.CONTROLLER_PASSWORD,
        "1 - Standard",
        {
            "username": config.CONTROLLER_USERNAME,
            "password": config.CONTROLLER_PASSWORD,
        },
    ):
        print("\n✅ Login successful with Method 1!")
        return 0

    # Method 2: With remember flag
    if test_login_method(
        session,
        base_url,
        config.CONTROLLER_USERNAME,
        config.CONTROLLER_PASSWORD,
        "2 - With remember flag",
        {
            "username": config.CONTROLLER_USERNAME,
            "password": config.CONTROLLER_PASSWORD,
            "remember": True,
        },
    ):
        print("\n✅ Login successful with Method 2!")
        return 0

    # Method 3: With strict flag
    if test_login_method(
        session,
        base_url,
        config.CONTROLLER_USERNAME,
        config.CONTROLLER_PASSWORD,
        "3 - With strict flag",
        {
            "username": config.CONTROLLER_USERNAME,
            "password": config.CONTROLLER_PASSWORD,
            "strict": True,
        },
    ):
        print("\n✅ Login successful with Method 3!")
        return 0

    # Method 4: Try as form data instead of JSON
    print(f"\n  Method 4 - Form Data:")
    try:
        session.headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        response = session.post(
            f"{base_url}/api/login",
            data={
                "username": config.CONTROLLER_USERNAME,
                "password": config.CONTROLLER_PASSWORD,
            },
            timeout=30,
        )
        print(f"    Status: {response.status_code}")

        if response.status_code == 200:
            print(f"    ✅ SUCCESS!")
            return 0
        else:
            print(f"    ❌ Failed")
            if response.text:
                print(f"    Response: {response.text[:200]}")
    except Exception as e:
        print(f"    ❌ Error: {str(e)[:100]}")

    # Check what the server actually says
    print("\n" + "=" * 80)
    print("  Checking server response details...")
    print("=" * 80)

    session.headers.update(
        {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )

    response = session.post(
        f"{base_url}/api/login",
        json={
            "username": config.CONTROLLER_USERNAME,
            "password": config.CONTROLLER_PASSWORD,
        },
        timeout=30,
    )

    print(f"\n  Status Code: {response.status_code}")
    print(f"  Headers: {dict(response.headers)}")
    print(f"  Response Body: {response.text}")
    print(f"  Cookies: {session.cookies.get_dict()}")

    print("\n" + "=" * 80)
    print("  All methods failed")
    print("=" * 80)
    print("\n  Possible issues:")
    print("  1. The password might have special characters that need escaping")
    print("  2. The account might not have API access permissions")
    print("  3. The controller might have API access disabled")
    print("  4. The account might require 2FA (check web UI login)")
    print("\n  Try:")
    print("  1. Log into web UI to verify credentials work there")
    print("  2. Check if there's a 2FA prompt when you log in")
    print("  3. Verify the account has 'Super Administrator' role")
    print("  4. Try creating a new local admin without special characters in password")

    return 1


if __name__ == "__main__":
    sys.exit(main())
