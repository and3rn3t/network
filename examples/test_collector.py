"""Test script for data collector."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.collector import CollectorConfig, DataCollector


def main():
    """Test data collector with API."""
    print("\n" + "=" * 60)
    print("TESTING DATA COLLECTOR")
    print("=" * 60)

    # Load API key
    try:
        import config

        api_key = config.API_KEY
    except (ImportError, AttributeError):
        print("\n❌ Error: config.py not found or API_KEY not set")
        print("Please create config.py with your API_KEY")
        return

    # Configure collector
    collector_config = CollectorConfig(
        api_key=api_key,
        api_base_url="https://api.ui.com/v1",
        collection_interval=300,  # 5 minutes
        status_retention_days=90,
        event_retention_days=365,
        metric_retention_days=30,
        enable_metrics=True,
        enable_events=True,
        log_level="INFO",
        db_path="data/unifi_network.db",
    )

    print("\n✅ Configuration loaded")
    print(f"   - Collection interval: {collector_config.collection_interval}s")
    print(f"   - Status retention: {collector_config.status_retention_days} days")
    print(f"   - Event retention: {collector_config.event_retention_days} days")
    print(f"   - Metric retention: {collector_config.metric_retention_days} days")
    print(f"   - Database: {collector_config.db_path}")

    # Create collector
    print("\n" + "-" * 60)
    print("Initializing collector...")
    print("-" * 60)

    collector = DataCollector(collector_config)

    print("✅ Collector initialized")

    # Run collection
    print("\n" + "-" * 60)
    print("Running collection cycle...")
    print("-" * 60)

    try:
        stats = collector.collect()

        print("\n✅ Collection completed!")
        print("\n📊 Collection Statistics:")
        print(f"   - Duration: {stats['duration_seconds']:.2f}s")
        print(f"   - Hosts processed: {stats['hosts_processed']}")
        print(f"   - Hosts created: {stats['hosts_created']}")
        print(f"   - Hosts updated: {stats['hosts_updated']}")
        print(f"   - Status records: {stats['status_records']}")
        print(f"   - Events created: {stats['events_created']}")
        print(f"   - Metrics created: {stats['metrics_created']}")
        print(f"   - Errors: {stats['errors']}")

    except Exception as e:
        print(f"\n❌ Collection failed: {e}")
        import traceback

        traceback.print_exc()
        return

    # Get collector stats
    print("\n" + "-" * 60)
    print("Collector Statistics")
    print("-" * 60)

    collector_stats = collector.get_stats()
    print(f"   - Last collection: {collector_stats['last_collection']}")
    print(f"   - Total collections: {collector_stats['collection_count']}")
    print(f"   - Total errors: {collector_stats['error_count']}")
    print(f"   - Total hosts: {collector_stats['total_hosts']}")
    print(f"   - Total statuses: {collector_stats['total_statuses']}")
    print(f"   - Total events: {collector_stats['total_events']}")
    print(f"   - Total metrics: {collector_stats['total_metrics']}")

    # Close collector
    collector.close()

    print("\n" + "=" * 60)
    print("✅ DATA COLLECTOR TEST COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
