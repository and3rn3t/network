"""
Generate Sample Metrics for UniFi Devices

This script generates realistic sample metrics data for testing the Historical Analysis Dashboard.
The UniFi Site Manager API doesn't provide detailed CPU/memory/network statistics,
so this generates sample data to demonstrate the dashboard functionality.

For production use, you would need to integrate with the local UniFi Controller API
or use SNMP/other monitoring tools.
"""

import logging
import random
import sys
from datetime import datetime, timedelta
from typing import List, Tuple

from src.database.database import Database

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def generate_realistic_metrics(hours: int = 24) -> List[Tuple[str, float]]:
    """
    Generate realistic time-series metrics.

    Args:
        hours: Number of hours of historical data to generate

    Returns:
        List of (timestamp, value) tuples
    """
    metrics = []
    now = datetime.utcnow()

    # Generate data points every 5 minutes
    intervals = hours * 12  # 12 intervals per hour (every 5 minutes)

    for i in range(intervals):
        timestamp = now - timedelta(minutes=5 * (intervals - i))
        metrics.append((timestamp.isoformat() + "Z", i))

    return metrics


def generate_cpu_metrics(hours: int) -> List[Tuple[str, float]]:
    """Generate realistic CPU usage metrics (0-100%)."""
    metrics = []
    now = datetime.utcnow()
    intervals = hours * 12

    # Base pattern with daily cycle
    for i in range(intervals):
        timestamp = now - timedelta(minutes=5 * (intervals - i))
        hour_of_day = timestamp.hour

        # Higher usage during business hours (9-17)
        if 9 <= hour_of_day <= 17:
            base_usage = random.uniform(40, 65)
        else:
            base_usage = random.uniform(15, 35)

        # Add some variation and occasional spikes
        variation = random.uniform(-5, 10)
        if random.random() < 0.05:  # 5% chance of spike
            variation += random.uniform(10, 25)

        usage = max(5, min(95, base_usage + variation))
        metrics.append((timestamp.isoformat() + "Z", round(usage, 2)))

    return metrics


def generate_memory_metrics(hours: int) -> List[Tuple[str, float]]:
    """Generate realistic memory usage metrics (0-100%)."""
    metrics = []
    now = datetime.utcnow()
    intervals = hours * 12

    # Memory tends to be more stable than CPU
    base_memory = random.uniform(45, 60)

    for i in range(intervals):
        timestamp = now - timedelta(minutes=5 * (intervals - i))

        # Slow drift over time
        drift = (i / intervals) * random.uniform(-5, 5)
        variation = random.uniform(-3, 3)

        usage = max(30, min(85, base_memory + drift + variation))
        metrics.append((timestamp.isoformat() + "Z", round(usage, 2)))

    return metrics


def generate_network_metrics(hours: int, metric_type: str) -> List[Tuple[str, float]]:
    """
    Generate realistic network throughput metrics (Mbps).

    Args:
        hours: Hours of data
        metric_type: 'rx' or 'tx'
    """
    metrics = []
    now = datetime.utcnow()
    intervals = hours * 12

    for i in range(intervals):
        timestamp = now - timedelta(minutes=5 * (intervals - i))
        hour_of_day = timestamp.hour

        # Network traffic pattern
        if 9 <= hour_of_day <= 17:
            # Business hours - higher traffic
            base_throughput = random.uniform(100, 300)
        elif 18 <= hour_of_day <= 23:
            # Evening - moderate traffic
            base_throughput = random.uniform(50, 150)
        else:
            # Night - low traffic
            base_throughput = random.uniform(5, 40)

        # RX typically higher than TX for most networks
        if metric_type == "rx":
            base_throughput *= random.uniform(1.2, 1.8)

        # Add variation and occasional bursts
        variation = random.uniform(-20, 30)
        if random.random() < 0.08:  # 8% chance of burst
            variation += random.uniform(50, 150)

        throughput = max(0, base_throughput + variation)
        metrics.append((timestamp.isoformat() + "Z", round(throughput, 2)))

    return metrics


def store_metrics_batch(
    db: Database,
    host_id: str,
    metric_name: str,
    values: List[Tuple[str, float]],
    unit: str,
) -> int:
    """
    Store a batch of metrics in the database.

    Args:
        db: Database instance
        host_id: Host identifier
        metric_name: Name of the metric
        values: List of (timestamp, value) tuples
        unit: Unit of measurement

    Returns:
        Number of metrics stored
    """
    count = 0
    with db.transaction():
        for timestamp, value in values:
            db.execute(
                """
                INSERT INTO metrics (host_id, metric_name, metric_value, unit, recorded_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (host_id, metric_name, value, unit, timestamp),
            )
            count += 1
    return count


def main():
    """Generate sample metrics for all devices."""
    logger.info("🎲 Sample Metrics Generator Starting...\n")

    # Configuration
    hours_of_data = 24  # Generate 24 hours of historical data

    logger.info(f"📊 Generating {hours_of_data} hours of sample metrics data")
    logger.info("   (Data points every 5 minutes)\n")

    # Connect to database
    logger.info("💾 Connecting to database...")
    db = Database("network.db")

    # Get all hosts
    cursor = db.execute("SELECT id, name, model FROM hosts")
    hosts = cursor.fetchall()

    if not hosts:
        logger.warning("⚠️  No devices found in database!")
        logger.info("💡 Run 'python quick_collect.py' first to populate devices.")
        return 1

    logger.info(f"Found {len(hosts)} device(s)\n")

    # Generate metrics for each host
    total_metrics = 0
    for host in hosts:
        host_id = host[0]
        name = host[1] or "Unknown"
        model = host[2] or "N/A"

        logger.info(f"🔧 {name} ({model})")

        # Generate different metric types
        logger.info("   📈 Generating CPU metrics...")
        cpu_data = generate_cpu_metrics(hours_of_data)
        stored = store_metrics_batch(db, host_id, "cpu_usage", cpu_data, "%")
        total_metrics += stored
        logger.info(f"      ✅ Stored {stored} data points")

        logger.info("   💾 Generating memory metrics...")
        mem_data = generate_memory_metrics(hours_of_data)
        stored = store_metrics_batch(db, host_id, "memory_usage", mem_data, "%")
        total_metrics += stored
        logger.info(f"      ✅ Stored {stored} data points")

        logger.info("   📡 Generating network RX metrics...")
        rx_data = generate_network_metrics(hours_of_data, "rx")
        stored = store_metrics_batch(db, host_id, "network_rx_mbps", rx_data, "Mbps")
        total_metrics += stored
        logger.info(f"      ✅ Stored {stored} data points")

        logger.info("   📡 Generating network TX metrics...")
        tx_data = generate_network_metrics(hours_of_data, "tx")
        stored = store_metrics_batch(db, host_id, "network_tx_mbps", tx_data, "Mbps")
        total_metrics += stored
        logger.info(f"      ✅ Stored {stored} data points")

        logger.info("")  # Blank line

    # Summary
    logger.info("=" * 70)
    logger.info("✅ Sample data generation complete!")
    logger.info(f"   Total metrics generated: {total_metrics:,}")
    logger.info(f"   Time range: Last {hours_of_data} hours")
    logger.info("=" * 70)
    logger.info("\n💡 Next steps:")
    logger.info("   1. Refresh your browser at http://localhost:3000")
    logger.info("   2. Navigate to the Historical Analysis page")
    logger.info("   3. Select your device and time range")
    logger.info("   4. View the performance charts!")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
