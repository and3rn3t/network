"""Test script for repository layer."""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from database import Database
from database.models import Event, Host, HostStatus, Metric
from database.repositories import (
    EventRepository,
    HostRepository,
    MetricRepository,
    StatusRepository,
)


def main():
    """Test all repository operations."""
    print("\n" + "=" * 60)
    print("TESTING REPOSITORY LAYER")
    print("=" * 60)

    # Use test database
    db_path = project_root / "data" / "test_repositories.db"
    db_path.unlink(missing_ok=True)  # Clean slate

    db = Database(db_path)
    db.initialize()

    print(f"\n✅ Test database initialized: {db_path}")

    # Initialize repositories
    host_repo = HostRepository(db)
    status_repo = StatusRepository(db)
    event_repo = EventRepository(db)
    metric_repo = MetricRepository(db)

    print("✅ Repositories initialized")

    # Test 1: Host Repository
    print("\n" + "-" * 60)
    print("TEST 1: Host Repository")
    print("-" * 60)

    # Create test host
    host = Host(
        id="test001",
        hardware_id="testdevice001",
        type="switch",
        name="Test Device",
        model="USW-24-POE",
        firmware_version="6.5.59",
        ip_address="192.168.1.100",
        mac_address="aa:bb:cc:dd:ee:ff",
        owner=False,
        is_blocked=False,
    )

    created_host = host_repo.create(host)
    host_id = created_host.id
    print(f"✅ Created host: {created_host}")

    # Retrieve host
    retrieved = host_repo.get_by_id(host_id)
    print(f"✅ Retrieved host: {retrieved.name}")

    # Search for host
    results = host_repo.search("Test")
    print(f"✅ Search found {len(results)} host(s)")

    # Get online hosts
    online = host_repo.get_online_hosts()
    print(f"✅ Found {len(online)} online host(s)")

    # Test 2: Status Repository
    print("\n" + "-" * 60)
    print("TEST 2: Status Repository")
    print("-" * 60)

    # Create status records
    statuses = []
    for i in range(5):
        is_online = i % 2 == 0
        status = HostStatus(
            host_id=host_id,
            status="online" if is_online else "offline",
            is_online=is_online,
            uptime_seconds=3600 * i if is_online else 0,
            cpu_usage=20.0 + i * 5,
            memory_usage=40.0 + i * 2,
            temperature=38.0 + i,
            recorded_at=datetime.now() - timedelta(hours=5 - i),
        )
        created_status = status_repo.create(status)
        statuses.append(created_status.id)

    print(f"✅ Created {len(statuses)} status records")

    # Get latest status
    latest = status_repo.get_latest_for_host(host_id)
    print(f"✅ Latest status: {'online' if latest.is_online else 'offline'}")

    # Get history
    history = status_repo.get_history_for_host(host_id, limit=10)
    print(f"✅ Retrieved {len(history)} history records")

    # Get uptime stats
    stats = status_repo.get_uptime_stats(host_id)
    print(f"✅ Uptime stats: {stats['uptime_percentage']:.1f}% uptime")

    # Test 3: Event Repository
    print("\n" + "-" * 60)
    print("TEST 3: Event Repository")
    print("-" * 60)

    # Create events
    events = []

    # Status change event
    event1 = Event.create_status_change(
        host_id=host_id, old_status="offline", new_status="online"
    )
    created_event1 = event_repo.create(event1)
    events.append(created_event1.id)

    # Error event
    event2 = Event.create_error(
        host_id=host_id, title="Test Error", description="This is a test error event"
    )
    created_event2 = event_repo.create(event2)
    events.append(created_event2.id)

    print(f"✅ Created {len(events)} events")

    # Get recent events
    recent = event_repo.get_recent(limit=10)
    print(f"✅ Retrieved {len(recent)} recent events")

    # Get errors
    errors = event_repo.get_errors()
    print(f"✅ Found {len(errors)} error events")

    # Get by type
    status_events = event_repo.get_by_type("status_change")
    print(f"✅ Found {len(status_events)} status change events")

    # Test 4: Metric Repository
    print("\n" + "-" * 60)
    print("TEST 4: Metric Repository")
    print("-" * 60)

    # Create metric batch
    metrics = []
    base_time = datetime.now() - timedelta(hours=1)

    for i in range(10):
        metric = Metric(
            host_id=host_id,
            metric_name="cpu_usage",
            metric_value=20.0 + i * 2,
            unit="percent",
        )
        metrics.append(metric)

    # Batch insert
    metrics_created = metric_repo.create_many(metrics)
    print(f"✅ Batch created {metrics_created} metrics")

    # Get latest metrics
    latest_metrics = metric_repo.get_latest_metrics(host_id)
    print(f"✅ Retrieved {len(latest_metrics)} latest metrics")

    # Get metric history
    cpu_history = metric_repo.get_metric_history(
        host_id=host_id, metric_name="cpu_usage", hours=2
    )
    print(f"✅ Retrieved {len(cpu_history)} CPU history records")

    # Get average
    avg_cpu = metric_repo.get_average(host_id=host_id, metric_name="cpu_usage", hours=1)
    if avg_cpu:
        print(f"✅ Average CPU: {avg_cpu:.1f}%")
    else:
        print("✅ No CPU data for averaging")

    # Test 5: Cross-Repository Operations
    print("\n" + "-" * 60)
    print("TEST 5: Cross-Repository Operations")
    print("-" * 60)

    # Simulate a status change - update host info
    host.name = "Updated Test Device"
    host_repo.update(host)

    new_status = HostStatus(
        host_id=host_id,
        status="offline",
        is_online=False,
        uptime_seconds=0,
        cpu_usage=0,
        memory_usage=0,
        temperature=None,
        recorded_at=datetime.now(),
    )
    status_repo.create(new_status)

    change_event = Event.create_status_change(
        host_id=host_id, old_status="online", new_status="offline"
    )
    event_repo.create(change_event)

    print("✅ Simulated status change across repositories")

    # Verify data consistency
    updated_host = host_repo.get_by_id(host_id)
    latest_status = status_repo.get_latest_for_host(host_id)
    all_events = event_repo.get_for_host(host_id)

    print(f"✅ Host name: {updated_host.name}")
    print(f"✅ Latest status online: {latest_status.is_online}")
    print(f"✅ Total events: {len(all_events)}")

    # Test 6: Data Cleanup
    print("\n" + "-" * 60)
    print("TEST 6: Data Cleanup")
    print("-" * 60)

    # Count before cleanup
    total_statuses = status_repo.count()
    total_events = event_repo.count()
    total_metrics = metric_repo.count()

    print(f"Before cleanup:")
    print(f"  - Statuses: {total_statuses}")
    print(f"  - Events: {total_events}")
    print(f"  - Metrics: {total_metrics}")

    # Delete old data (beyond retention period)
    deleted_statuses = status_repo.delete_old_records(days=0)
    deleted_events = event_repo.delete_old_events(days=0)
    deleted_metrics = metric_repo.delete_old_metrics(days=0)

    print(f"\nAfter cleanup:")
    print(f"  - Deleted {deleted_statuses} old status records")
    print(f"  - Deleted {deleted_events} old events")
    print(f"  - Deleted {deleted_metrics} old metrics")

    # Final stats
    print("\n" + "=" * 60)
    print("FINAL DATABASE STATS")
    print("=" * 60)

    stats = db.get_stats()
    print(f"Database: {stats['database_path']}")
    print(f"Size: {stats['database_size_bytes'] / 1024 / 1024:.2f} MB")
    print(f"Schema version: {stats['schema_version']}")
    print(f"Hosts: {stats['hosts_count']}")
    print(f"Statuses: {stats['host_status_count']}")
    print(f"Events: {stats['events_count']}")
    print(f"Metrics: {stats['metrics_count']}")

    print("\n✅ ALL TESTS PASSED!")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
