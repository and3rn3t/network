# UniFi Local Controller Configuration Guide

## Overview

This guide covers configuration for the UniFi Local Controller integration, including both standard controllers and UDM/UDM Pro devices.

## Quick Start

### Minimum Configuration

Create `config.py` in the project root:

```python
# config.py
UNIFI_CONFIG = {
    'host': '192.168.1.1',      # Controller IP address
    'port': 443,                 # 443 for UDM, 8443 for standard
    'username': 'admin',         # Local admin username
    'password': 'your-password', # Local admin password
    'verify_ssl': False,         # False for self-signed certs
    'site': 'default'            # Usually 'default'
}
```

### Example Configuration

Copy `config.example.py` to `config.py`:

```powershell
Copy-Item config.example.py config.py
```

Then edit with your controller details.

## Configuration Parameters

### Required Parameters

#### `host` (string)

- **Description**: Controller IP address or hostname
- **Examples**:
  - `'192.168.1.1'` (UDM/UDM Pro)
  - `'192.168.1.10'` (Standard controller)
  - `'unifi.local'` (Hostname)
- **Finding**: Check your UniFi device IP in router DHCP table or use `ping unifi.local`

#### `port` (integer)

- **Description**: HTTPS port for controller
- **Values**:
  - `443` - UDM/UDM Pro (standard HTTPS)
  - `8443` - Standard controller, CloudKey
- **Default**: None (must specify)

#### `username` (string)

- **Description**: Local administrator username
- **Requirements**:
  - Must be a **local account** (not cloud/SSO)
  - Must have **administrator** privileges
  - Cannot be read-only user
- **Examples**: `'admin'`, `'api-user'`
- **Creating**: Settings → Admins → Add Admin → Select "Local Access"

#### `password` (string)

- **Description**: Local administrator password
- **Security**:
  - Use strong password (20+ characters)
  - Store in config file (already in `.gitignore`)
  - Never commit to version control
  - Consider environment variables for production

### Optional Parameters

#### `verify_ssl` (boolean)

- **Description**: Verify SSL certificates
- **Values**:
  - `True` - Verify certificates (production)
  - `False` - Skip verification (development, self-signed certs)
- **Default**: `True`
- **Recommendation**:
  - Use `False` for development with self-signed certs
  - Use `True` for production with valid SSL certificates

#### `site` (string)

- **Description**: Default site name for operations
- **Values**: Site name from controller (usually `'default'`)
- **Default**: `'default'`
- **Finding**: Use `get_sites()` to list available sites

#### `timeout` (integer)

- **Description**: Request timeout in seconds
- **Default**: `30`
- **Recommendations**:
  - `30` - Normal networks
  - `60` - Slow networks or busy controllers
  - `10` - Fast local networks

## Configuration Examples

### UDM Pro Configuration

```python
# config.py - UDM Pro
UNIFI_CONFIG = {
    'host': '192.168.1.1',
    'port': 443,                  # Standard HTTPS port
    'username': 'admin',
    'password': 'SecurePassword123!',
    'verify_ssl': False,          # Self-signed cert
    'site': 'default',
    'timeout': 30
}
```

### Standard Controller Configuration

```python
# config.py - Standard Controller / CloudKey
UNIFI_CONFIG = {
    'host': '192.168.1.10',
    'port': 8443,                 # Controller uses 8443
    'username': 'admin',
    'password': 'SecurePassword123!',
    'verify_ssl': False,          # Self-signed cert
    'site': 'default',
    'timeout': 30
}
```

### Production Configuration (Environment Variables)

```python
# config.py - Production with environment variables
import os

UNIFI_CONFIG = {
    'host': os.getenv('UNIFI_HOST', '192.168.1.1'),
    'port': int(os.getenv('UNIFI_PORT', '443')),
    'username': os.getenv('UNIFI_USERNAME'),      # Required
    'password': os.getenv('UNIFI_PASSWORD'),      # Required
    'verify_ssl': os.getenv('UNIFI_VERIFY_SSL', 'true').lower() == 'true',
    'site': os.getenv('UNIFI_SITE', 'default'),
    'timeout': int(os.getenv('UNIFI_TIMEOUT', '30'))
}

# Validate required environment variables
if not UNIFI_CONFIG['username']:
    raise ValueError("UNIFI_USERNAME environment variable not set")
if not UNIFI_CONFIG['password']:
    raise ValueError("UNIFI_PASSWORD environment variable not set")
```

### Multi-Site Configuration

```python
# config.py - Multiple sites
UNIFI_CONTROLLERS = {
    'home': {
        'host': '192.168.1.1',
        'port': 443,
        'username': 'admin',
        'password': 'password1',
        'verify_ssl': False,
        'site': 'default'
    },
    'office': {
        'host': '10.0.0.1',
        'port': 443,
        'username': 'admin',
        'password': 'password2',
        'verify_ssl': False,
        'site': 'default'
    }
}

# Default controller
DEFAULT_CONTROLLER = 'home'
UNIFI_CONFIG = UNIFI_CONTROLLERS[DEFAULT_CONTROLLER]
```

## Account Setup

### Creating API User Account

**Recommended**: Create a dedicated local admin account for API access.

1. **Login to Controller**:

   - Navigate to `https://<controller_ip>/`
   - Login with your admin account

2. **Create New Admin**:

   - Go to: Settings → System → Admins
   - Click "Add Admin"
   - Fill in details:
     - Name: `API User`
     - Username: `api-user`
     - Email: `api@example.com` (optional)
     - Password: Generate strong password
     - Role: `Super Administrator`
   - **Important**: Select "Local Access" (not cloud SSO)
   - Save

3. **Test Account**:

   ```python
   from src.unifi_controller import UniFiController

   controller = UniFiController(
       host='192.168.1.1',
       port=443,
       username='api-user',
       password='new-password',
       verify_ssl=False
   )

   try:
       controller.login()
       print("✅ API user account works!")
       controller.logout()
   except Exception as e:
       print(f"❌ Error: {e}")
   ```

### Account Permissions

**Required Permissions**:

- Read access to devices
- Read access to clients
- Write access for device operations (reboot, locate, etc.)
- Write access for client operations (block, bandwidth, etc.)

**Recommended Role**: `Super Administrator`

**Not Supported**:

- Read-only accounts (cannot perform operations)
- Cloud/SSO accounts (API requires local auth)
- Limited admins (may not have full access)

## SSL Certificate Configuration

### Development (Self-Signed Certificates)

Most UniFi controllers use self-signed certificates by default.

```python
UNIFI_CONFIG = {
    # ... other settings
    'verify_ssl': False  # Skip verification for self-signed
}
```

**Warning**: Only use `verify_ssl=False` in development/testing environments!

### Production (Valid Certificates)

For production, install a valid SSL certificate:

#### Option 1: Let's Encrypt

1. Install Let's Encrypt certificate on controller
2. Configure automatic renewal
3. Enable SSL verification:

```python
UNIFI_CONFIG = {
    # ... other settings
    'verify_ssl': True  # Verify valid certificate
}
```

#### Option 2: Custom Certificate Bundle

If using custom CA or corporate certificates:

```python
UNIFI_CONFIG = {
    # ... other settings
    'verify_ssl': '/path/to/ca-bundle.crt'  # Path to CA bundle
}
```

## Network Configuration

### Firewall Rules

Ensure these ports are accessible from your monitoring system:

| Port | Protocol | Purpose              | Required For        |
| ---- | -------- | -------------------- | ------------------- |
| 443  | TCP      | HTTPS API (UDM)      | UDM/UDM Pro         |
| 8443 | TCP      | HTTPS API (Standard) | Standard controller |

**Example**: Windows Firewall rule

```powershell
# Allow incoming on port 443 (if monitoring FROM controller)
New-NetFirewallRule -DisplayName "UniFi API" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

### DNS Configuration

For hostname-based configuration:

```python
UNIFI_CONFIG = {
    'host': 'unifi.local',  # Or custom hostname
    # ... other settings
}
```

Ensure DNS resolution works:

```powershell
# Test DNS resolution
nslookup unifi.local

# Test connectivity
Test-NetConnection -ComputerName unifi.local -Port 443
```

### Static IP Recommendation

**Recommended**: Assign static IP to UniFi controller to prevent configuration changes.

1. **UDM/UDM Pro**: Already has static IP
2. **CloudKey**: Assign via DHCP reservation
3. **Software Controller**: Configure static IP on host

## Advanced Configuration

### Logging Configuration

```python
# config.py
import logging

# Configure logging for UniFi integration
LOGGING_CONFIG = {
    'level': logging.INFO,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': {
        'file': {
            'filename': 'logs/unifi_controller.log',
            'max_bytes': 10485760,  # 10 MB
            'backup_count': 5
        },
        'console': {
            'enabled': True
        }
    }
}

# Apply logging configuration
logging.basicConfig(
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format']
)
```

### Performance Tuning

```python
# config.py
PERFORMANCE_CONFIG = {
    'timeout': 30,              # Request timeout (seconds)
    'max_retries': 3,           # Retry attempts for transient failures
    'retry_backoff': 2.0,       # Exponential backoff factor
    'session_reuse': True,      # Reuse HTTP session (recommended)
    'connection_pool_size': 10  # Max concurrent connections
}
```

### Monitoring Configuration

```python
# config.py
MONITORING_CONFIG = {
    'poll_interval': 60,        # Seconds between polls
    'devices_enabled': True,    # Monitor devices
    'clients_enabled': True,    # Monitor clients
    'health_check_interval': 300,  # Controller health check (seconds)
    'alert_on_offline': True,   # Alert when devices go offline
    'alert_on_auth_fail': True  # Alert on authentication failures
}
```

## Configuration Validation

### Test Configuration

Create `test_config.py`:

```python
# test_config.py
from src.unifi_controller import UniFiController
from config import UNIFI_CONFIG

def test_configuration():
    """Test UniFi controller configuration."""

    print("Testing UniFi Controller configuration...")
    print(f"Host: {UNIFI_CONFIG['host']}")
    print(f"Port: {UNIFI_CONFIG['port']}")
    print(f"Username: {UNIFI_CONFIG['username']}")
    print(f"SSL Verify: {UNIFI_CONFIG['verify_ssl']}")

    controller = UniFiController(**UNIFI_CONFIG)

    try:
        # Test authentication
        print("\n1. Testing authentication...")
        controller.login()
        print("✅ Authentication successful")

        # Test sites
        print("\n2. Testing site access...")
        sites = controller.get_sites()
        print(f"✅ Found {len(sites)} site(s)")
        for site in sites:
            print(f"   - {site['desc']} (name: {site['name']})")

        # Test devices
        print("\n3. Testing device access...")
        devices = controller.get_devices()
        print(f"✅ Found {len(devices)} device(s)")

        # Test clients
        print("\n4. Testing client access...")
        clients = controller.get_clients()
        print(f"✅ Found {len(clients)} client(s)")

        print("\n✅ Configuration is valid!")
        return True

    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        return False

    finally:
        controller.logout()

if __name__ == '__main__':
    success = test_configuration()
    exit(0 if success else 1)
```

Run test:

```powershell
python test_config.py
```

### Validate Network Connectivity

```powershell
# Test ping
ping 192.168.1.1

# Test port connectivity
Test-NetConnection -ComputerName 192.168.1.1 -Port 443

# Test HTTPS access (should show certificate error or login page)
curl -k https://192.168.1.1/
```

## Troubleshooting Configuration

### Common Issues

#### Authentication Fails (401)

**Check**:

- Username is correct (local account, not email)
- Password is correct
- Account is not locked
- Account has admin privileges

**Fix**:

```python
# Test credentials in web interface first
# https://<controller_ip>/

# Verify in config
UNIFI_CONFIG = {
    'username': 'admin',  # Not email address!
    'password': 'correct-password',
    # ...
}
```

#### Connection Timeout

**Check**:

- Controller IP is correct and reachable
- Port is correct (443 vs 8443)
- Firewall not blocking
- Controller is online

**Fix**:

```powershell
# Test connectivity
ping 192.168.1.1
Test-NetConnection -ComputerName 192.168.1.1 -Port 443

# Increase timeout if needed
UNIFI_CONFIG = {
    'timeout': 60,  # Increase from 30
    # ...
}
```

#### SSL Certificate Error

**Check**:

- Using self-signed certificate?
- Certificate expired?
- Certificate hostname mismatch?

**Fix**:

```python
# For self-signed certificates
UNIFI_CONFIG = {
    'verify_ssl': False,  # Disable verification
    # ...
}
```

#### Wrong Controller Type Detection

**Check**:

- Using correct port (443 for UDM, 8443 for standard)
- Controller responding to correct endpoint

**Fix**:
The UniFiController automatically detects controller type. If detection fails:

1. Verify port is correct
2. Check controller firmware is up to date
3. Test both endpoints manually:

   ```powershell
   curl -k https://<ip>:443/api/auth/login  # UDM endpoint
   curl -k https://<ip>:8443/api/login      # Standard endpoint
   ```

## Security Best Practices

### 1. Credential Management

- ✅ Use dedicated API account
- ✅ Use strong, unique passwords (20+ characters)
- ✅ Store credentials in config file (already in `.gitignore`)
- ✅ Never commit credentials to version control
- ✅ Use environment variables in production
- ✅ Rotate passwords periodically

### 2. Network Security

- ✅ Access controller from trusted networks only
- ✅ Use VPN for remote access
- ✅ Enable firewall rules
- ✅ Use SSL certificate verification in production

### 3. Access Control

- ✅ Limit API account permissions to required access
- ✅ Monitor API account activity
- ✅ Disable account when not in use (long-term)
- ✅ Use separate accounts for dev/prod

### 4. Logging & Monitoring

- ✅ Enable logging for all API operations
- ✅ Monitor for authentication failures
- ✅ Alert on configuration changes
- ✅ Regular security audits

## Environment-Specific Configuration

### Development

```python
# config.development.py
UNIFI_CONFIG = {
    'host': '192.168.1.1',
    'port': 443,
    'username': 'api-dev',
    'password': 'dev-password',
    'verify_ssl': False,  # OK for development
    'timeout': 10,        # Shorter timeout
}

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Production

```python
# config.production.py
import os

UNIFI_CONFIG = {
    'host': os.getenv('UNIFI_HOST'),  # From environment
    'port': int(os.getenv('UNIFI_PORT')),
    'username': os.getenv('UNIFI_USERNAME'),
    'password': os.getenv('UNIFI_PASSWORD'),
    'verify_ssl': True,   # Must verify in production
    'timeout': 30,
}

# Warning logging only
import logging
logging.basicConfig(level=logging.WARNING)
```

### Testing

```python
# config.testing.py
UNIFI_CONFIG = {
    'host': 'mock-controller.local',  # Mock server
    'port': 8443,
    'username': 'test-user',
    'password': 'test-password',
    'verify_ssl': False,
    'timeout': 5,  # Fast timeout for tests
}
```

## Additional Resources

- [UDM Setup Guide](UDM_SETUP.md) - UDM/UDM Pro specific setup
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions
- [API Reference](UNIFI_CONTROLLER_API_REFERENCE.md) - Complete API documentation
- [Performance Testing](TASK_8_COMPLETE.md) - Performance benchmarks and optimization

## Next Steps

1. ✅ Create `config.py` with your controller details
2. ✅ Run `python test_config.py` to validate configuration
3. ✅ Test basic operations with `python quick_test_unifi.py`
4. ✅ Review [API Reference](UNIFI_CONTROLLER_API_REFERENCE.md) for available operations
5. ✅ Check [Troubleshooting Guide](TROUBLESHOOTING.md) if issues occur
