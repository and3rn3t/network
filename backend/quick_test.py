"""Quick WebSocket connection test."""

import asyncio
import json
from datetime import datetime

from websockets.asyncio.client import connect


async def test_websocket_connection():
    """Test WebSocket connection and subscriptions."""
    uri = "ws://localhost:8000/api/ws?client_id=test-client-1"

    print(f"🔌 Connecting to {uri}")

    try:
        async with connect(uri) as websocket:
            # Receive welcome message
            welcome = await websocket.recv()
            print(f"✅ Connected! Welcome: {welcome}")

            # Subscribe to metrics room
            subscribe_msg = json.dumps({"type": "subscribe", "room": "metrics"})
            await websocket.send(subscribe_msg)
            print(f"📡 Sent subscription request: {subscribe_msg}")

            # Wait for confirmation
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            print(f"📥 Received: {response}")

            # Listen for metrics broadcasts (10 seconds)
            print("\n📊 Listening for metric broadcasts (10 seconds)...")
            try:
                for i in range(3):
                    message = await asyncio.wait_for(websocket.recv(), timeout=12.0)
                    data = json.loads(message)
                    print(f"\n📈 Metric Update #{i+1}:")
                    print(f"   Timestamp: {data.get('timestamp')}")
                    if "data" in data:
                        for key, value in data["data"].items():
                            print(f"   {key}: {value}")
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for metrics (server sends every 10s)")

            # Test ping
            print("\n🏓 Testing ping...")
            ping_msg = json.dumps({"type": "ping"})
            await websocket.send(ping_msg)
            pong = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            print(f"✅ Pong received: {pong}")

            # Unsubscribe
            unsubscribe_msg = json.dumps({"type": "unsubscribe", "room": "metrics"})
            await websocket.send(unsubscribe_msg)
            print(f"\n🔕 Unsubscribed from metrics")

            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            print(f"📥 Received: {response}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧪 WebSocket Connection Test")
    print("=" * 70 + "\n")

    asyncio.run(test_websocket_connection())

    print("\n" + "=" * 70)
    print("✅ Test Complete!")
    print("=" * 70 + "\n")
