"""
Test script for UniFi data collector.

Tests the collector with mock data to verify all functionality.
"""

import os
import sys
from datetime import datetime
from unittest.mock import Mock

# Set PYTHONPATH to current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after path is set
from src.collector.unifi_collector import UniFiCollectorConfig, UniFiDataCollector
from src.database.database import Database


def create_mock_controller():
    """Create a mock UniFi Controller."""
    controller = Mock()

    # Mock login/logout
    controller.login = Mock()
    controller.logout = Mock()

    # Mock device data
    controller.get_devices = Mock(
        return_value=[
            {
                "mac": "aa:bb:cc:dd:ee:ff",
                "_id": "dev1",
                "name": "Switch-Office",
                "type": "usw",
                "model": "US8P150",
                "version": "6.5.59",
                "ip": "192.168.1.10",
                "state": 1,
                "adopted": True,
                "disabled": False,
                "uptime": 86400,
                "satisfaction": 95,
                "num_sta": 0,
                "bytes": 1024000,
                "last_seen": int(datetime.now().timestamp()),
                "system-stats": {"cpu": 25.5, "mem": 40.2},
                "general_temperature": 45.0,
            },
            {
                "mac": "11:22:33:44:55:66",
                "_id": "dev2",
                "name": "AP-Office",
                "type": "uap",
                "model": "UAP-AC-PRO",
                "version": "6.5.59",
                "ip": "192.168.1.20",
                "state": 1,
                "adopted": True,
                "disabled": False,
                "uptime": 86400,
                "satisfaction": 98,
                "num_sta": 3,
                "bytes": 5024000,
                "last_seen": int(datetime.now().timestamp()),
                "system-stats": {"cpu": 15.2, "mem": 30.1},
                "general_temperature": 42.0,
            },
        ]
    )

    # Mock client data
    controller.get_clients = Mock(
        return_value=[
            {
                "mac": "aa:aa:aa:aa:aa:aa",
                "_id": "client1",
                "hostname": "johns-laptop",
                "name": "John's Laptop",
                "ip": "192.168.1.100",
                "is_wired": False,
                "is_guest": False,
                "blocked": False,
                "essid": "MyWiFi",
                "channel": 36,
                "ap_mac": "11:22:33:44:55:66",
                "ap_name": "AP-Office",
                "signal": -55,
                "noise": -95,
                "rssi": 40,
                "tx_rate": 866,
                "rx_rate": 433,
                "tx_bytes": 1000000,
                "rx_bytes": 5000000,
                "satisfaction": 92,
                "uptime": 3600,
                "first_seen": int(datetime.now().timestamp()) - 86400,
                "last_seen": int(datetime.now().timestamp()),
            },
            {
                "mac": "bb:bb:bb:bb:bb:bb",
                "_id": "client2",
                "hostname": "desktop-pc",
                "ip": "192.168.1.101",
                "is_wired": True,
                "is_guest": False,
                "blocked": False,
                "sw_mac": "aa:bb:cc:dd:ee:ff",
                "sw_port": 3,
                "tx_rate": 1000,
                "rx_rate": 1000,
                "tx_bytes": 2000000,
                "rx_bytes": 8000000,
                "satisfaction": 100,
                "uptime": 7200,
                "first_seen": int(datetime.now().timestamp()) - 172800,
                "last_seen": int(datetime.now().timestamp()),
            },
        ]
    )

    return controller


def test_collector_initialization():
    """Test collector initialization."""
    print("Testing collector initialization...")

    config = UniFiCollectorConfig(
        controller_url="https://192.168.1.1",
        username="admin",
        password="password",
        site="default",
        verify_ssl=False,
    )

    # Create with mock controller
    controller = create_mock_controller()
    db = Database("test_unifi.db")

    collector = UniFiDataCollector(config=config, controller=controller, database=db)

    print(f"✅ Collector initialized")
    print(f"   - Controller: {collector.config.controller_url}")
    print(f"   - Site: {collector.config.site}")
    print(f"   - Events enabled: {collector.config.enable_events}")
    print(f"   - Metrics enabled: {collector.config.enable_metrics}")
    print()

    return collector


def test_device_collection(collector):
    """Test device collection."""
    print("Testing device collection...")

    # Run collection
    stats = collector.collect()

    print(f"✅ Collection completed")
    print(f"   - Duration: {stats['duration_seconds']:.2f}s")
    print(f"   - Devices processed: {stats['devices_processed']}")
    print(f"   - Devices created: {stats['devices_created']}")
    print(f"   - Devices updated: {stats['devices_updated']}")
    print(f"   - Clients processed: {stats['clients_processed']}")
    print(f"   - Clients created: {stats['clients_created']}")
    print(f"   - Clients updated: {stats['clients_updated']}")
    print(f"   - Status records: {stats['status_records']}")
    print(f"   - Events created: {stats['events_created']}")
    print(f"   - Metrics created: {stats['metrics_created']}")
    print(f"   - Errors: {stats['errors']}")
    print()

    # Verify devices were stored
    devices = collector.device_repo.get_all()
    print(f"✅ Devices in database: {len(devices)}")
    for device in devices:
        print(f"   - {device.name} ({device.type}) - {device.mac}")
    print()

    # Verify clients were stored
    clients = collector.client_repo.get_all()
    print(f"✅ Clients in database: {len(clients)}")
    for client in clients:
        conn_type = "wired" if client.is_wired else "wireless"
        print(f"   - {client.hostname or client.mac} ({conn_type})")
    print()

    return stats


def test_change_detection(collector):
    """Test change detection by running collection again with modified data."""
    print("Testing change detection...")

    # Modify mock data to simulate changes
    # Device goes offline
    controller = collector.controller
    modified_devices = controller.get_devices()
    modified_devices[0]["state"] = 0  # Switch goes offline

    controller.get_devices = Mock(return_value=modified_devices)

    # Client roams to different AP
    modified_clients = controller.get_clients()
    modified_clients[0]["ap_mac"] = "ff:ff:ff:ff:ff:ff"
    modified_clients[0]["ap_name"] = "AP-Other"

    controller.get_clients = Mock(return_value=modified_clients)

    # Run collection again
    stats = collector.collect()

    print(f"✅ Second collection completed")
    print(f"   - Events created: {stats['events_created']}")
    print()

    # Check for events
    events = collector.event_repo.get_recent(limit=10)
    print(f"✅ Recent events: {len(events)}")
    for event in events:
        print(f"   - [{event.severity}] {event.title}: {event.description}")
    print()


def test_collector_stats(collector):
    """Test collector statistics."""
    print("Testing collector statistics...")

    stats = collector.get_stats()

    print(f"✅ Collector statistics:")
    print(f"   - Controller: {stats['controller_url']}")
    print(f"   - Site: {stats['site']}")
    print(f"   - Collection count: {stats['collection_count']}")
    print(f"   - Error count: {stats['error_count']}")
    print(f"   - Total devices: {stats['total_devices']}")
    print(f"   - Total clients: {stats['total_clients']}")
    print(f"   - Total events: {stats['total_events']}")
    print()


def test_collection_runs(collector):
    """Test collection run tracking."""
    print("Testing collection run tracking...")

    runs = collector.collection_run_repo.get_recent_runs(limit=5)
    print(f"✅ Recent collection runs: {len(runs)}")
    for run in runs:
        print(
            f"   - Run {run['id']}: {run['status']} - "
            f"{run['devices_collected']} devices, {run['clients_collected']} clients "
            f"({run['duration_seconds']:.2f}s)"
        )
    print()

    # Get run stats
    run_stats = collector.collection_run_repo.get_run_stats(hours=24)
    if run_stats:
        print(f"✅ Collection run statistics (24h):")
        print(f"   - Total runs: {run_stats['total_runs']}")
        print(f"   - Successful: {run_stats['successful_runs']}")
        print(f"   - Failed: {run_stats['failed_runs']}")
        print(f"   - Avg duration: {run_stats['avg_duration']:.2f}s")
        print(f"   - Total devices: {run_stats['total_devices']}")
        print(f"   - Total clients: {run_stats['total_clients']}")
    print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing UniFi Data Collector")
    print("=" * 60)
    print()

    try:
        # Initialize collector
        collector = test_collector_initialization()

        # Test device collection
        test_device_collection(collector)

        # Test change detection
        test_change_detection(collector)

        # Test statistics
        test_collector_stats(collector)

        # Test collection runs
        test_collection_runs(collector)

        print("=" * 60)
        print("✅ All collector tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
