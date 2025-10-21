"""
UniFi Network Analytics Demo

Demonstrates the analytics capabilities for UniFi network data.
"""

import sys
from datetime import datetime

from src.analytics import UniFiAnalyticsEngine
from src.database import Database


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_device_health(health):
    """Print device health information"""
    print(f"Device: {health.device_name} ({health.device_model})")
    print(f"  MAC: {health.device_mac}")
    print(f"  Overall Health: {health.health_score:.1f}/100 [{health.status.upper()}]")
    print(f"  CPU Score: {health.cpu_score:.1f}")
    print(f"  Memory Score: {health.memory_score:.1f}")
    print(f"  Uptime Score: {health.uptime_score:.1f}")
    print(f"  Client Load Score: {health.client_score:.1f}")


def print_client_experience(exp):
    """Print client experience information"""
    hostname = exp.client_hostname or "Unknown"
    print(f"Client: {hostname}")
    print(f"  MAC: {exp.client_mac}")
    print(f"  Experience Score: {exp.experience_score:.1f}/100")
    print(f"  Signal: {exp.signal_strength:.1f} dBm [{exp.signal_quality.upper()}]")
    if exp.avg_latency:
        print(f"  Avg Latency: {exp.avg_latency:.1f} ms")
    print(f"  Connection Stability: {exp.connection_stability:.1%}")
    print(f"  Bandwidth Usage: {exp.bandwidth_utilization:.1f}%")


def print_topology(topology):
    """Print network topology"""
    print(f"Total Devices: {topology.total_devices}")
    print(f"Total Clients: {topology.total_clients}")
    print(f"\nDevices by Type:")
    for device_type, count in topology.devices_by_type.items():
        print(f"  {device_type}: {count}")

    if topology.busiest_device:
        client_count = topology.clients_per_device.get(topology.busiest_device, 0)
        print(f"\nBusiest Device: {topology.busiest_device} ({client_count} clients)")

    if topology.underutilized_devices:
        print(f"\nUnderutilized Devices ({len(topology.underutilized_devices)}):")
        for mac in topology.underutilized_devices[:5]:
            client_count = topology.clients_per_device.get(mac, 0)
            print(f"  {mac} ({client_count} clients)")


def print_signal_quality(signal):
    """Print signal quality analysis"""
    total = (
        signal.excellent_count
        + signal.good_count
        + signal.fair_count
        + signal.poor_count
    )

    if total == 0:
        print("No wireless clients found")
        return

    print(f"Total Wireless Clients: {total}")
    print(f"\nSignal Distribution:")
    print(
        f"  Excellent (≥-60 dBm): {signal.excellent_count} ({signal.excellent_count/total:.1%})"
    )
    print(f"  Good (-70 to -60): {signal.good_count} ({signal.good_count/total:.1%})")
    print(f"  Fair (-80 to -70): {signal.fair_count} ({signal.fair_count/total:.1%})")
    print(f"  Poor (<-80 dBm): {signal.poor_count} ({signal.poor_count/total:.1%})")
    print(f"\nAverage RSSI: {signal.avg_rssi:.1f} dBm")
    print(f"Median RSSI: {signal.median_rssi:.1f} dBm")

    if signal.weakest_clients:
        print(f"\nWeakest Clients:")
        for mac, rssi in signal.weakest_clients:
            print(f"  {mac}: {rssi:.1f} dBm")


def print_trend(trend):
    """Print trend analysis"""
    print(f"Metric: {trend.metric_name}")
    print(f"Entity: {trend.entity_name} ({trend.entity_mac})")
    print(f"  Trend: {trend.direction.upper()}")
    print(f"  Change: {trend.change_percent:+.1f}%")
    print(f"  Slope: {trend.slope:+.4f} per hour")
    print(f"  Confidence: {trend.confidence:.1%}")


def main():
    """Run analytics demo"""
    # Check for database
    db_path = "network_monitor.db"
    try:
        db = Database(db_path)
        print(f"✅ Connected to database: {db_path}")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print(f"\nPlease run data collection first:")
        print(f"  python collect_unifi_data.py")
        return 1

    # Initialize analytics engine
    analytics = UniFiAnalyticsEngine(db)

    # Get network health summary
    print_section("Network Health Summary")
    try:
        summary = analytics.get_network_health_summary(hours=24)

        print(f"Analysis Time: {summary['timestamp']}")
        print(f"Period: Last {summary['analysis_period_hours']} hours")

        print(f"\n📊 Devices:")
        print(f"  Total: {summary['devices']['total']}")
        if summary["devices"]["avg_health_score"]:
            print(f"  Avg Health: {summary['devices']['avg_health_score']:.1f}/100")
        print(f"  Unhealthy: {summary['devices']['unhealthy_count']}")

        if summary["devices"]["unhealthy_devices"]:
            print(f"  Unhealthy Devices:")
            for dev in summary["devices"]["unhealthy_devices"][:5]:
                print(f"    {dev['name']}: {dev['score']:.1f}/100")

        print(f"\n👥 Clients:")
        print(f"  Total Active: {summary['clients']['total_active']}")
        if summary["clients"]["avg_experience_score"]:
            print(
                f"  Avg Experience: {summary['clients']['avg_experience_score']:.1f}/100"
            )
        print(f"  Poor Experience: {summary['clients']['poor_experience_count']}")

        print(f"\n📡 Signal Quality:")
        sq = summary["signal_quality"]
        print(f"  Excellent: {sq['excellent']}")
        print(f"  Good: {sq['good']}")
        print(f"  Fair: {sq['fair']}")
        print(f"  Poor: {sq['poor']}")
        print(f"  Avg RSSI: {sq['avg_rssi']:.1f} dBm")

        print(f"\n🔔 Events:")
        print(f"  Total: {summary['events']['total']}")
        if summary["events"]["by_type"]:
            print(f"  By Type:")
            for event_type, count in sorted(
                summary["events"]["by_type"].items(), key=lambda x: x[1], reverse=True
            )[:5]:
                print(f"    {event_type}: {count}")

    except Exception as e:
        print(f"❌ Error getting network summary: {e}")

    # Network topology
    print_section("Network Topology")
    try:
        topology = analytics.analyze_network_topology()
        print_topology(topology)
    except Exception as e:
        print(f"❌ Error analyzing topology: {e}")

    # Signal quality
    print_section("Signal Quality Analysis")
    try:
        signal = analytics.analyze_signal_quality()
        print_signal_quality(signal)
    except Exception as e:
        print(f"❌ Error analyzing signal quality: {e}")

    # Device health (show first 5 devices)
    print_section("Device Health Scores (Top 5)")
    try:
        from src.database.repositories.unifi_repository import UniFiDeviceRepository

        device_repo = UniFiDeviceRepository(db)
        devices = device_repo.get_all()[:5]

        if not devices:
            print("No devices found")
        else:
            for i, device in enumerate(devices, 1):
                health = analytics.calculate_device_health(device.mac, hours=24)
                if health:
                    print(f"\n{i}. ", end="")
                    print_device_health(health)

    except Exception as e:
        print(f"❌ Error calculating device health: {e}")

    # Client experience (show first 5 clients)
    print_section("Client Experience (First 5)")
    try:
        from src.database.repositories.unifi_repository import UniFiClientRepository

        client_repo = UniFiClientRepository(db)
        clients = client_repo.get_active_clients()[:5]

        if not clients:
            print("No active clients found")
        else:
            for i, client in enumerate(clients, 1):
                exp = analytics.analyze_client_experience(client.mac, hours=24)
                if exp:
                    print(f"\n{i}. ", end="")
                    print_client_experience(exp)

    except Exception as e:
        print(f"❌ Error analyzing client experience: {e}")

    # Trend analysis (show first device CPU trend)
    print_section("Trend Analysis (Sample)")
    try:
        from src.database.repositories.unifi_repository import UniFiDeviceRepository

        device_repo = UniFiDeviceRepository(db)
        devices = device_repo.get_all()[:1]

        if devices:
            device = devices[0]
            for metric in ["cpu", "memory"]:
                trend = analytics.detect_metric_trend(device.mac, metric, hours=24)
                if trend:
                    print()
                    print_trend(trend)
        else:
            print("No devices found for trend analysis")

    except Exception as e:
        print(f"❌ Error detecting trends: {e}")

    print_section("Analytics Demo Complete")
    print("✅ All analytics operations completed successfully!")
    print(
        "\nFor more details, use the UniFiAnalyticsEngine class directly in your code."
    )

    db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
