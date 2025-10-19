"""Test multiple WebSocket connections simultaneously."""

import asyncio
import json
from websockets.asyncio.client import connect


async def client_listener(client_id: str, room: str, duration: int = 15):
    """Connect and listen to a specific room."""
    uri = f"ws://localhost:8000/api/ws?client_id={client_id}"
    
    print(f"[{client_id}] Connecting...")
    
    try:
        async with connect(uri) as websocket:
            # Welcome
            welcome = await websocket.recv()
            print(f"[{client_id}] ✅ Connected")
            
            # Subscribe
            await websocket.send(json.dumps({"type": "subscribe", "room": room}))
            response = await websocket.recv()
            print(f"[{client_id}] 📡 Subscribed to '{room}'")
            
            # Listen for messages
            end_time = asyncio.get_event_loop().time() + duration
            message_count = 0
            
            while asyncio.get_event_loop().time() < end_time:
                try:
                    message = await asyncio.wait_for(
                        websocket.recv(), 
                        timeout=2.0
                    )
                    data = json.loads(message)
                    message_count += 1
                    
                    if data.get('type') == 'metrics':
                        devices = data.get('data', {}).get('total_devices', '?')
                        print(f"[{client_id}] 📊 Metric #{message_count} - "
                              f"Devices: {devices}")
                    elif data.get('type') == 'alert':
                        print(f"[{client_id}] 🚨 Alert received!")
                    
                except asyncio.TimeoutError:
                    pass  # No message yet
            
            print(f"[{client_id}] 📋 Received {message_count} messages")
            print(f"[{client_id}] 👋 Disconnecting...")
            
    except Exception as e:
        print(f"[{client_id}] ❌ Error: {e}")


async def test_multiple_clients():
    """Test multiple concurrent WebSocket clients."""
    print("\n" + "=" * 70)
    print("🧪 Testing Multiple WebSocket Clients")
    print("=" * 70 + "\n")
    
    # Create multiple clients subscribing to different rooms
    clients = [
        ("client-metrics-1", "metrics", 15),
        ("client-metrics-2", "metrics", 15),
        ("client-alerts-1", "alerts", 15),
        ("client-devices-1", "devices", 15),
    ]
    
    # Run all clients concurrently
    tasks = [
        client_listener(client_id, room, duration)
        for client_id, room, duration in clients
    ]
    
    await asyncio.gather(*tasks)
    
    print("\n" + "=" * 70)
    print("✅ All clients completed!")
    print("=" * 70 + "\n")


async def check_stats():
    """Check connection statistics."""
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:8000/api/ws/stats') as resp:
            data = await resp.json()
            print(f"\n📊 Server Stats:")
            print(f"   Total Connections: {data.get('total_connections', 0)}")
            print(f"   Rooms: {list(data.get('rooms', {}).keys())}")
            for room, count in data.get('rooms', {}).items():
                print(f"      - {room}: {count} subscriber(s)")


if __name__ == "__main__":
    # Check stats before
    print("\n📊 Checking stats before test...")
    try:
        asyncio.run(check_stats())
    except Exception as e:
        print(f"Could not fetch stats: {e}")
    
    # Run test
    asyncio.run(test_multiple_clients())
