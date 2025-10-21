"""
Quick port scanner to find UniFi controller.
Tests common UniFi controller ports and endpoints.
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


def test_port(host, port):
    """Test if a UniFi controller is accessible on the given port."""
    print(f"\n  Testing port {port}...")

    base_url = f"https://{host}:{port}"

    # Test endpoints
    endpoints = [
        "/api/login",  # Standard login
        "/manage",  # Web UI redirect
        "/",  # Root
    ]

    session = requests.Session()
    session.verify = False

    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = session.get(url, timeout=5, allow_redirects=False)

            if response.status_code in [200, 302, 400]:
                print(f"    ✅ {endpoint} - HTTP {response.status_code}")
                if endpoint == "/api/login" and response.status_code == 400:
                    print(f"       → Login endpoint exists (expecting POST)")
                    return True, port
                elif response.status_code in [200, 302]:
                    print(f"       → Endpoint accessible")
                    return True, port
            else:
                print(f"    ❌ {endpoint} - HTTP {response.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"    ❌ {endpoint} - Connection refused")
        except requests.exceptions.Timeout:
            print(f"    ⏱️  {endpoint} - Timeout")
        except Exception as e:
            print(f"    ❌ {endpoint} - {str(e)[:50]}")

    return False, None


def main():
    print("\n" + "=" * 80)
    print("  UniFi Controller Port Scanner")
    print("=" * 80)
    print(f"\n  Host: {config.CONTROLLER_HOST}")

    # Common UniFi controller ports
    ports_to_test = [
        8443,  # Default HTTPS port
        443,  # Alternative HTTPS port
        8080,  # HTTP redirect (some configs)
        8880,  # Alternative HTTP
    ]

    print(f"\n🔍 Scanning {len(ports_to_test)} common UniFi ports...")

    found_ports = []

    for port in ports_to_test:
        success, found_port = test_port(config.CONTROLLER_HOST, port)
        if success:
            found_ports.append(found_port)

    print("\n" + "=" * 80)
    print("  RESULTS")
    print("=" * 80)

    if found_ports:
        print(
            f"\n✅ Found UniFi controller on port(s): {', '.join(map(str, found_ports))}"
        )
        print("\n📝 Update config.py:")
        print(f"   CONTROLLER_PORT = {found_ports[0]}")

        if len(found_ports) > 1:
            print(f"\n   Alternative port(s): {', '.join(map(str, found_ports[1:]))}")
    else:
        print("\n❌ No UniFi controller found on common ports")
        print("\n   Troubleshooting:")
        print(f"   1. Verify controller is at {config.CONTROLLER_HOST}")
        print("   2. Check if controller is running")
        print("   3. Try accessing web UI manually")
        print("   4. Check firewall rules")
        print("   5. Verify you're on the same network")

    print()


if __name__ == "__main__":
    main()
