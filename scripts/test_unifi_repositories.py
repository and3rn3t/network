"""
Test script for UniFi repositories.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.database import Database
from database.models_unifi import (
    UniFiClient,
    UniFiClientStatus,
    UniFiDevice,
    UniFiDeviceStatus,
    UniFiEvent,
)
from database.repositories.unifi_repository import (
    UniFiClientRepository,
    UniFiClientStatusRepository,
    UniFiCollectionRunRepository,
    UniFiDeviceRepository,
    UniFiDeviceStatusRepository,
    UniFiEventRepository,
    UniFiMetricsRepository,
)


def test_device_repository():
    """Test UniFiDeviceRepository."""
    print("Testing UniFiDeviceRepository...")

    db = Database("test_unifi.db")
    repo = UniFiDeviceRepository(db)

    # Create test device
    device = UniFiDevice(
        mac="aa:bb:cc:dd:ee:ff",
        device_id="dev123",
        name="Test-Switch",
        type="usw",
        model="US8P150",
        version="6.5.59",
        ip="192.168.1.10",
        site_name="default",
        state=1,
        adopted=True,
        uptime=86400,
        satisfaction=95,
    )

    # Test upsert
    created = repo.upsert(device)
    print(f"✅ Created device: {created.mac}")

    # Test get_by_mac
    retrieved = repo.get_by_mac(device.mac)
    assert retrieved is not None
    assert retrieved.name == "Test-Switch"
    print(f"✅ Retrieved device: {retrieved.name}")

    # Test get_online_devices
    online = repo.get_online_devices()
    assert len(online) > 0
    print(f"✅ Found {len(online)} online device(s)")

    # Test update_state
    success = repo.update_state(device.mac, 0)
    assert success
    print(f"✅ Updated device state to offline")

    print()


def test_device_status_repository():
    """Test UniFiDeviceStatusRepository."""
    print("Testing UniFiDeviceStatusRepository...")

    db = Database("test_unifi.db")
    repo = UniFiDeviceStatusRepository(db)

    # Create test status
    status = UniFiDeviceStatus(
        device_mac="aa:bb:cc:dd:ee:ff",
        state=1,
        uptime=86400,
        cpu_usage=25.5,
        memory_usage=40.2,
        temperature=45.0,
        num_clients=5,
        satisfaction=95,
        bytes_rx=500000,
        bytes_tx=300000,
    )

    # Test create
    created = repo.create(status)
    print(f"✅ Created device status with ID: {created.id}")

    # Test get_latest_by_device
    latest = repo.get_latest_by_device("aa:bb:cc:dd:ee:ff")
    assert latest is not None
    assert latest.cpu_usage == 25.5
    print(f"✅ Retrieved latest status: CPU {latest.cpu_usage}%")

    # Test get_history
    history = repo.get_history("aa:bb:cc:dd:ee:ff", limit=10)
    assert len(history) > 0
    print(f"✅ Retrieved {len(history)} status record(s)")

    print()


def test_client_repository():
    """Test UniFiClientRepository."""
    print("Testing UniFiClientRepository...")

    db = Database("test_unifi.db")
    repo = UniFiClientRepository(db)

    # Create test client (wireless)
    client = UniFiClient(
        mac="11:22:33:44:55:66",
        client_id="client123",
        hostname="test-laptop",
        name="Test Laptop",
        ip="192.168.1.100",
        site_name="default",
        is_wired=False,
        essid="TestWiFi",
        channel=36,
        ap_mac="aa:bb:cc:dd:ee:ff",
        ap_name="AP-Office",
    )

    # Test upsert
    created = repo.upsert(client)
    print(f"✅ Created client: {created.hostname}")

    # Test get_by_mac
    retrieved = repo.get_by_mac(client.mac)
    assert retrieved is not None
    assert retrieved.hostname == "test-laptop"
    print(f"✅ Retrieved client: {retrieved.hostname}")

    # Test get_by_connection_type
    wireless = repo.get_by_connection_type(is_wired=False)
    assert len(wireless) > 0
    print(f"✅ Found {len(wireless)} wireless client(s)")

    # Test get_by_ap
    ap_clients = repo.get_by_ap("aa:bb:cc:dd:ee:ff")
    assert len(ap_clients) > 0
    print(f"✅ Found {len(ap_clients)} client(s) on AP")

    print()


def test_client_status_repository():
    """Test UniFiClientStatusRepository."""
    print("Testing UniFiClientStatusRepository...")

    db = Database("test_unifi.db")
    repo = UniFiClientStatusRepository(db)

    # Create test status
    status = UniFiClientStatus(
        client_mac="11:22:33:44:55:66",
        ip="192.168.1.100",
        is_wired=False,
        signal=-55,
        noise=-95,
        rssi=40,
        tx_bytes=100000,
        rx_bytes=500000,
        tx_rate=866,
        rx_rate=433,
        satisfaction=92,
    )

    # Test create
    created = repo.create(status)
    print(f"✅ Created client status with ID: {created.id}")

    # Test get_latest_by_client
    latest = repo.get_latest_by_client("11:22:33:44:55:66")
    assert latest is not None
    assert latest.signal == -55
    print(f"✅ Retrieved latest status: Signal {latest.signal} dBm")

    # Test get_signal_stats
    stats = repo.get_signal_stats("11:22:33:44:55:66", hours=24)
    if stats:
        print(f"✅ Signal stats: Avg {stats['avg_signal_dbm']:.1f} dBm")
    else:
        print(f"✅ No signal stats yet (need more data)")

    print()


def test_event_repository():
    """Test UniFiEventRepository."""
    print("Testing UniFiEventRepository...")

    db = Database("test_unifi.db")
    repo = UniFiEventRepository(db)

    # Create test event
    event = UniFiEvent(
        event_type="status_change",
        severity="warning",
        title="Device went offline",
        description="Test-Switch lost connection",
        device_mac="aa:bb:cc:dd:ee:ff",
        previous_value="1",
        new_value="0",
        metadata=json.dumps({"location": "Office"}),
    )

    # Test create
    created = repo.create(event)
    assert created.id is not None
    print(f"✅ Created event with ID: {created.id}")

    # Test get_recent
    recent = repo.get_recent(limit=10)
    assert len(recent) > 0
    print(f"✅ Retrieved {len(recent)} recent event(s)")

    # Test get_by_device
    device_events = repo.get_by_device("aa:bb:cc:dd:ee:ff", limit=10)
    assert len(device_events) > 0
    print(f"✅ Retrieved {len(device_events)} device event(s)")

    # Test severity filter
    warnings = repo.get_recent(limit=10, severity="warning")
    print(f"✅ Retrieved {len(warnings)} warning(s)")

    print()


def test_metrics_repository():
    """Test UniFiMetricsRepository."""
    print("Testing UniFiMetricsRepository...")

    db = Database("test_unifi.db")
    repo = UniFiMetricsRepository(db)

    # Test create_device_metric
    metric_id = repo.create_device_metric(
        device_mac="aa:bb:cc:dd:ee:ff",
        metric_name="cpu_usage",
        metric_value=25.5,
        unit="percent",
    )
    print(f"✅ Created device metric with ID: {metric_id}")

    # Test create_client_metric
    metric_id = repo.create_client_metric(
        client_mac="11:22:33:44:55:66",
        metric_name="signal_strength",
        metric_value=-55.0,
        unit="dbm",
    )
    print(f"✅ Created client metric with ID: {metric_id}")

    # Test get_device_metrics
    metrics = repo.get_device_metrics("aa:bb:cc:dd:ee:ff", limit=10)
    assert len(metrics) > 0
    print(f"✅ Retrieved {len(metrics)} device metric(s)")

    # Test get_client_metrics
    metrics = repo.get_client_metrics("11:22:33:44:55:66", limit=10)
    assert len(metrics) > 0
    print(f"✅ Retrieved {len(metrics)} client metric(s)")

    print()


def test_collection_run_repository():
    """Test UniFiCollectionRunRepository."""
    print("Testing UniFiCollectionRunRepository...")

    db = Database("test_unifi.db")
    repo = UniFiCollectionRunRepository(db)

    # Test create_run
    run_id = repo.create_run(controller_host="192.168.1.1")
    print(f"✅ Created collection run with ID: {run_id}")

    # Test complete_run
    success = repo.complete_run(
        run_id=run_id,
        devices_collected=5,
        clients_collected=10,
        errors_encountered=0,
    )
    assert success
    print(f"✅ Completed collection run")

    # Test get_recent_runs
    runs = repo.get_recent_runs(limit=5)
    assert len(runs) > 0
    print(f"✅ Retrieved {len(runs)} recent run(s)")

    # Test get_run_stats
    stats = repo.get_run_stats(hours=24)
    if stats:
        print(
            f"✅ Run stats: {stats['total_runs']} total, "
            f"{stats['successful_runs']} successful"
        )
    else:
        print(f"✅ No run stats yet")

    print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing UniFi Repositories")
    print("=" * 60)
    print()

    try:
        test_device_repository()
        test_device_status_repository()
        test_client_repository()
        test_client_status_repository()
        test_event_repository()
        test_metrics_repository()
        test_collection_run_repository()

        print("=" * 60)
        print("✅ All repository tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
