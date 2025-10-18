#!/usr/bin/env python3
"""
UniFi Network Dashboard

Simple CLI dashboard to view collected network data and statistics.
Displays real-time status, recent events, and device health overview.
"""

import os
import sys
from datetime import datetime, timedelta
from statistics import mean

from src.database import Database
from src.database.repositories import (
    EventRepository,
    HostRepository,
    MetricRepository,
    StatusRepository,
)


def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def format_timestamp(dt):
    """Format datetime for display"""
    if not dt:
        return "Never"
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)

    # Show relative time for recent events
    now = datetime.now()
    diff = now - dt

    if diff.total_seconds() < 60:
        return "Just now"
    elif diff.total_seconds() < 3600:
        mins = int(diff.total_seconds() / 60)
        return f"{mins}m ago"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"{hours}h ago"
    else:
        return dt.strftime("%Y-%m-%d %H:%M")


def format_uptime(seconds):
    """Format uptime in human-readable format"""
    if not seconds:
        return "Unknown"

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60

    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def print_header():
    """Print dashboard header"""
    print("=" * 80)
    print(" " * 20 + "UniFi Network Dashboard")
    print("=" * 80)
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()


def print_network_summary(host_repo, event_repo):
    """Print network overview statistics"""
    all_hosts = host_repo.get_all()
    active_hosts = host_repo.get_active()

    # Get recent events (last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)
    recent_events = event_repo.get_by_time_range(yesterday, datetime.now())

    print("📊 NETWORK SUMMARY")
    print("-" * 80)
    print(f"  Total Devices:    {len(all_hosts)}")
    print(
        f"  Active Devices:   {len(active_hosts)} ({'✓ All online' if len(active_hosts) == len(all_hosts) else f'⚠ {len(all_hosts) - len(active_hosts)} offline'})"
    )
    print(f"  Events (24h):     {len(recent_events)}")
    print()


def print_device_status(host_repo, status_repo, metric_repo):
    """Print device status table"""
    print("💻 DEVICE STATUS")
    print("-" * 80)

    # Header
    print(f"{'Device Name':<25} {'Status':<10} {'Last Seen':<15} {'Uptime':<12}")
    print("-" * 80)

    # Get all hosts with latest status
    hosts = host_repo.get_all()

    for host in hosts[:15]:  # Show first 15 devices
        # Get latest status
        statuses = status_repo.get_by_host_id(host.id, limit=1)
        status = statuses[0] if statuses else None

        # Get latest metric for uptime
        metrics = metric_repo.get_by_host_id(host.id, limit=1)
        metric = metrics[0] if metrics else None

        # Format fields
        name = host.name[:24] if host.name else "Unknown"
        is_online = status.is_online if status else False
        status_text = "🟢 Online" if is_online else "🔴 Offline"
        last_seen = format_timestamp(host.last_seen)
        uptime = format_uptime(metric.uptime) if metric and metric.uptime else "N/A"

        print(f"{name:<25} {status_text:<10} {last_seen:<15} {uptime:<12}")

    if len(hosts) > 15:
        print(f"\n  ... and {len(hosts) - 15} more devices")
    print()


def print_recent_events(event_repo):
    """Print recent events"""
    print("📋 RECENT EVENTS")
    print("-" * 80)

    # Get last 10 events
    yesterday = datetime.now() - timedelta(days=1)
    events = event_repo.get_by_time_range(yesterday, datetime.now())
    events = sorted(events, key=lambda e: e.timestamp, reverse=True)[:10]

    if not events:
        print("  No recent events")
        print()
        return

    # Event type icons
    icons = {
        "host_discovered": "🆕",
        "host_online": "✅",
        "host_offline": "❌",
        "metrics_updated": "📊",
        "status_changed": "🔄",
    }

    for event in events:
        icon = icons.get(event.event_type, "•")
        timestamp = format_timestamp(event.timestamp)
        desc = event.description[:60] if event.description else "No description"
        print(f"  {icon} [{timestamp:>10}] {desc}")

    print()


def print_device_health(host_repo, metric_repo):
    """Print device health metrics"""
    print("🏥 DEVICE HEALTH (Last 24 hours)")
    print("-" * 80)

    # Get hosts with metrics
    hosts = host_repo.get_all()
    yesterday = datetime.now() - timedelta(days=1)

    print(f"{'Device Name':<25} {'Avg CPU':<10} {'Avg Memory':<12} {'Max Temp':<10}")
    print("-" * 80)

    devices_with_metrics = 0

    for host in hosts[:10]:  # Show first 10 devices
        # Get metrics from last 24 hours
        metrics = metric_repo.get_by_time_range(
            host_id=host.id, start_time=yesterday, end_time=datetime.now()
        )

        if not metrics:
            continue

        devices_with_metrics += 1

        # Calculate averages
        cpu_values = [m.cpu_usage for m in metrics if m.cpu_usage is not None]
        mem_values = [m.memory_usage for m in metrics if m.memory_usage is not None]
        temp_values = [m.temperature for m in metrics if m.temperature is not None]

        avg_cpu = f"{mean(cpu_values):.1f}%" if cpu_values else "N/A"
        avg_mem = f"{mean(mem_values):.1f}%" if mem_values else "N/A"
        max_temp = f"{max(temp_values):.1f}°C" if temp_values else "N/A"

        # Color code high values
        if cpu_values and mean(cpu_values) > 80:
            avg_cpu = f"⚠️ {avg_cpu}"
        if mem_values and mean(mem_values) > 80:
            avg_mem = f"⚠️ {avg_mem}"
        if temp_values and max(temp_values) > 70:
            max_temp = f"⚠️ {max_temp}"

        name = host.name[:24] if host.name else "Unknown"
        print(f"{name:<25} {avg_cpu:<10} {avg_mem:<12} {max_temp:<10}")

    if devices_with_metrics == 0:
        print("  No health metrics available")

    print()


def print_event_breakdown(event_repo):
    """Print event type breakdown"""
    print("📈 EVENT BREAKDOWN (Last 7 days)")
    print("-" * 80)

    # Get events from last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    event_counts = event_repo.get_event_counts(week_ago, datetime.now())

    if not event_counts:
        print("  No events in the last 7 days")
        print()
        return

    # Sort by count
    sorted_events = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)

    for event_type, count in sorted_events:
        bar_length = min(40, int(count / max(event_counts.values()) * 40))
        bar = "█" * bar_length
        print(f"  {event_type:<20} {bar} {count}")

    print()


def print_footer():
    """Print dashboard footer"""
    print("=" * 80)
    print("Commands: [R]efresh | [Q]uit")
    print("=" * 80)


def show_dashboard(db_path="data/unifi_network.db"):
    """Display the main dashboard"""
    # Initialize database and repositories
    db = Database(db_path)
    host_repo = HostRepository(db)
    status_repo = StatusRepository(db)
    event_repo = EventRepository(db)
    metric_repo = MetricRepository(db)

    clear_screen()

    # Print all sections
    print_header()
    print_network_summary(host_repo, event_repo)
    print_device_status(host_repo, status_repo, metric_repo)
    print_recent_events(event_repo)
    print_device_health(host_repo, metric_repo)
    print_event_breakdown(event_repo)
    print_footer()


def interactive_dashboard(db_path="data/unifi_network.db"):
    """Run interactive dashboard with auto-refresh"""
    import time

    try:
        while True:
            show_dashboard(db_path)

            # Wait for user input (with timeout for auto-refresh)
            print(
                "\nPress 'q' to quit, or wait 30s for auto-refresh...",
                end="",
                flush=True,
            )

            # Simple input with timeout (works on Windows and Unix)
            start_time = time.time()
            refresh_interval = 30  # seconds

            while time.time() - start_time < refresh_interval:
                # Check for keyboard input (simplified)
                time.sleep(0.1)

            # Auto-refresh

    except KeyboardInterrupt:
        print("\n\nDashboard stopped.")
        sys.exit(0)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="UniFi Network Dashboard")
    parser.add_argument(
        "--db",
        default="data/unifi_network.db",
        help="Path to database file (default: data/unifi_network.db)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Show dashboard once and exit (no auto-refresh)",
    )

    args = parser.parse_args()

    # Check if database exists
    if not os.path.exists(args.db):
        print(f"Error: Database not found at {args.db}")
        print("Run the data collector first to populate the database.")
        sys.exit(1)

    if args.once:
        # Show once and exit
        show_dashboard(args.db)
    else:
        # Interactive mode with auto-refresh
        print("Starting interactive dashboard...")
        print("Press Ctrl+C to stop\n")
        time.sleep(2)
        interactive_dashboard(args.db)


if __name__ == "__main__":
    main()
