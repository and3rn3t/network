"""
Command-line interface for UniFi Network Alert System.

Provides commands for managing alert rules, viewing alerts, managing notification
channels, and testing the alert system.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from alerts import AlertManager, AlertRule, NotificationChannel
from src.alerts.notifiers import EmailNotifier, WebhookNotifier
from src.database.database import Database


class AlertCLI:
    """Command-line interface for alert system."""

    def __init__(self, db_path: str = "data/unifi_network.db"):
        """
        Initialize the CLI.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.db = Database(db_path)
        self.db.initialize()
        self.db.initialize_alerts()

    def _get_manager(self) -> AlertManager:
        """Get AlertManager instance."""
        return AlertManager(self.db)

    def _format_timestamp(self, ts: Optional[str]) -> str:
        """Format timestamp for display."""
        if not ts:
            return "N/A"
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return ts

    def _format_severity(self, severity: str) -> str:
        """Format severity with color indicators."""
        indicators = {
            "info": "ℹ️ ",
            "warning": "⚠️ ",
            "critical": "🔴",
        }
        return f"{indicators.get(severity, '')} {severity.upper()}"

    # Rule Management Commands

    def rule_create(self, args: argparse.Namespace) -> int:
        """Create a new alert rule."""
        try:
            # Parse notification channels (comma-separated)
            channels = [ch.strip() for ch in args.channels.split(",")]

            # Create rule object
            rule = AlertRule(
                name=args.name,
                rule_type=args.type,
                metric_name=args.metric,
                condition=args.condition,
                threshold=args.threshold,
                severity=args.severity,
                notification_channels=channels,
                enabled=not args.disabled,
                cooldown_minutes=args.cooldown,
                description=args.description,
            )

            # Filter by host if specified
            if args.host:
                rule.host_id = args.host

            # Create rule
            with self._get_manager() as manager:
                created = manager.create_rule(rule)

            print(f"✅ Created rule: {created.name} (ID: {created.id})")
            print(f"   Type: {created.rule_type}")
            print(
                f"   Condition: {created.metric_name} {created.condition} {created.threshold}"
            )
            print(f"   Severity: {self._format_severity(created.severity)}")
            print(f"   Channels: {', '.join(created.notification_channels)}")
            print(f"   Enabled: {'Yes' if created.enabled else 'No'}")

            return 0

        except Exception as e:
            print(f"❌ Error creating rule: {e}", file=sys.stderr)
            return 1

    def rule_list(self, args: argparse.Namespace) -> int:
        """List alert rules."""
        try:
            with self._get_manager() as manager:
                rules = manager.list_rules(enabled_only=args.enabled_only)

            if not rules:
                print("No rules found.")
                return 0

            print(
                f"\n{'ID':<5} {'Name':<30} {'Type':<12} {'Condition':<25} {'Severity':<10} {'Enabled':<8}"
            )
            print("-" * 105)

            for rule in rules:
                condition_str = f"{rule.metric_name} {rule.condition} {rule.threshold}"
                enabled_str = "✓" if rule.enabled else "✗"
                print(
                    f"{rule.id:<5} {rule.name[:29]:<30} {rule.rule_type:<12} "
                    f"{condition_str[:24]:<25} {rule.severity:<10} {enabled_str:<8}"
                )

            print(f"\nTotal: {len(rules)} rule(s)")

            return 0

        except Exception as e:
            print(f"❌ Error listing rules: {e}", file=sys.stderr)
            return 1

    def rule_show(self, args: argparse.Namespace) -> int:
        """Show detailed information about a rule."""
        try:
            with self._get_manager() as manager:
                rule = manager.get_rule(args.rule_id)

            if not rule:
                print(f"❌ Rule {args.rule_id} not found", file=sys.stderr)
                return 1

            print(f"\n📋 Rule Details")
            print(f"{'=' * 60}")
            print(f"ID:                  {rule.id}")
            print(f"Name:                {rule.name}")
            print(f"Description:         {rule.description or 'N/A'}")
            print(f"Type:                {rule.rule_type}")
            print(f"Metric:              {rule.metric_name}")
            print(f"Condition:           {rule.condition} {rule.threshold}")
            print(f"Severity:            {self._format_severity(rule.severity)}")
            print(f"Enabled:             {'Yes' if rule.enabled else 'No'}")
            print(f"Cooldown:            {rule.cooldown_minutes} minutes")
            print(f"Channels:            {', '.join(rule.notification_channels)}")
            print(f"Host Filter:         {rule.host_id or 'All hosts'}")
            print(f"Created:             {self._format_timestamp(rule.created_at)}")
            print(f"Updated:             {self._format_timestamp(rule.updated_at)}")

            # last_triggered_at is not in model, would need to query separately
            # print(f"Last Triggered:      {self._format_timestamp(rule.last_triggered_at)}")

            return 0

        except Exception as e:
            print(f"❌ Error showing rule: {e}", file=sys.stderr)
            return 1

    def rule_enable(self, args: argparse.Namespace) -> int:
        """Enable an alert rule."""
        try:
            with self._get_manager() as manager:
                success = manager.enable_rule(args.rule_id)

            if success:
                print(f"✅ Enabled rule {args.rule_id}")
                return 0
            else:
                print(f"❌ Failed to enable rule {args.rule_id}", file=sys.stderr)
                return 1

        except Exception as e:
            print(f"❌ Error enabling rule: {e}", file=sys.stderr)
            return 1

    def rule_disable(self, args: argparse.Namespace) -> int:
        """Disable an alert rule."""
        try:
            with self._get_manager() as manager:
                success = manager.disable_rule(args.rule_id)

            if success:
                print(f"✅ Disabled rule {args.rule_id}")
                return 0
            else:
                print(f"❌ Failed to disable rule {args.rule_id}", file=sys.stderr)
                return 1

        except Exception as e:
            print(f"❌ Error disabling rule: {e}", file=sys.stderr)
            return 1

    def rule_delete(self, args: argparse.Namespace) -> int:
        """Delete an alert rule."""
        try:
            # Confirm deletion unless --force is used
            if not args.force:
                response = input(f"Delete rule {args.rule_id}? [y/N]: ")
                if response.lower() != "y":
                    print("Cancelled.")
                    return 0

            with self._get_manager() as manager:
                success = manager.delete_rule(args.rule_id)

            if success:
                print(f"✅ Deleted rule {args.rule_id}")
                return 0
            else:
                print(f"❌ Failed to delete rule {args.rule_id}", file=sys.stderr)
                return 1

        except Exception as e:
            print(f"❌ Error deleting rule: {e}", file=sys.stderr)
            return 1

    # Alert Management Commands

    def alert_list(self, args: argparse.Namespace) -> int:
        """List alerts."""
        try:
            with self._get_manager() as manager:
                if args.recent:
                    alerts = manager.list_recent_alerts(hours=args.recent)
                else:
                    alerts = manager.list_active_alerts(
                        severity=args.severity, host_id=args.host
                    )

            if not alerts:
                print("No alerts found.")
                return 0

            print(
                f"\n{'ID':<5} {'Rule':<25} {'Severity':<10} {'Host':<20} "
                f"{'Value':<8} {'Triggered':<20}"
            )
            print("-" * 105)

            for alert in alerts:
                triggered = self._format_timestamp(alert.triggered_at)
                host = (alert.host_id or "N/A")[:19]
                rule_name = (alert.rule_name or f"Rule {alert.rule_id}")[:24]
                value = f"{alert.current_value:.1f}" if alert.current_value else "N/A"

                print(
                    f"{alert.id:<5} {rule_name:<25} {alert.severity:<10} "
                    f"{host:<20} {value:<8} {triggered:<20}"
                )

            print(f"\nTotal: {len(alerts)} alert(s)")

            return 0

        except Exception as e:
            print(f"❌ Error listing alerts: {e}", file=sys.stderr)
            return 1

    def alert_show(self, args: argparse.Namespace) -> int:
        """Show detailed information about an alert."""
        try:
            with self._get_manager() as manager:
                alert = manager.get_alert(args.alert_id)

            if not alert:
                print(f"❌ Alert {args.alert_id} not found", file=sys.stderr)
                return 1

            print(f"\n🚨 Alert Details")
            print(f"{'=' * 60}")
            print(f"ID:                  {alert.id}")
            print(f"Rule ID:             {alert.rule_id}")
            print(f"Rule Name:           {alert.rule_name or 'N/A'}")
            print(f"Severity:            {self._format_severity(alert.severity)}")
            print(f"Host ID:             {alert.host_id or 'N/A'}")
            print(f"Current Value:       {alert.current_value}")
            print(f"Threshold:           {alert.threshold_value}")
            print(f"Message:             {alert.message}")
            print(f"Triggered:           {self._format_timestamp(alert.triggered_at)}")
            print(
                f"Acknowledged:        {self._format_timestamp(alert.acknowledged_at)}"
            )
            print(f"Acknowledged By:     {alert.acknowledged_by or 'N/A'}")
            print(f"Resolved:            {self._format_timestamp(alert.resolved_at)}")

            if alert.notification_status:
                print(f"\n📬 Notification Status:")
                for channel, status in alert.notification_status.items():
                    status_icon = "✓" if status == "sent" else "✗"
                    print(f"  {status_icon} {channel}: {status}")

            return 0

        except Exception as e:
            print(f"❌ Error showing alert: {e}", file=sys.stderr)
            return 1

    def alert_acknowledge(self, args: argparse.Namespace) -> int:
        """Acknowledge an alert."""
        try:
            with self._get_manager() as manager:
                success = manager.acknowledge_alert(
                    args.alert_id, acknowledged_by=args.by or "cli-user"
                )

            if success:
                print(f"✅ Acknowledged alert {args.alert_id}")
                return 0
            else:
                print(
                    f"❌ Failed to acknowledge alert {args.alert_id}", file=sys.stderr
                )
                return 1

        except Exception as e:
            print(f"❌ Error acknowledging alert: {e}", file=sys.stderr)
            return 1

    def alert_resolve(self, args: argparse.Namespace) -> int:
        """Resolve an alert."""
        try:
            with self._get_manager() as manager:
                success = manager.resolve_alert(args.alert_id)

            if success:
                print(f"✅ Resolved alert {args.alert_id}")
                return 0
            else:
                print(f"❌ Failed to resolve alert {args.alert_id}", file=sys.stderr)
                return 1

        except Exception as e:
            print(f"❌ Error resolving alert: {e}", file=sys.stderr)
            return 1

    def alert_stats(self, args: argparse.Namespace) -> int:
        """Show alert statistics."""
        try:
            with self._get_manager() as manager:
                stats = manager.get_alert_statistics(days=args.days)

            print(f"\n📊 Alert Statistics (Last {args.days} days)")
            print(f"{'=' * 60}")
            print(f"ℹ️  Info:             {stats.get('info', 0)}")
            print(f"⚠️  Warning:          {stats.get('warning', 0)}")
            print(f"🔴 Critical:         {stats.get('critical', 0)}")
            print(f"─" * 60)
            print(f"Total:              {stats.get('total', 0)}")

            return 0

        except Exception as e:
            print(f"❌ Error getting statistics: {e}", file=sys.stderr)
            return 1

    # Channel Management Commands

    def channel_create(self, args: argparse.Namespace) -> int:
        """Create a notification channel."""
        try:
            # Load config from file
            config_path = Path(args.config)
            if not config_path.exists():
                print(f"❌ Config file not found: {args.config}", file=sys.stderr)
                return 1

            with open(config_path, "r") as f:
                config = json.load(f)

            # Create channel
            channel = NotificationChannel(
                id=args.id,
                name=args.name,
                channel_type=args.type,
                config=config,
                enabled=not args.disabled,
            )

            with self._get_manager() as manager:
                created = manager.create_channel(channel)

            print(f"✅ Created channel: {created.name} (ID: {created.id})")
            print(f"   Type: {created.channel_type}")
            print(f"   Enabled: {'Yes' if created.enabled else 'No'}")

            return 0

        except Exception as e:
            print(f"❌ Error creating channel: {e}", file=sys.stderr)
            return 1

    def channel_list(self, args: argparse.Namespace) -> int:
        """List notification channels."""
        try:
            with self._get_manager() as manager:
                channels = manager.list_channels(
                    channel_type=args.type, enabled_only=args.enabled_only
                )

            if not channels:
                print("No channels found.")
                return 0

            print(f"\n{'ID':<20} {'Name':<30} {'Type':<12} {'Enabled':<8}")
            print("-" * 75)

            for channel in channels:
                enabled_str = "✓" if channel.enabled else "✗"
                print(
                    f"{channel.id[:19]:<20} {channel.name[:29]:<30} "
                    f"{channel.channel_type:<12} {enabled_str:<8}"
                )

            print(f"\nTotal: {len(channels)} channel(s)")

            return 0

        except Exception as e:
            print(f"❌ Error listing channels: {e}", file=sys.stderr)
            return 1

    def channel_enable(self, args: argparse.Namespace) -> int:
        """Enable a notification channel."""
        try:
            with self._get_manager() as manager:
                success = manager.enable_channel(args.channel_id)

            if success:
                print(f"✅ Enabled channel {args.channel_id}")
                return 0
            else:
                print(f"❌ Failed to enable channel {args.channel_id}", file=sys.stderr)
                return 1

        except Exception as e:
            print(f"❌ Error enabling channel: {e}", file=sys.stderr)
            return 1

    def channel_disable(self, args: argparse.Namespace) -> int:
        """Disable a notification channel."""
        try:
            with self._get_manager() as manager:
                success = manager.disable_channel(args.channel_id)

            if success:
                print(f"✅ Disabled channel {args.channel_id}")
                return 0
            else:
                print(
                    f"❌ Failed to disable channel {args.channel_id}", file=sys.stderr
                )
                return 1

        except Exception as e:
            print(f"❌ Error disabling channel: {e}", file=sys.stderr)
            return 1

    # Mute Management Commands

    def mute_create(self, args: argparse.Namespace) -> int:
        """Mute an alert rule."""
        try:
            with self._get_manager() as manager:
                mute = manager.mute_rule(
                    rule_id=args.rule_id,
                    muted_by=args.by or "cli-user",
                    duration_minutes=args.duration,
                    host_id=args.host,
                    reason=args.reason,
                )

            if mute:
                duration_str = (
                    f"{args.duration} minutes" if args.duration else "indefinitely"
                )
                host_str = f" for host {args.host}" if args.host else ""
                print(f"✅ Muted rule {args.rule_id}{host_str} for {duration_str}")
                return 0
            else:
                print(f"❌ Failed to mute rule {args.rule_id}", file=sys.stderr)
                return 1

        except Exception as e:
            print(f"❌ Error muting rule: {e}", file=sys.stderr)
            return 1

    def mute_list(self, args: argparse.Namespace) -> int:
        """List active mutes."""
        try:
            with self._get_manager() as manager:
                mutes = manager.list_active_mutes()

            if not mutes:
                print("No active mutes.")
                return 0

            print(f"\n{'Rule ID':<8} {'Host':<20} {'Expires':<20} {'Reason':<30}")
            print("-" * 85)

            for mute in mutes:
                host = (mute.host_id or "All")[:19]
                expires = (
                    self._format_timestamp(mute.expires_at)
                    if mute.expires_at
                    else "Never"
                )
                reason = (mute.reason or "")[:29]
                print(f"{mute.rule_id:<8} {host:<20} {expires:<20} {reason:<30}")

            print(f"\nTotal: {len(mutes)} active mute(s)")

            return 0

        except Exception as e:
            print(f"❌ Error listing mutes: {e}", file=sys.stderr)
            return 1

    def mute_remove(self, args: argparse.Namespace) -> int:
        """Remove a mute."""
        try:
            with self._get_manager() as manager:
                success = manager.unmute_rule(rule_id=args.rule_id, host_id=args.host)

            if success:
                host_str = f" for host {args.host}" if args.host else ""
                print(f"✅ Unmuted rule {args.rule_id}{host_str}")
                return 0
            else:
                print(f"❌ Failed to unmute rule {args.rule_id}", file=sys.stderr)
                return 1

        except Exception as e:
            print(f"❌ Error unmuting rule: {e}", file=sys.stderr)
            return 1

    # Evaluation Commands

    def evaluate(self, args: argparse.Namespace) -> int:
        """Evaluate all alert rules."""
        try:
            with self._get_manager() as manager:
                # Register notifiers if email config provided
                if args.email_config:
                    config_path = Path(args.email_config)
                    if config_path.exists():
                        with open(config_path, "r") as f:
                            email_config = json.load(f)
                        manager.register_notifier("email", EmailNotifier(email_config))

                # Evaluate rules
                alerts = manager.evaluate_rules()

            print(f"✅ Evaluation complete: {len(alerts)} alert(s) triggered")

            if alerts and args.verbose:
                print("\nTriggered Alerts:")
                for alert in alerts:
                    print(f"  {self._format_severity(alert.severity)} {alert.message}")

            return 0

        except Exception as e:
            print(f"❌ Error evaluating rules: {e}", file=sys.stderr)
            return 1


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="UniFi Network Alert System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a threshold rule
  %(prog)s rule create --name "High CPU" --type threshold --metric cpu_usage \\
      --condition gt --threshold 80 --severity warning --channels email-1

  # List active alerts
  %(prog)s alert list

  # Acknowledge an alert
  %(prog)s alert acknowledge 123 --by admin

  # Mute a rule for 1 hour
  %(prog)s mute create 5 --duration 60 --reason "Maintenance"

  # Evaluate rules
  %(prog)s evaluate --email-config email_config.json
""",
    )

    parser.add_argument(
        "--db",
        default="data/unifi_network.db",
        help="Path to database (default: data/unifi_network.db)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Rule commands
    rule_parser = subparsers.add_parser("rule", help="Manage alert rules")
    rule_subparsers = rule_parser.add_subparsers(dest="subcommand")

    # rule create
    rule_create = rule_subparsers.add_parser("create", help="Create a new rule")
    rule_create.add_argument("--name", required=True, help="Rule name")
    rule_create.add_argument(
        "--type",
        required=True,
        choices=["threshold", "status_change"],
        help="Rule type",
    )
    rule_create.add_argument("--metric", required=True, help="Metric name")
    rule_create.add_argument(
        "--condition",
        required=True,
        choices=["gt", "gte", "lt", "lte", "eq", "ne"],
        help="Condition",
    )
    rule_create.add_argument(
        "--threshold", type=float, required=True, help="Threshold value"
    )
    rule_create.add_argument(
        "--severity",
        required=True,
        choices=["info", "warning", "critical"],
        help="Alert severity",
    )
    rule_create.add_argument(
        "--channels", required=True, help="Notification channels (comma-separated)"
    )
    rule_create.add_argument("--description", help="Rule description")
    rule_create.add_argument("--host", help="Host filter (MAC address)")
    rule_create.add_argument(
        "--cooldown", type=int, default=30, help="Cooldown minutes (default: 30)"
    )
    rule_create.add_argument(
        "--disabled", action="store_true", help="Create rule disabled"
    )

    # rule list
    rule_list = rule_subparsers.add_parser("list", help="List rules")
    rule_list.add_argument(
        "--enabled-only", action="store_true", help="Show only enabled rules"
    )

    # rule show
    rule_show = rule_subparsers.add_parser("show", help="Show rule details")
    rule_show.add_argument("rule_id", type=int, help="Rule ID")

    # rule enable
    rule_enable = rule_subparsers.add_parser("enable", help="Enable a rule")
    rule_enable.add_argument("rule_id", type=int, help="Rule ID")

    # rule disable
    rule_disable = rule_subparsers.add_parser("disable", help="Disable a rule")
    rule_disable.add_argument("rule_id", type=int, help="Rule ID")

    # rule delete
    rule_delete = rule_subparsers.add_parser("delete", help="Delete a rule")
    rule_delete.add_argument("rule_id", type=int, help="Rule ID")
    rule_delete.add_argument("--force", action="store_true", help="Skip confirmation")

    # Alert commands
    alert_parser = subparsers.add_parser("alert", help="Manage alerts")
    alert_subparsers = alert_parser.add_subparsers(dest="subcommand")

    # alert list
    alert_list = alert_subparsers.add_parser("list", help="List alerts")
    alert_list.add_argument(
        "--severity", choices=["info", "warning", "critical"], help="Filter by severity"
    )
    alert_list.add_argument("--host", help="Filter by host MAC address")
    alert_list.add_argument(
        "--recent", type=int, metavar="HOURS", help="Show recent alerts (hours)"
    )

    # alert show
    alert_show = alert_subparsers.add_parser("show", help="Show alert details")
    alert_show.add_argument("alert_id", type=int, help="Alert ID")

    # alert acknowledge
    alert_ack = alert_subparsers.add_parser("acknowledge", help="Acknowledge an alert")
    alert_ack.add_argument("alert_id", type=int, help="Alert ID")
    alert_ack.add_argument("--by", help="Acknowledged by (default: cli-user)")

    # alert resolve
    alert_resolve = alert_subparsers.add_parser("resolve", help="Resolve an alert")
    alert_resolve.add_argument("alert_id", type=int, help="Alert ID")

    # alert stats
    alert_stats = alert_subparsers.add_parser("stats", help="Show alert statistics")
    alert_stats.add_argument(
        "--days", type=int, default=7, help="Days to analyze (default: 7)"
    )

    # Channel commands
    channel_parser = subparsers.add_parser(
        "channel", help="Manage notification channels"
    )
    channel_subparsers = channel_parser.add_subparsers(dest="subcommand")

    # channel create
    channel_create = channel_subparsers.add_parser("create", help="Create a channel")
    channel_create.add_argument("--id", required=True, help="Channel ID")
    channel_create.add_argument("--name", required=True, help="Channel name")
    channel_create.add_argument(
        "--type",
        required=True,
        choices=["email", "slack", "discord", "webhook"],
        help="Channel type",
    )
    channel_create.add_argument(
        "--config", required=True, help="Config file path (JSON)"
    )
    channel_create.add_argument(
        "--disabled", action="store_true", help="Create channel disabled"
    )

    # channel list
    channel_list = channel_subparsers.add_parser("list", help="List channels")
    channel_list.add_argument(
        "--type",
        choices=["email", "slack", "discord", "webhook"],
        help="Filter by type",
    )
    channel_list.add_argument(
        "--enabled-only", action="store_true", help="Show only enabled channels"
    )

    # channel enable
    channel_enable = channel_subparsers.add_parser("enable", help="Enable a channel")
    channel_enable.add_argument("channel_id", help="Channel ID")

    # channel disable
    channel_disable = channel_subparsers.add_parser("disable", help="Disable a channel")
    channel_disable.add_argument("channel_id", help="Channel ID")

    # Mute commands
    mute_parser = subparsers.add_parser("mute", help="Manage rule mutes")
    mute_subparsers = mute_parser.add_subparsers(dest="subcommand")

    # mute create
    mute_create = mute_subparsers.add_parser("create", help="Mute a rule")
    mute_create.add_argument("rule_id", type=int, help="Rule ID")
    mute_create.add_argument(
        "--duration", type=int, help="Duration in minutes (omit for indefinite)"
    )
    mute_create.add_argument("--host", help="Mute for specific host only")
    mute_create.add_argument("--reason", help="Reason for muting")
    mute_create.add_argument("--by", help="Muted by (default: cli-user)")

    # mute list
    mute_list = mute_subparsers.add_parser("list", help="List active mutes")

    # mute remove
    mute_remove = mute_subparsers.add_parser("remove", help="Remove a mute")
    mute_remove.add_argument("rule_id", type=int, help="Rule ID")
    mute_remove.add_argument("--host", help="Unmute for specific host only")

    # Evaluate command
    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate all alert rules")
    evaluate_parser.add_argument("--email-config", help="Email config file (JSON)")
    evaluate_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show triggered alerts"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize CLI
    cli = AlertCLI(db_path=args.db)

    # Route to appropriate handler
    try:
        if args.command == "rule":
            if args.subcommand == "create":
                return cli.rule_create(args)
            elif args.subcommand == "list":
                return cli.rule_list(args)
            elif args.subcommand == "show":
                return cli.rule_show(args)
            elif args.subcommand == "enable":
                return cli.rule_enable(args)
            elif args.subcommand == "disable":
                return cli.rule_disable(args)
            elif args.subcommand == "delete":
                return cli.rule_delete(args)
            else:
                rule_parser.print_help()
                return 1

        elif args.command == "alert":
            if args.subcommand == "list":
                return cli.alert_list(args)
            elif args.subcommand == "show":
                return cli.alert_show(args)
            elif args.subcommand == "acknowledge":
                return cli.alert_acknowledge(args)
            elif args.subcommand == "resolve":
                return cli.alert_resolve(args)
            elif args.subcommand == "stats":
                return cli.alert_stats(args)
            else:
                alert_parser.print_help()
                return 1

        elif args.command == "channel":
            if args.subcommand == "create":
                return cli.channel_create(args)
            elif args.subcommand == "list":
                return cli.channel_list(args)
            elif args.subcommand == "enable":
                return cli.channel_enable(args)
            elif args.subcommand == "disable":
                return cli.channel_disable(args)
            else:
                channel_parser.print_help()
                return 1

        elif args.command == "mute":
            if args.subcommand == "create":
                return cli.mute_create(args)
            elif args.subcommand == "list":
                return cli.mute_list(args)
            elif args.subcommand == "remove":
                return cli.mute_remove(args)
            else:
                mute_parser.print_help()
                return 1

        elif args.command == "evaluate":
            return cli.evaluate(args)

        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        if args.command == "evaluate" and hasattr(args, "verbose") and args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
