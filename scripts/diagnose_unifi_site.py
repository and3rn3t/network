"""
Diagnostic script to find the correct UniFi site name.

This will attempt to login and list all available sites to help you
find the correct site identifier to use in config.py.
"""

import sys

import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
    import config
except ImportError:
    print("❌ Error: config.py not found")
    sys.exit(1)


def main():
    print("\n" + "=" * 80)
    print("  UniFi Controller Site Diagnostic")
    print("=" * 80)
    print(f"\n  Controller: {config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}")

    # Create a session
    session = requests.Session()
    session.verify = False
    session.headers.update(
        {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )

    base_url = f"https://{config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}"

    # Try to login
    print("\n🔐 Attempting to login...")
    login_endpoint = f"{base_url}/api/login"
    payload = {
        "username": config.CONTROLLER_USERNAME,
        "password": config.CONTROLLER_PASSWORD,
    }

    try:
        response = session.post(login_endpoint, json=payload, timeout=30)
        print(f"  Login response status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Login successful!")

            # Now try to get sites using the default site path
            print("\n📍 Fetching sites list...")

            # Try method 1: /api/self/sites (works on most controllers)
            sites_endpoint = f"{base_url}/api/self/sites"
            response = session.get(sites_endpoint, timeout=30)

            if response.status_code == 200:
                data = response.json()
                sites = data.get("data", [])

                if sites:
                    print(f"✅ Found {len(sites)} site(s):\n")
                    for i, site in enumerate(sites, 1):
                        name = site.get("name", "unknown")
                        desc = site.get("desc", "No description")
                        site_id = site.get("_id", "unknown")
                        role = site.get("role", "unknown")

                        print(f"  {i}. Site Name: '{name}'")
                        print(f"     Description: {desc}")
                        print(f"     ID: {site_id}")
                        print(f"     Role: {role}")
                        print()

                    # Recommend which one to use
                    print("=" * 80)
                    print("📝 CONFIGURATION RECOMMENDATION:")
                    print("=" * 80)

                    if len(sites) == 1:
                        recommended = sites[0].get("name", "default")
                        print(f"\nUpdate config.py with:")
                        print(f"  CONTROLLER_SITE = '{recommended}'")
                    else:
                        print(
                            "\nYou have multiple sites. Choose one and update config.py:"
                        )
                        for site in sites:
                            name = site.get("name", "unknown")
                            desc = site.get("desc", "No description")
                            print(f"  CONTROLLER_SITE = '{name}'  # {desc}")

                    print("\nNote: Use the 'name' value, not the description!")
                    print()
                else:
                    print("⚠️  No sites found (empty response)")
            else:
                print(f"❌ Failed to fetch sites: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")

            # Logout
            print("\n🚪 Logging out...")
            logout_endpoint = f"{base_url}/api/logout"
            session.post(logout_endpoint, timeout=30)
            print("✅ Logged out")

        elif response.status_code == 400:
            print("❌ Login failed: Bad request (check username/password)")
            print(f"   Response: {response.text[:200]}")
        elif response.status_code == 401:
            print("❌ Login failed: Unauthorized (wrong username/password)")
        elif response.status_code == 404:
            print("❌ Login endpoint not found (404)")
            print("\n   This could mean:")
            print("   1. Wrong controller IP address")
            print("   2. Wrong port (try 443 instead of 8443, or vice versa)")
            print("   3. Not a UniFi Network Controller at this address")
            print("\n   Try accessing the web UI manually:")
            print(f"   https://{config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}")
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")

    except requests.exceptions.ConnectTimeout:
        print("❌ Connection timeout")
        print("   - Check if controller is running")
        print("   - Verify the IP address and port")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {str(e)}")
        print("   - Check if controller is accessible")
        print("   - Verify firewall settings")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
