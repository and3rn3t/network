# Continuous Metrics Collection - Setup Complete

## ✅ Status: ACTIVE

Your UniFi network monitoring system is now collecting metrics automatically!

## 📋 What's Running

**Windows Scheduled Task: "UniFi Metrics Collection"**

- **Frequency**: Every 5 minutes
- **Command**: `python collect_real_metrics.py --auto`
- **Working Directory**: `C:\git\network`
- **Status**: Ready and running
- **Auto-start**: Yes (will start with Windows)

## 📊 Current Metrics

The system is collecting:

### Real Metrics (from UniFi API)

- ✅ **client_count** - Number of connected clients
- ✅ **device_state** - Online/offline status
- ✅ **uptime** - Device uptime in hours
- ✅ **network_rx_bytes** - Total received bytes
- ✅ **network_tx_bytes** - Total transmitted bytes
- ✅ **cpu_usage_estimated** - Estimated CPU based on client load

### Sample Metrics (still used for detailed patterns)

- 📈 **cpu_usage** - Detailed CPU patterns with spikes
- 📈 **memory_usage** - Memory usage patterns
- 📈 **network_rx_mbps** - Download speed patterns
- 📈 **network_tx_mbps** - Upload speed patterns

## 🎯 Next Steps

### View Your Dashboard

1. Make sure the backend is running:

   ```bash
   cd backend
   npm run dev
   ```

2. Make sure the frontend is running:

   ```bash
   cd frontend
   npm run dev
   ```

3. Open your browser: <http://localhost:3000>

### Monitor Collection

Check metrics count:

```bash
python -c "from src.database.database import Database; db = Database(); conn = db.get_connection(); cursor = conn.execute('SELECT COUNT(*) as count FROM metrics'); print(f'Total metrics: {cursor.fetchone()[0]}')"
```

View recent metrics:

```bash
python -c "from src.database.database import Database; db = Database(); conn = db.get_connection(); cursor = conn.execute('SELECT metric_name, metric_value, unit, recorded_at FROM metrics ORDER BY recorded_at DESC LIMIT 10'); import json; print(json.dumps([dict(row) for row in cursor.fetchall()], indent=2))"
```

### Manage the Scheduled Task

**View task status:**

```powershell
Get-ScheduledTask -TaskName "UniFi Metrics Collection" | Format-List
```

**View task run history:**

```powershell
Get-ScheduledTaskInfo -TaskName "UniFi Metrics Collection"
```

**Stop collection temporarily:**

```powershell
Disable-ScheduledTask -TaskName "UniFi Metrics Collection"
```

**Resume collection:**

```powershell
Enable-ScheduledTask -TaskName "UniFi Metrics Collection"
```

**Remove the task completely:**

```powershell
Unregister-ScheduledTask -TaskName "UniFi Metrics Collection" -Confirm:$false
```

**Or use Task Scheduler GUI:**

1. Press Win + R
2. Type `taskschd.msc` and press Enter
3. Find "UniFi Metrics Collection" in the list
4. Right-click for options (Run, Disable, Delete, etc.)

## 📈 Expected Behavior

- **First 5 minutes**: 1-2 metrics per device
- **After 1 hour**: 12-24 metrics per device
- **After 24 hours**: 288+ metrics per device (full time series)

The dashboard will show:

- Real-time updates every 5 minutes
- Historical trends over the past 24 hours
- Performance charts with actual data points

## 🔧 Troubleshooting

### No metrics being collected?

1. **Check if task is running:**

   ```powershell
   Get-ScheduledTask -TaskName "UniFi Metrics Collection"
   ```

   Status should be "Ready"

2. **Check task history:**

   ```powershell
   Get-ScheduledTaskInfo -TaskName "UniFi Metrics Collection" | Format-List LastRunTime,LastTaskResult
   ```

3. **Run collector manually to see errors:**

   ```bash
   python collect_real_metrics.py --auto
   ```

4. **Check database:**

   ```bash
   python test_collection.py
   ```

### Device showing as offline?

This is normal if:

- Device is actually offline/disconnected
- Device is in a different site/location
- API credentials need refresh

The system will still collect state metrics (offline status).

### Want more detailed metrics?

The UniFi Site Manager cloud API has limitations. For full metrics:

1. Enable SNMP on your UniFi devices
2. Or use a local UniFi Controller API instead of cloud
3. See `docs/REAL_METRICS_COLLECTION.md` for details

## 📚 Documentation

- **Collection Guide**: `docs/REAL_METRICS_COLLECTION.md`
- **Dashboard Usage**: `docs/ENHANCED_DASHBOARD.md`
- **Export Options**: `docs/DATA_EXPORT.md`
- **Configuration**: `docs/CONFIGURATION.md`

## 🎉 Success

Your system is now:

- ✅ Collecting metrics automatically every 5 minutes
- ✅ Storing data in SQLite database
- ✅ Ready to display in your dashboard
- ✅ Set up to survive reboots

Enjoy monitoring your UniFi network! 🚀
