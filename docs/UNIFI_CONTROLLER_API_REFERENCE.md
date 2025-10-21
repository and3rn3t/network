# UniFi Local Controller API Reference

This document provides detailed information about the UniFi Local Controller API implementation, including all available methods, parameters, and return values.

## Overview

The `UniFiController` class provides a Python interface to interact with UniFi Network Controllers, including standard controllers and UDM/UDM Pro devices.

### Features

- ✅ **Automatic Controller Detection**: Detects UDM vs standard controller and uses appropriate endpoints
- ✅ **Session Management**: Efficient session reuse with automatic cookie handling
- ✅ **Error Handling**: Comprehensive error handling with specific exception types
- ✅ **MAC Validation**: Automatic MAC address format validation and normalization
- ✅ **Retry Logic**: Exponential backoff retry for transient failures
- ✅ **Type Safety**: Full type hints for all methods
- ✅ **Thread Safety**: Safe for concurrent operations

### Performance Characteristics

Based on testing with UDM Pro (6 devices, 36 clients):

| Operation     | Average Response Time |
| ------------- | --------------------- |
| login()       | ~500ms                |
| get_sites()   | ~13ms                 |
| get_devices() | ~34ms                 |
| get_clients() | ~23ms                 |
| get_device()  | ~32ms                 |

**Memory Usage**: <1 MB typical, <70KB per device, <10KB per client

**Session Reuse Benefit**: 170% efficiency improvement over creating new sessions

## Installation

```python
from src.unifi_controller import UniFiController
```

## Quick Start

```python
from src.unifi_controller import UniFiController

# Initialize controller
controller = UniFiController(
    host='192.168.1.1',
    port=443,
    username='admin',
    password='your-password',
    verify_ssl=False
)

try:
    # Login
    controller.login()

    # Get devices
    devices = controller.get_devices()
    print(f"Found {len(devices)} devices")

    # Get clients
    clients = controller.get_clients()
    print(f"Found {len(clients)} clients")

finally:
    # Always logout
    controller.logout()
```

## Constructor

### `UniFiController(host, port, username, password, verify_ssl, timeout)`

Initialize a UniFi Controller client.

**Parameters**:

- **host** (`str`): Controller IP address or hostname

  - Example: `'192.168.1.1'`

- **port** (`int`): Controller HTTPS port

  - Standard controller: `8443`
  - UDM/UDM Pro: `443`

- **username** (`str`): Local administrator username

  - Must be a local account, not cloud/SSO
  - Example: `'admin'`

- **password** (`str`): Local administrator password

  - Example: `'password123'`

- **verify_ssl** (`bool`, optional): Verify SSL certificates

  - Default: `True`
  - Set to `False` for self-signed certificates (development only)

- **timeout** (`int`, optional): Request timeout in seconds
  - Default: `30`
  - Increase for slow networks or busy controllers

**Returns**: `UniFiController` instance

**Example**:

```python
# Standard controller
controller = UniFiController(
    host='192.168.1.10',
    port=8443,
    username='admin',
    password='password',
    verify_ssl=False
)

# UDM Pro
controller = UniFiController(
    host='192.168.1.1',
    port=443,
    username='admin',
    password='password',
    verify_ssl=False
)
```

## Authentication Methods

### `login()`

Authenticate with the controller and create a session.

**Parameters**: None

**Returns**: `dict` - Login response data from controller

**Raises**:

- `UniFiAuthError`: If authentication fails (wrong credentials, account locked)
- `UniFiConnectionError`: If unable to connect to controller
- `UniFiTimeoutError`: If request times out

**Example**:

```python
try:
    response = controller.login()
    print("Login successful!")
except UniFiAuthError as e:
    print(f"Authentication failed: {e}")
except UniFiConnectionError as e:
    print(f"Connection failed: {e}")
```

**Notes**:

- Creates a persistent session stored in `controller.session`
- Session cookies are automatically reused for subsequent requests
- Must call `login()` before any other API operations
- UDM detection happens automatically during login

### `logout()`

End the current session and clean up resources.

**Parameters**: None

**Returns**: `None`

**Raises**:

- `UniFiAPIError`: If logout request fails (usually non-critical)

**Example**:

```python
controller.logout()
print("Logged out successfully")
```

**Notes**:

- Always call `logout()` when done to clean up server resources
- Use `try/finally` block to ensure logout happens even if errors occur
- Failure to logout may leave sessions open on controller

## Site Methods

### `get_sites()`

Retrieve list of all sites managed by the controller.

**Parameters**: None

**Returns**: `list[dict]` - List of site objects

**Raises**:

- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If API request fails

**Retry Behavior**: Automatic retry with exponential backoff (max 3 attempts)

**Example**:

```python
sites = controller.get_sites()

for site in sites:
    print(f"Site: {site['desc']} (Name: {site['name']})")
    print(f"  ID: {site['_id']}")
    print(f"  Devices: {site.get('num_devices', 0)}")
    print(f"  Adopted: {site.get('num_adopted', 0)}")
```

**Response Fields**:

```python
{
    '_id': '5f2c...',           # Unique site ID
    'name': 'default',          # Site name (URL-safe)
    'desc': 'My Home Network',  # Human-readable description
    'num_devices': 6,           # Number of devices
    'num_adopted': 6,           # Number of adopted devices
    'role': 'admin',            # User role for this site
    'attr_hidden_id': 'default' # Hidden ID attribute
}
```

**Notes**:

- Most home installations have one site named 'default'
- Enterprise installations may have multiple sites
- Site 'name' field is used as identifier in API calls

## Device Methods

### `get_devices(site='default')`

Retrieve list of all devices (switches, APs, gateways) from a site.

**Parameters**:

- **site** (`str`, optional): Site name
  - Default: `'default'`
  - Get from `get_sites()` response

**Returns**: `list[dict]` - List of device objects

**Raises**:

- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If API request fails

**Retry Behavior**: Automatic retry with exponential backoff (max 3 attempts)

**Example**:

```python
devices = controller.get_devices(site='default')

for device in devices:
    state = '🟢 Online' if device['state'] == 1 else '🔴 Offline'
    print(f"{state} {device['name']} ({device['type']})")
    print(f"  Model: {device['model']}")
    print(f"  MAC: {device['mac']}")
    print(f"  IP: {device['ip']}")
    print(f"  Version: {device.get('version', 'Unknown')}")
    print(f"  Uptime: {device.get('uptime', 0)} seconds")
```

**Response Fields**:

```python
{
    '_id': '5f2c...',                    # Unique device ID
    'mac': 'aa:bb:cc:dd:ee:ff',          # MAC address (lowercase with colons)
    'name': 'Office Switch',             # Device name
    'type': 'usw',                       # Device type (see types below)
    'model': 'US8P150',                  # Model number
    'version': '6.2.14.13665',           # Firmware version
    'state': 1,                          # State (1=connected, 0=disconnected)
    'ip': '192.168.1.5',                 # IP address
    'uptime': 86400,                     # Uptime in seconds
    'adopted': True,                     # Adoption status
    'disabled': False,                   # Whether device is disabled
    'satisfaction': 100,                 # Client satisfaction (0-100)
    'num_sta': 5,                        # Number of connected clients (APs)
    'bytes': 1234567890,                 # Total bytes transferred
    'last_seen': 1634567890,             # Last seen timestamp
    'led_override': 'default',           # LED override setting
    'led_override_color': '#0000ff',     # LED color if overridden
    'config_network': {...},             # Network configuration
    'port_table': [...]                  # Port information (switches)
}
```

**Device Types**:

| Type  | Description            |
| ----- | ---------------------- |
| `usw` | UniFi Switch           |
| `uap` | UniFi Access Point     |
| `ugw` | UniFi Gateway          |
| `udm` | UniFi Dream Machine    |
| `uxg` | UniFi Next-Gen Gateway |
| `ubb` | UniFi Building Bridge  |

**Notes**:

- Device `state` field: `1` = online, `0` = offline/disconnected
- MAC addresses returned in lowercase with colon separators
- `num_sta` only available for access points
- `port_table` only available for switches

### `get_device(mac, site='default')`

Retrieve detailed information about a specific device by MAC address.

**Parameters**:

- **mac** (`str`): Device MAC address

  - Accepts formats: `aa:bb:cc:dd:ee:ff`, `AA-BB-CC-DD-EE-FF`, `aabbccddeeff`
  - Automatically normalized and validated

- **site** (`str`, optional): Site name
  - Default: `'default'`

**Returns**: `dict | None` - Device object or None if not found

**Raises**:

- `ValueError`: If MAC address format is invalid
- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If API request fails

**Example**:

```python
# Various MAC formats accepted
mac = 'aa:bb:cc:dd:ee:ff'  # or 'AA-BB-CC-DD-EE-FF' or 'aabbccddeeff'

device = controller.get_device(mac)
if device:
    print(f"Device: {device['name']}")
    print(f"Status: {'Online' if device['state'] == 1 else 'Offline'}")
    print(f"Model: {device['model']}")
else:
    print("Device not found")
```

**Notes**:

- MAC address is validated before API call
- Returns `None` if device doesn't exist
- More efficient than filtering `get_devices()` results

### `reboot_device(mac, site='default')`

Reboot a specific device.

**Parameters**:

- **mac** (`str`): Device MAC address (any format)
- **site** (`str`, optional): Site name (default: `'default'`)

**Returns**: `dict` - Command response from controller

**Raises**:

- `ValueError`: If MAC address format is invalid
- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If command fails

**Example**:

```python
response = controller.reboot_device('aa:bb:cc:dd:ee:ff')
print("Device reboot initiated")
```

**Notes**:

- Device will go offline for ~1-2 minutes
- Does not wait for device to come back online
- Use `get_device()` to check status after reboot

### `locate_device(mac, site='default', enable=True)`

Enable or disable device locating (LED flashing).

**Parameters**:

- **mac** (`str`): Device MAC address (any format)
- **site** (`str`, optional): Site name (default: `'default'`)
- **enable** (`bool`, optional): Enable or disable locate (default: `True`)

**Returns**: `dict` - Command response from controller

**Raises**:

- `ValueError`: If MAC address format is invalid
- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If command fails

**Example**:

```python
# Start blinking LED
controller.locate_device('aa:bb:cc:dd:ee:ff', enable=True)
print("Device is now blinking")

# Stop blinking LED
controller.locate_device('aa:bb:cc:dd:ee:ff', enable=False)
print("Device stopped blinking")
```

**Notes**:

- LED will blink until disabled or device is rebooted
- Useful for physically identifying devices
- Not all devices support this feature

### `rename_device(mac, name, site='default')`

Rename a device.

**Parameters**:

- **mac** (`str`): Device MAC address (any format)
- **name** (`str`): New device name
- **site** (`str`, optional): Site name (default: `'default'`)

**Returns**: `dict` - Updated device configuration

**Raises**:

- `ValueError`: If MAC address format is invalid
- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If command fails

**Example**:

```python
controller.rename_device('aa:bb:cc:dd:ee:ff', 'Office Switch')
print("Device renamed successfully")
```

**Notes**:

- Name appears in controller UI and API responses
- Name should be descriptive and unique
- Changes take effect immediately

### `restart_device_port(mac, port_idx, site='default')`

Restart a specific port on a switch (PoE cycle).

**Parameters**:

- **mac** (`str`): Switch MAC address (any format)
- **port_idx** (`int`): Port number (1-based, usually 1-48)
- **site** (`str`, optional): Site name (default: `'default'`)

**Returns**: `dict` - Command response from controller

**Raises**:

- `ValueError`: If MAC address format is invalid or port number invalid
- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If command fails

**Example**:

```python
# Restart port 8 (PoE cycle)
controller.restart_device_port('aa:bb:cc:dd:ee:ff', port_idx=8)
print("Port 8 restarted")
```

**Notes**:

- Only works on PoE switches
- Power cycles the port (off then on)
- Connected device will reboot
- Port number is 1-based (port 1 = first port)

## Client Methods

### `get_clients(site='default')`

Retrieve list of all active and recently active clients.

**Parameters**:

- **site** (`str`, optional): Site name (default: `'default'`)

**Returns**: `list[dict]` - List of client objects

**Raises**:

- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If API request fails

**Retry Behavior**: Automatic retry with exponential backoff (max 3 attempts)

**Example**:

```python
clients = controller.get_clients()

for client in clients:
    hostname = client.get('hostname', 'Unknown')
    mac = client['mac']
    ip = client.get('ip', 'No IP')

    # Connection info
    is_wired = client.get('is_wired', False)
    connection = 'Wired' if is_wired else f"WiFi ({client.get('essid', 'Unknown')})"

    print(f"{hostname} ({mac})")
    print(f"  IP: {ip}")
    print(f"  Connection: {connection}")
    print(f"  Device: {client.get('ap_name', 'Unknown')}")
```

**Response Fields**:

```python
{
    '_id': '5f2c...',                    # Unique client ID
    'mac': 'aa:bb:cc:dd:ee:ff',          # Client MAC address
    'hostname': 'Johns-iPhone',          # Client hostname
    'name': 'Johns iPhone',              # Friendly name (if set)
    'ip': '192.168.1.100',               # IP address
    'is_wired': False,                   # Wired vs wireless
    'is_guest': False,                   # Guest network client
    'essid': 'My WiFi',                  # WiFi SSID (wireless only)
    'channel': 36,                       # WiFi channel (wireless only)
    'signal': -42,                       # Signal strength in dBm (wireless only)
    'noise': -95,                        # Noise floor in dBm (wireless only)
    'ap_mac': 'bb:cc:dd:ee:ff:00',      # Connected AP MAC (wireless only)
    'ap_name': 'Living Room AP',         # Connected AP name (wireless only)
    'sw_mac': 'cc:dd:ee:ff:00:11',      # Connected switch MAC (wired only)
    'sw_port': 8,                        # Connected switch port (wired only)
    'tx_bytes': 1234567,                 # Bytes transmitted
    'rx_bytes': 7654321,                 # Bytes received
    'tx_rate': 433300,                   # TX rate in Kbps
    'rx_rate': 433300,                   # RX rate in Kbps
    'uptime': 3600,                      # Connection uptime in seconds
    'first_seen': 1634567890,            # First seen timestamp
    'last_seen': 1634571490,             # Last seen timestamp
    'satisfaction': 98,                  # Client satisfaction score (0-100)
    'blocked': False,                    # Whether client is blocked
    'noted': False,                      # Whether client has notes
    'use_fixedip': False,                # Whether client has fixed IP
    'network': 'LAN',                    # Network name
    'oui': 'Apple',                      # Manufacturer (from OUI)
    'usergroup_id': ''                   # User group ID (if assigned)
}
```

**Notes**:

- Includes both active and recently seen clients
- Wireless clients have additional fields (signal, channel, AP info)
- Wired clients have switch/port information
- Guest network clients marked with `is_guest=True`

### `get_client(mac, site='default')`

Retrieve information about a specific client by MAC address.

**Parameters**:

- **mac** (`str`): Client MAC address (any format)
- **site** (`str`, optional): Site name (default: `'default'`)

**Returns**: `dict | None` - Client object or None if not found

**Raises**:

- `ValueError`: If MAC address format is invalid
- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If API request fails

**Example**:

```python
client = controller.get_client('aa:bb:cc:dd:ee:ff')

if client:
    print(f"Client: {client.get('hostname', 'Unknown')}")
    print(f"IP: {client.get('ip', 'No IP')}")

    if client.get('is_wired'):
        print(f"Connected to switch port {client.get('sw_port')}")
    else:
        print(f"Connected to WiFi: {client.get('essid')}")
        print(f"Signal: {client.get('signal')} dBm")
else:
    print("Client not found or offline")
```

**Notes**:

- Only returns currently active or recently active clients
- Returns `None` if client hasn't been seen recently
- More efficient than filtering `get_clients()` results

### `block_client(mac, site='default')`

Block a client from accessing the network.

**Parameters**:

- **mac** (`str`): Client MAC address (any format)
- **site** (`str`, optional): Site name (default: `'default'`)

**Returns**: `dict` - Command response from controller

**Raises**:

- `ValueError`: If MAC address format is invalid
- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If command fails

**Example**:

```python
controller.block_client('aa:bb:cc:dd:ee:ff')
print("Client blocked")
```

**Notes**:

- Client is disconnected immediately
- Block persists across reboots
- Use `unblock_client()` to restore access
- Blocked clients cannot connect to any network

### `unblock_client(mac, site='default')`

Unblock a previously blocked client.

**Parameters**:

- **mac** (`str`): Client MAC address (any format)
- **site** (`str`, optional): Site name (default: `'default'`)

**Returns**: `dict` - Command response from controller

**Raises**:

- `ValueError`: If MAC address format is invalid
- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If command fails

**Example**:

```python
controller.unblock_client('aa:bb:cc:dd:ee:ff')
print("Client unblocked")
```

**Notes**:

- Client can connect again immediately
- Does not automatically reconnect client
- Use `reconnect_client()` to force reconnection

### `reconnect_client(mac, site='default')`

Force a client to reconnect (disconnect and allow immediate reconnection).

**Parameters**:

- **mac** (`str`): Client MAC address (any format)
- **site** (`str`, optional): Site name (default: `'default'`)

**Returns**: `dict` - Command response from controller

**Raises**:

- `ValueError`: If MAC address format is invalid
- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If command fails

**Example**:

```python
controller.reconnect_client('aa:bb:cc:dd:ee:ff')
print("Client reconnecting...")
```

**Notes**:

- Client is disconnected immediately
- Client will automatically reconnect if configured
- Useful for applying network configuration changes
- Wireless clients may roam to different AP

### `set_client_bandwidth_limit(mac, down_kbps, up_kbps, site='default')`

Set bandwidth limits for a specific client.

**Parameters**:

- **mac** (`str`): Client MAC address (any format)
- **down_kbps** (`int`): Download limit in Kbps (0 = unlimited)
- **up_kbps** (`int`): Upload limit in Kbps (0 = unlimited)
- **site** (`str`, optional): Site name (default: `'default'`)

**Returns**: `dict` - Updated client configuration

**Raises**:

- `ValueError`: If MAC address or bandwidth values invalid
- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If command fails

**Example**:

```python
# Limit to 10 Mbps down, 5 Mbps up
controller.set_client_bandwidth_limit(
    mac='aa:bb:cc:dd:ee:ff',
    down_kbps=10000,  # 10 Mbps
    up_kbps=5000      # 5 Mbps
)
print("Bandwidth limit applied")

# Remove limit
controller.set_client_bandwidth_limit(
    mac='aa:bb:cc:dd:ee:ff',
    down_kbps=0,  # Unlimited
    up_kbps=0     # Unlimited
)
print("Bandwidth limit removed")
```

**Notes**:

- Bandwidth limits in Kbps (1 Mbps = 1000 Kbps)
- Set to 0 to remove limits
- Limits persist across reconnections
- Applies to all connections from this MAC

### `authorize_guest(mac, minutes, site='default')`

Authorize a guest client for a specific duration.

**Parameters**:

- **mac** (`str`): Guest client MAC address (any format)
- **minutes** (`int`): Authorization duration in minutes
- **site** (`str`, optional): Site name (default: `'default'`)

**Returns**: `dict` - Command response from controller

**Raises**:

- `ValueError`: If MAC address format is invalid or minutes <= 0
- `UniFiAuthError`: If not authenticated
- `UniFiAPIError`: If command fails

**Example**:

```python
# Authorize guest for 4 hours
controller.authorize_guest('aa:bb:cc:dd:ee:ff', minutes=240)
print("Guest authorized for 4 hours")

# Authorize guest for 1 day
controller.authorize_guest('aa:bb:cc:dd:ee:ff', minutes=1440)
print("Guest authorized for 24 hours")
```

**Notes**:

- Only works for clients on guest networks
- Authorization expires automatically after specified time
- Client must be connected to guest network
- Use portal authentication for more control

## Helper Functions

### `validate_mac_address(mac)`

Validate MAC address format.

**Parameters**:

- **mac** (`str`): MAC address to validate

**Returns**: `bool` - True if valid, False otherwise

**Example**:

```python
from src.unifi_controller import validate_mac_address

# Valid formats
validate_mac_address('aa:bb:cc:dd:ee:ff')  # True
validate_mac_address('AA-BB-CC-DD-EE-FF')  # True
validate_mac_address('aabbccddeeff')       # True

# Invalid formats
validate_mac_address('invalid')            # False
validate_mac_address('aa:bb:cc:dd:ee')     # False (too short)
validate_mac_address('zz:bb:cc:dd:ee:ff')  # False (non-hex)
```

**Notes**:

- Accepts colons, dashes, or no separators
- Requires exactly 12 hex characters
- Case insensitive

### `normalize_mac_address(mac)`

Normalize MAC address to standard format (lowercase, no separators).

**Parameters**:

- **mac** (`str`): MAC address to normalize

**Returns**: `str` - Normalized MAC address

**Raises**:

- `ValueError`: If MAC address format is invalid

**Example**:

```python
from src.unifi_controller import normalize_mac_address

normalize_mac_address('aa:bb:cc:dd:ee:ff')  # 'aabbccddeeff'
normalize_mac_address('AA-BB-CC-DD-EE-FF')  # 'aabbccddeeff'
normalize_mac_address('AABBCCDDEEFF')       # 'aabbccddeeff'
```

**Notes**:

- Always returns lowercase without separators
- Validates format before normalization
- Used internally by all MAC-accepting methods

## Exception Classes

### `UniFiAPIError`

Base exception for all UniFi API errors.

**Attributes**:

- `message`: Error message
- `status_code`: HTTP status code (if applicable)
- `response`: Full response object (if applicable)

### `UniFiAuthError`

Authentication-related errors (401, 403).

**Common Causes**:

- Invalid username or password
- Expired session
- Insufficient permissions
- Account locked

### `UniFiConnectionError`

Network connection errors.

**Common Causes**:

- Controller unreachable
- Network connectivity issues
- Firewall blocking requests
- Wrong IP address or port

### `UniFiTimeoutError`

Request timeout errors.

**Common Causes**:

- Slow network
- Controller overloaded
- Timeout value too low

### `UniFiNotFoundError`

Resource not found errors (404).

**Common Causes**:

- Invalid endpoint
- Device/client doesn't exist
- Wrong site name
- UDM proxy prefix missing

### `UniFiRateLimitError`

Rate limiting errors (429).

**Common Causes**:

- Too many requests
- Multiple concurrent sessions
- Rapid login/logout cycles

**Attributes**:

- `retry_after`: Seconds to wait before retry (from Retry-After header)

### `UniFiServerError`

Server-side errors (5xx).

**Common Causes**:

- Controller internal error
- Service unavailable
- Database issues

## Error Handling Best Practices

```python
from src.unifi_controller import (
    UniFiController,
    UniFiAuthError,
    UniFiConnectionError,
    UniFiTimeoutError,
    UniFiRateLimitError,
    UniFiAPIError
)

controller = UniFiController(host='192.168.1.1', ...)

try:
    controller.login()

    # Your operations
    devices = controller.get_devices()

except UniFiAuthError as e:
    print(f"Authentication failed: {e}")
    # Check credentials, account status

except UniFiConnectionError as e:
    print(f"Connection failed: {e}")
    # Check network, controller availability

except UniFiTimeoutError as e:
    print(f"Request timed out: {e}")
    # Increase timeout or check controller load

except UniFiRateLimitError as e:
    print(f"Rate limited: {e}")
    if e.retry_after:
        print(f"Retry after {e.retry_after} seconds")
    # Implement session reuse, reduce request frequency

except UniFiAPIError as e:
    print(f"API error: {e}")
    # Generic error handling

finally:
    # Always logout
    try:
        controller.logout()
    except:
        pass  # Ignore logout errors
```

## Rate Limiting and Best Practices

### Automatic Retry

Critical operations (`get_devices`, `get_clients`, `get_sites`) have automatic retry with exponential backoff:

- **Max retries**: 3
- **Backoff factor**: 2.0
- **Retry delays**: 0s → 2s → 4s → 8s
- **Retries on**: Connection errors, timeouts, server errors (5xx)
- **No retry on**: Auth errors (401/403), not found (404), bad request (400)

### Session Reuse

**❌ Don't**: Create new sessions for each operation

```python
# Bad - triggers rate limiting
for i in range(100):
    controller = UniFiController(...)
    controller.login()
    devices = controller.get_devices()
    controller.logout()
```

**✅ Do**: Reuse session across operations

```python
# Good - 170% more efficient
controller = UniFiController(...)
controller.login()

for i in range(100):
    devices = controller.get_devices()
    # Process devices

controller.logout()
```

### Bulk Operations

**❌ Don't**: Make individual API calls in loops

```python
# Bad - many API calls
for mac in mac_list:
    device = controller.get_device(mac)
```

**✅ Do**: Get all data and filter locally

```python
# Good - single API call
devices = controller.get_devices()
device_dict = {d['mac']: d for d in devices}

for mac in mac_list:
    device = device_dict.get(mac)
```

### Concurrent Requests

The controller is thread-safe for concurrent operations:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    # Limit concurrent requests to 5
    results = executor.map(controller.get_device, mac_list)
```

**Recommendations**:

- Limit to 5-10 concurrent requests
- Use session reuse with concurrent operations
- Handle exceptions in worker threads

## Controller Detection

The UniFiController automatically detects controller type:

### Standard Controller

- Authentication endpoint: `/api/login`
- Site endpoints: `/api/s/{site}/...`
- Default port: `8443`

### UDM/UDM Pro

- Authentication endpoint: `/api/auth/login`
- Site endpoints: `/proxy/network/api/s/{site}/...`
- Default port: `443`

**Detection**: Attempted automatically during `login()`, no configuration needed.

## Complete Example

```python
from src.unifi_controller import UniFiController, UniFiAPIError
from config import UNIFI_CONFIG
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize controller
    controller = UniFiController(**UNIFI_CONFIG)

    try:
        # Login
        logger.info("Connecting to controller...")
        controller.login()
        logger.info("✅ Connected successfully")

        # Get sites
        sites = controller.get_sites()
        logger.info(f"Found {len(sites)} site(s)")

        # Get devices
        devices = controller.get_devices()
        logger.info(f"Found {len(devices)} device(s)")

        # Analyze devices
        online_devices = [d for d in devices if d['state'] == 1]
        offline_devices = [d for d in devices if d['state'] != 1]

        logger.info(f"  Online: {len(online_devices)}")
        logger.info(f"  Offline: {len(offline_devices)}")

        # Get clients
        clients = controller.get_clients()
        logger.info(f"Found {len(clients)} active client(s)")

        # Analyze clients
        wired_clients = [c for c in clients if c.get('is_wired')]
        wireless_clients = [c for c in clients if not c.get('is_wired')]
        guest_clients = [c for c in clients if c.get('is_guest')]

        logger.info(f"  Wired: {len(wired_clients)}")
        logger.info(f"  Wireless: {len(wireless_clients)}")
        logger.info(f"  Guests: {len(guest_clients)}")

        # Find offline devices
        if offline_devices:
            logger.warning("⚠️ Offline devices detected:")
            for device in offline_devices:
                logger.warning(f"  - {device['name']} ({device['mac']})")

    except UniFiAPIError as e:
        logger.error(f"❌ Error: {e}")
        return 1

    finally:
        # Always logout
        controller.logout()
        logger.info("✅ Disconnected")

    return 0

if __name__ == '__main__':
    exit(main())
```

## API Endpoint Reference

### Authentication

| Endpoint          | Method | Description                 |
| ----------------- | ------ | --------------------------- |
| `/api/login`      | POST   | Login (standard controller) |
| `/api/auth/login` | POST   | Login (UDM/UDM Pro)         |
| `/api/logout`     | POST   | Logout (all controllers)    |

### Sites

| Endpoint          | Method | Description    |
| ----------------- | ------ | -------------- |
| `/api/self/sites` | GET    | List all sites |

### Devices

| Endpoint                          | Method | Description                            |
| --------------------------------- | ------ | -------------------------------------- |
| `/api/s/{site}/stat/device`       | GET    | List all devices                       |
| `/api/s/{site}/stat/device/{mac}` | GET    | Get device by MAC                      |
| `/api/s/{site}/cmd/devmgr`        | POST   | Device commands (reboot, locate, etc.) |
| `/api/s/{site}/rest/device/{id}`  | PUT    | Update device config                   |

### Clients

| Endpoint                        | Method | Description                              |
| ------------------------------- | ------ | ---------------------------------------- |
| `/api/s/{site}/stat/sta`        | GET    | List all clients                         |
| `/api/s/{site}/stat/user/{mac}` | GET    | Get client by MAC                        |
| `/api/s/{site}/cmd/stamgr`      | POST   | Client commands (block, reconnect, etc.) |
| `/api/s/{site}/rest/user/{id}`  | PUT    | Update client config                     |

**Note**: UDM/UDM Pro requires `/proxy/network` prefix before `/api/s/{site}/...`

## Version Compatibility

| Component                     | Version       |
| ----------------------------- | ------------- |
| **Python**                    | 3.8+          |
| **UniFi Network Application** | 7.x, 8.x      |
| **UDM/UDM Pro Firmware**      | 3.x+          |
| **Standard Controller**       | 6.x, 7.x, 8.x |

## Additional Resources

- [UDM Setup Guide](UDM_SETUP.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Configuration Guide](CONFIGURATION.md)
- [Performance Testing Results](TASK_8_COMPLETE.md)
