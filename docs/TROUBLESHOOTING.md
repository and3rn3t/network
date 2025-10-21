# UniFi Controller Integration - Troubleshooting Guide

## Common Issues and Solutions

This guide covers common problems you may encounter when integrating with UniFi controllers (including UDM/UDM Pro) and how to resolve them.

## Authentication Issues

### Problem: 401 Unauthorized Error

**Symptoms**:

```
UniFiAuthError: Authentication failed (401): Invalid username or password
```

**Common Causes**:

1. Incorrect username or password
2. Using cloud/SSO account instead of local account
3. Account locked due to failed login attempts
4. Two-factor authentication enabled

**Solutions**:

1. **Verify credentials**:

   ```python
   # Test login via web interface first
   # Visit: https://<controller_ip>/
   ```

2. **Use local admin account**:

   - UDM/UDM Pro require local administrator accounts
   - Cloud accounts (UI.com SSO) do not work for API access
   - Create dedicated local admin: Settings → Admins → Add Admin

3. **Check account status**:

   - Ensure account is not locked
   - Disable two-factor authentication for API account (if applicable)

4. **Verify configuration**:

   ```python
   # config.py
   UNIFI_CONFIG = {
       'username': 'admin',  # Local username, not email
       'password': 'password123',
       # ... other settings
   }
   ```

### Problem: 403 Forbidden Error

**Symptoms**:

```
UniFiAuthError: Access forbidden (403): Insufficient permissions
```

**Solutions**:

1. Ensure the account has administrator privileges
2. Check site access permissions
3. Verify account is not read-only

## Connection Issues

### Problem: Connection Timeout

**Symptoms**:

```
UniFiTimeoutError: Request timed out after 30.0 seconds
```

**Diagnostics**:

```powershell
# Test network connectivity
ping <controller_ip>

# Test port accessibility
Test-NetConnection -ComputerName <controller_ip> -Port 443
```

**Solutions**:

1. **Verify IP address**:

   - Check controller IP is correct
   - Test web interface access: `https://<controller_ip>/`

2. **Check network connectivity**:

   - Ensure no firewall blocking
   - Verify VPN connection if needed
   - Check controller is online

3. **Increase timeout**:

   ```python
   UNIFI_CONFIG = {
       'timeout': 60,  # Increase from default 30s
       # ... other settings
   }
   ```

4. **Check controller load**:
   - High CPU/memory may slow responses
   - Too many simultaneous API clients

### Problem: SSL Certificate Errors

**Symptoms**:

```
requests.exceptions.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**Solutions**:

1. **Development/Testing** - Disable SSL verification:

   ```python
   UNIFI_CONFIG = {
       'verify_ssl': False,  # Only for development!
       # ... other settings
   }
   ```

2. **Production** - Install valid certificate:

   - Use Let's Encrypt or commercial SSL certificate
   - Import certificate to controller
   - Set `verify_ssl=True` in config

3. **Custom certificate** - Add to trusted store:

   ```python
   UNIFI_CONFIG = {
       'verify_ssl': '/path/to/custom-ca-bundle.crt',
       # ... other settings
   }
   ```

## API Response Issues

### Problem: Empty Device/Client Lists

**Symptoms**:

```python
devices = controller.get_devices()
print(len(devices))  # Output: 0
```

**Solutions**:

1. **Verify devices are adopted**:

   - Check web interface: Devices → All Devices
   - Ensure devices show as "Connected" or "Managed"

2. **Check site name**:

   ```python
   # List all sites first
   sites = controller.get_sites()
   print(sites)

   # Use correct site name
   devices = controller.get_devices(site='correct-site-name')
   ```

3. **Verify API access**:

   - Ensure account has access to the site
   - Check "Access to Sites" in admin settings

4. **Wait for adoption**:
   - Newly added devices may take a few minutes to appear

### Problem: Invalid MAC Address Errors

**Symptoms**:

```
ValueError: Invalid MAC address format: 'invalid-mac'
```

**Solutions**:

1. **Use correct MAC format**:

   ```python
   # Accepted formats:
   'aa:bb:cc:dd:ee:ff'  # Colons
   'AA-BB-CC-DD-EE-FF'  # Dashes
   'aabbccddeeff'       # No separators

   # The client normalizes to: aabbccddeeff
   ```

2. **Validate MAC before use**:

   ```python
   from src.unifi_controller import validate_mac_address

   mac = 'aa:bb:cc:dd:ee:ff'
   if validate_mac_address(mac):
       device = controller.get_device(mac)
   else:
       print(f"Invalid MAC: {mac}")
   ```

3. **Extract MAC from device data**:

   ```python
   devices = controller.get_devices()
   for device in devices:
       mac = device.get('mac')  # Already in correct format
       # Use mac for operations
   ```

## Rate Limiting Issues

### Problem: 429 Too Many Requests

**Symptoms**:

```
UniFiRateLimitError: Rate limit exceeded. Retry after 60 seconds
```

**Causes**:

- Too many rapid API calls
- Multiple concurrent sessions
- Creating/destroying sessions rapidly (login/logout)

**Solutions**:

1. **Use session reuse** (170% efficiency improvement):

   ```python
   # Good: Reuse controller instance
   controller = UniFiController(...)
   controller.login()

   for _ in range(100):
       devices = controller.get_devices()
       # Process devices

   controller.logout()
   ```

   ```python
   # Bad: Creating new sessions each time
   for _ in range(100):
       controller = UniFiController(...)
       controller.login()
       devices = controller.get_devices()
       controller.logout()  # Triggers rate limiting!
   ```

2. **Add delays between operations**:

   ```python
   import time

   for mac in device_macs:
       device = controller.get_device(mac)
       time.sleep(0.5)  # 500ms delay
   ```

3. **Use bulk operations**:

   ```python
   # Good: Single call
   devices = controller.get_devices()

   # Bad: Multiple calls
   for mac in mac_list:
       device = controller.get_device(mac)
   ```

4. **Implement backoff** (automatic in retry decorator):
   - Exponential backoff already implemented
   - Retries: 0s → 2s → 4s → 8s
   - Respects Retry-After header from controller

## UDM-Specific Issues

### Problem: Wrong API Endpoint (UDM)

**Symptoms**:

```
UniFiAPIError: Not found (404): /api/login
```

**Solution**:
The UniFiController class automatically detects UDM and uses correct endpoints:

- Authentication: `/api/auth/login` (UDM) vs `/api/login` (standard)
- API calls: `/proxy/network/api/s/{site}/...` (UDM) vs `/api/s/{site}/...` (standard)

If you still encounter this:

1. Verify you're using the latest version of `src/unifi_controller.py`
2. Check controller type detection logic in `_get_base_url()`

### Problem: Wrong Port (UDM)

**Symptoms**:
Connection fails when using port 8443

**Solution**:
UDM/UDM Pro use port 443 (standard HTTPS):

```python
UNIFI_CONFIG = {
    'port': 443,  # Not 8443!
    # ... other settings
}
```

## Performance Issues

### Problem: Slow API Responses

**Symptoms**:

- API calls taking >1 second
- Timeouts occurring frequently

**Diagnostics**:

```python
# Run performance test
python test_performance.py
```

**Expected Performance** (UDM Pro, 6 devices, 36 clients):

- Login: ~500ms
- get_devices(): ~34ms
- get_clients(): ~23ms
- get_sites(): ~13ms

**Solutions**:

1. **Check network latency**:

   ```powershell
   ping -n 10 <controller_ip>
   # Look for average latency
   ```

2. **Verify controller resources**:

   - Check CPU/memory usage in web interface
   - High load may slow API responses

3. **Reduce concurrent requests**:

   ```python
   # Limit concurrent operations
   from concurrent.futures import ThreadPoolExecutor

   with ThreadPoolExecutor(max_workers=5) as executor:
       # Limit to 5 concurrent requests
       results = executor.map(controller.get_device, mac_list)
   ```

4. **Use bulk operations**:
   - Prefer `get_devices()` over multiple `get_device()` calls
   - Prefer `get_clients()` over multiple `get_client()` calls

### Problem: Memory Leaks

**Symptoms**:

- Memory usage growing over time
- Application crashes after extended use

**Diagnostics**:

```python
import tracemalloc

tracemalloc.start()

# Your code here
controller.login()
for _ in range(100):
    devices = controller.get_devices()

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f} MB")
print(f"Peak: {peak / 1024 / 1024:.1f} MB")

tracemalloc.stop()
```

**Solutions**:

- The UniFiController class has been tested for memory leaks
- Expected usage: <1 MB for typical operations
- If leaks persist, ensure you're calling `logout()` properly

## Data Validation Issues

### Problem: Device Not Found

**Symptoms**:

```python
device = controller.get_device('aa:bb:cc:dd:ee:ff')
# Returns None or empty dict
```

**Solutions**:

1. **Verify device exists**:

   ```python
   devices = controller.get_devices()
   print([d.get('mac') for d in devices])
   ```

2. **Check MAC format**:

   - Use lowercase without separators: `aabbccddeeff`
   - Or use accepted formats and let client normalize

3. **Ensure device is online**:

   - Device must be adopted and connected
   - Check in web interface

4. **Check site context**:

   ```python
   # Specify correct site
   device = controller.get_device('aabbccddeeff', site='default')
   ```

## Debugging Tools

### Enable Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Run your code
controller = UniFiController(...)
controller.login()
```

### Test Script

```python
# debug_controller.py
from src.unifi_controller import UniFiController
from config import UNIFI_CONFIG

controller = UniFiController(**UNIFI_CONFIG)

try:
    print("1. Testing connection...")
    controller.login()
    print("✅ Login successful")

    print("\n2. Testing sites...")
    sites = controller.get_sites()
    print(f"✅ Found {len(sites)} site(s): {[s.get('desc') for s in sites]}")

    print("\n3. Testing devices...")
    devices = controller.get_devices()
    print(f"✅ Found {len(devices)} device(s)")
    for device in devices[:3]:  # First 3
        print(f"   - {device.get('name')} ({device.get('mac')})")

    print("\n4. Testing clients...")
    clients = controller.get_clients()
    print(f"✅ Found {len(clients)} client(s)")
    for client in clients[:3]:  # First 3
        print(f"   - {client.get('hostname')} ({client.get('mac')})")

    print("\n5. Testing device lookup...")
    if devices:
        mac = devices[0].get('mac')
        device = controller.get_device(mac)
        print(f"✅ Device lookup successful: {device.get('name')}")

    print("\n✅ All tests passed!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    controller.logout()
    print("\n✅ Logged out")
```

### Network Capture

For deep debugging, capture API traffic:

```powershell
# Using Wireshark or tcpdump
# Filter: host <controller_ip> and port 443
```

## Getting Help

### Before Requesting Help

Gather this information:

1. Controller type (UDM/UDM Pro/CloudKey/Software)
2. Controller version (UniFi Network Application version)
3. Python version: `python --version`
4. Error message (full stack trace)
5. Configuration (remove sensitive data)
6. Output from debug script above

### Resources

- **Project Documentation**: `docs/` directory
- **API Reference**: `docs/API_REFERENCE.md`
- **UDM Setup**: `docs/UDM_SETUP.md`
- **Configuration Guide**: `docs/CONFIGURATION.md`

### Common Error Messages Quick Reference

| Error                   | Likely Cause             | Solution                             |
| ----------------------- | ------------------------ | ------------------------------------ |
| 401 Unauthorized        | Wrong credentials        | Check username/password              |
| 403 Forbidden           | Insufficient permissions | Use admin account                    |
| 404 Not Found           | Wrong endpoint/site      | Check UDM detection, site name       |
| 429 Too Many Requests   | Rate limiting            | Implement session reuse              |
| Timeout                 | Network/controller issue | Check connectivity, increase timeout |
| SSL Error               | Certificate issue        | Use verify_ssl=False (dev only)      |
| ValueError: Invalid MAC | Wrong MAC format         | Use aa:bb:cc:dd:ee:ff format         |

## Prevention Best Practices

1. **Always use try/except**:

   ```python
   try:
       devices = controller.get_devices()
   except UniFiAuthError:
       # Handle authentication failure
   except UniFiTimeoutError:
       # Handle timeout
   except Exception as e:
       # Handle unexpected errors
   ```

2. **Always logout**:

   ```python
   try:
       controller.login()
       # Do work
   finally:
       controller.logout()
   ```

3. **Validate inputs**:

   ```python
   from src.unifi_controller import validate_mac_address

   if not validate_mac_address(mac):
       raise ValueError(f"Invalid MAC: {mac}")
   ```

4. **Use session reuse**:

   - Keep controller instance alive between operations
   - Don't create/destroy sessions rapidly

5. **Handle errors gracefully**:
   - Don't crash on single API failures
   - Log errors for debugging
   - Implement retry logic for transient failures (built-in)

## Still Having Issues?

If you've tried the solutions above and still encounter problems:

1. Run the debug script and save output
2. Check the logs for detailed error messages
3. Review API_REFERENCE.md for correct usage
4. Search existing issues in the project repository
5. Create a new issue with all relevant information
