#!/usr/bin/env python3
"""
Enhanced UniFi Network Dashboard

Rich terminal UI dashboard with analytics integration.
Displays real-time network status, health scores, trends, and anomalies.
"""

import sys
import time
from datetime import datetime, timedelta

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.analytics import AnalyticsEngine
from src.database import Database
from src.database.repositories import (
    EventRepository,
    HostRepository,
    MetricRepository,
    StatusRepository,
)

console = Console()


def create_header(refresh_time: datetime) -> Panel:
    """Create dashboard header"""
    header_text = Text()
    header_text.append("UniFi Network Dashboard", style="bold cyan")
    header_text.append("\n")
    header_text.append(
        f"Last Updated: {refresh_time.strftime('%Y-%m-%d %H:%M:%S')}",
        style="dim",
    )

    return Panel(
        header_text,
        box=box.DOUBLE,
        style="cyan",
    )


def create_network_summary(analytics: AnalyticsEngine) -> Panel:
    """Create network summary panel"""
    summary = analytics.get_network_summary(days=7)

    # Create summary text with colors
    text = Text()

    # Total hosts
    text.append("Total Devices: ", style="bold")
    text.append(f"{summary['total_hosts']}\n", style="cyan")

    # Active/Offline with color coding
    text.append("Active: ", style="bold")
    if summary["active_hosts"] == summary["total_hosts"]:
        text.append(f"{summary['active_hosts']} ", style="green")
        text.append("✓ All Online\n", style="green")
    else:
        text.append(f"{summary['active_hosts']}\n", style="yellow")

    text.append("Offline: ", style="bold")
    if summary["offline_hosts"] > 0:
        text.append(f"{summary['offline_hosts']}\n", style="red")
    else:
        text.append(f"{summary['offline_hosts']}\n", style="green")

    # Health score with color coding
    if summary["avg_health_score"] is not None:
        text.append("\nAvg Health: ", style="bold")
        health = summary["avg_health_score"]
        if health >= 80:
            color = "green"
            icon = "🟢"
        elif health >= 60:
            color = "yellow"
            icon = "🟡"
        elif health >= 40:
            color = "orange3"
            icon = "🟠"
        else:
            color = "red"
            icon = "🔴"
        text.append(f"{health:.1f}/100 {icon}\n", style=color)

    # Events
    text.append("\nEvents (7d): ", style="bold")
    text.append(f"{summary['total_events']}", style="cyan")

    return Panel(
        text,
        title="[bold]📊 Network Summary[/bold]",
        border_style="blue",
        box=box.ROUNDED,
    )


def create_device_table(
    host_repo: HostRepository,
    analytics: AnalyticsEngine,
) -> Table:
    """Create device status table with health scores and trends"""
    table = Table(
        title="💻 Device Status",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("Device", style="white", no_wrap=True, width=25)
    table.add_column("Status", justify="center", width=12)
    table.add_column("Health", justify="center", width=10)
    table.add_column("CPU Trend", justify="center", width=12)
    table.add_column("Last Seen", justify="right", width=18)

    hosts = host_repo.get_all()

    for host in hosts[:10]:  # Show first 10
        # Device name
        name = host.name[:24] if host.name else "Unknown"

        # Status
        online_hosts = host_repo.get_online_hosts()
        is_online = any(h.id == host.id for h in online_hosts)

        if is_online:
            status = Text("🟢 Online", style="green")
        else:
            status = Text("🔴 Offline", style="red")

        # Health score
        health_score = analytics.get_host_health_score(host.id, days=7)
        if health_score is not None:
            if health_score >= 80:
                health = Text(f"{health_score:.0f}/100", style="green")
            elif health_score >= 60:
                health = Text(f"{health_score:.0f}/100", style="yellow")
            elif health_score >= 40:
                health = Text(f"{health_score:.0f}/100", style="orange3")
            else:
                health = Text(f"{health_score:.0f}/100", style="red")
        else:
            health = Text("N/A", style="dim")

        # CPU Trend
        cpu_trend = analytics.detect_trend(host.id, "cpu", days=7)
        if cpu_trend:
            if cpu_trend.direction == "up":
                trend = Text(f"📈 {cpu_trend.change_percent:+.1f}%", style="red")
            elif cpu_trend.direction == "down":
                trend = Text(f"📉 {cpu_trend.change_percent:+.1f}%", style="green")
            else:
                trend = Text(f"➡️ {cpu_trend.change_percent:+.1f}%", style="dim")
        else:
            trend = Text("—", style="dim")

        # Last seen
        if host.last_seen:
            last_seen = format_relative_time(host.last_seen)
        else:
            last_seen = "Never"

        table.add_row(name, status, health, trend, last_seen)

    if len(hosts) > 10:
        table.caption = f"Showing 10 of {len(hosts)} devices"

    return table


def create_events_panel(event_repo: EventRepository) -> Panel:
    """Create recent events panel"""
    yesterday = datetime.now() - timedelta(days=1)
    events = event_repo.get_by_time_range(yesterday, datetime.now())
    events = sorted(events, key=lambda e: e.created_at, reverse=True)[:8]

    if not events:
        text = Text("No recent events", style="dim")
    else:
        text = Text()
        for event in events:
            # Event type icon
            if event.event_type == "host_discovered":
                icon = "🆕"
                style = "cyan"
            elif event.event_type == "host_online":
                icon = "✅"
                style = "green"
            elif event.event_type == "host_offline":
                icon = "❌"
                style = "red"
            elif "error" in event.event_type.lower():
                icon = "⚠️"
                style = "yellow"
            else:
                icon = "•"
                style = "white"

            # Format timestamp
            time_str = format_relative_time(event.created_at)

            # Add to text
            text.append(f"{icon} ", style=style)
            text.append(f"[{time_str}] ", style="dim")
            desc = event.description[:50] if event.description else "No description"
            text.append(f"{desc}\n", style=style)

    return Panel(
        text,
        title="[bold]📋 Recent Events (24h)[/bold]",
        border_style="yellow",
        box=box.ROUNDED,
    )


def create_alerts_panel(analytics: AnalyticsEngine, host_repo: HostRepository) -> Panel:
    """Create alerts and anomalies panel"""
    text = Text()
    alert_count = 0

    hosts = host_repo.get_all()

    for host in hosts[:5]:  # Check first 5 hosts
        # Check for anomalies
        cpu_anomalies = analytics.detect_anomalies(host.id, "cpu", days=1)
        mem_anomalies = analytics.detect_anomalies(host.id, "memory", days=1)

        anomalies = cpu_anomalies + mem_anomalies

        # Check for capacity warnings
        cpu_forecast = analytics.forecast_capacity(
            host.id, "cpu", threshold=90.0, days=7
        )
        mem_forecast = analytics.forecast_capacity(
            host.id, "memory", threshold=90.0, days=7
        )

        # Display high-severity anomalies
        for anomaly in anomalies:
            if anomaly.severity == "high" and alert_count < 5:
                text.append("🔴 ", style="red")
                host_name = host.name[:20] if host.name else "Unknown"
                text.append(f"{host_name}: ", style="bold")
                text.append(f"{anomaly.description[:40]}\n", style="red")
                alert_count += 1

        # Display capacity warnings
        if cpu_forecast and cpu_forecast.days_until_threshold:
            if cpu_forecast.days_until_threshold < 7 and alert_count < 5:
                text.append("⚠️ ", style="yellow")
                host_name = host.name[:20] if host.name else "Unknown"
                text.append(f"{host_name}: ", style="bold")
                text.append(
                    f"CPU will hit 90% in {cpu_forecast.days_until_threshold} days\n",
                    style="yellow",
                )
                alert_count += 1

        if mem_forecast and mem_forecast.days_until_threshold:
            if mem_forecast.days_until_threshold < 7 and alert_count < 5:
                text.append("⚠️ ", style="yellow")
                host_name = host.name[:20] if host.name else "Unknown"
                text.append(f"{host_name}: ", style="bold")
                text.append(
                    f"Memory will hit 90% in {mem_forecast.days_until_threshold} days\n",
                    style="yellow",
                )
                alert_count += 1

    if alert_count == 0:
        text.append("✓ No alerts", style="green")

    return Panel(
        text,
        title=f"[bold]🚨 Alerts & Warnings ({alert_count})[/bold]",
        border_style="red" if alert_count > 0 else "green",
        box=box.ROUNDED,
    )


def format_relative_time(timestamp: str) -> str:
    """Format timestamp as relative time"""
    if not timestamp:
        return "Never"

    try:
        dt = datetime.fromisoformat(timestamp)
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
        elif diff.total_seconds() < 604800:
            days = int(diff.total_seconds() / 86400)
            return f"{days}d ago"
        else:
            return dt.strftime("%Y-%m-%d")
    except Exception:
        return "Unknown"


def create_dashboard_layout(
    analytics: AnalyticsEngine,
    host_repo: HostRepository,
    event_repo: EventRepository,
) -> Layout:
    """Create the complete dashboard layout"""
    layout = Layout()

    # Split into header and body
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="body"),
    )

    # Header
    layout["header"].update(create_header(datetime.now()))

    # Body split into left and right
    layout["body"].split_row(
        Layout(name="left", ratio=2),
        Layout(name="right", ratio=1),
    )

    # Left side: device table
    layout["left"].update(create_device_table(host_repo, analytics))

    # Right side split into panels
    layout["right"].split_column(
        Layout(name="summary"),
        Layout(name="events"),
        Layout(name="alerts"),
    )

    layout["right"]["summary"].update(create_network_summary(analytics))
    layout["right"]["events"].update(create_events_panel(event_repo))
    layout["right"]["alerts"].update(create_alerts_panel(analytics, host_repo))

    return layout


def show_dashboard_once(db_path: str = "data/unifi_network.db"):
    """Display dashboard once and exit"""
    db = Database(db_path)
    analytics = AnalyticsEngine(db)
    host_repo = HostRepository(db)
    event_repo = EventRepository(db)

    layout = create_dashboard_layout(analytics, host_repo, event_repo)
    console.print(layout)


def run_live_dashboard(
    db_path: str = "data/unifi_network.db", refresh_seconds: int = 30
):
    """Run dashboard with live updates"""
    db = Database(db_path)
    analytics = AnalyticsEngine(db)
    host_repo = HostRepository(db)
    event_repo = EventRepository(db)

    def generate_layout():
        """Generate fresh layout"""
        return create_dashboard_layout(analytics, host_repo, event_repo)

    console.print(
        "\n[bold cyan]Starting Enhanced Dashboard[/bold cyan]",
        justify="center",
    )
    console.print(
        f"[dim]Refreshing every {refresh_seconds} seconds. Press Ctrl+C to exit.[/dim]\n",
        justify="center",
    )

    try:
        with Live(
            generate_layout(),
            refresh_per_second=1 / refresh_seconds,
            console=console,
            screen=True,
        ) as live:
            while True:
                time.sleep(refresh_seconds)
                live.update(generate_layout())
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Dashboard stopped.[/yellow]", justify="center")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced UniFi Network Dashboard")
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
    parser.add_argument(
        "--refresh",
        type=int,
        default=30,
        help="Refresh interval in seconds (default: 30)",
    )

    args = parser.parse_args()

    # Check if database exists
    import os

    if not os.path.exists(args.db):
        console.print(f"[red]Error: Database not found at {args.db}[/red]")
        console.print(
            "[yellow]Run the data collector first to populate the database.[/yellow]"
        )
        sys.exit(1)

    if args.once:
        # Show once and exit
        show_dashboard_once(args.db)
    else:
        # Live mode with auto-refresh
        run_live_dashboard(args.db, args.refresh)


if __name__ == "__main__":
    main()
