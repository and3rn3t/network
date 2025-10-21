# Testing Guide - UniFi Controller API Integration

**Created**: October 20, 2025
**Status**: Ready for Testing
**Task**: Task 6 - Test with Real Controller

---

## 📋 Prerequisites

Before you can test the integration, you need:

1. **UniFi Network Controller** (version 7.0+)

   - Running and accessible on your network
   - Can be self-hosted or Cloud Key
   - NOT the cloud Site Manager (api.ui.com)

2. **Admin Credentials**

   - Username with admin privileges
   - Password for the admin account

3. **Network Connectivity**

   - Controller must be reachable from your test machine
   - Ports 443 or 8443 open (HTTPS)

4. **Test Devices/Clients** (optional)
   - At least 1 UniFi device for device operation testing
   - At least 1 connected client for client operation testing

---

## 🔧 Step 1: Configure Controller Connection

Edit `config.py` and update the controller settings:

```python
# =============================================================================
# UniFi Network Controller (Local/Self-hosted)
# =============================================================================
CONTROLLER_HOST = "192.168.1.10"     # ← Change to your controller's IP
CONTROLLER_PORT = 8443                # ← Usually 8443 or 443
CONTROLLER_USERNAME = "admin"         # ← Your admin username
CONTROLLER_PASSWORD = "YourPassword"  # ← Your admin password
CONTROLLER_SITE = "default"           # ← Usually "default"
CONTROLLER_VERIFY_SSL = False         # ← False for self-signed certs

# Choose which API to use
API_TYPE = "local"  # ← Make sure this is "local"
```

### How to Find Your Controller Details

**Controller IP Address:**

- Check your router's DHCP leases
- Look in UniFi mobile app: Settings → System Settings
- If using Cloud Key: Check device label or Network app
- Default gateway if controller is your router: `192.168.1.1`

**Controller Port:**

- Default HTTPS port: `8443`
- Alternative: `443`
- Check Network app → System Settings → Controller

**Username/Password:**

- The credentials you use to log into the controller web interface
- NOT your Ubiquiti account credentials
- Must have Admin or Super Admin role

**Site Name:**

- Usually `default` for single-site setups
- Check URL when logged in: `https://ip:8443/manage/site/SITENAME/...`
- Or use the quick test to list available sites

---

## 🚀 Step 2: Run Quick Connection Test

This test verifies basic connectivity without making any changes:

```powershell
# From the project root
python quick_test_unifi.py
```

**What it tests:**

- ✅ Connection to controller
- ✅ Authentication with credentials
- ✅ List sites
- ✅ List devices
- ✅ List clients

**Expected Output:**

```
================================================================================
  Quick UniFi Controller Connection Test
================================================================================

  Time: 2025-10-20 15:45:00
  Controller: 192.168.1.10:8443
  Site: default

📡 Initializing controller connection...
🔐 Testing connection...
✅ Connection successful!
🔑 Authenticating...
✅ Authentication successful!

📍 Fetching sites...
✅ Found 1 site(s)
   • default: Default

🖥️  Fetching devices...
✅ Found 3 device(s)
   1. Office Switch (USW-24-POE) - aa:bb:cc:dd:ee:ff - 🟢 Online
   2. Living Room AP (U6-LR) - 11:22:33:44:55:66 - 🟢 Online
   3. Garage AP (UAP-AC-PRO) - 77:88:99:aa:bb:cc - 🔴 Offline

👥 Fetching clients...
✅ Found 12 active client(s)
   1. iPhone - 12:34:56:78:90:ab - 192.168.1.50
   2. Laptop - ab:cd:ef:12:34:56 - 192.168.1.51
   ... and 10 more

🚪 Logging out...
✅ Logged out successfully

================================================================================
  ✅ All basic tests passed!
================================================================================
```

### Troubleshooting Quick Test

**Error: "Cannot connect to controller"**

- Check `CONTROLLER_HOST` is correct IP
- Verify controller is running
- Check firewall/network connectivity
- Try: `ping 192.168.1.10` (your controller IP)
- Try: Access web UI at `https://192.168.1.10:8443`

**Error: "Authentication failed"**

- Verify `CONTROLLER_USERNAME` and `CONTROLLER_PASSWORD`
- Make sure user has admin privileges
- Check for account lockout (too many failed attempts)

**Error: "SSL verification failed"**

- Set `CONTROLLER_VERIFY_SSL = False` in config.py
- Controllers often use self-signed certificates

**Error: "Connection timeout"**

- Check `CONTROLLER_PORT` (try 443 if 8443 fails)
- Verify no firewall blocking connection
- Increase timeout in test script (default: 30s)

---

## 🧪 Step 3: Run Comprehensive Test Suite

Once the quick test passes, run the full test suite:

```powershell
python test_unifi_integration.py
```

This interactive test will:

1. ✅ Test connection and authentication (automatic)
2. ✅ List sites, devices, and clients (automatic)
3. ⚠️ Prompt for device operations testing (interactive)
4. ⚠️ Prompt for client operations testing (interactive)

**The interactive tests are SAFE** but will:

- Blink device LEDs (locate test)
- Briefly disconnect clients (reconnect test)
- Ask for confirmation before each operation

### Interactive Test Example

```
================================================================================
  Interactive Tests
================================================================================

  The following tests require user interaction and may affect
  devices/clients on your network. Proceed with caution!

  Run interactive tests? (y/N): y

================================================================================
  Device Operations
================================================================================

  Available devices for testing:
    1. Office Switch (USW-24-POE) - aa:bb:cc:dd:ee:ff
    2. Living Room AP (U6-LR) - 11:22:33:44:55:66
    3. Garage AP (UAP-AC-PRO) - 77:88:99:aa:bb:cc

  Enter device number to test (or 0 to skip): 1

  Testing with device: Office Switch (aa:bb:cc:dd:ee:ff)

  Testing get_device()...
✅ Get Device by MAC: Retrieved device info

  Testing get_device_statistics()...
✅ Get Device Statistics: Retrieved device statistics
    CPU: 15%, Memory: 45%

  Test locate (LED blink) on this device? (y/N): y
✅ Locate Device: Locate command sent (check device LED)
  Press Enter after verifying LED is blinking...
  Locate disabled
```

### Understanding Test Results

**Test Summary:**

```
================================================================================
TEST SUMMARY
================================================================================
Total Tests:  15
✅ Passed:    13
❌ Failed:    0
⏭️  Skipped:   2
Success Rate: 86.7%
================================================================================
```

- **Passed**: Test completed successfully
- **Failed**: Test encountered an error (see details below summary)
- **Skipped**: Test was not run (user skipped or not applicable)

---

## 🔍 Step 4: Test Backend API Endpoints

After the integration tests pass, test the FastAPI endpoints:

### Start the Backend Server

```powershell
cd backend
python src/main.py
```

Expected output:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Access Swagger UI

Open your browser: **http://localhost:8000/docs**

This provides an interactive API testing interface.

### Test Device Operations

**1. List Devices:**

- Endpoint: `GET /api/devices`
- Click "Try it out" → "Execute"
- Should return all devices from your controller

**2. Reboot Device:**

- Endpoint: `POST /api/devices/{device_id}/reboot`
- Find a device ID from the list above
- Click "Try it out"
- Enter the device ID
- Click "Execute"
- ⚠️ This will actually reboot the device!

**3. Locate Device (Safe):**

- Endpoint: `POST /api/devices/{device_id}/locate`
- Enter device ID and duration (e.g., 10 seconds)
- Click "Execute"
- Device LED will blink

**4. Get Device Info:**

- Endpoint: `GET /api/devices/{device_id}/info`
- Enter device ID
- Click "Execute"
- Returns comprehensive device information with live stats

### Test Client Operations

**1. List Clients:**

- Endpoint: `GET /api/clients`
- Returns all active clients

**2. Get Client History:**

- Endpoint: `GET /api/clients/{mac}/history`
- Enter client MAC address (format: `aa:bb:cc:dd:ee:ff`)
- Optional: Set hours (default: 24)
- Click "Execute"
- Returns connection history

**3. Reconnect Client (Careful):**

- Endpoint: `POST /api/clients/{mac}/reconnect`
- Enter client MAC address
- ⚠️ This will disconnect and reconnect the client
- Use a device you can easily reconnect manually if needed

### Using cURL (Alternative)

```powershell
# List devices
curl http://localhost:8000/api/devices

# Get device info
curl http://localhost:8000/api/devices/1/info

# Locate device
curl -X POST "http://localhost:8000/api/devices/1/locate?duration=10"

# List clients
curl http://localhost:8000/api/clients

# Get client history
curl "http://localhost:8000/api/clients/aa:bb:cc:dd:ee:ff/history?hours=24"
```

---

## 📊 Step 5: Verify Database Logging

Check that operations are being logged to the database:

```powershell
# View recent events
python -c "from backend.src.database import Database; db = Database(); events = db.execute_query('SELECT * FROM events ORDER BY timestamp DESC LIMIT 10'); print(events)"
```

Or use a SQLite viewer:

```powershell
# Install DB Browser for SQLite or use:
sqlite3 network_monitor.db "SELECT * FROM events ORDER BY timestamp DESC LIMIT 10;"
```

Expected event types:

- `device_reboot`
- `device_locate`
- `device_rename`
- `client_block`
- `client_reconnect`
- etc.

---

## ✅ Success Criteria

The integration is successful when:

- [x] Quick test connects and lists devices/clients
- [x] Comprehensive test passes all automatic tests
- [x] At least one device operation works (e.g., locate)
- [x] At least one client operation works (e.g., get history)
- [x] Backend API endpoints return real data
- [x] Database logs operations correctly
- [x] No authentication errors during normal operation

---

## 🐛 Common Issues & Solutions

### Issue: "Module not found" errors

**Solution:**

```powershell
# Install dependencies
pip install -r requirements.txt

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

### Issue: "Device not found" when testing operations

**Possible causes:**

1. Device MAC not in database yet
2. Device offline or removed from controller

**Solution:**

```powershell
# Sync devices from controller to database
python backend/src/sync_devices.py
```

### Issue: Operations timeout

**Solution:**

- Increase timeout in `src/unifi_controller.py`:
  ```python
  def __init__(self, ..., timeout=60):  # Increase from 30 to 60
  ```
- Check network latency to controller
- Verify controller isn't overloaded

### Issue: "Session expired" errors

**Root cause:** Session timeout on controller (usually 24 hours)

**Solution:** Already handled by `_ensure_logged_in()` - automatically re-authenticates

### Issue: Client history returns empty

**Root causes:**

1. Client recently connected (no history yet)
2. Controller log retention settings
3. Client data cleared

**Solution:** Normal behavior - some clients won't have history

---

## 📝 Test Results Documentation

Create a test results file: `docs/TEST_RESULTS.md`

Document:

- Controller version tested
- Number of devices in test environment
- Number of clients in test environment
- Which operations were tested
- Any issues encountered
- Performance observations

Example:

```markdown
# Test Results - UniFi Controller Integration

**Date**: 2025-10-20
**Tester**: Your Name
**Controller Version**: 7.5.187

## Environment

- Devices: 5 (3 APs, 2 switches)
- Active Clients: 15
- Controller: UDM-Pro

## Test Results

- Connection Test: ✅ PASS
- Authentication: ✅ PASS
- Device Listing: ✅ PASS (5 devices)
- Client Listing: ✅ PASS (15 clients)
- Device Reboot: ✅ PASS (tested on UAP-AC-PRO)
- Device Locate: ✅ PASS (LED blink confirmed)
- Client Reconnect: ✅ PASS (client reconnected in 5s)
- Client History: ✅ PASS (24h history retrieved)

## Issues Found

None - all tests passed successfully

## Performance

- API response time: <500ms average
- Bulk operations: 3 devices in 2.5s
```

---

## 🎯 Next Steps After Testing

Once testing is complete:

1. **Task 7: Error Handling & Validation**

   - Add retry logic for transient failures
   - Improve error messages
   - Add input validation

2. **Task 8: Performance Testing**

   - Test with larger device counts
   - Benchmark bulk operations
   - Identify bottlenecks

3. **Task 9: Update Documentation**
   - Document actual behavior
   - Create troubleshooting guide
   - Update API reference

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review controller logs (Settings → System → Logs)
3. Enable debug logging in `config.py`: `LOG_LEVEL = "DEBUG"`
4. Check `logs/unifi_api.log` for detailed error messages

---

**Last Updated**: October 20, 2025
**Status**: Ready for Testing
**Next**: Run `python quick_test_unifi.py`
