# Database Access Fix - November 12, 2025

## Problem Identified

The WebSocket broadcasts and analytics endpoints were failing because the code was trying to access database rows using **integer indices** (`row[0]`, `row[1]`), but the `Database` class methods `fetch_one()` and `fetch_all()` return **dictionaries**, not tuples.

## Root Cause

```python
# Database class returns dictionaries:
row = db.fetch_one("SELECT COUNT(*) as total FROM devices")
# Returns: {'total': 6}

# But code was trying to access by index:
total = row[0]  # ❌ FAILS - dictionaries don't support integer indexing
```

## Files Fixed

### 1. `backend/src/api/analytics.py` - Network Insights Endpoint

**Fixed 3 locations:**

```python
# BEFORE (broken):
device_row = db.fetch_one(device_query)
total_devices = device_row[0] if device_row else 0
online_devices = device_row[1] if device_row else 0

# AFTER (fixed):
device_row = db.fetch_one(device_query)
total_devices = device_row["total"] if device_row else 0
online_devices = device_row["online"] if device_row else 0
```

```python
# BEFORE (broken):
avg_metrics = {row[0]: round(row[1], 2) for row in metrics_rows}

# AFTER (fixed):
avg_metrics = {row["metric_name"]: round(row["avg_val"], 2) for row in metrics_rows}
```

```python
# BEFORE (broken):
active_alerts = alert_row[0] if alert_row else 0

# AFTER (fixed):
# Also added try/except since alert_history table doesn't exist yet
active_alerts = 0
try:
    alert_query = """
        SELECT COUNT(*) as alert_count
        FROM alert_history
        WHERE status = 'triggered' AND triggered_at >= ?
    """
    alert_row = db.fetch_one(alert_query, (since_24h.isoformat(),))
    active_alerts = alert_row["alert_count"] if alert_row else 0
except Exception:
    pass  # Alert system not configured
```

### 2. `backend/src/api/websocket.py` - Broadcast Functions

**Fixed metrics broadcast:**

```python
# BEFORE (broken):
metrics_data = [
    {
        "device_id": row[0],
        "device_name": row[1],
        "metric_name": row[2],
        "metric_value": row[3],
        "recorded_at": row[4],
    }
    for row in rows
]

# AFTER (fixed):
metrics_data = [
    {
        "device_id": row["id"],
        "device_name": row["name"],
        "metric_name": row["metric_name"],
        "metric_value": row["metric_value"],
        "recorded_at": row["recorded_at"],
    }
    for row in rows
]
```

**Fixed health broadcast:**

```python
# BEFORE (broken):
device_row = db.fetch_one(device_query)
total_devices = device_row[0] if device_row else 0
online_devices = device_row[1] if device_row else 0
active_alerts = alert_row[0] if alert_row else 0

# AFTER (fixed):
device_row = db.fetch_one(device_query)
total_devices = device_row["total"] if device_row else 0
online_devices = device_row["online"] if device_row else 0

# Also wrapped alert query in try/except
active_alerts = 0
try:
    alert_row = db.fetch_one(alert_query, (since_24h.isoformat(),))
    active_alerts = alert_row["alert_count"] if alert_row else 0
except Exception:
    pass  # Alert system not configured
```

## Verification Tests Created

### Test Scripts

1. **`scripts/test_db_fetch.py`** - Verified fetch_one/fetch_all return dictionaries
2. **`scripts/test_analytics_query.py`** - Tested all analytics endpoint queries
3. **`scripts/test_websocket_queries.py`** - Tested all broadcast queries

### Test Results

```
✅ Device query: {'total': 6, 'online': 6}
✅ Metrics query: 6 metrics with avg values
✅ Metrics broadcast query: 100 recent metrics
✅ Health calculation: Score 100.0 (excellent)
```

## Additional Fixes

1. **Alert table handling**: Added try/except blocks since `alert_history` table doesn't exist yet
2. **Column naming**: Used named columns in COUNT queries (`COUNT(*) as alert_count`) for clarity
3. **Database schema compatibility**: All queries now match actual schema:
   - `unifi_devices` table with `state` column (1=online)
   - `unifi_device_metrics` table with `metric_name`, `metric_value`, `recorded_at`

## What's Required Now

**⚠️ Backend MUST be restarted** for these fixes to take effect:

```powershell
# In backend terminal:
# 1. Stop: Ctrl+C
# 2. Restart:
python backend/src/main.py
```

After restart:
- ✅ Analytics endpoint `/api/analytics/network-insights` will work
- ✅ Metrics broadcasts will start every 30 seconds
- ✅ Health broadcasts will start every 60 seconds

## Expected Behavior After Restart

### Analytics Endpoint Response

```json
{
  "network_summary": {
    "total_devices": 6,
    "online_devices": 6,
    "offline_devices": 0,
    "active_alerts": 0
  },
  "avg_metrics_24h": {
    "connected_clients": 5.2,
    "cpu_usage": 15.5,
    "memory_usage": 45.3,
    "satisfaction": 100.0,
    "temperature": 45.2,
    "uptime": 86400.0
  },
  "insights": [
    "✅ All devices healthy (100% online)",
    "✅ CPU usage is healthy (15.5%)"
  ],
  "recommendations": [],
  "generated_at": "2025-11-12T..."
}
```

### WebSocket Metrics Broadcast (every 30s)

```json
{
  "type": "metrics_update",
  "data": [
    {
      "device_id": 2,
      "device_name": "Office AP",
      "metric_name": "connected_clients",
      "metric_value": 7.0,
      "recorded_at": "2025-11-13 01:44:17"
    }
  ],
  "count": 100,
  "timestamp": "2025-11-12T19:45:00"
}
```

### WebSocket Health Broadcast (every 60s)

```json
{
  "type": "health_update",
  "data": {
    "health_score": 100.0,
    "health_status": "excellent",
    "total_devices": 6,
    "online_devices": 6,
    "offline_devices": 0,
    "active_alerts": 0
  },
  "timestamp": "2025-11-12T19:45:00"
}
```

## Testing After Restart

Run the comprehensive test:

```powershell
python scripts/test_realtime_system.py
```

Expected results:
- ✅ API Health: PASSED
- ✅ WebSocket Stats: PASSED  
- ✅ Analytics Endpoints: PASSED (was failing before)
- ✅ WebSocket Connection: PASSED
- ✅ Metrics Broadcasts: Received (was failing before)
- ✅ Health Broadcasts: Received (was failing before)

---

**Status**: All code fixes complete. Backend restart required for testing.
