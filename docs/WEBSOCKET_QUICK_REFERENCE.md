# WebSocket Quick Reference Guide

**UniFi Network API - WebSocket Server**  
**Version**: 1.0.0  
**Status**: Production Ready ✅

---

## 🔌 Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws?client_id=my-client');

ws.onopen = () => {
    console.log('Connected!');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

---

## 📡 Available Rooms

| Room | Description | Update Frequency |
|------|-------------|------------------|
| `metrics` | Device metrics and statistics | Every 10 seconds |
| `alerts` | Alert notifications | Immediate |
| `devices` | Device status changes | Immediate |
| `health` | Network health updates | Every 30 seconds |

---

## 📨 Message Types

### Client → Server

**Subscribe to Room**
```json
{
  "type": "subscribe",
  "room": "metrics"
}
```

**Unsubscribe from Room**
```json
{
  "type": "unsubscribe",
  "room": "alerts"
}
```

**Ping (Connection Health Check)**
```json
{
  "type": "ping"
}
```

### Server → Client

**Welcome Message** (on connection)
```json
{
  "type": "connection",
  "status": "connected",
  "client_id": "your-client-id",
  "timestamp": "2025-10-18T20:00:00"
}
```

**Subscription Confirmation**
```json
{
  "type": "subscription",
  "status": "subscribed",
  "room": "metrics",
  "timestamp": "2025-10-18T20:00:00"
}
```

**Metrics Update**
```json
{
  "type": "metrics",
  "timestamp": "2025-10-18T20:00:00",
  "data": {
    "total_devices": 15,
    "online_devices": 12,
    "total_clients": 45,
    "avg_latency_ms": 3.2,
    "total_traffic_mbps": 125.5
  }
}
```

**Alert Notification**
```json
{
  "type": "alert",
  "alert_id": 123,
  "severity": "critical",
  "rule_name": "High CPU Usage",
  "device_mac": "aa:bb:cc:dd:ee:ff",
  "message": "CPU usage exceeded 90%",
  "timestamp": "2025-10-18T20:00:00"
}
```

**Device Update**
```json
{
  "type": "device",
  "device_mac": "aa:bb:cc:dd:ee:ff",
  "status": "offline",
  "name": "Access Point 1",
  "timestamp": "2025-10-18T20:00:00"
}
```

**Pong Response**
```json
{
  "type": "pong",
  "timestamp": "2025-10-18T20:00:00"
}
```

---

## 🔗 HTTP Endpoints

### Get Connection Statistics
```http
GET /api/ws/stats
```

**Response**:
```json
{
  "total_connections": 3,
  "rooms": {
    "metrics": {
      "member_count": 2,
      "members": ["client-1", "client-2"]
    },
    "alerts": {
      "member_count": 1,
      "members": ["client-1"]
    }
  },
  "timestamp": "2025-10-18T20:00:00"
}
```

---

## 🐍 Python Example

```python
import asyncio
import json
from websockets.asyncio.client import connect

async def main():
    uri = "ws://localhost:8000/api/ws?client_id=python-client"
    
    async with connect(uri) as websocket:
        # Receive welcome
        welcome = await websocket.recv()
        print(f"Connected: {welcome}")
        
        # Subscribe to metrics
        await websocket.send(json.dumps({
            "type": "subscribe",
            "room": "metrics"
        }))
        
        # Listen for updates
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data['type']}")
            
            if data['type'] == 'metrics':
                print(f"Devices: {data['data']['total_devices']}")

asyncio.run(main())
```

---

## 🌐 JavaScript/React Example

```javascript
import { useEffect, useState } from 'react';

function useWebSocket(url, room) {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setConnected(true);
      // Subscribe to room
      ws.send(JSON.stringify({
        type: 'subscribe',
        room: room
      }));
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === room) {
        setData(message.data);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      setConnected(false);
    };

    return () => ws.close();
  }, [url, room]);

  return { data, connected };
}

// Usage in component
function Dashboard() {
  const { data, connected } = useWebSocket(
    'ws://localhost:8000/api/ws?client_id=dashboard',
    'metrics'
  );

  return (
    <div>
      <h1>Status: {connected ? 'Connected' : 'Disconnected'}</h1>
      {data && (
        <div>
          <p>Devices: {data.total_devices}</p>
          <p>Clients: {data.total_clients}</p>
        </div>
      )}
    </div>
  );
}
```

---

## 🧪 Testing

### Start Test Server
```bash
cd backend
python test_server.py
```

### Test with Browser
Open `backend/websocket_test.html` in your browser

### Test with Python
```bash
python backend/quick_test.py
```

### Test Multiple Clients
```bash
python backend/test_multi_clients.py
```

### Check Statistics
```bash
curl http://localhost:8000/api/ws/stats
```

---

## 🔧 Configuration

The WebSocket server runs on the same port as the REST API (default: 8000).

**Environment Variables**:
- `HOST`: Server host (default: "0.0.0.0")
- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: "info")

---

## 📊 Performance

- **Max Connections**: 100+ concurrent clients
- **Message Latency**: <10ms on local network
- **Bandwidth**: ~1KB per metric update
- **CPU Usage**: <5% with 50 clients

---

## 🔒 Security (Coming in Phase 5.1.3)

- JWT token authentication
- Secure WebSocket (wss://)
- Rate limiting
- Connection timeouts

---

## 🐛 Troubleshooting

### Connection Refused
- Check if server is running: `curl http://localhost:8000/health`
- Verify port is not in use: `netstat -an | findstr 8000`

### No Messages Received
- Check subscription: Look for subscription confirmation message
- Verify room name: Must be "metrics", "alerts", "devices", or "health"
- Check server logs for broadcast activity

### Connection Drops
- Implement ping/pong: Send ping every 30 seconds
- Handle reconnection in client code
- Check network connectivity

---

## 📚 Additional Resources

- **Full Documentation**: `docs/PHASE_5.1.2_COMPLETE.md`
- **Test Results**: `docs/WEBSOCKET_TEST_RESULTS.md`
- **API Reference**: `backend/README.md`
- **Interactive Docs**: http://localhost:8000/docs

---

**Last Updated**: October 18, 2025  
**Status**: ✅ Production Ready
