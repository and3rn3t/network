# Real Metrics Collection Guide

## Overview

This guide explains how to collect real performance metrics from your UniFi network devices. The system supports multiple collection methods to gather comprehensive device performance data.

## Collection Methods

### 1. UniFi API Metrics (Available Now)

The UniFi Site Manager API provides limited performance data:

**Available Metrics:**

- ✅ **Client Count** - Number of connected devices
- ✅ **Device State** - Online/offline status
- ✅ **Uptime** - Device uptime in hours
- ✅ **Port Statistics** - Network throughput on switch ports
- ✅ **Estimated CPU** - Calculated based on client load

**Limitations:**

- ❌ **No Real CPU/Memory** - Cloud API doesn't expose system stats
- ❌ **No Interface Rates** - Can't get real-time Mbps on router interfaces
- ❌ **Snapshot Only** - Each API call gets current state, not historical

### 2. SNMP Monitoring (Future Enhancement)

For full metrics, enable SNMP on your UniFi devices:

**Additional Metrics:**

- ✅ Real CPU usage percentage
- ✅ Real memory usage percentage
- ✅ Interface traffic rates (Mbps)
- ✅ Temperature sensors
- ✅ Fan speeds

**Setup Required:**

1. Enable SNMP on UniFi device (Settings → Services → SNMP)
2. Set community string (default: public)
3. Install Python SNMP library: `pip install pysnmp`
4. Update collector to use SNMP queries

### 3. Local Controller API (Best Option)

If you have a self-hosted UniFi Controller:

**Advantages:**

- ✅ Full system stats available
- ✅ Real-time CPU/memory data
- ✅ Detailed interface statistics
- ✅ Historical data retention

**Setup:**

- Use local controller IP instead of cloud API
- Same authentication method
- Fuller API responses with system-stats

## Quick Start

### Option A: One-Time Collection

Collect current metrics snapshot:

```bash
python collect_real_metrics.py
# Choose option 1: Collect current metrics
```

### Option B: Generate Historical Data

Generate 24 hours of estimated historical metrics:

```bash
python collect_real_metrics.py
# Choose option 2: Generate historical metrics
```

This creates estimated data based on current device state with realistic variation.

### Option C: Continuous Monitoring

Run background service that collects every 5 minutes:

```bash
python start_metrics_collection.py
```

**For Production:**

**Linux/Mac** - Add to crontab:

```bash
# Collect every 5 minutes
*/5 * * * * cd /path/to/network && python collect_real_metrics.py > /dev/null 2>&1
```

**Windows** - Create scheduled task:

```powershell
# Run PowerShell as Administrator
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\git\network\collect_real_metrics.py"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "UniFi Metrics Collection" -Action $action -Trigger $trigger
```

## Collected Metrics

### Current Implementation

| Metric                | Type  | Source     | Description                          |
| --------------------- | ----- | ---------- | ------------------------------------ |
| `cpu_usage_estimated` | %     | Calculated | Estimated CPU based on client count  |
| `client_count`        | count | API        | Number of connected clients          |
| `device_state`        | state | API        | Device online/offline status         |
| `uptime`              | hours | API        | Device uptime                        |
| `network_rx_bytes`    | bytes | API        | Total received bytes (cumulative)    |
| `network_tx_bytes`    | bytes | API        | Total transmitted bytes (cumulative) |

### Future Metrics (with SNMP/Local Controller)

| Metric            | Type | Description                   |
| ----------------- | ---- | ----------------------------- |
| `cpu_usage`       | %    | Real CPU usage from device    |
| `memory_usage`    | %    | Real memory usage from device |
| `network_rx_mbps` | Mbps | Real-time receive rate        |
| `network_tx_mbps` | Mbps | Real-time transmit rate       |
| `temperature`     | °C   | Device temperature            |
| `fan_speed`       | RPM  | Cooling fan speed             |

## Data Flow

```
┌─────────────────┐
│  UniFi Devices  │
│  (Cloud/Local)  │
└────────┬────────┘
         │
         │ API Calls
         ↓
┌─────────────────────┐
│  Metrics Collector  │
│  (Python Script)    │
└─────────┬───────────┘
          │
          │ Store
          ↓
┌──────────────────────┐
│   SQLite Database    │
│   (network.db)       │
│   metrics table      │
└──────────┬───────────┘
           │
           │ Query
           ↓
┌──────────────────────┐
│   FastAPI Backend    │
│   /api/devices/*/    │
│   metrics endpoint   │
└──────────┬───────────┘
           │
           │ Fetch
           ↓
┌──────────────────────┐
│  React Frontend      │
│  Historical Analysis │
│  Dashboard Charts    │
└──────────────────────┘
```

## Troubleshooting

### No Metrics Collected

**Issue:** Script runs but collects 0 metrics

**Solutions:**

1. Check UniFi API credentials in `config.py`
2. Verify devices exist in database: `sqlite3 network.db "SELECT * FROM hosts"`
3. Ensure devices are online in UniFi Controller
4. Check MAC addresses match between database and API

### Estimated CPU Inaccurate

**Issue:** CPU estimates don't match reality

**Explanation:**

- CPU estimation is based on client count only
- Real CPU usage depends on: routing, VPN, DPI, threat detection, etc.
- Estimates provide rough approximation for demonstration

**Solution:**

- Enable SNMP on devices for real CPU data
- Or use local UniFi Controller API

### Missing System Stats

**Issue:** No real CPU/memory even though expected

**Cause:**

- UniFi Site Manager (cloud API) doesn't provide system-stats
- Only local controller API exposes full metrics

**Solution:**

1. Check if using cloud vs local controller
2. For cloud users: Must use SNMP or switch to local controller
3. For local users: Verify API endpoint is local IP, not unifi.ui.com

## Database Schema

Metrics are stored in the `metrics` table:

```sql
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id TEXT NOT NULL,           -- References hosts.id
    metric_name TEXT NOT NULL,       -- e.g., 'cpu_usage_estimated'
    metric_value REAL NOT NULL,      -- Numeric value
    unit TEXT,                       -- e.g., '%', 'Mbps', 'clients'
    recorded_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (host_id) REFERENCES hosts(id) ON DELETE CASCADE
);
```

## Next Steps

### Immediate

1. Run `collect_real_metrics.py` to populate with current data
2. View metrics in Historical Analysis Dashboard
3. Schedule script for continuous monitoring

### Future Enhancements

1. Implement SNMP polling for real metrics
2. Add local controller API support
3. Calculate rate metrics (Mbps) from byte counters
4. Add metric aggregation (hourly averages)
5. Implement metric retention policies (e.g., keep raw data 7 days, hourly avg 30 days)

## FAQ

**Q: Why use estimated CPU instead of real?**
A: UniFi Cloud API doesn't provide CPU stats. Need SNMP or local controller.

**Q: How often should I collect metrics?**
A: Every 5 minutes provides good balance. More frequent = more storage, less frequent = gaps in data.

**Q: Can I collect metrics from multiple sites?**
A: Yes, modify collector to iterate through sites. Default is "default" site.

**Q: Does this work with UDM/UXG consoles?**
A: Yes, works with all UniFi devices. Consoles may provide more metrics via local API.

**Q: What about bandwidth attribution by client?**
A: That requires DPI data which is available in different API endpoints. Future feature.

## Support

For issues or questions:

1. Check logs for error messages
2. Verify API connectivity: `python -c "from src.unifi_client import UniFiClient; from src.config_loader import load_config; c = UniFiClient(**load_config().__dict__); c.login(); print('OK')"`
3. Review database: `sqlite3 network.db "SELECT COUNT(*) FROM metrics"`
