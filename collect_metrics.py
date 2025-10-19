"""
Metrics Collector for UniFi Devices

This script collects real-time performance metrics (CPU, memory, network, uptime)
from UniFi devices and stores them in the database for historical analysis.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List

from config import API_KEY, BASE_URL
from src.database.database import Database
from src.unifi_client import UniFiClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def extract_metrics(
    host_data: Dict[str, Any], status_data: Dict[str, Any]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract metrics from host and status data.

    Args:
        host_data: Host information from get_host()
        status_data: Status information from get_host_status()

    Returns:
        Dictionary of metrics grouped by type
    """
    metrics = {"cpu": [], "memory": [], "network": [], "uptime": [], "temperature": []}

    # Extract from reportedState
    reported = host_data.get("reportedState", {})
    hardware = reported.get("hardware", {})
    system_stats = reported.get("systemStats", {})

    # CPU metrics
    cpu_usage = system_stats.get("cpu", 0)
    if cpu_usage:
        metrics["cpu"].append(
            {"name": "cpu_usage", "value": float(cpu_usage), "unit": "%"}
        )

    # Memory metrics
    mem_usage = system_stats.get("mem", 0)
    if mem_usage:
        metrics["memory"].append(
            {"name": "memory_usage", "value": float(mem_usage), "unit": "%"}
        )

    mem_total = system_stats.get("memTotal")
    mem_used = system_stats.get("memUsed")
    if mem_total and mem_used:
        metrics["memory"].extend(
            [
                {"name": "memory_total", "value": float(mem_total), "unit": "bytes"},
                {"name": "memory_used", "value": float(mem_used), "unit": "bytes"},
            ]
        )

    # Network metrics
    interfaces = reported.get("interfaces", [])
    total_rx_bytes = 0
    total_tx_bytes = 0
    total_rx_packets = 0
    total_tx_packets = 0

    for interface in interfaces:
        total_rx_bytes += interface.get("rxBytes", 0)
        total_tx_bytes += interface.get("txBytes", 0)
        total_rx_packets += interface.get("rxPackets", 0)
        total_tx_packets += interface.get("txPackets", 0)

    if total_rx_bytes or total_tx_bytes:
        metrics["network"].extend(
            [
                {
                    "name": "network_rx_bytes",
                    "value": float(total_rx_bytes),
                    "unit": "bytes",
                },
                {
                    "name": "network_tx_bytes",
                    "value": float(total_tx_bytes),
                    "unit": "bytes",
                },
                {
                    "name": "network_rx_packets",
                    "value": float(total_rx_packets),
                    "unit": "packets",
                },
                {
                    "name": "network_tx_packets",
                    "value": float(total_tx_packets),
                    "unit": "packets",
                },
            ]
        )

    # Uptime
    uptime = reported.get("uptime", 0)
    if uptime:
        metrics["uptime"].append(
            {"name": "uptime", "value": float(uptime), "unit": "seconds"}
        )

    # Temperature
    temps = hardware.get("temperatures", [])
    if temps:
        for i, temp in enumerate(temps):
            temp_value = temp.get("value")
            if temp_value:
                metrics["temperature"].append(
                    {
                        "name": f'temperature_{temp.get("name", i)}',
                        "value": float(temp_value),
                        "unit": "celsius",
                    }
                )

    return metrics


def store_metrics(
    db: Database, host_id: str, metrics: Dict[str, List[Dict[str, Any]]]
) -> int:
    """
    Store metrics in the database.

    Args:
        db: Database instance
        host_id: Host identifier
        metrics: Dictionary of metrics

    Returns:
        Number of metrics stored
    """
    count = 0
    timestamp = datetime.utcnow().isoformat() + "Z"

    with db.transaction():
        for category, metric_list in metrics.items():
            for metric in metric_list:
                db.execute(
                    """
                    INSERT INTO metrics (host_id, metric_name, metric_value, unit, recorded_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        host_id,
                        metric["name"],
                        metric["value"],
                        metric["unit"],
                        timestamp,
                    ),
                )
                count += 1

    return count


def collect_device_metrics(
    client: UniFiClient, db: Database, host_id: str, hardware_id: str
) -> bool:
    """
    Collect metrics for a single device.

    Args:
        client: UniFi API client
        db: Database instance
        host_id: Host ID in database
        hardware_id: Hardware ID from UniFi API

    Returns:
        True if successful
    """
    try:
        # Get host details
        logger.info(f"  📊 Fetching data for {host_id}...")
        host_data = client.get_host(hardware_id)

        # Get host status
        status_data = client.get_host_status(hardware_id)

        # Extract metrics
        metrics = extract_metrics(host_data, status_data)

        # Count total metrics
        total_metrics = sum(len(m) for m in metrics.values())

        if total_metrics == 0:
            logger.warning(f"  ⚠️  No metrics found for {host_id}")
            return False

        # Store in database
        stored = store_metrics(db, host_id, metrics)

        # Log summary
        summary = []
        for category, metric_list in metrics.items():
            if metric_list:
                summary.append(f"{category}({len(metric_list)})")

        logger.info(f"  ✅ Stored {stored} metrics: {', '.join(summary)}")
        return True

    except Exception as e:
        logger.error(f"  ❌ Error collecting metrics for {host_id}: {e}")
        return False


def main():
    """Main metrics collection routine."""
    logger.info("🚀 UniFi Metrics Collector Starting...\n")

    # Initialize
    logger.info("📡 Connecting to UniFi API...")
    client = UniFiClient(api_key=API_KEY, base_url=BASE_URL)

    logger.info("💾 Connecting to database...")
    db = Database("network.db")

    # Get all hosts from database
    logger.info("\n📋 Fetching devices from database...")
    cursor = db.execute(
        "SELECT id, hardware_id, name, model FROM hosts WHERE hardware_id IS NOT NULL"
    )
    hosts = cursor.fetchall()

    if not hosts:
        logger.warning("⚠️  No devices found in database!")
        logger.info("💡 Run 'python quick_collect.py' first to populate devices.")
        return 1

    logger.info(f"Found {len(hosts)} device(s)\n")

    # Collect metrics for each host
    success_count = 0
    for host in hosts:
        host_id = host[0]
        hardware_id = host[1]
        name = host[2] or "Unknown"
        model = host[3] or "N/A"

        logger.info(f"🔍 {name} ({model})")

        if collect_device_metrics(client, db, host_id, hardware_id):
            success_count += 1

        logger.info("")  # Blank line

    # Summary
    logger.info("=" * 60)
    logger.info(f"✅ Collection complete!")
    logger.info(
        f"   Successfully collected metrics from {success_count}/{len(hosts)} device(s)"
    )
    logger.info("=" * 60)

    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
