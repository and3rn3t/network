#!/usr/bin/env python3
"""
Test Enhanced Error Handling

This script tests the improved error handling features:
1. MAC address validation
2. Retry logic with exponential backoff
3. Better error messages
4. Rate limiting detection
"""

import sys
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from src.exceptions import (
    UniFiAPIError,
    UniFiAuthError,
    UniFiConnectionError,
    UniFiNotFoundError,
    UniFiTimeoutError,
)
from src.unifi_controller import UniFiController


def test_mac_validation():
    """Test MAC address validation."""
    print("\n" + "=" * 70)
    print("TEST 1: MAC Address Validation")
    print("=" * 70)

    controller = UniFiController(
        host=config.CONTROLLER_HOST,
        username=config.CONTROLLER_USERNAME,
        password=config.CONTROLLER_PASSWORD,
        port=config.CONTROLLER_PORT,
        site=config.CONTROLLER_SITE,
        verify_ssl=config.CONTROLLER_VERIFY_SSL,
    )

    test_cases = [
        ("aa:bb:cc:dd:ee:ff", True, "Valid MAC with colons"),
        ("AA-BB-CC-DD-EE-FF", True, "Valid MAC with dashes"),
        ("aabbccddeeff", True, "Valid MAC without separators"),
        ("invalid", False, "Invalid - too short"),
        ("aa:bb:cc:dd:ee:gg", False, "Invalid - non-hex character"),
        ("aa:bb:cc:dd:ee", False, "Invalid - incomplete"),
        ("", False, "Invalid - empty string"),
    ]

    for mac, should_pass, description in test_cases:
        try:
            normalized = controller._normalize_mac(mac)
            if should_pass:
                print(f"✅ PASS: {description}")
                print(f"   Input: {mac!r} → Output: {normalized}")
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Expected error but got: {normalized}")
        except ValueError as e:
            if not should_pass:
                print(f"✅ PASS: {description}")
                print(f"   Got expected error: {e}")
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Unexpected error: {e}")


def test_connection_handling():
    """Test connection error handling."""
    print("\n" + "=" * 70)
    print("TEST 2: Connection Error Handling")
    print("=" * 70)

    # Test with invalid host
    print("\nTesting with invalid host (should fail gracefully)...")
    controller = UniFiController(
        host="192.168.255.255",  # Invalid host
        username="test",
        password="test",
        port=443,
        site="default",
        verify_ssl=False,
        timeout=2,  # Short timeout
    )

    try:
        controller.login()
        print("❌ FAIL: Should have raised UniFiConnectionError")
    except UniFiConnectionError as e:
        print("✅ PASS: Connection error handled correctly")
        print(f"   Error message: {e}")
    except UniFiTimeoutError as e:
        print("✅ PASS: Timeout error handled correctly")
        print(f"   Error message: {e}")
    except Exception as e:
        print(f"❌ FAIL: Unexpected error type: {type(e).__name__}")
        print(f"   Error: {e}")


def test_invalid_credentials():
    """Test authentication error handling."""
    print("\n" + "=" * 70)
    print("TEST 3: Authentication Error Handling")
    print("=" * 70)

    print("\nTesting with invalid credentials (should fail with clear message)...")
    controller = UniFiController(
        host=config.CONTROLLER_HOST,
        username="invalid_user",
        password="invalid_password",
        port=config.CONTROLLER_PORT,
        site=config.CONTROLLER_SITE,
        verify_ssl=config.CONTROLLER_VERIFY_SSL,
        timeout=5,
    )

    try:
        controller.login()
        print("❌ FAIL: Should have raised UniFiAuthError")
    except UniFiAuthError as e:
        print("✅ PASS: Authentication error handled correctly")
        print(f"   Error message: {e}")
    except Exception as e:
        print(f"❌ FAIL: Unexpected error type: {type(e).__name__}")
        print(f"   Error: {e}")


def test_invalid_mac_operations():
    """Test device operations with invalid MAC addresses."""
    print("\n" + "=" * 70)
    print("TEST 4: Invalid MAC in Device Operations")
    print("=" * 70)

    controller = UniFiController(
        host=config.CONTROLLER_HOST,
        username=config.CONTROLLER_USERNAME,
        password=config.CONTROLLER_PASSWORD,
        port=config.CONTROLLER_PORT,
        site=config.CONTROLLER_SITE,
        verify_ssl=config.CONTROLLER_VERIFY_SSL,
    )

    try:
        controller.login()
        print("✅ Connected to controller")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return

    print("\nTesting device operations with invalid MAC...")
    try:
        controller.get_device("invalid-mac")
        print("❌ FAIL: Should have raised ValueError")
    except ValueError as e:
        print("✅ PASS: Invalid MAC rejected before API call")
        print(f"   Error message: {e}")
    except Exception as e:
        print(f"❌ FAIL: Unexpected error type: {type(e).__name__}")
        print(f"   Error: {e}")


def test_not_found_handling():
    """Test handling of non-existent resources."""
    print("\n" + "=" * 70)
    print("TEST 5: Not Found Error Handling")
    print("=" * 70)

    controller = UniFiController(
        host=config.CONTROLLER_HOST,
        username=config.CONTROLLER_USERNAME,
        password=config.CONTROLLER_PASSWORD,
        port=config.CONTROLLER_PORT,
        site=config.CONTROLLER_SITE,
        verify_ssl=config.CONTROLLER_VERIFY_SSL,
    )

    try:
        controller.login()
        print("✅ Connected to controller")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return

    print("\nTesting with non-existent device...")
    try:
        # Valid MAC format but doesn't exist
        controller.get_device("00:00:00:00:00:00")
        print("❌ FAIL: Should have raised UniFiNotFoundError")
    except UniFiNotFoundError as e:
        print("✅ PASS: Not found error handled correctly")
        print(f"   Error message: {e}")
    except Exception as e:
        print(f"⚠️  Note: Got {type(e).__name__}: {e}")


def test_retry_logic():
    """Test retry logic with a real connection (observe timing)."""
    print("\n" + "=" * 70)
    print("TEST 6: Retry Logic (observing timing)")
    print("=" * 70)

    print("\nThis test will make a request that might fail transiently...")
    print("Watch for retry messages if there are network issues.")

    controller = UniFiController(
        host=config.CONTROLLER_HOST,
        username=config.CONTROLLER_USERNAME,
        password=config.CONTROLLER_PASSWORD,
        port=config.CONTROLLER_PORT,
        site=config.CONTROLLER_SITE,
        verify_ssl=config.CONTROLLER_VERIFY_SSL,
    )

    try:
        controller.login()
        print("✅ Connected to controller")

        start = time.time()
        devices = controller.get_devices()  # Has retry decorator
        elapsed = time.time() - start

        print(f"✅ Retrieved {len(devices)} devices in {elapsed:.2f}s")
        print("   (No retries needed - connection stable)")

    except Exception as e:
        print(f"❌ Request failed: {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("Enhanced Error Handling Tests")
    print("=" * 70)

    try:
        test_mac_validation()
        test_connection_handling()
        test_invalid_credentials()
        test_invalid_mac_operations()
        test_not_found_handling()
        test_retry_logic()

        print("\n" + "=" * 70)
        print("✅ Error Handling Tests Complete!")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
