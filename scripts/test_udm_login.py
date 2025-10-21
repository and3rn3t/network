"""
Test UDM-specific login endpoints.
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


def test_udm_login():
    print("\n" + "=" * 80)
    print("  Testing UDM/UDM-Pro Login")
    print("=" * 80)

    base_url = f"https://{config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}"

    session = requests.Session()
    session.verify = False
    session.headers.update(
        {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )

    print(f"\n  Controller: {base_url}")
    print(f"  Username: {config.CONTROLLER_USERNAME}")

    # Try the UDM proxy path
    print("\n🔐 Method 1: UDM Proxy Path (/proxy/network/api/login)")
    endpoint = "/proxy/network/api/login"
    payload = {
        "username": config.CONTROLLER_USERNAME,
        "password": config.CONTROLLER_PASSWORD,
    }

    try:
        response = session.post(f"{base_url}{endpoint}", json=payload, timeout=30)

        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")

        if response.status_code == 200:
            print("\n✅ SUCCESS! UDM proxy login works!")
            print("\nThis is a UDM/UDM-Pro device.")
            print("The UniFi controller code needs to be updated to use:")
            print("  endpoint = '/proxy/network/api/login'")
            return True

    except Exception as e:
        print(f"  Error: {str(e)}")

    # Try standard path again for comparison
    print("\n🔐 Method 2: Standard Path (/api/login)")
    endpoint = "/api/login"

    try:
        response = session.post(f"{base_url}{endpoint}", json=payload, timeout=30)

        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")

        if response.status_code == 200:
            print("\n✅ SUCCESS! Standard login works!")
            return True

    except Exception as e:
        print(f"  Error: {str(e)}")

    print("\n❌ Both methods failed")
    print("\nThe credentials might still be incorrect, or there might be:")
    print("  - 2FA enabled on the account")
    print("  - Account type mismatch (Ubiquiti Account vs Local)")
    print("  - API access restrictions")

    return False


if __name__ == "__main__":
    result = test_udm_login()
    sys.exit(0 if result else 1)
