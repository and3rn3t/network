"""
Alert management system - High-level API for alert operations.

Coordinates AlertEngine and NotificationManager to provide a unified
interface for managing the complete alert lifecycle.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.alerts.alert_engine import AlertEngine
from src.alerts.models import Alert, AlertMute, AlertRule, NotificationChannel
from src.alerts.notification_manager import NotificationManager
from src.alerts.notifiers import BaseNotifier, EmailNotifier, WebhookNotifier
from src.database.database import Database
from src.database.repositories.alert_mute_repository import AlertMuteRepository
from src.database.repositories.alert_repository import AlertRepository
from src.database.repositories.alert_rule_repository import AlertRuleRepository
from src.database.repositories.notification_channel_repository import (
    NotificationChannelRepository,
)

logger = logging.getLogger(__name__)


class AlertManager:
    """
    High-level alert management system.

    Provides a unified API for:
    - Rule management (CRUD)
    - Alert evaluation and triggering
    - Notification delivery
    - Alert lifecycle (acknowledge, resolve)
    - Muting/unmuting
    """

    def __init__(self, db: Database):
        """
        Initialize alert manager.

        Args:
            db: Database instance
        """
        self.db = db

        # Initialize repositories
        self.rule_repo = AlertRuleRepository(db)
        self.alert_repo = AlertRepository(db)
        self.channel_repo = NotificationChannelRepository(db)
        self.mute_repo = AlertMuteRepository(db)

        # Initialize alert engine
        self.engine = AlertEngine(db)

        # Initialize notification manager
        self.notification_manager = NotificationManager(
            alert_repo=self.alert_repo,
            channel_repo=self.channel_repo,
        )

        logger.info("AlertManager initialized")

    def register_notifier(self, channel_type: str, notifier: BaseNotifier) -> None:
        """
        Register a notification channel implementation.

        Args:
            channel_type: Type of channel (email, slack, discord, etc.)
            notifier: Notifier instance
        """
        self.notification_manager.register_notifier(channel_type, notifier)

    def setup_default_notifiers(
        self,
        email_config: Optional[Dict] = None,
        webhook_configs: Optional[List[Dict]] = None,
    ) -> None:
        """
        Setup default notifiers with provided configurations.

        Args:
            email_config: Email configuration dict
            webhook_configs: List of webhook configuration dicts
        """
        if email_config:
            email_notifier = EmailNotifier(email_config)
            self.register_notifier("email", email_notifier)
            logger.info("Registered email notifier")

        if webhook_configs:
            for config in webhook_configs:
                webhook_notifier = WebhookNotifier(config)
                platform = config.get("platform", "generic")
                self.register_notifier(f"webhook_{platform}", webhook_notifier)
                logger.info(f"Registered webhook notifier: {platform}")

    # ==================== Rule Management ====================

    def create_rule(self, rule: AlertRule) -> AlertRule:
        """
        Create a new alert rule.

        Args:
            rule: AlertRule to create

        Returns:
            Created rule with ID assigned
        """
        created_rule = self.rule_repo.create(rule)
        logger.info(f"Created alert rule: {created_rule.name} (ID: {created_rule.id})")
        return created_rule

    def create_alert_rule(self, **kwargs) -> AlertRule:
        """
        Create a new alert rule (convenience method).

        Accepts individual parameters and creates an AlertRule object.
        This is a convenience wrapper around create_rule().

        Supports both shorthand (`>`, `<`, `=`, etc.) and
        full condition names (`gt`, `lt`, `eq`, etc.).

        Args:
            **kwargs: AlertRule parameters

        Returns:
            Created rule with ID assigned
        """
        # Map shorthand conditions to full names
        condition_map = {
            ">": "gt",
            "<": "lt",
            "=": "eq",
            "==": "eq",
            "!=": "ne",
            ">=": "gte",
            "<=": "lte",
        }

        if "condition" in kwargs:
            condition = kwargs["condition"]
            kwargs["condition"] = condition_map.get(condition, condition)

        # Provide default severity if not specified
        if "severity" not in kwargs:
            kwargs["severity"] = "warning"

        rule = AlertRule(**kwargs)
        return self.create_rule(rule)

    def get_rule(self, rule_id: int) -> Optional[AlertRule]:
        """
        Get alert rule by ID.

        Args:
            rule_id: Rule ID

        Returns:
            AlertRule if found, None otherwise
        """
        return self.rule_repo.get_by_id(rule_id)

    def list_rules(
        self,
        enabled_only: bool = False,
        host_id: Optional[str] = None,
    ) -> List[AlertRule]:
        """
        List alert rules.

        Args:
            enabled_only: Only return enabled rules
            host_id: Filter by host ID

        Returns:
            List of alert rules
        """
        if enabled_only:
            return self.rule_repo.get_all_enabled()
        elif host_id:
            return self.rule_repo.get_by_host(host_id)
        else:
            return self.rule_repo.get_all()

    def update_rule(self, rule: AlertRule) -> bool:
        """
        Update an existing alert rule.

        Args:
            rule: AlertRule with updated values

        Returns:
            True if updated, False if not found
        """
        success = self.rule_repo.update(rule)
        if success:
            logger.info(f"Updated alert rule: {rule.name} (ID: {rule.id})")
        return success

    def enable_rule(self, rule_id: int) -> bool:
        """
        Enable an alert rule.

        Args:
            rule_id: Rule ID

        Returns:
            True if enabled, False if not found
        """
        success = self.rule_repo.enable(rule_id)
        if success:
            logger.info(f"Enabled alert rule ID: {rule_id}")
        return success

    def disable_rule(self, rule_id: int) -> bool:
        """
        Disable an alert rule.

        Args:
            rule_id: Rule ID

        Returns:
            True if disabled, False if not found
        """
        success = self.rule_repo.disable(rule_id)
        if success:
            logger.info(f"Disabled alert rule ID: {rule_id}")
        return success

    def delete_rule(self, rule_id: int) -> bool:
        """
        Delete an alert rule.

        Args:
            rule_id: Rule ID

        Returns:
            True if deleted, False if not found
        """
        success = self.rule_repo.delete(rule_id)
        if success:
            logger.info(f"Deleted alert rule ID: {rule_id}")
        return success

    # ==================== Alert Evaluation ====================

    def evaluate_rules(self) -> List[Alert]:
        """
        Evaluate all enabled rules against current metrics.

        Returns:
            List of triggered alerts
        """
        alerts = self.engine.evaluate_all_rules()

        # Send notifications for new alerts
        for alert in alerts:
            if alert.id:  # Only for successfully created alerts
                self._send_alert_notifications(alert)

        return alerts

    def _send_alert_notifications(self, alert: Alert) -> None:
        """
        Send notifications for an alert.

        Args:
            alert: Alert to send notifications for
        """
        # Get the rule to find notification channels
        rule = self.rule_repo.get_by_id(alert.alert_rule_id)
        if not rule:
            logger.warning(
                f"Cannot send notifications: Rule {alert.alert_rule_id} not found"
            )
            return

        # Send to configured channels
        if rule.notification_channels:
            results = self.notification_manager.send_alert(
                alert, rule.notification_channels
            )

            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)

            logger.info(
                f"Sent alert notifications: {success_count}/{total_count} "
                f"channels for alert {alert.id}"
            )

    def resolve_stale_alerts(self, hours: int = 24) -> int:
        """
        Automatically resolve alerts older than specified hours.

        Args:
            hours: Age threshold in hours

        Returns:
            Number of alerts resolved
        """
        count = self.engine.resolve_stale_alerts(hours)
        if count > 0:
            logger.info(f"Auto-resolved {count} stale alerts (>{hours}h old)")
        return count

    # ==================== Alert Management ====================

    def get_alert(self, alert_id: int) -> Optional[Alert]:
        """
        Get alert by ID.

        Args:
            alert_id: Alert ID

        Returns:
            Alert if found, None otherwise
        """
        return self.alert_repo.get_by_id(alert_id)

    def list_active_alerts(
        self,
        severity: Optional[str] = None,
        host_id: Optional[str] = None,
    ) -> List[Alert]:
        """
        List active (unresolved) alerts.

        Args:
            severity: Filter by severity
            host_id: Filter by host ID

        Returns:
            List of active alerts
        """
        # Get all active alerts
        alerts = self.alert_repo.get_active()

        # Apply filters
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if host_id:
            alerts = [a for a in alerts if a.host_id == host_id]

        return alerts

    def list_recent_alerts(
        self,
        hours: int = 24,
        severity: Optional[str] = None,
    ) -> List[Alert]:
        """
        List recent alerts.

        Args:
            hours: Time window in hours
            severity: Filter by severity

        Returns:
            List of recent alerts
        """
        alerts = self.alert_repo.get_recent(hours=hours)

        # Apply severity filter if specified
        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts

    def acknowledge_alert(
        self,
        alert_id: int,
        acknowledged_by: str,
    ) -> bool:
        """
        Acknowledge an alert.

        Args:
            alert_id: Alert ID
            acknowledged_by: Username or identifier

        Returns:
            True if acknowledged, False if not found
        """
        success = self.alert_repo.acknowledge(alert_id, acknowledged_by)
        if success:
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
        return success

    def resolve_alert(self, alert_id: int) -> bool:
        """
        Resolve an alert.

        Args:
            alert_id: Alert ID

        Returns:
            True if resolved, False if not found
        """
        success = self.alert_repo.resolve(alert_id)
        if success:
            logger.info(f"Alert {alert_id} resolved")
        return success

    def get_alert_statistics(
        self,
        days: int = 7,
    ) -> Dict[str, int]:
        """
        Get alert statistics for the specified time period.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with alert counts by severity
        """
        hours = days * 24
        return self.alert_repo.get_alert_counts(hours=hours)

    # ==================== Mute Management ====================

    def mute_rule(
        self,
        rule_id: int,
        muted_by: str,
        duration_minutes: Optional[int] = None,
        host_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> AlertMute:
        """
        Mute an alert rule.

        Args:
            rule_id: Rule ID to mute
            muted_by: Username or identifier of who is muting
            duration_minutes: Mute duration (None for indefinite)
            host_id: Specific host to mute (None for all hosts)
            reason: Reason for muting

        Returns:
            Created AlertMute
        """
        mute = self.mute_repo.mute_rule(
            rule_id=rule_id,
            muted_by=muted_by,
            duration_minutes=duration_minutes,
            host_id=host_id,
            reason=reason,
        )
        duration_str = (
            f" for {duration_minutes}m" if duration_minutes else " indefinitely"
        )
        logger.info(
            f"Muted rule {rule_id}"
            + (f" for host {host_id}" if host_id else "")
            + duration_str
        )
        return mute

    def unmute_rule(
        self,
        rule_id: int,
        host_id: Optional[str] = None,
    ) -> bool:
        """
        Unmute an alert rule.

        Args:
            rule_id: Rule ID to unmute
            host_id: Specific host to unmute (None for all hosts)

        Returns:
            True if unmuted, False if not found
        """
        count = self.mute_repo.unmute_rule(rule_id, host_id)
        if count > 0:
            logger.info(
                f"Unmuted rule {rule_id}" + (f" for host {host_id}" if host_id else "")
            )
        return count > 0

    def list_active_mutes(self) -> List[AlertMute]:
        """
        List all active mutes.

        Returns:
            List of active AlertMutes
        """
        return self.mute_repo.get_active()

    def cleanup_expired_mutes(self) -> int:
        """
        Remove expired mutes from database.

        Returns:
            Number of mutes deleted
        """
        count = self.mute_repo.delete_expired()
        if count > 0:
            logger.info(f"Cleaned up {count} expired mutes")
        return count

    # ==================== Channel Management ====================

    def create_channel(self, channel: NotificationChannel) -> NotificationChannel:
        """
        Create a notification channel.

        Args:
            channel: NotificationChannel to create

        Returns:
            Created channel
        """
        created = self.channel_repo.create(channel)
        logger.info(f"Created notification channel: {created.name} ({created.id})")
        return created

    def list_channels(
        self,
        enabled_only: bool = False,
        channel_type: Optional[str] = None,
    ) -> List[NotificationChannel]:
        """
        List notification channels.

        Args:
            enabled_only: Only return enabled channels
            channel_type: Filter by channel type

        Returns:
            List of notification channels
        """
        if enabled_only:
            return self.channel_repo.get_all_enabled()
        elif channel_type:
            return self.channel_repo.get_by_type(channel_type)
        else:
            return self.channel_repo.get_all()

    def enable_channel(self, channel_id: str) -> bool:
        """
        Enable a notification channel.

        Args:
            channel_id: Channel ID

        Returns:
            True if enabled, False if not found
        """
        success = self.channel_repo.enable(channel_id)
        if success:
            logger.info(f"Enabled notification channel: {channel_id}")
        return success

    def disable_channel(self, channel_id: str) -> bool:
        """
        Disable a notification channel.

        Args:
            channel_id: Channel ID

        Returns:
            True if disabled, False if not found
        """
        success = self.channel_repo.disable(channel_id)
        if success:
            logger.info(f"Disabled notification channel: {channel_id}")
        return success

    def close(self) -> None:
        """Cleanup resources."""
        self.notification_manager.close()
        logger.info("AlertManager shut down")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
