"""
WebSocket Integration Test Suite
Tests connection, reconnection, data flow, and performance
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any

import websockets
from websockets.client import WebSocketClientProtocol


class WebSocketTester:
    """WebSocket integration tester"""

    def __init__(self, url: str = "ws://localhost:8000/ws"):
        self.url = url
        self.results: dict[str, Any] = {
            "connection": {"passed": 0, "failed": 0, "tests": []},
            "reconnection": {"passed": 0, "failed": 0, "tests": []},
            "data_flow": {"passed": 0, "failed": 0, "tests": []},
            "performance": {"passed": 0, "failed": 0, "tests": []},
            "error_handling": {"passed": 0, "failed": 0, "tests": []},
        }

    async def test_basic_connection(self) -> bool:
        """Test basic WebSocket connection"""
        print("🔍 Testing basic connection...")
        try:
            async with websockets.connect(self.url) as websocket:
                # Connection successful
                self._record_test("connection", "Basic connection", True)
                print("✅ Basic connection successful")
                return True
        except Exception as e:
            self._record_test("connection", "Basic connection", False, str(e))
            print(f"❌ Basic connection failed: {e}")
            return False

    async def test_message_echo(self) -> bool:
        """Test sending and receiving messages"""
        print("🔍 Testing message echo...")
        try:
            async with websockets.connect(self.url) as websocket:
                # Send ping
                message = {"type": "ping", "timestamp": datetime.now().isoformat()}
                await websocket.send(json.dumps(message))

                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)

                if data.get("type") == "pong":
                    self._record_test("data_flow", "Ping/Pong", True)
                    print("✅ Message echo successful")
                    return True
                self._record_test(
                    "data_flow", "Ping/Pong", False, "Invalid response type"
                )
                print("❌ Invalid response type")
                return False
        except asyncio.TimeoutError:
            self._record_test("data_flow", "Ping/Pong", False, "Timeout")
            print("❌ Message echo timeout")
            return False
        except Exception as e:
            self._record_test("data_flow", "Ping/Pong", False, str(e))
            print(f"❌ Message echo failed: {e}")
            return False

    async def test_room_subscription(self) -> bool:
        """Test room subscription functionality"""
        print("🔍 Testing room subscription...")
        try:
            async with websockets.connect(self.url) as websocket:
                # Subscribe to metrics room
                subscribe_msg = {"type": "subscribe", "room": "metrics"}
                await websocket.send(json.dumps(subscribe_msg))

                # Wait for confirmation
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)

                if data.get("status") == "subscribed":
                    self._record_test("data_flow", "Room subscription", True)
                    print("✅ Room subscription successful")
                    return True
                self._record_test(
                    "data_flow", "Room subscription", False, "No confirmation"
                )
                print("❌ No subscription confirmation")
                return False
        except Exception as e:
            self._record_test("data_flow", "Room subscription", False, str(e))
            print(f"❌ Room subscription failed: {e}")
            return False

    async def test_multiple_connections(self) -> bool:
        """Test multiple concurrent connections"""
        print("🔍 Testing multiple concurrent connections...")
        try:
            connections: list[WebSocketClientProtocol] = []

            # Open 5 concurrent connections
            for i in range(5):
                ws = await websockets.connect(self.url)
                connections.append(ws)

            # Send ping from each
            for i, ws in enumerate(connections):
                message = {"type": "ping", "client": i}
                await ws.send(json.dumps(message))

            # Receive responses
            responses = 0
            for ws in connections:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    data = json.loads(response)
                    if data.get("type") == "pong":
                        responses += 1
                except asyncio.TimeoutError:
                    pass

            # Close all connections
            for ws in connections:
                await ws.close()

            if responses == 5:
                self._record_test("connection", "Multiple connections", True)
                print(f"✅ Multiple connections successful ({responses}/5)")
                return True
            self._record_test(
                "connection",
                "Multiple connections",
                False,
                f"Only {responses}/5 responded",
            )
            print(f"⚠️ Multiple connections partial ({responses}/5)")
            return False
        except Exception as e:
            self._record_test("connection", "Multiple connections", False, str(e))
            print(f"❌ Multiple connections failed: {e}")
            return False

    async def test_reconnection(self) -> bool:
        """Test reconnection after disconnect"""
        print("🔍 Testing reconnection...")
        try:
            # First connection
            ws1 = await websockets.connect(self.url)
            await ws1.close()

            # Wait a bit
            await asyncio.sleep(1)

            # Reconnect
            ws2 = await websockets.connect(self.url)
            message = {"type": "ping"}
            await ws2.send(json.dumps(message))

            response = await asyncio.wait_for(ws2.recv(), timeout=5.0)
            data = json.loads(response)

            await ws2.close()

            if data.get("type") == "pong":
                self._record_test("reconnection", "Basic reconnection", True)
                print("✅ Reconnection successful")
                return True
            self._record_test(
                "reconnection", "Basic reconnection", False, "Invalid response"
            )
            print("❌ Reconnection failed")
            return False
        except Exception as e:
            self._record_test("reconnection", "Basic reconnection", False, str(e))
            print(f"❌ Reconnection failed: {e}")
            return False

    async def test_rapid_messages(self) -> bool:
        """Test handling rapid message bursts"""
        print("🔍 Testing rapid message handling...")
        try:
            async with websockets.connect(self.url) as websocket:
                start_time = time.time()

                # Send 100 messages rapidly
                for i in range(100):
                    message = {"type": "ping", "sequence": i}
                    await websocket.send(json.dumps(message))

                # Try to receive all responses
                received = 0
                try:
                    for _ in range(100):
                        await asyncio.wait_for(websocket.recv(), timeout=0.1)
                        received += 1
                except asyncio.TimeoutError:
                    pass

                elapsed = time.time() - start_time

                if received >= 90:  # 90% success rate
                    self._record_test(
                        "performance",
                        "Rapid messages",
                        True,
                        f"{received}/100 in {elapsed:.2f}s",
                    )
                    print(f"✅ Rapid messages: {received}/100 in {elapsed:.2f}s")
                    return True
                self._record_test(
                    "performance",
                    "Rapid messages",
                    False,
                    f"Only {received}/100 received",
                )
                print(f"⚠️ Rapid messages: {received}/100 in {elapsed:.2f}s")
                return False
        except Exception as e:
            self._record_test("performance", "Rapid messages", False, str(e))
            print(f"❌ Rapid messages failed: {e}")
            return False

    async def test_invalid_message(self) -> bool:
        """Test error handling for invalid messages"""
        print("🔍 Testing invalid message handling...")
        try:
            async with websockets.connect(self.url) as websocket:
                # Send invalid JSON
                await websocket.send("invalid json {]")

                # Should receive error or connection should stay open
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    # Got a response, connection still alive
                    self._record_test("error_handling", "Invalid message", True)
                    print("✅ Invalid message handled gracefully")
                    return True
                except asyncio.TimeoutError:
                    # No response but connection still open
                    # Try sending valid message
                    await websocket.send(json.dumps({"type": "ping"}))
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    if data.get("type") == "pong":
                        self._record_test("error_handling", "Invalid message", True)
                        print("✅ Invalid message handled gracefully")
                        return True
        except Exception as e:
            self._record_test("error_handling", "Invalid message", False, str(e))
            print(f"❌ Invalid message handling failed: {e}")
            return False
        return False

    async def test_long_connection(self) -> bool:
        """Test connection stability over time"""
        print("🔍 Testing long-term connection stability (30s)...")
        try:
            async with websockets.connect(self.url) as websocket:
                start_time = time.time()
                pings_sent = 0
                pongs_received = 0

                # Send pings every 3 seconds for 30 seconds
                while time.time() - start_time < 30:
                    message = {"type": "ping"}
                    await websocket.send(json.dumps(message))
                    pings_sent += 1

                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        data = json.loads(response)
                        if data.get("type") == "pong":
                            pongs_received += 1
                    except asyncio.TimeoutError:
                        pass

                    await asyncio.sleep(3)

                success_rate = pongs_received / pings_sent if pings_sent > 0 else 0

                if success_rate >= 0.9:  # 90% success rate
                    self._record_test(
                        "performance",
                        "Long connection",
                        True,
                        f"{pongs_received}/{pings_sent} pongs",
                    )
                    print(
                        f"✅ Long connection stable: {pongs_received}/{pings_sent} pongs"
                    )
                    return True
                self._record_test(
                    "performance",
                    "Long connection",
                    False,
                    f"Only {pongs_received}/{pings_sent} pongs",
                )
                print(
                    f"⚠️ Long connection unstable: {pongs_received}/{pings_sent} pongs"
                )
                return False
        except Exception as e:
            self._record_test("performance", "Long connection", False, str(e))
            print(f"❌ Long connection failed: {e}")
            return False

    def _record_test(
        self, category: str, test_name: str, passed: bool, details: str = ""
    ) -> None:
        """Record test result"""
        self.results[category]["tests"].append(
            {"name": test_name, "passed": passed, "details": details}
        )
        if passed:
            self.results[category]["passed"] += 1
        else:
            self.results[category]["failed"] += 1

    def print_summary(self) -> None:
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 WEBSOCKET TEST SUMMARY")
        print("=" * 60)

        total_passed = 0
        total_failed = 0

        for category, data in self.results.items():
            passed = data["passed"]
            failed = data["failed"]
            total = passed + failed

            total_passed += passed
            total_failed += failed

            status = "✅" if failed == 0 else "⚠️" if passed > 0 else "❌"
            print(
                f"\n{status} {category.upper().replace('_', ' ')}: {passed}/{total} passed"
            )

            for test in data["tests"]:
                icon = "  ✅" if test["passed"] else "  ❌"
                details = f" ({test['details']})" if test["details"] else ""
                print(f"{icon} {test['name']}{details}")

        print("\n" + "=" * 60)
        total = total_passed + total_failed
        percentage = (total_passed / total * 100) if total > 0 else 0
        print(f"OVERALL: {total_passed}/{total} tests passed ({percentage:.1f}%)")
        print("=" * 60 + "\n")


async def run_all_tests():
    """Run all WebSocket tests"""
    print("🚀 Starting WebSocket Integration Tests\n")

    tester = WebSocketTester()

    # Run tests
    await tester.test_basic_connection()
    await tester.test_message_echo()
    await tester.test_room_subscription()
    await tester.test_multiple_connections()
    await tester.test_reconnection()
    await tester.test_rapid_messages()
    await tester.test_invalid_message()
    await tester.test_long_connection()

    # Print summary
    tester.print_summary()


if __name__ == "__main__":
    print("WebSocket Integration Test Suite")
    print("Make sure the backend server is running on localhost:8000\n")

    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}")
