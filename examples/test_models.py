"""
Test data models.

Verify that all models can be created, serialized, and converted properly.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.models import CollectionRun, Event, Host, HostStatus, Metric


def test_host_model():
    """Test Host model creation and methods."""
    print("🔧 Testing Host Model...")

    # Test from_api_response
    api_data = {
        "id": "test-host-123",
        "hardwareId": "hw-456",
        "type": "console",
        "ipAddress": "192.168.1.100",
        "mac": "00:11:22:33:44:55",
        "name": "UniFi Cloud Key",
        "owner": True,
        "isBlocked": False,
        "firmwareVersion": "3.2.7",
        "model": "UCK-G2-PLUS",
        "registrationTime": "2020-08-23T18:34:03Z",
    }

    host = Host.from_api_response(api_data)
    print(f"   Created from API: {host}")
    print(f"   ID: {host.id}")
    print(f"   Name: {host.name}")
    print(f"   Type: {host.type}")
    print(f"   IP: {host.ip_address}")

    # Test to_db_params
    params = host.to_db_params()
    print(f"   DB params: {len(params)} fields")

    # Test to_dict
    host_dict = host.to_dict()
    print(f"   Dict keys: {list(host_dict.keys())[:5]}...")

    print("   ✅ Host model works!\n")
    return host


def test_host_status_model():
    """Test HostStatus model creation and methods."""
    print("📊 Testing HostStatus Model...")

    # Test from_api_response
    api_data = {
        "isOnline": True,
        "uptimeSeconds": 86400,
        "lastConnectionStateChange": "2025-10-17T10:00:00Z",
        "latestBackupTime": "2025-10-17T02:00:00Z",
        "metrics": {"cpu": 15.5, "memory": 45.2, "temperature": 55.0},
    }

    status = HostStatus.from_api_response("test-host-123", api_data)
    print(f"   Created from API: {status}")
    print(f"   Status: {status.status}")
    print(f"   Online: {status.is_online}")
    print(f"   Uptime: {status.uptime_seconds}s")
    print(f"   CPU: {status.cpu_usage}%")
    print(f"   Memory: {status.memory_usage}%")
    print(f"   Temp: {status.temperature}°C")

    # Test to_db_params
    params = status.to_db_params()
    print(f"   DB params: {len(params)} fields")

    # Verify raw_data is JSON
    raw_data = json.loads(status.raw_data)
    print(f"   Raw data keys: {list(raw_data.keys())}")

    print("   ✅ HostStatus model works!\n")
    return status


def test_event_model():
    """Test Event model creation and methods."""
    print("📝 Testing Event Model...")

    # Test status change event
    event1 = Event.create_status_change(
        host_id="test-host-123",
        old_status="offline",
        new_status="online",
        severity="info",
    )
    print(f"   Status change: {event1}")
    print(f"   Title: {event1.title}")
    print(f"   Previous: {event1.previous_value}")
    print(f"   New: {event1.new_value}")

    # Test error event
    event2 = Event.create_error(
        host_id="test-host-123",
        title="Connection timeout",
        description="Failed to connect after 3 retries",
        severity="error",
    )
    print(f"   Error event: {event2}")
    print(f"   Severity: {event2.severity}")

    # Test to_db_params
    params = event1.to_db_params()
    print(f"   DB params: {len(params)} fields")

    print("   ✅ Event model works!\n")
    return event1, event2


def test_metric_model():
    """Test Metric model creation and methods."""
    print("📈 Testing Metric Model...")

    # Create metrics
    cpu_metric = Metric(
        host_id="test-host-123", metric_name="cpu_usage", metric_value=25.5, unit="%"
    )
    print(f"   CPU metric: {cpu_metric}")

    uptime_metric = Metric(
        host_id="test-host-123",
        metric_name="uptime",
        metric_value=86400,
        unit="seconds",
    )
    print(f"   Uptime metric: {uptime_metric}")

    memory_metric = Metric(
        host_id="test-host-123",
        metric_name="memory_usage",
        metric_value=512.0,
        unit="MB",
    )
    print(f"   Memory metric: {memory_metric}")

    # Test to_db_params
    params = cpu_metric.to_db_params()
    print(f"   DB params: {len(params)} fields")

    print("   ✅ Metric model works!\n")
    return cpu_metric, uptime_metric, memory_metric


def test_collection_run_model():
    """Test CollectionRun model creation and methods."""
    print("🔄 Testing CollectionRun Model...")

    # Create collection run
    run = CollectionRun(start_time="2025-10-17T10:00:00Z", status="running")
    print(f"   Collection run: {run}")
    print(f"   Status: {run.status}")
    print(f"   Start: {run.start_time}")

    # Simulate completion
    run.status = "success"
    run.end_time = "2025-10-17T10:00:05Z"
    run.hosts_collected = 5
    run.duration_seconds = 5.2
    print(f"   After completion: {run}")
    print(f"   Hosts collected: {run.hosts_collected}")
    print(f"   Duration: {run.duration_seconds}s")

    # Test to_db_params
    params = run.to_db_params()
    print(f"   DB params: {len(params)} fields")

    print("   ✅ CollectionRun model works!\n")
    return run


def test_serialization():
    """Test model serialization."""
    print("💾 Testing Serialization...")

    host = Host(id="test-123", hardware_id="hw-456", type="console", name="Test Device")

    # Convert to dict
    host_dict = host.to_dict()
    print(f"   Host as dict: {len(host_dict)} keys")

    # Convert to JSON
    host_json = json.dumps(host_dict, indent=2)
    print(f"   Host as JSON: {len(host_json)} chars")

    # Parse back
    parsed = json.loads(host_json)
    print(f"   Parsed back: {parsed['name']}")

    print("   ✅ Serialization works!\n")


def main():
    print("🚀 Testing Data Models...\n")
    print("=" * 60)
    print()

    # Test all models
    host = test_host_model()
    status = test_host_status_model()
    event1, event2 = test_event_model()
    cpu, uptime, memory = test_metric_model()
    run = test_collection_run_model()
    test_serialization()

    print("=" * 60)
    print()
    print("🎉 All model tests passed!")
    print()
    print("✅ Models are ready to use:")
    print("   • Host - Device information")
    print("   • HostStatus - Status tracking")
    print("   • Event - Event logging")
    print("   • Metric - Time-series metrics")
    print("   • CollectionRun - Collection tracking")
    print()
    print("Next step: Create repository classes for CRUD operations!")


if __name__ == "__main__":
    main()
