# Backend API Quick Reference

**Version:** 1.0
**Base URL:** `http://localhost:8000`
**Status:** ✅ Production Ready

---

## 🚀 Quick Start

### Start the Server

```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

Server will start at: http://localhost:8000

- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/health

---

## 🔐 Authentication

### Login

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123!"
}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_superuser": true
  }
}
```

### Using the Token

Include the token in the `Authorization` header:

```bash
Authorization: Bearer YOUR_TOKEN_HERE
```

---

## 📡 API Endpoints

### Devices

| Endpoint                           | Method | Auth     | Description                              |
| ---------------------------------- | ------ | -------- | ---------------------------------------- |
| `/api/devices`                     | GET    | Optional | List all devices with optional filtering |
| `/api/devices/{device_id}`         | GET    | Optional | Get device details                       |
| `/api/devices/{device_id}/metrics` | GET    | Optional | Get device metrics                       |

**Query Parameters:**

- `skip`: Pagination offset (default: 0)
- `limit`: Items per page (default: 100)
- `status`: Filter by status (online/offline)
- `model`: Filter by model type

### Alerts

| Endpoint                             | Method | Auth     | Description                    |
| ------------------------------------ | ------ | -------- | ------------------------------ |
| `/api/alerts`                        | GET    | Optional | List all alerts with filtering |
| `/api/alerts/{alert_id}`             | GET    | Optional | Get alert details              |
| `/api/alerts/{alert_id}/acknowledge` | POST   | Required | Acknowledge an alert           |
| `/api/alerts/{alert_id}/resolve`     | POST   | Required | Resolve an alert               |

**Query Parameters:**

- `skip`: Pagination offset
- `limit`: Items per page
- `severity`: Filter by severity (info/warning/critical)
- `status`: Filter by status (open/acknowledged/resolved)
- `device_id`: Filter by device

### Alert Rules

| Endpoint               | Method | Auth     | Description          |
| ---------------------- | ------ | -------- | -------------------- |
| `/api/rules`           | GET    | Required | List all alert rules |
| `/api/rules/{rule_id}` | GET    | Required | Get rule details     |
| `/api/rules`           | POST   | Required | Create new rule      |
| `/api/rules/{rule_id}` | PUT    | Required | Update rule          |
| `/api/rules/{rule_id}` | DELETE | Required | Delete rule          |

### Notification Channels

| Endpoint                          | Method | Auth     | Description         |
| --------------------------------- | ------ | -------- | ------------------- |
| `/api/channels`                   | GET    | Required | List all channels   |
| `/api/channels/{channel_id}`      | GET    | Required | Get channel details |
| `/api/channels`                   | POST   | Required | Create new channel  |
| `/api/channels/{channel_id}`      | PUT    | Required | Update channel      |
| `/api/channels/{channel_id}`      | DELETE | Required | Delete channel      |
| `/api/channels/{channel_id}/test` | POST   | Required | Test channel        |

### Analytics

| Endpoint                   | Method | Auth     | Description            |
| -------------------------- | ------ | -------- | ---------------------- |
| `/api/analytics/stats`     | GET    | Optional | Get general statistics |
| `/api/analytics/trends`    | GET    | Optional | Get metric trends      |
| `/api/analytics/forecasts` | GET    | Optional | Get forecasted values  |
| `/api/analytics/anomalies` | GET    | Optional | Detect anomalies       |

**Query Parameters:**

- `metric`: Metric type (cpu/memory/temperature)
- `device_id`: Filter by device
- `days`: Time range in days (default: 7)

### Authentication

| Endpoint                    | Method | Auth      | Description      |
| --------------------------- | ------ | --------- | ---------------- |
| `/api/auth/login`           | POST   | No        | User login       |
| `/api/auth/logout`          | POST   | Required  | User logout      |
| `/api/auth/me`              | GET    | Required  | Get current user |
| `/api/auth/change-password` | POST   | Required  | Change password  |
| `/api/auth/users`           | GET    | Superuser | List all users   |
| `/api/auth/users`           | POST   | Superuser | Create new user  |

---

## 🔌 WebSocket

### Connection

```javascript
const ws = new WebSocket("ws://localhost:8000/api/ws");

ws.onopen = () => {
  console.log("Connected");

  // Subscribe to rooms
  ws.send(
    JSON.stringify({
      type: "subscribe",
      room: "devices", // or 'alerts', 'metrics'
    })
  );
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
};
```

### Message Types

**Client → Server:**

```json
// Subscribe to a room
{"type": "subscribe", "room": "devices"}

// Unsubscribe from a room
{"type": "unsubscribe", "room": "devices"}

// Ping (keep-alive)
{"type": "ping"}
```

**Server → Client:**

```json
// Device update
{
  "type": "device_update",
  "data": {
    "device_id": "abc123",
    "status": "online",
    "metrics": {...}
  }
}

// Alert update
{
  "type": "alert_update",
  "data": {
    "alert_id": 42,
    "severity": "critical",
    "message": "..."
  }
}

// Metric update
{
  "type": "metric_update",
  "data": {
    "device_id": "abc123",
    "metric": "cpu",
    "value": 75.5
  }
}

// Pong (keep-alive response)
{"type": "pong"}
```

### Available Rooms

- `devices` - Device status changes
- `alerts` - New and updated alerts
- `metrics` - Real-time metric updates

---

## 🧪 Testing with cURL

### Health Check

```bash
curl http://localhost:8000/api/health
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123!"}'
```

### Get Devices (with auth)

```bash
TOKEN="your-token-here"

curl http://localhost:8000/api/devices \
  -H "Authorization: Bearer $TOKEN"
```

### List Alerts

```bash
curl "http://localhost:8000/api/alerts?severity=critical&status=open" \
  -H "Authorization: Bearer $TOKEN"
```

### Acknowledge Alert

```bash
curl -X POST http://localhost:8000/api/alerts/123/acknowledge \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"comment": "Investigating the issue"}'
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in `backend/` directory:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Database
DATABASE_PATH=../network_monitor.db
```

### CORS Configuration

By default, the API allows requests from:

- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)

Add more origins in `config.py` or `.env` file.

---

## 📚 Response Formats

### Success Response

```json
{
  "id": 123,
  "name": "Device Name",
  "status": "online",
  "created_at": "2025-10-18T12:00:00"
}
```

### Error Response

```json
{
  "error": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content (successful delete)
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

---

## 🔐 Security

### Default Credentials

**⚠️ Change these in production!**

```
Username: admin
Password: admin123!
```

### Password Requirements

- Minimum 8 characters
- Required for all user accounts

### Token Security

- **Algorithm:** HS256
- **Expiration:** 24 hours
- **Storage:** Client-side (localStorage/sessionStorage)
- **Transmission:** Authorization header only

### Best Practices

1. **Always use HTTPS in production**
2. **Change default admin password immediately**
3. **Rotate SECRET_KEY regularly**
4. **Set shorter token expiration (1-2 hours)**
5. **Implement token refresh mechanism**
6. **Add rate limiting**
7. **Enable CORS only for trusted origins**

---

## 🐛 Troubleshooting

### Server won't start

**Issue:** Port already in use

```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Use a different port
uvicorn src.main:app --port 8001
```

### Authentication fails

**Issue:** Invalid token or expired

- Check token hasn't expired (24 hours by default)
- Verify token is sent in Authorization header
- Ensure Bearer prefix is included

### CORS errors

**Issue:** Frontend can't connect

- Add frontend origin to CORS_ORIGINS in config
- Check that CORS middleware is enabled
- Verify Origin header in browser dev tools

### WebSocket connection fails

**Issue:** Connection drops or won't establish

- Check WebSocket URL uses `ws://` (or `wss://` for HTTPS)
- Verify server is running
- Check firewall settings
- Look for connection timeout issues

---

## 📖 Additional Resources

- **Full Documentation:** `docs/PHASE_5.1_COMPLETE.md`
- **Authentication Guide:** `docs/AUTH_QUICK_REFERENCE.md`
- **API Explorer:** http://localhost:8000/docs (when server running)
- **ReDoc:** http://localhost:8000/redoc (when server running)

---

## 📞 Support

For issues or questions:

1. Check the full documentation in `docs/`
2. Review test files in `backend/`
3. Check server logs for error messages
4. Use interactive API docs at `/docs`

---

**Last Updated:** October 18, 2025
**API Version:** 1.0
**Status:** ✅ Production Ready
