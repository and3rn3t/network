"""Test script for WebSocket broadcasting."""

import asyncio
from datetime import datetime

import httpx


async def test_websocket_stats():
    """Test getting WebSocket statistics."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/ws/stats")
            print("WebSocket Statistics:")
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.json()}")
        except Exception as e:
            print(f"Error getting stats: {e}")


async def simulate_alert():
    """Simulate broadcasting an alert."""
    print("\nSimulating alert broadcast...")
    print("(In production, this would be called from alert system)")

    # Example of what would be sent
    alert_data = {
        "id": 123,
        "rule_id": 1,
        "host_id": 5,
        "severity": "warning",
        "status": "triggered",
        "message": "High CPU usage detected",
        "metric_value": 85.5,
        "threshold_value": 80.0,
        "triggered_at": datetime.now().isoformat(),
    }

    print(f"  Alert data: {alert_data}")
    print("  This alert would be broadcast to all clients subscribed to 'alerts' room")


async def simulate_metrics():
    """Simulate metrics broadcast."""
    print("\nSimulating metrics broadcast...")
    print("(In production, this runs every 30 seconds)")

    # Example of what would be sent
    metrics_data = [
        {
            "host_id": 1,
            "host_name": "UDM-Pro",
            "metric_type": "cpu_usage",
            "value": 45.2,
            "timestamp": datetime.now().isoformat(),
        },
        {
            "host_id": 2,
            "host_name": "Switch-01",
            "metric_type": "memory_usage",
            "value": 62.8,
            "timestamp": datetime.now().isoformat(),
        },
    ]

    print(f"  Metrics count: {len(metrics_data)}")
    print("  These metrics would be broadcast to 'metrics' room subscribers")


async def main():
    """Run WebSocket tests."""
    print("=" * 60)
    print("WebSocket Test Suite")
    print("=" * 60)

    print("\nTesting WebSocket endpoints...")

    # Test 1: Get WebSocket stats
    await test_websocket_stats()

    # Test 2: Simulate broadcasts
    await simulate_alert()
    await simulate_metrics()

    print("\n" + "=" * 60)
    print("WebSocket Integration Notes:")
    print("=" * 60)
    print(
        """
1. WebSocket endpoint: ws://localhost:8000/ws
2. Test client: Open backend/websocket_test.html in browser
3. Available rooms:
   - 'metrics': Real-time device metrics (updates every 30s)
   - 'alerts': Alert notifications (on alert trigger)
   - 'devices': Device status changes (on status change)
   - 'health': Network health updates (periodic)

4. Message Types:
   - subscribe: Join a room
   - unsubscribe: Leave a room
   - ping: Test connection

5. Broadcast Functions (for integration):
   - broadcast_alert_update(alert_data)
   - broadcast_device_update(device_data)
   - broadcast_health_update(health_data)
   - broadcast_metrics_task(db) - background task
    """
    )


if __name__ == "__main__":
    asyncio.run(main())
