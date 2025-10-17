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

## Additional Resources

- [Official UniFi API Documentation](https://developer.ui.com/site-manager-api/gettingstarted)
- [UniFi Community Forums](https://community.ui.com/)
- [UniFi API GitHub Discussions](https://github.com/topics/unifi-api)

## Notes

- API endpoints and response formats are subject to change
- Always check the official documentation for the most up-to-date information
- Some features may require specific UniFi controller versions
- Beta/Early Access features may have limited availability
