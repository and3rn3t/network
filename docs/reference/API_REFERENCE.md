# UniFi Site Manager API Reference

This document provides detailed information about the UniFi Site Manager API endpoints and their usage.

## Base Information

- **Base URL:** `https://api.ui.com/v1`
- **Authentication:** API Key via `X-API-KEY` header
- **Response Format:** JSON
- **Rate Limits:**
  - Early Access: 100 requests/minute
  - Stable Release: 10,000 requests/minute

## Authentication

All API requests require an API key in the request header:

```http
X-API-KEY: your-api-key-here
```

### Getting an API Key

1. Visit [UniFi Site Manager](https://unifi.ui.com)
2. Sign in to your account
3. Navigate to Settings → API
4. Click "Create API Key"
5. Copy and securely store your API key

## Endpoints

### Hosts (Devices)

#### List All Hosts

**Endpoint:** `GET /hosts`

**Description:** Retrieve a list of all network devices managed by your UniFi controller.

**Request:**

```http
GET https://api.ui.com/v1/hosts
X-API-KEY: your-api-key
```

**Response:**

```json
[
  {
    "id": "host-id-123",
    "name": "Access Point Living Room",
    "model": "UAP-AC-PRO",
    "mac": "00:11:22:33:44:55",
    "ip": "192.168.1.100",
    "state": "online",
    "version": "4.3.28.11361",
    "uptime": 86400
  }
]
```

**Fields:**

- `id`: Unique identifier for the host
- `name`: Friendly name of the device
- `model`: Device model number
- `mac`: MAC address
- `ip`: IP address
- `state`: Current state (online, offline, etc.)
- `version`: Firmware version
- `uptime`: Uptime in seconds

#### Get Host Details

**Endpoint:** `GET /hosts/{hostId}`

**Description:** Retrieve detailed information about a specific host.

**Request:**

```http
GET https://api.ui.com/v1/hosts/{hostId}
X-API-KEY: your-api-key
```

**Parameters:**

- `hostId` (path): The unique identifier of the host

**Response:**

```json
{
  "id": "host-id-123",
  "name": "Access Point Living Room",
  "model": "UAP-AC-PRO",
  "mac": "00:11:22:33:44:55",
  "ip": "192.168.1.100",
  "state": "online",
  "version": "4.3.28.11361",
  "uptime": 86400,
  "cpu": 15,
  "memory": 45,
  "temperature": 42,
  "clients": 8,
  "tx_bytes": 1048576000,
  "rx_bytes": 2097152000
}
```

**Additional Fields:**

- `cpu`: CPU usage percentage
- `memory`: Memory usage percentage
- `temperature`: Temperature in Celsius
- `clients`: Number of connected clients
- `tx_bytes`: Transmitted bytes
- `rx_bytes`: Received bytes

#### Get Host Status

**Endpoint:** `GET /hosts/{hostId}/status`

**Description:** Get the current operational status of a host.

**Request:**

```http
GET https://api.ui.com/v1/hosts/{hostId}/status
X-API-KEY: your-api-key
```

**Response:**

```json
{
  "id": "host-id-123",
  "state": "online",
  "last_seen": "2025-10-17T22:45:00Z",
  "uptime": 86400,
  "cpu_usage": 15,
  "memory_usage": 45
}
```

#### Reboot Host

**Endpoint:** `POST /hosts/{hostId}/reboot`

**Description:** Remotely reboot a network device.

**Request:**

```http
POST https://api.ui.com/v1/hosts/{hostId}/reboot
X-API-KEY: your-api-key
```

**Response:**

```json
{
  "status": "success",
  "message": "Reboot command sent to device"
}
```

⚠️ **Warning:** This will temporarily disconnect the device and any clients connected to it.

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid or missing API key
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "The request was invalid or cannot be served"
  }
}
```

## Best Practices

### 1. Rate Limiting

Implement exponential backoff when hitting rate limits:

```python
import time

def make_request_with_retry(client, method, max_retries=3):
    for attempt in range(max_retries):
        try:
            return method()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                raise
```

### 2. Caching

Cache frequently accessed data to reduce API calls:

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=128)
def get_hosts_cached(timestamp):
    return client.get_hosts()

# Use with 5-minute cache
timestamp = datetime.now().replace(second=0, microsecond=0)
timestamp = timestamp - timedelta(minutes=timestamp.minute % 5)
hosts = get_hosts_cached(timestamp)
```

### 3. Error Handling

Always handle errors gracefully:

```python
try:
    hosts = client.get_hosts()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 429:
        print("Rate limit exceeded")
    else:
        print(f"HTTP error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

### 4. Logging

Log all API interactions for debugging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/api.log'
)
```

## Alert System API (Local)

### AlertManager

The `AlertManager` class provides a high-level API for managing alerts, rules, and notifications.

#### Initialization

```python
from database.database import Database
from alerts import AlertManager

db = Database("data/unifi_network.db")
db.initialize()
db.initialize_alerts()

manager = AlertManager(db)
# or use as context manager
with AlertManager(db) as manager:
    # operations here
    pass
```

#### Rule Management

**Create Rule:**

```python
from alerts import AlertRule

rule = AlertRule(
    name="High CPU Alert",
    rule_type="threshold",
    metric_name="cpu_usage",
    condition="gt",
    threshold=85.0,
    severity="warning",
    notification_channels=["email-1"],
    cooldown_minutes=30
)
created_rule = manager.create_rule(rule)
```

**List Rules:**

```python
# All rules
rules = manager.list_rules()

# Only enabled rules
enabled_rules = manager.list_rules(enabled_only=True)
```

**Get Rule:**

```python
rule = manager.get_rule(rule_id=1)
```

**Update Rule:**

```python
rule.threshold = 90.0
manager.update_rule(rule)
```

**Enable/Disable Rule:**

```python
manager.enable_rule(rule_id=1)
manager.disable_rule(rule_id=1)
```

**Delete Rule:**

```python
manager.delete_rule(rule_id=1)
```

#### Alert Operations

**Evaluate Rules:**

```python
# Evaluate all enabled rules
alerts = manager.evaluate_rules()
```

**Get Alert:**

```python
alert = manager.get_alert(alert_id=1)
```

**List Active Alerts:**

```python
# All active
active = manager.list_active_alerts()

# Filter by severity
critical = manager.list_active_alerts(severity="critical")

# Filter by host
host_alerts = manager.list_active_alerts(host_id="00:11:22:33:44:55")
```

**List Recent Alerts:**

```python
# Last 24 hours
recent = manager.list_recent_alerts(hours=24)
```

**Acknowledge Alert:**

```python
manager.acknowledge_alert(alert_id=1, acknowledged_by="admin@example.com")
```

**Resolve Alert:**

```python
manager.resolve_alert(alert_id=1)
```

**Resolve Stale Alerts:**

```python
count = manager.resolve_stale_alerts(hours=48)
```

**Get Alert Statistics:**

```python
stats = manager.get_alert_statistics(days=7)
# Returns: {'info': 5, 'warning': 12, 'critical': 2, 'total': 19}
```

#### Notification Management

**Register Notifier:**

```python
from alerts.notifiers import EmailNotifier, WebhookNotifier

# Email
email_config = {
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "alerts@example.com",
    "smtp_password": "app_password",
    "from_email": "alerts@example.com",
    "to_emails": ["admin@example.com"],
    "use_tls": True
}
manager.register_notifier("email", EmailNotifier(email_config))

# Slack
slack_config = {
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "platform": "slack"
}
manager.register_notifier("slack", WebhookNotifier(slack_config))
```

**Create Channel:**

```python
from alerts import NotificationChannel

channel = NotificationChannel(
    id="email-ops",
    name="Operations Email",
    channel_type="email",
    config=email_config,
    enabled=True
)
manager.create_channel(channel)
```

**List Channels:**

```python
# All channels
channels = manager.list_channels()

# Filter by type
email_channels = manager.list_channels(channel_type="email")

# Only enabled
enabled = manager.list_channels(enabled_only=True)
```

**Enable/Disable Channel:**

```python
manager.enable_channel("email-ops")
manager.disable_channel("email-ops")
```

#### Mute Management

**Mute Rule:**

```python
# Mute for 2 hours
mute = manager.mute_rule(
    rule_id=1,
    muted_by="admin",
    duration_minutes=120,
    reason="Maintenance window"
)

# Mute indefinitely
manager.mute_rule(rule_id=1, muted_by="admin")

# Mute for specific host
manager.mute_rule(
    rule_id=1,
    muted_by="admin",
    host_id="00:11:22:33:44:55",
    duration_minutes=60
)
```

**Unmute Rule:**

```python
success = manager.unmute_rule(rule_id=1)

# Unmute for specific host
manager.unmute_rule(rule_id=1, host_id="00:11:22:33:44:55")
```

**List Active Mutes:**

```python
mutes = manager.list_active_mutes()
```

**Cleanup Expired Mutes:**

```python
count = manager.cleanup_expired_mutes()
```

### CLI Commands

See [CLI_USER_GUIDE.md](CLI_USER_GUIDE.md) for complete command-line interface documentation.

Quick examples:

```bash
# Rule management
python -m alerts.cli rule create --name "High CPU" --type threshold \
  --metric cpu_usage --condition gt --threshold 85 \
  --severity warning --channels email-1

python -m alerts.cli rule list
python -m alerts.cli rule show 1

# Alert management
python -m alerts.cli alert list
python -m alerts.cli alert stats
python -m alerts.cli alert acknowledge 1 --by admin

# Channel management
python -m alerts.cli channel list
python -m alerts.cli channel create --id email-1 --name "Admin Email" \
  --type email --config email_config.json

# Mute management
python -m alerts.cli mute create 1 --duration 120 --reason "Maintenance"
python -m alerts.cli mute list

# Evaluation
python -m alerts.cli evaluate --verbose
```

## Additional Resources

- [Official UniFi API Documentation](https://developer.ui.com/site-manager-api/gettingstarted)
- [UniFi Community Forums](https://community.ui.com/)
- [Alert System Quick Reference](ALERT_SYSTEM_QUICKREF.md)
- [CLI User Guide](CLI_USER_GUIDE.md)

## Notes

- API endpoints and response formats are subject to change
- Always check the official documentation for the most up-to-date information
- Some features may require specific UniFi controller versions
- Beta/Early Access features may have limited availability
- Alert system APIs are local (not UniFi API endpoints)
- All alert operations use SQLite database for persistence
