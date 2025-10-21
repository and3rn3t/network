"""
Test script for UniFi Controller API integration.

This script tests all device and client operations against a real UniFi controller.
Make sure to configure config.py with your controller details before running.

Usage:
    python test_unifi_integration.py
"""

import sys
from datetime import datetime
from typing import Any, Dict, List

# Import configuration
try:
    import config
except ImportError:
    print(
        "❌ Error: config.py not found. Copy config.example.py to config.py and configure it."
    )
    sys.exit(1)

# Import UniFi controller
try:
    from src.unifi_controller import UniFiController
except ImportError:
    print(
        "❌ Error: Cannot import UniFiController. Make sure src/unifi_controller.py exists."
    )
    sys.exit(1)


class TestResults:
    """Track test results."""

    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.results: List[Dict[str, Any]] = []

    def add_result(self, test_name: str, status: str, message: str = ""):
        """Add a test result."""
        self.total += 1
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "SKIP":
            self.skipped += 1

        self.results.append(
            {
                "test": test_name,
                "status": status,
                "message": message,
                "timestamp": datetime.now(),
            }
        )

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests:  {self.total}")
        print(f"✅ Passed:    {self.passed}")
        print(f"❌ Failed:    {self.failed}")
        print(f"⏭️  Skipped:   {self.skipped}")
        print(
            f"Success Rate: {(self.passed/self.total*100):.1f}%"
            if self.total > 0
            else "N/A"
        )
        print("=" * 80)

        if self.failed > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if result["status"] == "FAIL":
                    print(f"  ❌ {result['test']}: {result['message']}")

        print()


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_test(name: str, status: str, message: str = ""):
    """Print a test result."""
    icons = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "INFO": "ℹ️"}
    icon = icons.get(status, "•")
    if message:
        print(f"{icon} {name}: {message}")
    else:
        print(f"{icon} {name}")


def test_connection(controller: UniFiController, results: TestResults) -> bool:
    """Test basic connection to controller."""
    print_section("Connection Tests")

    try:
        if controller.test_connection():
            print_test("Controller Connection", "PASS", "Successfully connected")
            results.add_result("Connection Test", "PASS")
            return True
        else:
            print_test("Controller Connection", "FAIL", "Connection test failed")
            results.add_result("Connection Test", "FAIL", "Connection returned False")
            return False
    except Exception as e:
        print_test("Controller Connection", "FAIL", f"Error: {str(e)}")
        results.add_result("Connection Test", "FAIL", str(e))
        return False


def test_authentication(controller: UniFiController, results: TestResults) -> bool:
    """Test authentication."""
    print_section("Authentication Tests")

    try:
        controller.login()
        print_test("Login", "PASS", "Successfully authenticated")
        results.add_result("Login Test", "PASS")
        return True
    except Exception as e:
        print_test("Login", "FAIL", f"Error: {str(e)}")
        results.add_result("Login Test", "FAIL", str(e))
        return False


def test_site_operations(controller: UniFiController, results: TestResults):
    """Test site operations."""
    print_section("Site Operations")

    try:
        sites = controller.get_sites()
        print_test("Get Sites", "PASS", f"Found {len(sites)} sites")
        results.add_result("Get Sites", "PASS")

        if sites:
            print(f"\n  Available sites:")
            for site in sites[:5]:  # Show first 5
                name = site.get("name", "unknown")
                desc = site.get("desc", "No description")
                print(f"    • {name}: {desc}")
            if len(sites) > 5:
                print(f"    ... and {len(sites) - 5} more")
    except Exception as e:
        print_test("Get Sites", "FAIL", f"Error: {str(e)}")
        results.add_result("Get Sites", "FAIL", str(e))


def test_device_listing(
    controller: UniFiController, results: TestResults
) -> List[Dict]:
    """Test device listing."""
    print_section("Device Listing")

    try:
        devices = controller.get_devices()
        print_test("Get Devices", "PASS", f"Found {len(devices)} devices")
        results.add_result("Get Devices", "PASS")

        if devices:
            print(f"\n  Devices found:")
            for device in devices[:5]:  # Show first 5
                mac = device.get("mac", "unknown")
                name = device.get("name", "Unnamed")
                model = device.get("model", "Unknown")
                state = device.get("state", 0)
                status = "🟢 Online" if state == 1 else "🔴 Offline"
                print(f"    • {name} ({model}) - MAC: {mac} - {status}")
            if len(devices) > 5:
                print(f"    ... and {len(devices) - 5} more")
        else:
            print(f"  ⚠️  No devices found")

        return devices
    except Exception as e:
        print_test("Get Devices", "FAIL", f"Error: {str(e)}")
        results.add_result("Get Devices", "FAIL", str(e))
        return []


def test_client_listing(
    controller: UniFiController, results: TestResults
) -> List[Dict]:
    """Test client listing."""
    print_section("Client Listing")

    try:
        clients = controller.get_clients()
        print_test("Get Clients", "PASS", f"Found {len(clients)} clients")
        results.add_result("Get Clients", "PASS")

        if clients:
            print(f"\n  Clients found:")
            for client in clients[:5]:  # Show first 5
                mac = client.get("mac", "unknown")
                hostname = client.get("hostname", client.get("name", "Unknown"))
                ip = client.get("ip", "No IP")
                print(f"    • {hostname} - MAC: {mac} - IP: {ip}")
            if len(clients) > 5:
                print(f"    ... and {len(clients) - 5} more")
        else:
            print(f"  ⚠️  No active clients found")

        return clients
    except Exception as e:
        print_test("Get Clients", "FAIL", f"Error: {str(e)}")
        results.add_result("Get Clients", "FAIL", str(e))
        return []


def test_device_operations(
    controller: UniFiController,
    devices: List[Dict],
    results: TestResults,
    interactive: bool = True,
):
    """Test device operations (interactive mode)."""
    print_section("Device Operations")

    if not devices:
        print_test("Device Operations", "SKIP", "No devices available for testing")
        results.add_result("Device Operations", "SKIP", "No devices")
        return

    # Select a test device
    print("  Available devices for testing:")
    for i, device in enumerate(devices[:10]):
        name = device.get("name", "Unnamed")
        model = device.get("model", "Unknown")
        mac = device.get("mac", "unknown")
        print(f"    {i+1}. {name} ({model}) - {mac}")

    if interactive:
        try:
            choice = input("\n  Enter device number to test (or 0 to skip): ")
            choice = int(choice)
            if choice == 0:
                print_test("Device Operations", "SKIP", "Skipped by user")
                results.add_result("Device Operations", "SKIP", "User skipped")
                return
            if choice < 1 or choice > len(devices):
                print_test("Device Operations", "FAIL", "Invalid choice")
                results.add_result(
                    "Device Operations", "FAIL", "Invalid device selection"
                )
                return

            test_device = devices[choice - 1]
            mac = test_device.get("mac")
            name = test_device.get("name", "Unnamed")

            print(f"\n  Testing with device: {name} ({mac})")

            # Test get_device
            print("\n  Testing get_device()...")
            try:
                device_info = controller.get_device(mac)
                if device_info:
                    print_test("Get Device by MAC", "PASS", f"Retrieved device info")
                    results.add_result("Get Device by MAC", "PASS")
                else:
                    print_test("Get Device by MAC", "FAIL", "No device info returned")
                    results.add_result("Get Device by MAC", "FAIL", "Empty response")
            except Exception as e:
                print_test("Get Device by MAC", "FAIL", str(e))
                results.add_result("Get Device by MAC", "FAIL", str(e))

            # Test get_device_statistics
            print("\n  Testing get_device_statistics()...")
            try:
                stats = controller.get_device_statistics(mac)
                if stats:
                    print_test(
                        "Get Device Statistics", "PASS", "Retrieved device statistics"
                    )
                    results.add_result("Get Device Statistics", "PASS")

                    # Show some stats
                    if "sys_stats" in stats:
                        sys_stats = stats["sys_stats"]
                        cpu = sys_stats.get("cpu", "N/A")
                        mem = sys_stats.get("mem", "N/A")
                        print(f"    CPU: {cpu}%, Memory: {mem}%")
                else:
                    print_test("Get Device Statistics", "FAIL", "No stats returned")
                    results.add_result(
                        "Get Device Statistics", "FAIL", "Empty response"
                    )
            except Exception as e:
                print_test("Get Device Statistics", "FAIL", str(e))
                results.add_result("Get Device Statistics", "FAIL", str(e))

            # Ask about locate test
            locate_test = input("\n  Test locate (LED blink) on this device? (y/N): ")
            if locate_test.lower() == "y":
                try:
                    controller.locate_device(mac, enable=True)
                    print_test(
                        "Locate Device",
                        "PASS",
                        "Locate command sent (check device LED)",
                    )
                    results.add_result("Locate Device", "PASS")

                    input("  Press Enter after verifying LED is blinking...")

                    # Disable locate
                    controller.locate_device(mac, enable=False)
                    print("  Locate disabled")
                except Exception as e:
                    print_test("Locate Device", "FAIL", str(e))
                    results.add_result("Locate Device", "FAIL", str(e))
            else:
                print_test("Locate Device", "SKIP", "Skipped by user")
                results.add_result("Locate Device", "SKIP", "User skipped")

        except ValueError:
            print_test("Device Operations", "FAIL", "Invalid input")
            results.add_result("Device Operations", "FAIL", "Invalid input")
        except KeyboardInterrupt:
            print("\n  Test interrupted by user")
            results.add_result("Device Operations", "SKIP", "Interrupted")
    else:
        print_test("Device Operations", "SKIP", "Non-interactive mode")
        results.add_result("Device Operations", "SKIP", "Non-interactive")


def test_client_operations(
    controller: UniFiController,
    clients: List[Dict],
    results: TestResults,
    interactive: bool = True,
):
    """Test client operations (interactive mode)."""
    print_section("Client Operations")

    if not clients:
        print_test("Client Operations", "SKIP", "No clients available for testing")
        results.add_result("Client Operations", "SKIP", "No clients")
        return

    # Select a test client
    print("  Available clients for testing:")
    for i, client in enumerate(clients[:10]):
        hostname = client.get("hostname", client.get("name", "Unknown"))
        mac = client.get("mac", "unknown")
        ip = client.get("ip", "No IP")
        print(f"    {i+1}. {hostname} - {mac} - {ip}")

    if interactive:
        try:
            choice = input("\n  Enter client number to test (or 0 to skip): ")
            choice = int(choice)
            if choice == 0:
                print_test("Client Operations", "SKIP", "Skipped by user")
                results.add_result("Client Operations", "SKIP", "User skipped")
                return
            if choice < 1 or choice > len(clients):
                print_test("Client Operations", "FAIL", "Invalid choice")
                results.add_result(
                    "Client Operations", "FAIL", "Invalid client selection"
                )
                return

            test_client = clients[choice - 1]
            mac = test_client.get("mac")
            hostname = test_client.get("hostname", test_client.get("name", "Unknown"))

            print(f"\n  Testing with client: {hostname} ({mac})")

            # Test get_client
            print("\n  Testing get_client()...")
            try:
                client_info = controller.get_client(mac)
                if client_info:
                    print_test("Get Client by MAC", "PASS", "Retrieved client info")
                    results.add_result("Get Client by MAC", "PASS")
                else:
                    print_test("Get Client by MAC", "FAIL", "No client info returned")
                    results.add_result("Get Client by MAC", "FAIL", "Empty response")
            except Exception as e:
                print_test("Get Client by MAC", "FAIL", str(e))
                results.add_result("Get Client by MAC", "FAIL", str(e))

            # Test get_client_history
            print("\n  Testing get_client_history()...")
            try:
                history = controller.get_client_history(mac, hours=24)
                if history:
                    print_test(
                        "Get Client History",
                        "PASS",
                        f"Retrieved {len(history)} history entries",
                    )
                    results.add_result("Get Client History", "PASS")
                else:
                    print_test(
                        "Get Client History",
                        "INFO",
                        "No history available (might be new client)",
                    )
                    results.add_result("Get Client History", "PASS", "No history")
            except Exception as e:
                print_test("Get Client History", "FAIL", str(e))
                results.add_result("Get Client History", "FAIL", str(e))

            print("\n  ⚠️  WARNING: The following tests may disconnect the client!")
            reconnect_test = input("  Test reconnect on this client? (y/N): ")
            if reconnect_test.lower() == "y":
                try:
                    controller.reconnect_client(mac)
                    print_test(
                        "Reconnect Client",
                        "PASS",
                        "Reconnect command sent (client will briefly disconnect)",
                    )
                    results.add_result("Reconnect Client", "PASS")
                except Exception as e:
                    print_test("Reconnect Client", "FAIL", str(e))
                    results.add_result("Reconnect Client", "FAIL", str(e))
            else:
                print_test("Reconnect Client", "SKIP", "Skipped by user")
                results.add_result("Reconnect Client", "SKIP", "User skipped")

        except ValueError:
            print_test("Client Operations", "FAIL", "Invalid input")
            results.add_result("Client Operations", "FAIL", "Invalid input")
        except KeyboardInterrupt:
            print("\n  Test interrupted by user")
            results.add_result("Client Operations", "SKIP", "Interrupted")
    else:
        print_test("Client Operations", "SKIP", "Non-interactive mode")
        results.add_result("Client Operations", "SKIP", "Non-interactive")


def main():
    """Main test execution."""
    print("\n" + "=" * 80)
    print("  UniFi Controller API Integration Test Suite")
    print("=" * 80)
    print(f"\n  Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Controller: {config.CONTROLLER_HOST}:{config.CONTROLLER_PORT}")
    print(f"  Site: {config.CONTROLLER_SITE}")
    print(f"  API Type: {getattr(config, 'API_TYPE', 'local')}")

    # Initialize test results tracker
    results = TestResults()

    # Initialize controller
    try:
        controller = UniFiController(
            host=config.CONTROLLER_HOST,
            username=config.CONTROLLER_USERNAME,
            password=config.CONTROLLER_PASSWORD,
            port=getattr(config, "CONTROLLER_PORT", 8443),
            site=getattr(config, "CONTROLLER_SITE", "default"),
            verify_ssl=getattr(config, "CONTROLLER_VERIFY_SSL", False),
            timeout=30,
        )
    except AttributeError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("Please make sure all required settings are in config.py:")
        print("  - CONTROLLER_HOST")
        print("  - CONTROLLER_USERNAME")
        print("  - CONTROLLER_PASSWORD")
        print("  - CONTROLLER_PORT (optional, default: 8443)")
        print("  - CONTROLLER_SITE (optional, default: 'default')")
        print("  - CONTROLLER_VERIFY_SSL (optional, default: False)")
        sys.exit(1)

    # Test connection
    if not test_connection(controller, results):
        print("\n❌ Cannot connect to controller. Please check:")
        print("  1. Controller is running and accessible")
        print("  2. Host and port are correct in config.py")
        print("  3. Network connectivity is working")
        print("  4. Firewall allows connection")
        results.print_summary()
        sys.exit(1)

    # Test authentication
    if not test_authentication(controller, results):
        print("\n❌ Authentication failed. Please check:")
        print("  1. Username and password are correct")
        print("  2. User has admin privileges")
        print("  3. Account is not locked")
        results.print_summary()
        sys.exit(1)

    # Test site operations
    test_site_operations(controller, results)

    # Test device listing
    devices = test_device_listing(controller, results)

    # Test client listing
    clients = test_client_listing(controller, results)

    # Interactive tests
    print("\n" + "=" * 80)
    print("  Interactive Tests")
    print("=" * 80)
    print("\n  The following tests require user interaction and may affect")
    print("  devices/clients on your network. Proceed with caution!")

    interactive = input("\n  Run interactive tests? (y/N): ")
    if interactive.lower() == "y":
        # Test device operations
        test_device_operations(controller, devices, results, interactive=True)

        # Test client operations
        test_client_operations(controller, clients, results, interactive=True)
    else:
        print("\n  Interactive tests skipped")
        results.add_result("Interactive Tests", "SKIP", "User skipped")

    # Cleanup
    try:
        controller.logout()
        print("\n✅ Logged out successfully")
    except Exception as e:
        print(f"\n⚠️  Logout warning: {str(e)}")

    # Print summary
    print(f"\n  End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results.print_summary()

    # Exit code based on results
    sys.exit(0 if results.failed == 0 else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
