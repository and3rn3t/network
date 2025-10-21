# UniFi Network API - Usage Guide

**Last Updated:** October 17, 2025

This guide provides detailed examples and best practices for using the UniFi Network API client and data collection system.

## Table of Contents

1. [Getting Started](#getting-started)
2. [API Client Usage](#api-client-usage)
3. [Data Collector](#data-collector)
4. [Database Queries](#database-queries)
5. [Event Monitoring](#event-monitoring)
6. [Metrics Analysis](#metrics-analysis)
7. [Common Patterns](#common-patterns)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- UniFi Site Manager account
- API key (see [Authentication](#authentication))

### Installation

```bash
# Clone the repository
git clone https://github.com/and3rn3t/network.git
cd network

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config.example.py config.py
```

### Authentication

1. Sign in to [UniFi Site Manager](https://unifi.ui.com)
2. Navigate to Settings → API
3. Click "Create API Key"
4. Copy the key and add it to `config.py`:

```python
# config.py
API_KEY = "your-api-key-here"
```

⚠️ **Security Note:** Never commit your API key to version control!

---

## API Client Usage

### Initialize the Client

```python
from src.unifi_client import UniFiClient
from config import API_KEY

# Create client instance
client = UniFiClient(api_key=API_KEY)
```

### Get All Hosts

```python
# Fetch all devices on your network
hosts = client.get_hosts()

print(f"Total devices: {len(hosts)}")

for host in hosts:
    print(f"Device: {host['name']}")
    print(f"  MAC: {host['macAddr']}")
    print(f"  Status: {'Online' if host['isOnline'] else 'Offline'}")
    print(f"  Type: {host.get('deviceType', 'Unknown')}")
    print()
```

### Get Specific Host Details

```python
# Get details for a specific device
host_id = "abc123..."
host = client.get_host(host_id)

print(f"Device Name: {host['name']}")
print(f"IP Address: {host.get('ip', 'N/A')}")
print(f"Last Seen: {host.get('lastSeen', 'N/A')}")
print(f"Manufacturer: {host.get('oui', 'Unknown')}")

# Check if metrics are available
if 'cpu' in host:
    print(f"CPU Usage: {host['cpu']}%")
if 'memory' in host:
    print(f"Memory Usage: {host['memory']}%")
```

### Filter Online Devices

```python
# Get only online devices
hosts = client.get_hosts()
online_hosts = [h for h in hosts if h.get('isOnline', False)]

print(f"Online devices: {len(online_hosts)}/{len(hosts)}")

for host in online_hosts:
    print(f"✓ {host['name']} - {host.get('ip', 'No IP')}")
```

### Error Handling

```python
from src.exceptions import UniFiAPIError, UniFiAuthError, UniFiRateLimitError

try:
    hosts = client.get_hosts()
except UniFiAuthError as e:
    print(f"Authentication failed: {e}")
    print("Check your API key in config.py")
except UniFiRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    print("Wait a moment before retrying")
except UniFiAPIError as e:
    print(f"API error: {e}")
```

---

## Data Collector

### Basic Configuration

```python
from src.collector import CollectorConfig

# Create configuration
config = CollectorConfig(
    api_key=API_KEY,
    collection_interval=300,      # Collect every 5 minutes
    db_path="data/unifi_network.db",
    enable_metrics=True,           # Collect CPU, memory, temp
    enable_events=True,            # Track status changes
    host_retention_days=90,        # Keep host data for 90 days
    metrics_retention_days=365,    # Keep metrics for 1 year
    events_retention_days=30       # Keep events for 30 days
)
```

### Single Collection Run

```python
from src.collector import DataCollector

# Create collector
collector = DataCollector(config)

# Run one collection cycle
stats = collector.collect()

print("Collection Summary:")
print(f"  Hosts collected: {stats['hosts_collected']}")
print(f"  New hosts: {stats['hosts_created']}")
print(f"  Updated hosts: {stats['hosts_updated']}")
print(f"  Events generated: {stats['events_generated']}")
print(f"  Metrics recorded: {stats['metrics_recorded']}")
print(f"  Collection time: {stats['collection_time']:.2f}s")
```

### Run as Daemon

```python
from src.collector import run_collector

# Run continuously in the background
run_collector(
    config=config,
    daemon=True,        # Run as background service
    immediate=True      # Run first collection immediately
)

# The collector will:
# - Run an initial collection immediately
# - Then collect every 5 minutes (based on config)
# - Handle graceful shutdown on SIGINT/SIGTERM
# - Automatically retry on transient failures
```

### Custom Collection Script

```python
# examples/custom_collector.py
from src.collector import CollectorConfig, DataCollector
from config import API_KEY
import time

config = CollectorConfig(
    api_key=API_KEY,
    collection_interval=60,  # Every minute for testing
    db_path="data/test.db"
)

collector = DataCollector(config)

print("Starting custom collection...")
for i in range(10):  # Collect 10 times
    print(f"\nCollection #{i+1}")
    stats = collector.collect()
    print(f"  Collected {stats['hosts_collected']} hosts")

    if i < 9:  # Don't wait after last collection
        time.sleep(config.collection_interval)

print("\nDone!")
```

---

## Database Queries

### Using Repositories

```python
from src.database import Database
from src.database.repositories import HostRepository, EventRepository, MetricRepository

# Initialize database
db = Database("data/unifi_network.db")

# Create repositories
host_repo = HostRepository(db)
event_repo = EventRepository(db)
metric_repo = MetricRepository(db)
```

### Query Hosts

```python
# Get all hosts
all_hosts = host_repo.get_all()
print(f"Total hosts in database: {len(all_hosts)}")

# Get active hosts only
active_hosts = host_repo.get_active()
print(f"Active hosts: {len(active_hosts)}")

# Get specific host by ID
host = host_repo.get_by_id("host-id-123")
if host:
    print(f"Host: {host.name}")
    print(f"  MAC: {host.mac_addr}")
    print(f"  Last seen: {host.last_seen}")

# Get host by MAC address
host = host_repo.get_by_mac("aa:bb:cc:dd:ee:ff")

# Search hosts by name
switches = host_repo.search_by_name("switch")
for switch in switches:
    print(f"Switch: {switch.name}")
```

### Query Events

```python
from datetime import datetime, timedelta

# Get recent events (last 24 hours)
yesterday = datetime.now() - timedelta(days=1)
recent_events = event_repo.get_by_time_range(
    start_time=yesterday,
    end_time=datetime.now()
)

print(f"\nEvents in last 24 hours: {len(recent_events)}")
for event in recent_events:
    print(f"  [{event.timestamp}] {event.event_type}: {event.description}")

# Get events for specific host
host_events = event_repo.get_by_host_id("host-id-123")

# Get specific event types
offline_events = event_repo.get_by_type("host_offline")
for event in offline_events:
    print(f"Device went offline: {event.description}")

# Get event counts by type
event_counts = event_repo.get_event_counts(
    start_time=yesterday,
    end_time=datetime.now()
)
for event_type, count in event_counts.items():
    print(f"  {event_type}: {count}")
```

### Query Metrics

```python
# Get latest metrics for a host
latest_metrics = metric_repo.get_by_host_id(
    host_id="host-id-123",
    limit=10  # Last 10 data points
)

for metric in latest_metrics:
    print(f"[{metric.timestamp}]")
    print(f"  CPU: {metric.cpu_usage}%")
    print(f"  Memory: {metric.memory_usage}%")
    print(f"  Temperature: {metric.temperature}°C")

# Get metrics for time range
week_ago = datetime.now() - timedelta(days=7)
metrics = metric_repo.get_by_time_range(
    host_id="host-id-123",
    start_time=week_ago,
    end_time=datetime.now()
)

# Calculate average CPU over the week
if metrics:
    avg_cpu = sum(m.cpu_usage for m in metrics if m.cpu_usage) / len(metrics)
    print(f"Average CPU (7 days): {avg_cpu:.1f}%")
```

### Advanced Queries with SQL Views

```python
# Use the pre-built views for complex queries
import sqlite3

conn = sqlite3.connect("data/unifi_network.db")
conn.row_factory = sqlite3.Row

# View: host_status_summary
# Shows current status for all hosts
cursor = conn.execute("""
    SELECT * FROM host_status_summary
    WHERE status = 'offline'
""")
offline = cursor.fetchall()
print(f"\nOffline devices: {len(offline)}")
for row in offline:
    print(f"  {row['host_name']} (last seen: {row['last_seen']})")

# View: recent_events
# Shows events from last 24 hours
cursor = conn.execute("""
    SELECT * FROM recent_events
    WHERE event_type = 'host_offline'
    ORDER BY timestamp DESC
""")
events = cursor.fetchall()
print(f"\nRecent offline events: {len(events)}")

# View: host_metrics_latest
# Shows most recent metrics for each host
cursor = conn.execute("""
    SELECT host_name, cpu_usage, memory_usage, temperature
    FROM host_metrics_latest
    WHERE cpu_usage > 80
""")
high_cpu = cursor.fetchall()
print(f"\nHosts with high CPU: {len(high_cpu)}")
for row in high_cpu:
    print(f"  {row['host_name']}: {row['cpu_usage']}%")

conn.close()
```

---

## Event Monitoring

### Monitor Status Changes

```python
from src.database import Database
from src.database.repositories import EventRepository
from datetime import datetime
import time

db = Database("data/unifi_network.db")
event_repo = EventRepository(db)

print("Monitoring for new events... (Ctrl+C to stop)")

last_check = datetime.now()

try:
    while True:
        # Check for new events since last check
        new_events = event_repo.get_by_time_range(
            start_time=last_check,
            end_time=datetime.now()
        )

        for event in new_events:
            print(f"[{event.timestamp}] {event.event_type}")
            print(f"  {event.description}")
            if event.details:
                print(f"  Details: {event.details}")

        last_check = datetime.now()
        time.sleep(10)  # Check every 10 seconds

except KeyboardInterrupt:
    print("\nMonitoring stopped")
```

### Alert on Specific Events

```python
def check_for_offline_devices():
    """Alert when devices go offline"""
    db = Database("data/unifi_network.db")
    event_repo = EventRepository(db)

    # Check last 5 minutes
    recent = datetime.now() - timedelta(minutes=5)
    offline_events = event_repo.get_by_type("host_offline")
    offline_events = [e for e in offline_events if e.timestamp >= recent]

    if offline_events:
        print(f"⚠️  {len(offline_events)} device(s) went offline:")
        for event in offline_events:
            print(f"   - {event.description}")
            # Could send email, SMS, webhook, etc.

    return len(offline_events)

# Run every 5 minutes
while True:
    check_for_offline_devices()
    time.sleep(300)
```

---

## Metrics Analysis

### Calculate Statistics

```python
from src.database import Database
from src.database.repositories import MetricRepository
from datetime import datetime, timedelta
from statistics import mean, median

db = Database("data/unifi_network.db")
metric_repo = MetricRepository(db)

# Get metrics for last 7 days
week_ago = datetime.now() - timedelta(days=7)
metrics = metric_repo.get_by_time_range(
    host_id="host-id-123",
    start_time=week_ago,
    end_time=datetime.now()
)

if metrics:
    cpu_values = [m.cpu_usage for m in metrics if m.cpu_usage is not None]
    memory_values = [m.memory_usage for m in metrics if m.memory_usage is not None]

    print("CPU Statistics (7 days):")
    print(f"  Average: {mean(cpu_values):.1f}%")
    print(f"  Median: {median(cpu_values):.1f}%")
    print(f"  Min: {min(cpu_values):.1f}%")
    print(f"  Max: {max(cpu_values):.1f}%")

    print("\nMemory Statistics (7 days):")
    print(f"  Average: {mean(memory_values):.1f}%")
    print(f"  Median: {median(memory_values):.1f}%")
    print(f"  Min: {min(memory_values):.1f}%")
    print(f"  Max: {max(memory_values):.1f}%")
```

### Detect Trends

```python
def detect_upward_trend(values, threshold=0.1):
    """Detect if values are trending upward"""
    if len(values) < 2:
        return False

    # Simple linear regression slope
    n = len(values)
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(values) / n

    numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return False

    slope = numerator / denominator
    return slope > threshold

# Check if CPU is trending up
cpu_values = [m.cpu_usage for m in metrics if m.cpu_usage is not None]
if detect_upward_trend(cpu_values[-20:]):  # Last 20 readings
    print("⚠️  CPU usage is trending upward!")
```

### Export Metrics to CSV

```python
import csv
from datetime import datetime, timedelta

db = Database("data/unifi_network.db")
metric_repo = MetricRepository(db)
host_repo = HostRepository(db)

# Get all active hosts
hosts = host_repo.get_active()

# Export last 24 hours of metrics
yesterday = datetime.now() - timedelta(days=1)

with open('metrics_export.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Timestamp', 'Host Name', 'CPU %', 'Memory %', 'Temp °C', 'Uptime'])

    for host in hosts:
        metrics = metric_repo.get_by_time_range(
            host_id=host.id,
            start_time=yesterday,
            end_time=datetime.now()
        )

        for metric in metrics:
            writer.writerow([
                metric.timestamp,
                host.name,
                metric.cpu_usage,
                metric.memory_usage,
                metric.temperature,
                metric.uptime
            ])

print(f"Exported metrics to metrics_export.csv")
```

---

## Common Patterns

### Batch Processing

```python
from src.unifi_client import UniFiClient
from src.database import Database
from src.database.repositories import HostRepository
from config import API_KEY

client = UniFiClient(api_key=API_KEY)
db = Database("data/unifi_network.db")
host_repo = HostRepository(db)

# Get all hosts from API
api_hosts = client.get_hosts()

# Process in batches
batch_size = 10
for i in range(0, len(api_hosts), batch_size):
    batch = api_hosts[i:i + batch_size]
    print(f"Processing batch {i//batch_size + 1}...")

    for host_data in batch:
        # Update or create in database
        host = host_repo.get_by_id(host_data['id'])
        if host:
            host_repo.update(host_data['id'], host_data)
        else:
            host_repo.create(host_data)

    print(f"  Processed {len(batch)} hosts")
```

### Scheduled Reports

```python
from datetime import datetime, timedelta
import schedule
import time

def generate_daily_report():
    """Generate daily status report"""
    db = Database("data/unifi_network.db")
    host_repo = HostRepository(db)
    event_repo = EventRepository(db)

    # Get statistics
    total_hosts = len(host_repo.get_all())
    active_hosts = len(host_repo.get_active())

    # Get yesterday's events
    yesterday = datetime.now() - timedelta(days=1)
    events = event_repo.get_by_time_range(yesterday, datetime.now())

    print(f"\n{'='*50}")
    print(f"Daily Report - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*50}")
    print(f"Total Devices: {total_hosts}")
    print(f"Active Devices: {active_hosts}")
    print(f"Inactive Devices: {total_hosts - active_hosts}")
    print(f"Events (24h): {len(events)}")

    # Event breakdown
    event_counts = {}
    for event in events:
        event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1

    print("\nEvent Breakdown:")
    for event_type, count in event_counts.items():
        print(f"  {event_type}: {count}")
    print(f"{'='*50}\n")

# Schedule daily at 8 AM
schedule.every().day.at("08:00").do(generate_daily_report)

print("Daily report scheduler started...")
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Data Cleanup

```python
from datetime import datetime, timedelta

def cleanup_old_data(db_path="data/unifi_network.db"):
    """Clean up old data based on retention policies"""
    db = Database(db_path)

    # Delete old metrics (older than 365 days)
    metrics_cutoff = datetime.now() - timedelta(days=365)
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM metrics
        WHERE timestamp < ?
    """, (metrics_cutoff,))
    metrics_deleted = cursor.rowcount

    # Delete old events (older than 30 days)
    events_cutoff = datetime.now() - timedelta(days=30)
    cursor.execute("""
        DELETE FROM events
        WHERE timestamp < ?
    """, (events_cutoff,))
    events_deleted = cursor.rowcount

    conn.commit()
    conn.close()

    print(f"Cleanup complete:")
    print(f"  Deleted {metrics_deleted} old metrics")
    print(f"  Deleted {events_deleted} old events")

# Run cleanup weekly
schedule.every().week.do(cleanup_old_data)
```

---

## Troubleshooting

### Common Issues

#### 1. Authentication Errors

```python
# Problem: UniFiAuthError: Invalid API key
# Solution: Check your API key in config.py

from src.unifi_client import UniFiClient
from src.exceptions import UniFiAuthError

try:
    client = UniFiClient(api_key="your-key")
    hosts = client.get_hosts()
except UniFiAuthError:
    print("Check your API key:")
    print("1. Log in to unifi.ui.com")
    print("2. Go to Settings → API")
    print("3. Generate new key if needed")
```

#### 2. Rate Limiting

```python
# Problem: UniFiRateLimitError: Rate limit exceeded
# Solution: Use the built-in retry logic or increase intervals

from src.collector import CollectorConfig

config = CollectorConfig(
    api_key=API_KEY,
    collection_interval=600  # Increase to 10 minutes
)
```

#### 3. Database Locked

```python
# Problem: Database is locked
# Solution: Ensure only one writer at a time

# Don't do this:
# collector1 = DataCollector(config)  # Writing to DB
# collector2 = DataCollector(config)  # Also writing to same DB!

# Instead, use one collector or separate databases
config1 = CollectorConfig(api_key=API_KEY, db_path="data/collector1.db")
config2 = CollectorConfig(api_key=API_KEY, db_path="data/collector2.db")
```

#### 4. No Metrics Available

```python
# Some devices don't report metrics
host = client.get_host(host_id)

# Always check before using
cpu = host.get('cpu')
if cpu is not None:
    print(f"CPU: {cpu}%")
else:
    print("CPU metrics not available for this device")
```

### Enable Debug Logging

```python
import logging

# Enable debug output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now all API calls and database operations will be logged
client = UniFiClient(api_key=API_KEY)
hosts = client.get_hosts()  # Will show detailed request/response info
```

### Test Database Connection

```python
from src.database import Database

try:
    db = Database("data/unifi_network.db")
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM hosts")
    count = cursor.fetchone()[0]
    print(f"✓ Database OK - {count} hosts")
    conn.close()
except Exception as e:
    print(f"✗ Database error: {e}")
```

---

## Additional Resources

- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API method documentation
- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
- **[PHASE_2_COMPLETE.md](PHASE_2_COMPLETE.md)** - Phase 2 implementation details
- **[DATA_COLLECTOR_COMPLETE.md](DATA_COLLECTOR_COMPLETE.md)** - Collector deep dive

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review the [UniFi API Documentation](https://developer.ui.com/site-manager-api/gettingstarted)
3. Open an issue on GitHub

---

**Happy Monitoring! 🚀**
