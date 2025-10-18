# Data Export Documentation

## Overview

The UniFi Network Monitoring System provides flexible data export capabilities to integrate with external tools and systems. Export your monitoring data in multiple formats for analysis, visualization, and integration.

## Supported Formats

### 1. CSV (Comma-Separated Values)

- **Use Case**: Excel analysis, spreadsheet imports, data migration
- **Compatibility**: Excel, Google Sheets, LibreOffice Calc
- **Features**: Headers included, UTF-8 encoding, RFC 4180 compliant

### 2. JSON (JavaScript Object Notation)

- **Use Case**: API integration, programmatic access, data archiving
- **Compatibility**: Any JSON parser, REST APIs, web applications
- **Features**: Pretty-printed, ISO 8601 timestamps, metadata included

### 3. Prometheus Metrics

- **Use Case**: Prometheus monitoring, Grafana dashboards, alerting
- **Compatibility**: Prometheus, VictoriaMetrics, Grafana, Thanos
- **Features**: Standard Prometheus text format, labels, gauges/counters

## Quick Start

### Export Hosts to JSON

```bash
python examples/export_data.py --format json --type hosts
```

### Export Events to CSV

```bash
python examples/export_data.py --format csv --type events --days 30
```

### Generate Prometheus Metrics

```bash
python examples/export_data.py --format prometheus
```

## Export Types

### Hosts

Export complete host/device information including status, uptime, and network details.

**CSV Fields:**

- `id` - Unique host identifier
- `name` - Device name
- `mac` - MAC address
- `model` - Device model
- `status` - Current status
- `is_online` - Online/offline (Yes/No)
- `ip_address` - IP address
- `uptime` - Uptime in seconds
- `last_seen` - Last seen timestamp (ISO 8601)
- `created_at` - Record creation timestamp

**JSON Structure:**

```json
{
  "export_date": "2025-10-17T21:45:00",
  "total_hosts": 5,
  "hosts": [
    {
      "id": "abc123",
      "name": "AP Living Room",
      "mac": "00:11:22:33:44:55",
      "model": "UAP-AC-PRO",
      "status": "connected",
      "is_online": true,
      "ip_address": "192.168.1.100",
      "uptime": 86400,
      "last_seen": "2025-10-17T21:44:00",
      "created_at": "2025-10-01T10:00:00"
    }
  ]
}
```

### Events

Export event history including status changes, alerts, and notifications.

**CSV Fields:**

- `id` - Unique event identifier
- `timestamp` - Event timestamp (ISO 8601)
- `event_type` - Type of event
- `severity` - Severity level (info/warning/error)
- `message` - Event description
- `host_id` - Associated host ID
- `created_at` - Record creation timestamp

**JSON Structure:**

```json
{
  "export_date": "2025-10-17T21:45:00",
  "date_range": {
    "start": "2025-10-10T00:00:00",
    "end": "2025-10-17T21:45:00"
  },
  "total_events": 42,
  "events": [
    {
      "id": "evt_001",
      "timestamp": "2025-10-17T15:30:00",
      "event_type": "status_change",
      "severity": "warning",
      "message": "Device went offline",
      "host_id": "abc123"
    }
  ]
}
```

### Metrics

Export time-series metrics data (CPU, memory, temperature, uptime, etc.).

**CSV Fields:**

- `id` - Unique metric identifier
- `timestamp` - Measurement timestamp (ISO 8601)
- `host_id` - Host identifier
- `metric_name` - Metric name (cpu_usage, memory_usage, etc.)
- `metric_value` - Numeric value
- `created_at` - Record creation timestamp

**JSON Structure:**

```json
{
  "export_date": "2025-10-17T21:45:00",
  "date_range": {
    "start": "2025-10-10T00:00:00",
    "end": "2025-10-17T21:45:00"
  },
  "filters": {
    "host_id": null,
    "metric_name": "cpu_usage"
  },
  "total_metrics": 1000,
  "metrics": [
    {
      "id": "met_001",
      "timestamp": "2025-10-17T21:40:00",
      "host_id": "abc123",
      "metric_name": "cpu_usage",
      "metric_value": 45.2
    }
  ]
}
```

## Prometheus Metrics

### Available Metrics

#### Host Metrics

**unifi_hosts_total**

- Type: Gauge
- Description: Total number of hosts in the system

**unifi_hosts_online**

- Type: Gauge
- Description: Number of currently online hosts

**unifi_hosts_offline**

- Type: Gauge
- Description: Number of currently offline hosts

**unifi_host_uptime**

- Type: Gauge
- Labels: `host_id`, `host_name`, `mac`
- Description: Host uptime in seconds

**unifi_host_status**

- Type: Gauge
- Labels: `host_id`, `host_name`, `mac`
- Description: Host status (1=online, 0=offline)

#### Performance Metrics

Dynamic metrics based on collected data (last 5 minutes):

**unifi_cpu_usage**

- Type: Gauge
- Labels: `host_id`, `host_name`, `mac`
- Description: CPU usage percentage

**unifi_memory_usage**

- Type: Gauge
- Labels: `host_id`, `host_name`, `mac`
- Description: Memory usage percentage

**unifi_temperature**

- Type: Gauge
- Labels: `host_id`, `host_name`, `mac`
- Description: Device temperature in Celsius

#### Event Metrics

**unifi_events_24h**

- Type: Counter
- Description: Total events in last 24 hours

**unifi_events_by_severity**

- Type: Counter
- Labels: `severity`
- Description: Events by severity level (24h window)

### Prometheus Integration

#### Option 1: File-based (Simple)

1. Export metrics to file:

```bash
python examples/export_data.py --format prometheus --output /var/lib/prometheus/textfile/unifi.prom
```

2. Configure Prometheus textfile collector:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: "unifi-textfile"
    static_configs:
      - targets: ["localhost:9100"]
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: "unifi_.*"
        action: keep
```

3. Schedule periodic exports (cron):

```bash
*/5 * * * * cd /path/to/network && python examples/export_data.py --format prometheus --output /var/lib/prometheus/textfile/unifi.prom
```

#### Option 2: HTTP Endpoint (Advanced)

Create a simple HTTP server to serve metrics:

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
from src.export import PrometheusExporter

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            exporter = PrometheusExporter("network.db")
            metrics = exporter.generate_metrics()

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(metrics.encode('utf-8'))
        else:
            self.send_error(404)

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 9091), MetricsHandler)
    print("Metrics server running on :9091/metrics")
    server.serve_forever()
```

Configure Prometheus to scrape:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: "unifi"
    static_configs:
      - targets: ["localhost:9091"]
    scrape_interval: 30s
```

## Command-Line Options

### Basic Usage

```bash
python examples/export_data.py [OPTIONS]
```

### Options

**--format** {csv,json,prometheus}

- Export format (default: json)

**--type** {hosts,events,metrics}

- Data type to export (default: hosts)
- Not used with prometheus format

**--output** PATH

- Output file path (default: auto-generated timestamp)

**--db** PATH

- Database path (default: network.db)

**--days** N

- Number of days for events/metrics (default: 7)

**--host-id** ID

- Filter metrics by specific host ID

**--metric-name** NAME

- Filter metrics by metric name (e.g., cpu_usage)

### Examples

#### Export all hosts to CSV

```bash
python examples/export_data.py --format csv --type hosts --output hosts.csv
```

#### Export last 30 days of events to JSON

```bash
python examples/export_data.py --format json --type events --days 30
```

#### Export CPU metrics for specific host

```bash
python examples/export_data.py --format csv --type metrics --host-id abc123 --metric-name cpu_usage
```

#### Generate Prometheus metrics

```bash
python examples/export_data.py --format prometheus --output metrics.txt
```

## Programmatic Usage

### CSV Export

```python
from src.export import CSVExporter

exporter = CSVExporter("network.db")

# Export hosts
count = exporter.export_hosts("output/hosts.csv")
print(f"Exported {count} hosts")

# Export events (last 30 days)
count = exporter.export_events("output/events.csv", days=30)
print(f"Exported {count} events")

# Export metrics with filters
count = exporter.export_metrics(
    "output/metrics.csv",
    host_id="abc123",
    metric_name="cpu_usage",
    days=7
)
print(f"Exported {count} metrics")
```

### JSON Export

```python
from src.export import JSONExporter

exporter = JSONExporter("network.db")

# Export hosts
result = exporter.export_hosts("output/hosts.json")
print(f"Exported {result['rows']} hosts to {result['file']}")

# Export events
result = exporter.export_events("output/events.json", days=30)
print(f"Exported {result['rows']} events")

# Export metrics
result = exporter.export_metrics(
    "output/metrics.json",
    metric_name="memory_usage",
    days=7
)
```

### Prometheus Metrics

```python
from src.export import PrometheusExporter

exporter = PrometheusExporter("network.db")

# Generate metrics text
metrics_text = exporter.generate_metrics()
print(metrics_text)

# Export to file
count = exporter.export_to_file("metrics.prom")
print(f"Exported {count} metric lines")
```

## Grafana Integration

### Setup Steps

1. **Install Prometheus** (if not already installed)
2. **Configure metrics export** (file-based or HTTP endpoint)
3. **Add Prometheus as Grafana data source**
4. **Import or create dashboards**

### Sample Grafana Queries

#### Device Availability

```promql
# Percentage of online devices
100 * unifi_hosts_online / unifi_hosts_total
```

#### CPU Usage by Host

```promql
# CPU usage for all hosts
unifi_cpu_usage

# Average CPU across all hosts
avg(unifi_cpu_usage)

# Hosts with high CPU (>80%)
unifi_cpu_usage > 80
```

#### Memory Trends

```promql
# Memory usage rate of change (per minute)
rate(unifi_memory_usage[5m]) * 60

# Memory usage prediction (1 hour ahead)
predict_linear(unifi_memory_usage[1h], 3600)
```

#### Event Rate

```promql
# Events per minute (last 5 minutes)
rate(unifi_events_24h[5m]) * 60

# Events by severity
sum by(severity) (unifi_events_by_severity)
```

#### Uptime Monitoring

```promql
# Devices with uptime < 1 hour
unifi_host_uptime < 3600

# Average uptime across all hosts
avg(unifi_host_uptime)
```

## Automation

### Scheduled CSV Exports (Linux/Mac)

```bash
# Daily host export at midnight
0 0 * * * cd /path/to/network && python examples/export_data.py --format csv --type hosts --output /backups/hosts_$(date +\%Y\%m\%d).csv

# Weekly event export on Sunday
0 2 * * 0 cd /path/to/network && python examples/export_data.py --format json --type events --days 7 --output /backups/events_weekly.json
```

### Scheduled Exports (Windows Task Scheduler)

1. Create batch file `export_daily.bat`:

```batch
@echo off
cd C:\path\to\network
python examples\export_data.py --format csv --type hosts --output C:\backups\hosts.csv
```

2. Schedule in Task Scheduler:

- Trigger: Daily at desired time
- Action: Start program `C:\path\to\network\export_daily.bat`

## Best Practices

1. **Regular Exports**: Schedule daily/weekly exports for backup
2. **Date Ranges**: Use appropriate time ranges for events/metrics
3. **File Naming**: Use timestamps in filenames for version control
4. **Disk Space**: Monitor export directory size, implement rotation
5. **Compression**: Compress large CSV/JSON files for storage
6. **Security**: Protect exported files (contain network topology)
7. **Validation**: Verify exports complete successfully
8. **Documentation**: Document export schedules and formats

## Troubleshooting

### Empty Exports

**Issue**: Exported files contain no data

**Solutions**:

- Verify database has data: `sqlite3 network.db "SELECT COUNT(*) FROM hosts;"`
- Check date range for events/metrics
- Ensure data collector has run
- Verify database path is correct

### Prometheus Metrics Not Updating

**Issue**: Metrics show old data in Prometheus

**Solutions**:

- Check export schedule (cron/task scheduler)
- Verify file permissions on output file
- Check Prometheus textfile collector configuration
- Ensure Prometheus is scraping at correct interval

### Large File Sizes

**Issue**: Export files are too large

**Solutions**:

- Reduce date range (use --days parameter)
- Filter by specific hosts (--host-id)
- Filter by metric type (--metric-name)
- Export incrementally (daily instead of all-time)
- Compress output files (gzip)

## Performance

### Export Times

Based on 100 devices with 1 week of data:

- **CSV Hosts**: < 0.1 seconds
- **CSV Events**: 0.5-1 seconds (1,000 events)
- **CSV Metrics**: 1-2 seconds (10,000 metrics)
- **JSON Hosts**: < 0.1 seconds
- **JSON Events**: 0.5-1 seconds
- **JSON Metrics**: 1-2 seconds
- **Prometheus**: 0.1-0.5 seconds

### File Sizes

Typical sizes for 100 devices, 7 days:

- **Hosts CSV**: 5-10 KB
- **Events CSV**: 50-200 KB
- **Metrics CSV**: 500 KB - 2 MB
- **Hosts JSON**: 10-20 KB
- **Events JSON**: 100-400 KB
- **Metrics JSON**: 1-4 MB
- **Prometheus**: 10-50 KB

## API Reference

### CSVExporter

```python
class CSVExporter(DataExporter):
    def export_hosts(output_path: str) -> int
    def export_events(output_path: str, start_date=None, end_date=None, days=7) -> int
    def export_metrics(output_path: str, host_id=None, metric_name=None,
                      start_date=None, end_date=None, days=7) -> int
```

### JSONExporter

```python
class JSONExporter(DataExporter):
    def export_hosts(output_path: str) -> Dict[str, Any]
    def export_events(output_path: str, start_date=None, end_date=None,
                     days=7) -> Dict[str, Any]
    def export_metrics(output_path: str, host_id=None, metric_name=None,
                      start_date=None, end_date=None, days=7) -> Dict[str, Any]
```

### PrometheusExporter

```python
class PrometheusExporter(DataExporter):
    def generate_metrics() -> str
    def export_to_file(output_path: str) -> int
```

## Support

For questions or issues:

1. Check this documentation
2. Review example scripts in `examples/`
3. Check [GitHub Issues](https://github.com/your-repo/issues)
4. Create new issue with sample export output

---

**Last Updated**: October 17, 2025
**Version**: 1.0.0
