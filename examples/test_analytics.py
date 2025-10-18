"""
Test script for Analytics Engine

Tests statistical analysis, trend detection, anomaly detection,
and capacity planning features.
"""

from datetime import datetime, timedelta

from src.analytics import AnalyticsEngine
from src.database import Database


def print_section(title: str):
    """Print section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def test_analytics(db_path="data/unifi_network.db"):
    """Test the analytics engine"""

    # Initialize
    print("Initializing Analytics Engine...")
    db = Database(db_path)
    analytics = AnalyticsEngine(db)

    # Get a host to analyze
    from src.database.repositories import HostRepository

    host_repo = HostRepository(db)
    hosts = host_repo.get_all()

    if not hosts:
        print("No hosts found in database. Run the collector first.")
        return

    host = hosts[0]
    print(f"Analyzing host: {host.name} ({host.id})")

    # Test 1: Network Summary
    print_section("Network Summary")
    summary = analytics.get_network_summary(days=7)
    print(f"Total Hosts: {summary['total_hosts']}")
    print(f"Active Hosts: {summary['active_hosts']}")
    print(f"Offline Hosts: {summary['offline_hosts']}")
    if summary["avg_health_score"]:
        print(f"Avg Health Score: {summary['avg_health_score']:.1f}/100")
        print(f"Min Health Score: {summary['min_health_score']:.1f}/100")
        print(f"Max Health Score: {summary['max_health_score']:.1f}/100")
    print(f"Total Events (7d): {summary['total_events']}")
    print(f"\nEvent Breakdown:")
    for event_type, count in summary["event_breakdown"].items():
        print(f"  {event_type}: {count}")

    # Test 2: Statistics
    print_section("CPU Statistics (Last 7 Days)")
    cpu_stats = analytics.calculate_statistics(host.id, "cpu", days=7)
    if cpu_stats:
        print(f"Mean: {cpu_stats.mean:.2f}%")
        print(f"Median: {cpu_stats.median:.2f}%")
        print(f"Min: {cpu_stats.min:.2f}%")
        print(f"Max: {cpu_stats.max:.2f}%")
        print(f"Std Dev: {cpu_stats.stddev:.2f}%")
        print(f"Data Points: {cpu_stats.count}")
    else:
        print("No CPU data available")

    print_section("Memory Statistics (Last 7 Days)")
    mem_stats = analytics.calculate_statistics(host.id, "memory", days=7)
    if mem_stats:
        print(f"Mean: {mem_stats.mean:.2f}%")
        print(f"Median: {mem_stats.median:.2f}%")
        print(f"Min: {mem_stats.min:.2f}%")
        print(f"Max: {mem_stats.max:.2f}%")
        print(f"Std Dev: {mem_stats.stddev:.2f}%")
        print(f"Data Points: {mem_stats.count}")
    else:
        print("No memory data available")

    # Test 3: Trend Detection
    print_section("Trend Analysis (Last 7 Days)")
    cpu_trend = analytics.detect_trend(host.id, "cpu", days=7)
    if cpu_trend:
        direction_icon = {
            "up": "📈",
            "down": "📉",
            "stable": "➡️",
        }[cpu_trend.direction]
        print(f"CPU Trend: {direction_icon} {cpu_trend.direction.upper()}")
        print(f"  Slope: {cpu_trend.slope:.4f}% per day")
        print(f"  Confidence: {cpu_trend.confidence:.2%}")
        print(f"  Total Change: {cpu_trend.change_percent:+.2f}%")
    else:
        print("CPU: Insufficient data for trend analysis")

    mem_trend = analytics.detect_trend(host.id, "memory", days=7)
    if mem_trend:
        direction_icon = {
            "up": "📈",
            "down": "📉",
            "stable": "➡️",
        }[mem_trend.direction]
        print(f"\nMemory Trend: {direction_icon} {mem_trend.direction.upper()}")
        print(f"  Slope: {mem_trend.slope:.4f}% per day")
        print(f"  Confidence: {mem_trend.confidence:.2%}")
        print(f"  Total Change: {mem_trend.change_percent:+.2f}%")
    else:
        print("\nMemory: Insufficient data for trend analysis")

    # Test 4: Anomaly Detection
    print_section("Anomaly Detection (Last 7 Days)")
    cpu_anomalies = analytics.detect_anomalies(host.id, "cpu", days=7)
    mem_anomalies = analytics.detect_anomalies(host.id, "memory", days=7)

    all_anomalies = cpu_anomalies + mem_anomalies

    if all_anomalies:
        print(f"Found {len(all_anomalies)} anomalies:\n")
        for anomaly in all_anomalies[:10]:  # Show first 10
            severity_icon = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢",
            }[anomaly.severity]
            print(f"{severity_icon} [{anomaly.severity.upper()}] {anomaly.description}")
            print(f"   Time: {anomaly.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(
                f"   Expected: {anomaly.expected_range[0]:.1f} - "
                f"{anomaly.expected_range[1]:.1f}\n"
            )
        if len(all_anomalies) > 10:
            print(f"... and {len(all_anomalies) - 10} more anomalies")
    else:
        print("No anomalies detected")

    # Test 5: Capacity Forecasting
    print_section("Capacity Forecasting")
    cpu_forecast = analytics.forecast_capacity(host.id, "cpu", threshold=90.0, days=30)
    if cpu_forecast:
        print(f"CPU Capacity Forecast:")
        print(f"  Current: {cpu_forecast.current_value:.1f}%")
        print(f"  Threshold: {cpu_forecast.threshold:.1f}%")
        if cpu_forecast.days_until_threshold:
            print(f"  Days Until Threshold: {cpu_forecast.days_until_threshold}")
            print(f"  Predicted Value: {cpu_forecast.predicted_value:.1f}%")
            print(f"  Confidence: {cpu_forecast.confidence:.2%}")

            if cpu_forecast.days_until_threshold < 30:
                print(f"\n  ⚠️  WARNING: Approaching capacity!")
            else:
                print(f"\n  ✓ Capacity OK")
        else:
            print(f"  ✓ No capacity concerns")
    else:
        print("CPU: No upward trend detected or insufficient data")

    mem_forecast = analytics.forecast_capacity(
        host.id, "memory", threshold=90.0, days=30
    )
    if mem_forecast:
        print(f"\nMemory Capacity Forecast:")
        print(f"  Current: {mem_forecast.current_value:.1f}%")
        print(f"  Threshold: {mem_forecast.threshold:.1f}%")
        if mem_forecast.days_until_threshold:
            print(f"  Days Until Threshold: {mem_forecast.days_until_threshold}")
            print(f"  Predicted Value: {mem_forecast.predicted_value:.1f}%")
            print(f"  Confidence: {mem_forecast.confidence:.2%}")

            if mem_forecast.days_until_threshold < 30:
                print(f"\n  ⚠️  WARNING: Approaching capacity!")
            else:
                print(f"\n  ✓ Capacity OK")
        else:
            print(f"  ✓ No capacity concerns")
    else:
        print("\nMemory: No upward trend detected or insufficient data")

    # Test 6: Health Score
    print_section("Host Health Score")
    health_score = analytics.get_host_health_score(host.id, days=7)
    if health_score is not None:
        if health_score >= 80:
            status = "🟢 Excellent"
        elif health_score >= 60:
            status = "🟡 Good"
        elif health_score >= 40:
            status = "🟠 Fair"
        else:
            status = "🔴 Poor"

        print(f"Overall Health Score: {health_score:.1f}/100 ({status})")
    else:
        print("Insufficient data to calculate health score")

    print(f"\n{'=' * 60}")
    print("Analytics test complete!")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    import os
    import sys

    # Check if database exists
    db_path = "data/unifi_network.db"
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        print("Run the data collector first to populate the database.")
        sys.exit(1)

    test_analytics(db_path)
