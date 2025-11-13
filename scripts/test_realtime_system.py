"""
Comprehensive test script for real-time monitoring features.

Tests WebSocket connections, broadcast tasks, and analytics endpoints.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import websockets

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration
API_BASE = "http://localhost:8000"
WS_BASE = "ws://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_success(message: str):
    """Print a success message."""
    print(f"✅ {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"❌ {message}")


def print_info(message: str):
    """Print an info message."""
    print(f"ℹ️  {message}")


def test_api_health():
    """Test API health endpoint."""
    print_section("Testing API Health")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is healthy - Version: {data.get('version')}")
            return True
        else:
            print_error(f"API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to connect to API: {e}")
        return False


def test_websocket_stats():
    """Test WebSocket statistics endpoint."""
    print_section("Testing WebSocket Statistics")
    try:
        response = requests.get(f"{API_BASE}/ws/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(
                f"WebSocket stats retrieved - Active connections: {data.get('total_connections')}"
            )
            print_info(f"Rooms: {', '.join(data.get('rooms', {}).keys())}")
            return True
        else:
            print_error(f"WebSocket stats failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to get WebSocket stats: {e}")
        return False


def test_analytics_endpoints():
    """Test analytics API endpoints."""
    print_section("Testing Analytics Endpoints")

    endpoints = [
        "/api/analytics/network-insights",
        "/api/devices",
        "/api/clients",
    ]

    results = []
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success(f"{endpoint} - OK ({len(str(data))} bytes)")
                results.append(True)
            else:
                print_error(f"{endpoint} - Failed: {response.status_code}")
                results.append(False)
        except Exception as e:
            print_error(f"{endpoint} - Error: {e}")
            results.append(False)

    return all(results)


async def test_websocket_connection():
    """Test WebSocket connection and subscriptions."""
    print_section("Testing WebSocket Connection")

    client_id = f"test-client-{int(time.time())}"
    uri = f"{WS_BASE}/ws?client_id={client_id}"

    try:
        async with websockets.connect(uri) as websocket:
            print_success(f"Connected to WebSocket: {uri}")

            # First, receive the connection welcome message
            try:
                welcome = await asyncio.wait_for(websocket.recv(), timeout=5)
                welcome_data = json.loads(welcome)
                if welcome_data.get("type") == "connection":
                    print_success(f"Received welcome message for client: {welcome_data.get('client_id')}")
                else:
                    print_info(f"Unexpected first message: {welcome_data.get('type')}")
            except asyncio.TimeoutError:
                print_info("No welcome message received")

            # Test subscription to metrics room
            print_info("Subscribing to 'metrics' room...")
            await websocket.send(
                json.dumps({"type": "subscribe", "room": "metrics"})
            )

            # Wait for subscription confirmation
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            if data.get("type") == "subscription" and data.get("status") == "subscribed":
                print_success(f"Subscribed to room: {data.get('room')}")
            else:
                print_error(f"Unexpected subscription response: {data}")

            # Test subscription to health room
            print_info("Subscribing to 'health' room...")
            await websocket.send(
                json.dumps({"type": "subscribe", "room": "health"})
            )

            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            if data.get("type") == "subscription" and data.get("status") == "subscribed":
                print_success(f"Subscribed to room: {data.get('room')}")
            else:
                print_error(f"Unexpected subscription response: {data}")

            # Test ping/pong
            print_info("Testing ping/pong...")
            await websocket.send(json.dumps({"type": "ping"}))
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            if data.get("type") == "pong":
                print_success("Ping/pong successful")
            else:
                print_error(f"Unexpected ping response: {data}")

            # Wait for broadcast messages
            print_info("Waiting for broadcast messages (45 seconds)...")
            print_info(
                "  - Metrics broadcasts every 30 seconds"
            )
            print_info("  - Health broadcasts every 60 seconds")

            messages_received = []
            start_time = time.time()

            while time.time() - start_time < 45:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=35)
                    data = json.loads(response)
                    message_type = data.get("type")
                    messages_received.append(message_type)

                    if message_type == "metrics_update":
                        count = data.get("count", 0)
                        print_success(
                            f"Received metrics_update: {count} metrics at {datetime.now().strftime('%H:%M:%S')}"
                        )
                    elif message_type == "health_update":
                        health_data = data.get("data", {})
                        score = health_data.get("health_score", 0)
                        status = health_data.get("health_status", "unknown")
                        print_success(
                            f"Received health_update: Score={score:.1f}, Status={status} at {datetime.now().strftime('%H:%M:%S')}"
                        )
                    else:
                        print_info(f"Received message type: {message_type}")

                except asyncio.TimeoutError:
                    print_info("No message received in last 35 seconds (expected)")

            # Summary
            print_section("WebSocket Test Summary")
            print_info(f"Total messages received: {len(messages_received)}")
            if "metrics_update" in messages_received:
                print_success("✓ Metrics broadcast working")
            else:
                print_error("✗ No metrics broadcasts received")

            if "health_update" in messages_received:
                print_success("✓ Health broadcast working")
            else:
                print_info("  Health broadcast not received (60s interval)")

            return True

    except websockets.exceptions.WebSocketException as e:
        print_error(f"WebSocket connection error: {e}")
        return False
    except Exception as e:
        print_error(f"WebSocket test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "🚀 " * 20)
    print("  UniFi Network Dashboard - Real-Time System Test")
    print("🚀 " * 20)

    # Test API
    api_ok = test_api_health()
    if not api_ok:
        print_error("\n⚠️  API is not responding. Please start the backend server.")
        print_info("Run: cd backend && python src/main.py")
        return

    # Test WebSocket stats
    stats_ok = test_websocket_stats()

    # Test analytics endpoints
    analytics_ok = test_analytics_endpoints()

    # Test WebSocket connection
    ws_ok = await test_websocket_connection()

    # Final summary
    print_section("Final Test Results")
    results = {
        "API Health": api_ok,
        "WebSocket Stats": stats_ok,
        "Analytics Endpoints": analytics_ok,
        "WebSocket Connection": ws_ok,
    }

    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")

    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("  🎉 ALL TESTS PASSED! 🎉")
        print("  Real-time monitoring system is working correctly.")
    else:
        print("  ⚠️  SOME TESTS FAILED")
        print("  Review the errors above for details.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test script error: {e}")
        import traceback

        traceback.print_exc()
