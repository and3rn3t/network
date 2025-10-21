# UniFi Analytics Engine - Complete Guide

## Overview

The UniFi Analytics Engine provides comprehensive network analysis for UniFi Controller data, including device health scoring, client experience analysis, network topology insights, signal quality monitoring, and trend detection.

**File**: `src/analytics/unifi_analytics.py` (567 lines)

## Key Features

### 1. Device Health Scoring

Calculates comprehensive health scores (0-100) for UniFi devices based on:

- **CPU Usage** (30% weight) - Lower is better
- **Memory Usage** (30% weight) - Lower is better
- **Uptime** (20% weight) - Higher is better (max score at 30 days)
- **Client Load** (20% weight) - Optimal 20-40 clients for APs

**Status Levels**:

- `excellent`: 90-100
- `good`: 75-89
- `fair`: 60-74
- `poor`: <60

### 2. Client Experience Analysis

Analyzes wireless client satisfaction based on:

- **Signal Strength** (40% weight) - RSSI in dBm
- **Latency** (30% weight) - Network response time
- **Connection Stability** (20% weight) - Reconnection frequency
- **Bandwidth Utilization** (10% weight) - Percentage of capacity

**Signal Quality Levels**:

- `excellent`: RSSI ≥ -60 dBm
- `good`: -70 to -60 dBm
- `fair`: -80 to -70 dBm
- `poor`: < -80 dBm

### 3. Network Topology Analysis

Provides insights into network structure:

- Device counts by type (uap, usw, ugw, etc.)
- Client distribution across devices
- Identification of busiest devices
- Detection of underutilized devices (<5 clients)

### 4. Signal Quality Monitoring

Analyzes wireless signal quality across all clients:

- Distribution by quality level (excellent/good/fair/poor)
- Average and median RSSI
- Identification of weakest clients
- Historical signal trends

### 5. Trend Detection

Linear regression analysis for any metric:

- Trend direction (up, down, stable)
- Slope (rate of change per hour)
- Percent change over period
- Confidence score (R-squared)

### 6. Network Health Summary

Comprehensive dashboard with:

- Device health aggregation
- Client experience scores
- Signal quality distribution
- Event analysis
- Topology insights

## API Reference

### UniFiAnalyticsEngine

```python
from src.analytics.unifi_analytics import UniFiAnalyticsEngine
from src.database import Database

db = Database("network_monitor.db")
analytics = UniFiAnalyticsEngine(db)
```

#### Methods

##### calculate_device_health()

```python
health = analytics.calculate_device_health(
    device_mac="aa:bb:cc:dd:ee:ff",
    hours=24
)

# Returns: DeviceHealthScore
print(f"Health: {health.health_score:.1f}/100")
print(f"Status: {health.status}")
print(f"CPU Score: {health.cpu_score:.1f}")
print(f"Memory Score: {health.memory_score:.1f}")
```

**Parameters**:

- `device_mac` (str): Device MAC address
- `hours` (int): Analysis period in hours (default: 24)

**Returns**: `DeviceHealthScore` or `None`

##### analyze_client_experience()

```python
experience = analytics.analyze_client_experience(
    client_mac="11:22:33:44:55:66",
    hours=24
)

# Returns: ClientExperience
print(f"Experience: {experience.experience_score:.1f}/100")
print(f"Signal: {experience.signal_strength:.1f} dBm")
print(f"Quality: {experience.signal_quality}")
```

**Parameters**:

- `client_mac` (str): Client MAC address
- `hours` (int): Analysis period in hours (default: 24)

**Returns**: `ClientExperience` or `None`

##### analyze_network_topology()

```python
topology = analytics.analyze_network_topology()

# Returns: NetworkTopology
print(f"Total Devices: {topology.total_devices}")
print(f"Total Clients: {topology.total_clients}")
print(f"Devices by Type: {topology.devices_by_type}")
print(f"Busiest Device: {topology.busiest_device}")
```

**Returns**: `NetworkTopology`

##### analyze_signal_quality()

```python
signal = analytics.analyze_signal_quality()

# Returns: SignalQuality
total = signal.excellent_count + signal.good_count + signal.fair_count + signal.poor_count
print(f"Excellent: {signal.excellent_count} ({signal.excellent_count/total:.1%})")
print(f"Average RSSI: {signal.avg_rssi:.1f} dBm")
```

**Returns**: `SignalQuality`

##### detect_metric_trend()

```python
trend = analytics.detect_metric_trend(
    entity_mac="aa:bb:cc:dd:ee:ff",
    metric_name="cpu",
    hours=24
)

# Returns: TrendAnalysis
print(f"Trend: {trend.direction}")
print(f"Change: {trend.change_percent:+.1f}%")
print(f"Confidence: {trend.confidence:.1%}")
```

**Parameters**:

- `entity_mac` (str): Device or client MAC address
- `metric_name` (str): Metric to analyze (e.g., 'cpu', 'memory', 'tx_bytes')
- `hours` (int): Analysis period in hours (default: 24)

**Returns**: `TrendAnalysis` or `None`

##### get_network_health_summary()

```python
summary = analytics.get_network_health_summary(hours=24)

# Returns: Dict with comprehensive network metrics
print(f"Total Devices: {summary['devices']['total']}")
print(f"Avg Health: {summary['devices']['avg_health_score']:.1f}")
print(f"Active Clients: {summary['clients']['total_active']}")
print(f"Avg Experience: {summary['clients']['avg_experience_score']:.1f}")
```

**Parameters**:

- `hours` (int): Analysis period in hours (default: 24)

**Returns**: Dictionary with the following structure:

```python
{
    "timestamp": "2025-10-20T18:30:00",
    "analysis_period_hours": 24,
    "devices": {
        "total": 10,
        "avg_health_score": 85.5,
        "unhealthy_count": 2,
        "unhealthy_devices": [
            {"mac": "...", "name": "AP-Living-Room", "score": 65.2}
        ]
    },
    "clients": {
        "total_active": 45,
        "avg_experience_score": 82.3,
        "poor_experience_count": 5,
        "poor_experience_clients": [
            {"mac": "...", "hostname": "iPhone", "score": 68.5}
        ]
    },
    "signal_quality": {
        "excellent": 20,
        "good": 15,
        "fair": 8,
        "poor": 2,
        "avg_rssi": -65.2
    },
    "topology": {
        "devices_by_type": {"uap": 5, "usw": 3, "ugw": 1},
        "busiest_device": "aa:bb:cc:dd:ee:ff",
        "underutilized_devices": ["11:22:33:44:55:66"]
    },
    "events": {
        "total": 150,
        "by_type": {
            "client_connected": 45,
            "client_disconnected": 42,
            "device_restart": 2
        }
    }
}
```

## Data Classes

### DeviceHealthScore

```python
@dataclass
class DeviceHealthScore:
    device_mac: str
    device_name: str
    device_model: str
    health_score: float      # 0-100
    cpu_score: float
    memory_score: float
    uptime_score: float
    client_score: float
    status: str              # 'excellent', 'good', 'fair', 'poor'
```

### ClientExperience

```python
@dataclass
class ClientExperience:
    client_mac: str
    client_hostname: Optional[str]
    experience_score: float  # 0-100
    signal_strength: float   # RSSI in dBm
    signal_quality: str      # 'excellent', 'good', 'fair', 'poor'
    avg_latency: Optional[float]
    connection_stability: float  # 0-1
    bandwidth_utilization: float # Percentage
```

### NetworkTopology

```python
@dataclass
class NetworkTopology:
    total_devices: int
    total_clients: int
    devices_by_type: Dict[str, int]
    clients_per_device: Dict[str, int]
    busiest_device: Optional[str]
    underutilized_devices: List[str]
```

### SignalQuality

```python
@dataclass
class SignalQuality:
    excellent_count: int     # RSSI >= -60 dBm
    good_count: int          # -70 <= RSSI < -60
    fair_count: int          # -80 <= RSSI < -70
    poor_count: int          # RSSI < -80
    avg_rssi: float
    median_rssi: float
    weakest_clients: List[Tuple[str, float]]  # (mac, rssi)
```

### TrendAnalysis

```python
@dataclass
class TrendAnalysis:
    metric_name: str
    entity_mac: str
    entity_name: str
    direction: str           # 'up', 'down', 'stable'
    slope: float
    change_percent: float
    confidence: float        # 0-1 (R-squared)
```

## Usage Examples

### Example 1: Device Health Dashboard

```python
from src.analytics.unifi_analytics import UniFiAnalyticsEngine
from src.database import Database
from src.database.repositories.unifi_repository import UniFiDeviceRepository

db = Database("network_monitor.db")
analytics = UniFiAnalyticsEngine(db)
device_repo = UniFiDeviceRepository(db)

# Get all devices
devices = device_repo.get_all()

print("Device Health Report")
print("=" * 80)

for device in devices:
    health = analytics.calculate_device_health(device.mac, hours=24)
    if health:
        print(f"\n{device.name} ({device.model})")
        print(f"  Overall: {health.health_score:.1f}/100 [{health.status.upper()}]")
        print(f"  CPU: {health.cpu_score:.1f} | Memory: {health.memory_score:.1f}")
        print(f"  Uptime: {health.uptime_score:.1f} | Clients: {health.client_score:.1f}")
```

### Example 2: Client Experience Report

```python
# Get active clients
client_repo = UniFiClientRepository(db)
clients = client_repo.get_active_clients()

# Find clients with poor experience
poor_clients = []
for client in clients:
    exp = analytics.analyze_client_experience(client.mac, hours=24)
    if exp and exp.experience_score < 70:
        poor_clients.append((client, exp))

# Sort by score (worst first)
poor_clients.sort(key=lambda x: x[1].experience_score)

print("\nClients with Poor Experience")
print("=" * 80)
for client, exp in poor_clients[:10]:
    print(f"\n{client.hostname or 'Unknown'} ({client.mac})")
    print(f"  Score: {exp.experience_score:.1f}/100")
    print(f"  Signal: {exp.signal_strength:.1f} dBm [{exp.signal_quality}]")
    if exp.avg_latency:
        print(f"  Latency: {exp.avg_latency:.1f} ms")
    print(f"  Stability: {exp.connection_stability:.1%}")
```

### Example 3: Network Health Dashboard

```python
# Get comprehensive network summary
summary = analytics.get_network_health_summary(hours=24)

print("\nNetwork Health Summary")
print("=" * 80)
print(f"Analysis Period: {summary['analysis_period_hours']} hours")

print(f"\nDevices:")
print(f"  Total: {summary['devices']['total']}")
if summary['devices']['avg_health_score']:
    print(f"  Average Health: {summary['devices']['avg_health_score']:.1f}/100")
print(f"  Unhealthy: {summary['devices']['unhealthy_count']}")

print(f"\nClients:")
print(f"  Total Active: {summary['clients']['total_active']}")
if summary['clients']['avg_experience_score']:
    print(f"  Average Experience: {summary['clients']['avg_experience_score']:.1f}/100")
print(f"  Poor Experience: {summary['clients']['poor_experience_count']}")

print(f"\nSignal Quality:")
sq = summary['signal_quality']
total = sq['excellent'] + sq['good'] + sq['fair'] + sq['poor']
if total > 0:
    print(f"  Excellent: {sq['excellent']} ({sq['excellent']/total:.1%})")
    print(f"  Good: {sq['good']} ({sq['good']/total:.1%})")
    print(f"  Fair: {sq['fair']} ({sq['fair']/total:.1%})")
    print(f"  Poor: {sq['poor']} ({sq['poor']/total:.1%})")
```

### Example 4: Trend Analysis

```python
# Analyze CPU trend for a device
device = device_repo.get_all()[0]

for metric in ['cpu', 'memory']:
    trend = analytics.detect_metric_trend(device.mac, metric, hours=48)
    if trend:
        print(f"\n{device.name} - {metric.upper()}")
        print(f"  Trend: {trend.direction.upper()}")
        print(f"  Change: {trend.change_percent:+.1f}%")
        print(f"  Rate: {trend.slope:+.4f} per hour")
        print(f"  Confidence: {trend.confidence:.1%}")

        if trend.direction == 'up' and trend.confidence > 0.7:
            print(f"  ⚠️ WARNING: {metric.upper()} trending upward with high confidence")
```

## Demo Script

Run the included demo script to see all analytics features:

```bash
python unifi_analytics_demo.py
```

The demo will show:

- Network health summary
- Network topology analysis
- Signal quality distribution
- Device health scores (top 5)
- Client experience analysis (first 5)
- Trend analysis samples

## Integration with Existing System

The UniFi Analytics Engine integrates seamlessly with the existing analytics system:

```python
# Import both engines
from src.analytics import AnalyticsEngine, UniFiAnalyticsEngine

# Cloud API analytics (for UniFi cloud-managed devices)
cloud_analytics = AnalyticsEngine(db)
cloud_summary = cloud_analytics.get_network_summary(days=7)

# UniFi Controller analytics (for local controller)
unifi_analytics = UniFiAnalyticsEngine(db)
unifi_summary = unifi_analytics.get_network_health_summary(hours=24)
```

## Performance Considerations

- Device health calculation: ~50-100ms per device
- Client experience: ~30-50ms per client
- Network topology: ~10-20ms (cached data)
- Signal quality: ~20-40ms (all active clients)
- Trend detection: ~100-200ms (linear regression)
- Network summary: ~500-1000ms (comprehensive analysis)

For large networks (>100 devices, >500 clients), consider:

- Analyzing in batches
- Caching results for dashboard views
- Running summary calculations in background tasks
- Limiting historical data ranges

## Best Practices

1. **Sampling Period**: Use 24 hours for real-time monitoring, 7 days for trend analysis
2. **Health Thresholds**: Adjust based on your network requirements
3. **Signal Quality**: -60 dBm is excellent for most scenarios, but may vary by environment
4. **Client Experience**: Weight signal strength higher for mobile devices
5. **Trend Confidence**: Only act on trends with confidence >0.7

## Troubleshooting

### No data returned

Check that:

- Data collection is running (`collect_unifi_data.py`)
- Database has recent entries
- MACs are formatted correctly (lowercase, with colons)

### Poor performance

- Reduce analysis time range
- Add database indexes (already included in schema)
- Sample clients instead of analyzing all
- Run analytics in background

### Inaccurate scores

- Verify sufficient historical data (at least 10 data points)
- Check for gaps in data collection
- Adjust scoring weights for your environment

## Next Steps

1. Run data collection: `python collect_unifi_data.py --daemon`
2. Wait for metrics to accumulate (at least 1 hour)
3. Run demo: `python unifi_analytics_demo.py`
4. Integrate into your monitoring dashboard
5. Set up alerts based on health scores

## Related Documentation

- **Data Collection**: See `collect_unifi_data.py`
- **Database Schema**: See `src/database/schema_unifi_controller.sql`
- **Data Models**: See `src/database/models_unifi.py`
- **Repositories**: See `src/database/repositories/unifi_repository.py`
