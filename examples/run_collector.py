"""Run data collector as a daemon."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.collector import CollectorConfig, run_collector


def main():
    """Run collector daemon."""
    print("\n" + "=" * 60)
    print("UNIFI NETWORK DATA COLLECTOR")
    print("=" * 60)

    # Load API key
    try:
        import config

        api_key = config.API_KEY
    except (ImportError, AttributeError):
        print("\n❌ Error: config.py not found or API_KEY not set")
        print("Please create config.py with your API_KEY")
        sys.exit(1)

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
    print(f"   - Database: {collector_config.db_path}")
    print(
        f"   - Metrics: {'Enabled' if collector_config.enable_metrics else 'Disabled'}"
    )
    print(f"   - Events: {'Enabled' if collector_config.enable_events else 'Disabled'}")

    print("\n🚀 Starting collector daemon...")
    print("   Press Ctrl+C to stop")
    print("-" * 60)

    # Run collector in daemon mode
    try:
        scheduler = run_collector(config=collector_config, daemon=True, immediate=True)
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
