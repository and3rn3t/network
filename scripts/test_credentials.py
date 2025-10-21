"""
Test UniFi controller credentials.
Helps verify username/password are correct.
"""

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


def main():
    print("\n" + "=" * 80)
    print("  UniFi Controller Credential Test")
    print("=" * 80)
    print(f"\n  Controller: https://{config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}")
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

    base_url = f"https://{config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}"
    login_endpoint = f"{base_url}/api/login"

    print("\n🔐 Testing login...")

    # Test the credentials
    payload = {
        "username": config.CONTROLLER_USERNAME,
        "password": config.CONTROLLER_PASSWORD,
    }

    try:
        response = session.post(login_endpoint, json=payload, timeout=30)

        print(f"  Response status: {response.status_code}")

        if response.status_code == 200:
            print("\n✅ SUCCESS! Credentials are correct!")
            print("\n  The UniFi controller authentication is working.")
            print("  You can now run: python quick_test_unifi.py")

            # Try to logout
            logout_endpoint = f"{base_url}/api/logout"
            session.post(logout_endpoint, timeout=30)
            return 0

        elif response.status_code == 401:
            print("\n❌ FAILED: Unauthorized (401)")
            print("\n  Possible issues:")
            print("  1. Username or password is incorrect")
            print("  2. Account is locked or disabled")
            print("  3. Two-factor authentication (2FA) is enabled")
            print("\n  To verify:")
            print(
                f"  1. Try logging into web UI: https://{config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}"
            )
            print("  2. Use the same username/password")
            print("  3. If 2FA is enabled, you may need an API token instead")
            return 1

        elif response.status_code == 400:
            print("\n❌ FAILED: Bad Request (400)")
            print("\n  The server didn't accept the credentials format.")
            print("  Response:", response.text[:200])
            return 1

        elif response.status_code == 404:
            print("\n❌ FAILED: Not Found (404)")
            print("\n  The login endpoint doesn't exist.")
            print("  This might not be a UniFi controller, or the port is wrong.")
            return 1

        else:
            print(f"\n❌ FAILED: Unexpected status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return 1

    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ CONNECTION ERROR: {str(e)[:100]}")
        print("\n  The controller is not accessible.")
        print("  Check:")
        print(f"  - Controller is running")
        print(f"  - IP address is correct: {config.CONTROLLER_HOST}")
        print(f"  - Port is correct: {config.CONTROLLER_PORT}")
        print(f"  - Firewall allows connection")
        return 1

    except requests.exceptions.Timeout:
        print("\n❌ TIMEOUT")
        print("  The controller didn't respond in time.")
        return 1

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
