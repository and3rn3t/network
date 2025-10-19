# Backend API

FastAPI backend for the UniFi Network Monitor web dashboard.

## Features

- **REST API** - Full CRUD operations for devices, alerts, rules, and channels
- **Real-time Updates** - WebSocket support for live data (coming in Phase 5.1.2)
- **Authentication** - JWT-based authentication (coming in Phase 5.1.3)
- **Analytics** - Metrics summaries, trends, and health scores
- **Auto Documentation** - Swagger UI at `/docs` and ReDoc at `/redoc`

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update settings:

```bash
cp .env.example .env
```

Edit `.env`:

```
SECRET_KEY=your-secret-key-here
DATABASE_PATH=../network_monitor.db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Run the Server

```bash
# Development mode with auto-reload
python src/main.py

# Or using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- **API**: <http://localhost:8000>
- **Docs**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## API Endpoints

### Health

- `GET /health` - Health check
- `GET /api/health` - API health check

### Devices

- `GET /api/devices` - List all devices
- `GET /api/devices/{id}` - Get device details
- `GET /api/devices/{id}/metrics` - Get device metrics history
- `GET /api/devices/{id}/alerts` - Get device alerts

### Alerts

- `GET /api/alerts` - List all alerts
- `GET /api/alerts/{id}` - Get alert details
- `POST /api/alerts/{id}/acknowledge` - Acknowledge alert
- `POST /api/alerts/{id}/resolve` - Resolve alert
- `GET /api/alerts/stats/summary` - Get alert statistics

### Rules

- `GET /api/rules` - List all alert rules
- `GET /api/rules/{id}` - Get rule details
- `POST /api/rules` - Create new rule
- `PUT /api/rules/{id}` - Update rule
- `DELETE /api/rules/{id}` - Delete rule
- `POST /api/rules/{id}/enable` - Enable rule
- `POST /api/rules/{id}/disable` - Disable rule

### Channels

- `GET /api/channels` - List notification channels
- `GET /api/channels/{id}` - Get channel details
- `POST /api/channels` - Create new channel
- `PUT /api/channels/{id}` - Update channel
- `DELETE /api/channels/{id}` - Delete channel

### Analytics

- `GET /api/analytics/metrics/summary` - Get metrics summary
- `GET /api/analytics/trends` - Get metric trends
- `GET /api/analytics/health-score` - Get network health score

### WebSocket (NEW!)

- `WS /api/ws` - WebSocket endpoint for real-time updates
- `GET /api/ws/stats` - Get WebSocket connection statistics

#### WebSocket Usage

Connect to `ws://localhost:8000/api/ws?client_id=your-client-id`

**Subscribe to Updates:**

```json
{
  "type": "subscribe",
  "room": "metrics" // or "alerts", "devices", "health"
}
```

**Available Rooms:**

- `metrics` - Real-time device metrics (30s interval)
- `alerts` - Alert notifications (immediate)
- `devices` - Device status changes (immediate)
- `health` - Network health updates (periodic)

**Test WebSocket:** Open `websocket_test.html` in your browser

## Project Structure

```
backend/
├── src/
│   ├── api/              # API route handlers
│   │   ├── devices.py
│   │   ├── alerts.py
│   │   ├── rules.py
│   │   ├── channels.py
│   │   ├── analytics.py
│   │   └── health.py
│   ├── auth/             # Authentication (Phase 5.1.3)
│   ├── schemas/          # Pydantic models (optional)
│   ├── services/         # Business logic
│   │   └── database_service.py
│   ├── middleware/       # Custom middleware
│   │   └── error_handler.py
│   ├── config.py         # Configuration
│   └── main.py           # FastAPI app
├── tests/                # Test files
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## Development

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type check
mypy src/
```

## Next Steps (Phase 5.1 Remaining)

- [ ] **WebSocket Server** - Real-time updates for metrics and alerts
- [ ] **Authentication** - JWT token-based authentication
- [ ] **Testing** - Unit and integration tests
- [ ] **API Documentation** - Enhanced docs with examples

## Status

✅ Project structure created
✅ REST API endpoints implemented
✅ Error handling middleware
✅ Database integration
⏳ WebSocket support (next)
⏳ Authentication (next)
⏳ Testing (next)

---

**Phase 5.1 Progress**: REST API Complete, WebSocket & Auth Next
