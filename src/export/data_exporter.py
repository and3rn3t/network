"""Data export functionality for UniFi Network monitoring.

This module provides exporters for various data formats including CSV, JSON,
and Prometheus metrics.
"""

import csv
import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.database import Database
from src.database.repositories import EventRepository, HostRepository, MetricRepository


class ExportFormat(Enum):
    """Supported export formats."""

    CSV = "csv"
    JSON = "json"
    PROMETHEUS = "prometheus"


class DataExporter:
    """Base class for data export functionality."""

    def __init__(self, database_path: str = "network.db"):
        """Initialize the data exporter.

        Args:
            database_path: Path to SQLite database
        """
        self.db = Database(database_path)
        self.db.initialize()

        self.host_repo = HostRepository(self.db)
        self.event_repo = EventRepository(self.db)
        self.metric_repo = MetricRepository(self.db)


class CSVExporter(DataExporter):
    """Export data to CSV format (Excel-compatible)."""

    def export_hosts(self, output_path: str) -> int:
        """Export all hosts to CSV.

        Args:
            output_path: Path to output CSV file

        Returns:
            Number of rows exported
        """
        hosts = self.host_repo.get_all()

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            if not hosts:
                # Write header only
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "id",
                        "name",
                        "mac",
                        "model",
                        "status",
                        "is_online",
                        "ip_address",
                        "uptime",
                        "last_seen",
                        "created_at",
                    ],
                )
                writer.writeheader()
                return 0

            # Get fieldnames from first host
            fieldnames = [
                "id",
                "name",
                "mac",
                "model",
                "status",
                "is_online",
                "ip_address",
                "uptime",
                "last_seen",
                "created_at",
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for host in hosts:
                writer.writerow(
                    {
                        "id": host.id,
                        "name": host.name or "",
                        "mac": host.mac,
                        "model": host.model or "",
                        "status": host.status,
                        "is_online": "Yes" if host.is_online else "No",
                        "ip_address": host.ip_address or "",
                        "uptime": host.uptime or 0,
                        "last_seen": (
                            host.last_seen.isoformat() if host.last_seen else ""
                        ),
                        "created_at": (
                            host.created_at.isoformat() if host.created_at else ""
                        ),
                    }
                )

        return len(hosts)

    def export_events(
        self,
        output_path: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 7,
    ) -> int:
        """Export events to CSV.

        Args:
            output_path: Path to output CSV file
            start_date: Start date (default: days ago)
            end_date: End date (default: now)
            days: Number of days if start_date not provided

        Returns:
            Number of rows exported
        """
        if end_date is None:
            end_date = datetime.now()

        if start_date is None:
            start_date = end_date - timedelta(days=days)

        events = self.event_repo.get_by_time_range(start_date, end_date)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "id",
                "timestamp",
                "event_type",
                "severity",
                "message",
                "host_id",
                "created_at",
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for event in events:
                writer.writerow(
                    {
                        "id": event.id,
                        "timestamp": event.timestamp.isoformat(),
                        "event_type": event.event_type,
                        "severity": event.severity,
                        "message": event.message,
                        "host_id": event.host_id or "",
                        "created_at": (
                            event.created_at.isoformat() if event.created_at else ""
                        ),
                    }
                )

        return len(events)

    def export_metrics(
        self,
        output_path: str,
        host_id: Optional[str] = None,
        metric_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 7,
    ) -> int:
        """Export metrics to CSV.

        Args:
            output_path: Path to output CSV file
            host_id: Optional host ID filter
            metric_name: Optional metric name filter
            start_date: Start date (default: days ago)
            end_date: End date (default: now)
            days: Number of days if start_date not provided

        Returns:
            Number of rows exported
        """
        if end_date is None:
            end_date = datetime.now()

        if start_date is None:
            start_date = end_date - timedelta(days=days)

        # Get all hosts if no specific host requested
        hosts = (
            [self.host_repo.get_by_id(host_id)] if host_id else self.host_repo.get_all()
        )

        all_metrics = []
        for host in hosts:
            if host:
                metrics = self.metric_repo.get_by_time_range(
                    host_id=host.id,
                    start_time=start_date,
                    end_time=end_date,
                    metric_name=metric_name,
                )
                all_metrics.extend(metrics)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "id",
                "timestamp",
                "host_id",
                "metric_name",
                "metric_value",
                "created_at",
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for metric in all_metrics:
                writer.writerow(
                    {
                        "id": metric.id,
                        "timestamp": metric.timestamp.isoformat(),
                        "host_id": metric.host_id,
                        "metric_name": metric.metric_name,
                        "metric_value": metric.metric_value,
                        "created_at": (
                            metric.created_at.isoformat() if metric.created_at else ""
                        ),
                    }
                )

        return len(all_metrics)


class JSONExporter(DataExporter):
    """Export data to JSON format (API-compatible)."""

    def export_hosts(self, output_path: str) -> Dict[str, Any]:
        """Export all hosts to JSON.

        Args:
            output_path: Path to output JSON file

        Returns:
            Dictionary with export metadata
        """
        hosts = self.host_repo.get_all()

        data = {
            "export_date": datetime.now().isoformat(),
            "total_hosts": len(hosts),
            "hosts": [
                {
                    "id": host.id,
                    "name": host.name,
                    "mac": host.mac,
                    "model": host.model,
                    "status": host.status,
                    "is_online": host.is_online,
                    "ip_address": host.ip_address,
                    "uptime": host.uptime,
                    "last_seen": host.last_seen.isoformat() if host.last_seen else None,
                    "created_at": (
                        host.created_at.isoformat() if host.created_at else None
                    ),
                    "updated_at": (
                        host.updated_at.isoformat() if host.updated_at else None
                    ),
                }
                for host in hosts
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return {"file": output_path, "rows": len(hosts), "format": "json"}

    def export_events(
        self,
        output_path: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Export events to JSON.

        Args:
            output_path: Path to output JSON file
            start_date: Start date (default: days ago)
            end_date: End date (default: now)
            days: Number of days if start_date not provided

        Returns:
            Dictionary with export metadata
        """
        if end_date is None:
            end_date = datetime.now()

        if start_date is None:
            start_date = end_date - timedelta(days=days)

        events = self.event_repo.get_by_time_range(start_date, end_date)

        data = {
            "export_date": datetime.now().isoformat(),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "total_events": len(events),
            "events": [
                {
                    "id": event.id,
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "message": event.message,
                    "host_id": event.host_id,
                    "created_at": (
                        event.created_at.isoformat() if event.created_at else None
                    ),
                }
                for event in events
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return {"file": output_path, "rows": len(events), "format": "json"}

    def export_metrics(
        self,
        output_path: str,
        host_id: Optional[str] = None,
        metric_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Export metrics to JSON.

        Args:
            output_path: Path to output JSON file
            host_id: Optional host ID filter
            metric_name: Optional metric name filter
            start_date: Start date (default: days ago)
            end_date: End date (default: now)
            days: Number of days if start_date not provided

        Returns:
            Dictionary with export metadata
        """
        if end_date is None:
            end_date = datetime.now()

        if start_date is None:
            start_date = end_date - timedelta(days=days)

        # Get all hosts if no specific host requested
        hosts = (
            [self.host_repo.get_by_id(host_id)] if host_id else self.host_repo.get_all()
        )

        all_metrics = []
        for host in hosts:
            if host:
                metrics = self.metric_repo.get_by_time_range(
                    host_id=host.id,
                    start_time=start_date,
                    end_time=end_date,
                    metric_name=metric_name,
                )
                all_metrics.extend(metrics)

        data = {
            "export_date": datetime.now().isoformat(),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "filters": {
                "host_id": host_id,
                "metric_name": metric_name,
            },
            "total_metrics": len(all_metrics),
            "metrics": [
                {
                    "id": metric.id,
                    "timestamp": metric.timestamp.isoformat(),
                    "host_id": metric.host_id,
                    "metric_name": metric.metric_name,
                    "metric_value": metric.metric_value,
                    "created_at": (
                        metric.created_at.isoformat() if metric.created_at else None
                    ),
                }
                for metric in all_metrics
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return {"file": output_path, "rows": len(all_metrics), "format": "json"}


class PrometheusExporter(DataExporter):
    """Export data in Prometheus metrics format."""

    def generate_metrics(self) -> str:
        """Generate Prometheus metrics text.

        Returns:
            Prometheus metrics in text format
        """
        metrics = []

        # Add header
        metrics.append("# UniFi Network Monitoring Metrics")
        metrics.append("")

        # Host metrics
        hosts = self.host_repo.get_all()
        online_hosts = self.host_repo.get_online_hosts()
        offline_hosts = self.host_repo.get_offline_hosts()

        metrics.append("# HELP unifi_hosts_total Total number of hosts")
        metrics.append("# TYPE unifi_hosts_total gauge")
        metrics.append(f"unifi_hosts_total {len(hosts)}")
        metrics.append("")

        metrics.append("# HELP unifi_hosts_online Number of online hosts")
        metrics.append("# TYPE unifi_hosts_online gauge")
        metrics.append(f"unifi_hosts_online {len(online_hosts)}")
        metrics.append("")

        metrics.append("# HELP unifi_hosts_offline Number of offline hosts")
        metrics.append("# TYPE unifi_hosts_offline gauge")
        metrics.append(f"unifi_hosts_offline {len(offline_hosts)}")
        metrics.append("")

        # Per-host uptime
        metrics.append("# HELP unifi_host_uptime Host uptime in seconds")
        metrics.append("# TYPE unifi_host_uptime gauge")
        for host in hosts:
            if host.uptime and host.is_online:
                labels = f'host_id="{host.id}",host_name="{host.name or "unknown"}",mac="{host.mac}"'
                metrics.append(f"unifi_host_uptime{{{labels}}} {host.uptime}")
        metrics.append("")

        # Per-host status (1 = online, 0 = offline)
        metrics.append("# HELP unifi_host_status Host status (1=online, 0=offline)")
        metrics.append("# TYPE unifi_host_status gauge")
        for host in hosts:
            labels = f'host_id="{host.id}",host_name="{host.name or "unknown"}",mac="{host.mac}"'
            status_value = 1 if host.is_online else 0
            metrics.append(f"unifi_host_status{{{labels}}} {status_value}")
        metrics.append("")

        # Recent metrics (last 5 minutes)
        five_min_ago = datetime.now() - timedelta(minutes=5)

        # Track if we exported any metrics
        exported_any_metrics = False

        for host in hosts:
            # Get recent metrics for this host
            recent_metrics = self.metric_repo.get_by_time_range(
                host_id=host.id, start_time=five_min_ago, end_time=datetime.now()
            )

            # Group by metric name and get latest value
            metric_values = {}
            for metric in recent_metrics:
                if metric.metric_name not in metric_values:
                    metric_values[metric.metric_name] = metric
                elif metric.timestamp > metric_values[metric.metric_name].timestamp:
                    metric_values[metric.metric_name] = metric

            # Export each metric type
            for metric_name, metric in metric_values.items():
                exported_any_metrics = True
                safe_metric_name = metric_name.replace("-", "_").replace(".", "_")

                # Add help and type only once per metric name
                if not any(f"# HELP unifi_{safe_metric_name}" in m for m in metrics):
                    metrics.append(f"# HELP unifi_{safe_metric_name} {metric_name}")
                    metrics.append(f"# TYPE unifi_{safe_metric_name} gauge")

                labels = f'host_id="{host.id}",host_name="{host.name or "unknown"}",mac="{host.mac}"'
                metrics.append(
                    f"unifi_{safe_metric_name}{{{labels}}} {metric.metric_value}"
                )

        if exported_any_metrics:  # Only add newline if we had metrics
            metrics.append("")

        # Event counts (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_events = self.event_repo.get_by_time_range(yesterday, datetime.now())

        metrics.append("# HELP unifi_events_24h Events in last 24 hours")
        metrics.append("# TYPE unifi_events_24h counter")
        metrics.append(f"unifi_events_24h {len(recent_events)}")
        metrics.append("")

        # Event counts by severity
        severity_counts = {}
        for event in recent_events:
            severity = event.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        metrics.append("# HELP unifi_events_by_severity Events by severity (24h)")
        metrics.append("# TYPE unifi_events_by_severity counter")
        for severity, count in severity_counts.items():
            metrics.append(f'unifi_events_by_severity{{severity="{severity}"}} {count}')
        metrics.append("")

        return "\n".join(metrics)

    def export_to_file(self, output_path: str) -> int:
        """Export Prometheus metrics to file.

        Args:
            output_path: Path to output file

        Returns:
            Number of metric lines exported
        """
        metrics_text = self.generate_metrics()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(metrics_text)

        # Count non-comment, non-empty lines
        metric_lines = [
            line
            for line in metrics_text.split("\n")
            if line and not line.startswith("#")
        ]

        return len(metric_lines)
