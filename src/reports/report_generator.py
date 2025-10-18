"""Report generation for UniFi Network monitoring.

This module generates comprehensive reports about network status, device health,
and performance metrics. Supports multiple formats and delivery methods.
"""

import smtplib
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.analytics.analytics_engine import AnalyticsEngine
from src.database import Database
from src.database.repositories.event_repository import EventRepository
from src.database.repositories.host_repository import HostRepository
from src.database.repositories.metric_repository import MetricRepository


class ReportType(Enum):
    """Report frequency types."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class ReportConfig:
    """Configuration for report generation."""

    report_type: ReportType
    database_path: str = "network.db"

    # Email settings (optional)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: Optional[str] = None
    email_to: Optional[List[str]] = None

    # PDF settings
    enable_pdf: bool = True
    pdf_output_dir: str = "reports"

    # Report content settings
    include_device_details: bool = True
    include_metrics: bool = True
    include_events: bool = True
    include_analytics: bool = True


class ReportGenerator:
    """Generates reports for UniFi Network monitoring.

    This class creates comprehensive reports including device status,
    events, metrics, and analytics. Supports HTML, PDF, and email delivery.
    """

    def __init__(self, config: ReportConfig):
        """Initialize the report generator.

        Args:
            config: Report configuration
        """
        self.config = config

        # Initialize database
        self.db = Database(config.database_path)
        self.db.initialize()  # Ensure schema is created

        # Initialize repositories
        self.host_repo = HostRepository(self.db)
        self.event_repo = EventRepository(self.db)
        self.metric_repo = MetricRepository(self.db)

        # Initialize analytics engine
        self.analytics = AnalyticsEngine(self.db)

        # Create output directory
        Path(config.pdf_output_dir).mkdir(parents=True, exist_ok=True)

    def generate_report(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive report.

        Args:
            start_date: Report start date (default: based on report type)
            end_date: Report end date (default: now)

        Returns:
            Dictionary containing report data and metadata
        """
        # Calculate date range if not provided
        if end_date is None:
            end_date = datetime.now()

        if start_date is None:
            start_date = self._calculate_start_date(end_date)

        # Gather report data
        report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": self.config.report_type.value,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "summary": self._generate_summary(start_date, end_date),
        }

        if self.config.include_device_details:
            report_data["devices"] = self._generate_device_section()

        if self.config.include_events:
            report_data["events"] = self._generate_events_section(start_date, end_date)

        if self.config.include_metrics:
            report_data["metrics"] = self._generate_metrics_section(
                start_date, end_date
            )

        if self.config.include_analytics:
            report_data["analytics"] = self._generate_analytics_section(
                start_date, end_date
            )

        return report_data

    def generate_and_save_report(self, output_filename: Optional[str] = None) -> str:
        """Generate report and save as HTML and optionally PDF.

        Args:
            output_filename: Custom filename (default: auto-generated)

        Returns:
            Path to the generated HTML file
        """
        report_data = self.generate_report()

        # Generate filename if not provided
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_type = self.config.report_type.value
            output_filename = f"network_report_{report_type}_{timestamp}"

        # Generate HTML
        html_content = self._generate_html(report_data)
        html_path = Path(self.config.pdf_output_dir) / f"{output_filename}.html"

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Generate PDF if enabled
        if self.config.enable_pdf:
            try:
                pdf_path = self._generate_pdf(html_content, output_filename)
                report_data["pdf_path"] = str(pdf_path)
            except ImportError:
                print(
                    "Warning: PDF generation requires weasyprint. Install with: pip install weasyprint"
                )
                print("Continuing with HTML report only.")

        return str(html_path)

    def generate_and_email_report(self, subject: Optional[str] = None) -> bool:
        """Generate report and send via email.

        Args:
            subject: Email subject (default: auto-generated)

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self._validate_email_config():
            print("Error: Email configuration incomplete. Check SMTP settings.")
            return False

        # Generate report
        html_path = self.generate_and_save_report()

        # Read HTML content
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Generate subject if not provided
        if subject is None:
            report_type = self.config.report_type.value.title()
            date_str = datetime.now().strftime("%Y-%m-%d")
            subject = f"UniFi Network {report_type} Report - {date_str}"

        # Send email
        return self._send_email(subject, html_content, html_path)

    def _calculate_start_date(self, end_date: datetime) -> datetime:
        """Calculate start date based on report type."""
        if self.config.report_type == ReportType.DAILY:
            return end_date - timedelta(days=1)
        elif self.config.report_type == ReportType.WEEKLY:
            return end_date - timedelta(weeks=1)
        else:  # MONTHLY
            return end_date - timedelta(days=30)

    def _generate_summary(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate summary section."""
        # Get network summary from analytics
        network_summary = self.analytics.get_network_summary()

        # Get event counts
        events = self.event_repo.get_by_time_range(start_date, end_date)
        event_counts = {}
        for event in events:
            event_type = event.event_type
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        return {
            "total_devices": network_summary["total_hosts"],
            "active_devices": network_summary["active_hosts"],
            "offline_devices": network_summary["offline_hosts"],
            "total_events": len(events),
            "event_breakdown": event_counts,
            "average_health": network_summary.get("avg_health_score", 0) or 0,
        }

    def _generate_device_section(self) -> List[Dict[str, Any]]:
        """Generate device details section."""
        hosts = self.host_repo.get_all()

        device_list = []
        for host in hosts:
            # Get health score
            health_score = self.analytics.get_host_health_score(host.id)

            device_list.append(
                {
                    "id": host.id,
                    "name": host.name or "Unknown",
                    "mac": host.mac,
                    "model": host.model or "Unknown",
                    "status": host.status,
                    "is_online": host.is_online,
                    "health_score": (
                        health_score.overall_score if health_score else None
                    ),
                    "uptime": host.uptime,
                    "last_seen": host.last_seen.isoformat() if host.last_seen else None,
                }
            )

        return device_list

    def _generate_events_section(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate events section."""
        events = self.event_repo.get_by_time_range(start_date, end_date)

        event_list = []
        for event in events:
            event_list.append(
                {
                    "timestamp": event.timestamp.isoformat(),
                    "type": event.event_type,
                    "severity": event.severity,
                    "message": event.message,
                    "host_id": event.host_id,
                }
            )

        return event_list

    def _generate_metrics_section(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate metrics section with statistics."""
        # Get all hosts
        hosts = self.host_repo.get_all()

        # Collect metrics for all hosts
        all_metrics = []
        for host in hosts:
            metrics = self.metric_repo.get_by_time_range(
                host_id=host.id, start_time=start_date, end_time=end_date
            )
            all_metrics.extend(metrics)

        # Group metrics by type
        metric_groups = {}
        for metric in all_metrics:
            metric_name = metric.metric_name
            if metric_name not in metric_groups:
                metric_groups[metric_name] = []
            metric_groups[metric_name].append(metric.metric_value)

        # Calculate statistics for each metric type
        from statistics import mean, median, stdev

        metric_stats = {}
        for metric_name, values in metric_groups.items():
            if values and len(values) >= 2:
                metric_stats[metric_name] = {
                    "count": len(values),
                    "mean": mean(values),
                    "median": median(values),
                    "min": min(values),
                    "max": max(values),
                    "std_dev": stdev(values) if len(values) > 1 else 0.0,
                }

        return {
            "total_data_points": len(all_metrics),
            "metric_types": list(metric_groups.keys()),
            "statistics": metric_stats,
        }

    def _generate_analytics_section(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate analytics section with insights."""
        analytics_data = {}

        # Get all hosts
        hosts = self.host_repo.get_all()

        # Analyze each host
        host_analytics = []
        for host in hosts:
            host_data = {"host_id": host.id, "name": host.name or "Unknown"}

            # Health score
            health = self.analytics.get_host_health_score(host.id)
            if health:
                host_data["health_score"] = health.overall_score
                host_data["health_factors"] = health.factors

            # Trends for key metrics
            trends = {}
            for metric_name in ["cpu_usage", "memory_usage", "temperature"]:
                trend = self.analytics.detect_trend(host.id, metric_name, days=7)
                if trend:
                    trends[metric_name] = {
                        "direction": trend.direction,
                        "slope": trend.slope,
                        "correlation": trend.correlation,
                    }

            if trends:
                host_data["trends"] = trends

            # Anomalies
            anomalies_list = []
            for metric_name in ["cpu_usage", "memory_usage", "temperature"]:
                anomalies = self.analytics.detect_anomalies(
                    host.id, metric_name, days=7
                )
                for anomaly in anomalies:
                    anomalies_list.append(
                        {
                            "metric": metric_name,
                            "value": anomaly.value,
                            "z_score": anomaly.z_score,
                            "timestamp": anomaly.timestamp.isoformat(),
                        }
                    )

            if anomalies_list:
                host_data["anomalies"] = anomalies_list

            host_analytics.append(host_data)

        analytics_data["host_analytics"] = host_analytics

        # Network-wide summary
        network_summary = self.analytics.get_network_summary()
        analytics_data["network_summary"] = {
            "total_hosts": network_summary["total_hosts"],
            "active_hosts": network_summary["active_hosts"],
            "offline_hosts": network_summary["offline_hosts"],
            "avg_health_score": network_summary.get("avg_health_score", 0) or 0,
        }

        return analytics_data

    def _generate_html(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML report from report data."""
        metadata = report_data["metadata"]
        summary = report_data["summary"]

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UniFi Network Report - {metadata['report_type'].title()}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .metadata {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #667eea;
            margin-top: 0;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .summary-card .label {{
            color: #666;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .status-online {{
            color: #28a745;
            font-weight: bold;
        }}
        .status-offline {{
            color: #dc3545;
            font-weight: bold;
        }}
        .health-good {{
            color: #28a745;
        }}
        .health-warning {{
            color: #ffc107;
        }}
        .health-critical {{
            color: #dc3545;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 UniFi Network Report</h1>
        <div class="metadata">
            <strong>Report Type:</strong> {metadata['report_type'].title()} |
            <strong>Period:</strong> {metadata['start_date'][:10]} to {metadata['end_date'][:10]} |
            <strong>Generated:</strong> {metadata['generated_at'][:19]}
        </div>
    </div>

    <div class="section">
        <h2>📊 Executive Summary</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <div class="value">{summary['total_devices']}</div>
                <div class="label">Total Devices</div>
            </div>
            <div class="summary-card">
                <div class="value status-online">{summary['active_devices']}</div>
                <div class="label">Active Devices</div>
            </div>
            <div class="summary-card">
                <div class="value status-offline">{summary['offline_devices']}</div>
                <div class="label">Offline Devices</div>
            </div>
            <div class="summary-card">
                <div class="value">{summary['total_events']}</div>
                <div class="label">Total Events</div>
            </div>
            <div class="summary-card">
                <div class="value">{summary.get('average_health', 0):.1f}</div>
                <div class="label">Avg Health Score</div>
            </div>
        </div>
    </div>
"""

        # Add device details section
        if "devices" in report_data:
            html += self._generate_device_table_html(report_data["devices"])

        # Add events section
        if "events" in report_data:
            html += self._generate_events_table_html(report_data["events"])

        # Add metrics section
        if "metrics" in report_data:
            html += self._generate_metrics_html(report_data["metrics"])

        # Add analytics section
        if "analytics" in report_data:
            html += self._generate_analytics_html(report_data["analytics"])

        html += """
    <div class="footer">
        <p>Generated by UniFi Network Monitoring System</p>
        <p>Made with ❤️ for network management</p>
    </div>
</body>
</html>
"""
        return html

    def _generate_device_table_html(self, devices: List[Dict[str, Any]]) -> str:
        """Generate HTML table for devices."""
        html = """
    <div class="section">
        <h2>🖥️ Device Details</h2>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Model</th>
                    <th>MAC Address</th>
                    <th>Status</th>
                    <th>Health Score</th>
                    <th>Last Seen</th>
                </tr>
            </thead>
            <tbody>
"""
        for device in devices:
            status_class = "status-online" if device["is_online"] else "status-offline"
            status_text = "🟢 Online" if device["is_online"] else "🔴 Offline"

            health_score = device.get("health_score", 0) or 0
            if health_score >= 80:
                health_class = "health-good"
            elif health_score >= 60:
                health_class = "health-warning"
            else:
                health_class = "health-critical"

            last_seen = device.get("last_seen", "Never")
            if last_seen != "Never":
                last_seen = last_seen[:19]

            html += f"""
                <tr>
                    <td>{device['name']}</td>
                    <td>{device['model']}</td>
                    <td><code>{device['mac']}</code></td>
                    <td class="{status_class}">{status_text}</td>
                    <td class="{health_class}">{health_score:.0f}/100</td>
                    <td>{last_seen}</td>
                </tr>
"""

        html += """
            </tbody>
        </table>
    </div>
"""
        return html

    def _generate_events_table_html(self, events: List[Dict[str, Any]]) -> str:
        """Generate HTML table for events."""
        if not events:
            return """
    <div class="section">
        <h2>📅 Recent Events</h2>
        <p>No events recorded during this period.</p>
    </div>
"""

        html = """
    <div class="section">
        <h2>📅 Recent Events</h2>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Type</th>
                    <th>Severity</th>
                    <th>Message</th>
                </tr>
            </thead>
            <tbody>
"""
        # Show only the most recent 50 events
        for event in events[:50]:
            timestamp = event["timestamp"][:19]
            html += f"""
                <tr>
                    <td>{timestamp}</td>
                    <td>{event['type']}</td>
                    <td>{event['severity']}</td>
                    <td>{event['message']}</td>
                </tr>
"""

        html += """
            </tbody>
        </table>
    </div>
"""
        return html

    def _generate_metrics_html(self, metrics: Dict[str, Any]) -> str:
        """Generate HTML for metrics section."""
        stats = metrics.get("statistics", {})

        if not stats:
            return """
    <div class="section">
        <h2>📈 Metrics Summary</h2>
        <p>No metrics data available for this period.</p>
    </div>
"""

        html = f"""
    <div class="section">
        <h2>📈 Metrics Summary</h2>
        <p><strong>Total Data Points:</strong> {metrics['total_data_points']}</p>
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Count</th>
                    <th>Mean</th>
                    <th>Median</th>
                    <th>Min</th>
                    <th>Max</th>
                    <th>Std Dev</th>
                </tr>
            </thead>
            <tbody>
"""

        for metric_name, stat in stats.items():
            html += f"""
                <tr>
                    <td>{metric_name}</td>
                    <td>{stat['count']}</td>
                    <td>{stat['mean']:.2f}</td>
                    <td>{stat['median']:.2f}</td>
                    <td>{stat['min']:.2f}</td>
                    <td>{stat['max']:.2f}</td>
                    <td>{stat['std_dev']:.2f}</td>
                </tr>
"""

        html += """
            </tbody>
        </table>
    </div>
"""
        return html

    def _generate_analytics_html(self, analytics: Dict[str, Any]) -> str:
        """Generate HTML for analytics section."""
        html = """
    <div class="section">
        <h2>🔍 Analytics & Insights</h2>
"""

        # Network summary
        summary = analytics.get("network_summary", {})
        html += f"""
        <h3>Network Overview</h3>
        <div class="summary-grid">
            <div class="summary-card">
                <div class="value">{summary.get('total_hosts', 0)}</div>
                <div class="label">Total Hosts</div>
            </div>
            <div class="summary-card">
                <div class="value">{summary.get('active_hosts', 0)}</div>
                <div class="label">Active Hosts</div>
            </div>
            <div class="summary-card">
                <div class="value">{summary.get('avg_health_score', 0):.1f}</div>
                <div class="label">Avg Health</div>
            </div>
        </div>
"""

        # Host analytics
        host_analytics = analytics.get("host_analytics", [])
        if host_analytics:
            html += """
        <h3>Host Analysis</h3>
        <table>
            <thead>
                <tr>
                    <th>Host</th>
                    <th>Health Score</th>
                    <th>Trends</th>
                    <th>Anomalies</th>
                </tr>
            </thead>
            <tbody>
"""
            for host in host_analytics:
                health = host.get("health_score", 0) or 0
                trends = host.get("trends", {})
                anomalies = host.get("anomalies", [])

                trend_text = ", ".join(
                    [f"{k}: {v['direction']}" for k, v in trends.items()]
                )
                if not trend_text:
                    trend_text = "—"

                anomaly_count = len(anomalies)

                html += f"""
                <tr>
                    <td>{host['name']}</td>
                    <td>{health:.0f}/100</td>
                    <td>{trend_text}</td>
                    <td>{anomaly_count} detected</td>
                </tr>
"""

            html += """
            </tbody>
        </table>
"""

        html += """
    </div>
"""
        return html

    def _generate_pdf(self, html_content: str, filename: str) -> Path:
        """Generate PDF from HTML content.

        Args:
            html_content: HTML content to convert
            filename: Base filename (without extension)

        Returns:
            Path to generated PDF file

        Raises:
            ImportError: If weasyprint is not installed
        """
        from weasyprint import HTML

        pdf_path = Path(self.config.pdf_output_dir) / f"{filename}.pdf"
        HTML(string=html_content).write_pdf(pdf_path)

        return pdf_path

    def _validate_email_config(self) -> bool:
        """Validate email configuration."""
        return all(
            [
                self.config.smtp_host,
                self.config.smtp_username,
                self.config.smtp_password,
                self.config.email_from,
                self.config.email_to,
            ]
        )

    def _send_email(
        self, subject: str, html_content: str, attachment_path: str
    ) -> bool:
        """Send email with report.

        Args:
            subject: Email subject
            html_content: HTML email body
            attachment_path: Path to HTML file to attach

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.config.email_from
            msg["To"] = ", ".join(self.config.email_to)
            msg["Subject"] = subject

            # Add HTML body
            msg.attach(MIMEText(html_content, "html"))

            # Attach HTML file
            with open(attachment_path, "rb") as f:
                attachment = MIMEApplication(f.read(), _subtype="html")
                attachment.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=Path(attachment_path).name,
                )
                msg.attach(attachment)

            # Send email
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_username, self.config.smtp_password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False
