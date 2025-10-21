# UniFi Local Controller Quick Start

Quick guide to get started with UniFi local controller data collection and monitoring.

## Prerequisites

- Python 3.11 or higher
- UniFi Network Controller (UDM Pro, UDM, Cloud Key, or self-hosted)
- Network access to your controller
- Admin credentials for the controller

## 1. Installation

```powershell
# Clone repository (if not already done)
git clone <repository-url>
cd network

# Install dependencies
pip install -r requirements.txt
```

## 2. Configuration

```powershell
# Copy example config
Copy-Item config.example.py config.py

# Edit config.py with your settings
notepad config.py
```

Update these settings:

```python
# API Type - use local controller
API_TYPE = "local"  # Changed from "cloud"

# UniFi Controller Settings
CONTROLLER_HOST = "192.168.1.1"  # Your UDM Pro or controller IP
CONTROLLER_PORT = 443
CONTROLLER_USERNAME = "admin"
CONTROLLER_PASSWORD = "your-password"
CONTROLLER_SITE = "default"
CONTROLLER_VERIFY_SSL = False  # Set True if you have valid SSL cert
```

## 3. Test Connection

```powershell
# Quick connection test
python scripts/quick_test_unifi.py
```

Expected output:

```
✅ Successfully connected to UniFi Controller
✅ Login successful
✅ Found 6 devices
✅ Found 37 clients
```

## 4. Setup Database

```powershell
# Create fresh database with all tables
python scripts/create_fresh_db.py
```

This creates `unifi_network.db` with:

- 8 UniFi tables (devices, clients, metrics, events, etc.)
- 6 views for common queries
- All necessary indexes

## 5. First Data Collection

```powershell
# Run single collection
python collect_unifi_data.py --verbose
```

Expected output:

```
Devices processed: 6
Clients processed: 38
Status records: 44
Events created: 38
Metrics created: 267
Duration: 2.93s
```

## 6. Verify Data

```powershell
# Check what was collected
python -c "import sqlite3; conn = sqlite3.connect('network_monitor.db'); print('Devices:', conn.execute('SELECT COUNT(*) FROM unifi_devices').fetchone()[0]); print('Clients:', conn.execute('SELECT COUNT(*) FROM unifi_clients').fetchone()[0])"
```

## 7. Continuous Collection (Daemon Mode)

```powershell
# Start continuous collection (every 5 minutes)
python collect_unifi_data.py --daemon --interval 300
```

Press `Ctrl+C` to stop.

## 8. View Analytics (After Some Data Collection)

```powershell
# View network analytics
python scripts/unifi_analytics_demo.py
```

This shows:

- Network health summary
- Device health scores
- Client experience analysis
- Signal quality distribution
- Top devices by traffic
- Recent events

## Quick Reference

### Useful Scripts

All scripts are in the `scripts/` directory:

```powershell
# Database utilities
python scripts/create_fresh_db.py       # Fresh database
python scripts/check_metrics.py         # Check collected metrics

# Testing
python scripts/quick_test_unifi.py      # Test controller connection
python scripts/test_unifi_integration.py # Full integration test

# Diagnostics
python scripts/diagnose_unifi_site.py   # Diagnose controller issues
python scripts/find_unifi_port.py       # Find correct port
```

### Common Tasks

**Check collection status:**

```powershell
python -c "import sqlite3; conn = sqlite3.connect('network_monitor.db'); print('Last run:', conn.execute('SELECT start_time FROM unifi_collection_runs ORDER BY id DESC LIMIT 1').fetchone()[0])"
```

**View latest devices:**

```powershell
python -c "import sqlite3; conn = sqlite3.connect('network_monitor.db'); [print(f'{r[0]:30} {r[1]}') for r in conn.execute('SELECT name, ip FROM unifi_devices')]"
```

**Check for errors:**

```powershell
python -c "import sqlite3; conn = sqlite3.connect('network_monitor.db'); [print(f'{r[0]} - {r[1]}') for r in conn.execute('SELECT timestamp, description FROM unifi_events WHERE event_type = \"error\" ORDER BY timestamp DESC LIMIT 5')]"
```

## Troubleshooting

### Connection Issues

If you can't connect:

1. **Check controller accessibility:**

   ```powershell
   Test-NetConnection -ComputerName 192.168.1.1 -Port 443
   ```

2. **Try different ports:**

   ```powershell
   python scripts/find_unifi_port.py
   ```

3. **Verify credentials:**
   ```powershell
   python scripts/test_credentials.py
   ```

### SSL Certificate Errors

If you see SSL warnings:

```python
# In config.py
CONTROLLER_VERIFY_SSL = False  # Disable SSL verification
```

### Database Locked Errors

If you see "database is locked":

1. Close any SQLite browser/viewer tools
2. Restart VS Code
3. Try again

Or use a fresh database:

```powershell
python scripts/create_fresh_db.py
Copy-Item -Force unifi_network.db network_monitor.db
```

### No Data Collected

If collection shows 0 devices:

1. Check you're on the correct site (default vs custom)
2. Verify controller access in web UI
3. Check firewall isn't blocking Python
4. Review logs for errors

## Next Steps

Once you have data collecting:

1. **Set up continuous collection** - Run in daemon mode
2. **Schedule collection** - Use Windows Task Scheduler or cron
3. **Configure alerts** - Set up monitoring alerts
4. **Generate reports** - Create automated reports
5. **Export data** - Export to Prometheus, Grafana, etc.

See [UNIFI_ANALYTICS_GUIDE.md](UNIFI_ANALYTICS_GUIDE.md) for analytics documentation.

## Support

For issues or questions:

1. Check [scripts/README.md](../scripts/README.md) for script documentation
2. Review [TASK_8_DATABASE_SETUP_SUMMARY.md](TASK_8_DATABASE_SETUP_SUMMARY.md) for setup details
3. See [UNIFI_ANALYTICS_GUIDE.md](UNIFI_ANALYTICS_GUIDE.md) for analytics help
