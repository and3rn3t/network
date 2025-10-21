#!/usr/bin/env python3
"""
Continuous Metrics Collection Service

Runs in the background and collects metrics every 5 minutes.
This provides real-time monitoring of your UniFi network devices.
"""

import signal
import sys
import time
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collect_real_metrics import RealMetricsCollector
from src.database.database import Database
from src.unifi_client import UniFiClient

# Import config directly
try:
    import config
except ImportError:
    print("❌ Error: config.py not found. Please create it from config.example.py")
    sys.exit(1)


class MetricsCollectionService:
    """Background service for continuous metrics collection."""

    def __init__(self, interval_minutes: int = 5):
        self.interval_minutes = interval_minutes
        self.running = False
        self.client = None
        self.db = None
        self.collector = None

    def setup(self):
        """Initialize connections."""
        print("🚀 Starting Metrics Collection Service")
        print("=" * 70)

        # Load configuration
        print("📋 Loading configuration...")
        api_key = config.API_KEY
        base_url = getattr(config, "BASE_URL", "https://api.ui.com/v1")

        # Initialize database
        print("💾 Connecting to database...")
        self.db = Database()
        print(f"   Database: {self.db.db_path}")

        # Initialize UniFi client
        print("🔗 Connecting to UniFi API...")
        self.client = UniFiClient(
            api_key=api_key,
            base_url=base_url,
        )
        print("   ✅ Connected successfully")

        # Create collector
        self.collector = RealMetricsCollector(self.client, self.db)

        print()
        print(f"⏱️  Collection interval: every {self.interval_minutes} minutes")
        print("🛑 Press Ctrl+C to stop")
        print("=" * 70)
        print()

    def run(self):
        """Run the collection service."""
        self.running = True
        collection_count = 0

        while self.running:
            try:
                collection_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                print(f"\n{'=' * 70}")
                print(f"📊 Collection #{collection_count} at {timestamp}")
                print(f"{'=' * 70}\n")

                # Collect metrics
                metrics_count = self.collector.collect_all_metrics()

                # Summary
                total_metrics = sum(metrics_count.values())
                print(
                    f"\n✅ Collected {total_metrics} metrics from {len(metrics_count)} device(s)"
                )

                if self.running:
                    # Calculate next collection time
                    next_collection = datetime.now().timestamp() + (
                        self.interval_minutes * 60
                    )
                    next_time = datetime.fromtimestamp(next_collection).strftime(
                        "%H:%M:%S"
                    )
                    print(f"⏰ Next collection at {next_time}")
                    print(f"   Sleeping for {self.interval_minutes} minutes...")

                    # Sleep in smaller intervals to allow quick shutdown
                    sleep_seconds = self.interval_minutes * 60
                    for _ in range(sleep_seconds):
                        if not self.running:
                            break
                        time.sleep(1)

            except KeyboardInterrupt:
                print("\n\n🛑 Received shutdown signal...")
                self.running = False
                break
            except Exception as e:
                print(f"\n❌ Error during collection: {e}")
                print("   Retrying in 1 minute...")
                time.sleep(60)

    def cleanup(self):
        """Cleanup resources."""
        print("\n🧹 Cleaning up...")

        if self.db:
            try:
                self.db.close()
                print("   ✅ Closed database connection")
            except Exception:
                pass

        print("\n👋 Metrics Collection Service stopped")
        print("=" * 70)


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print("\n\n🛑 Shutdown signal received")
    sys.exit(0)


def main():
    """Main entry point."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    service = MetricsCollectionService(interval_minutes=5)

    try:
        service.setup()
        service.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return 1
    finally:
        service.cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(main())
