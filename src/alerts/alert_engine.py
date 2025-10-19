"""
Alert engine for evaluating rules and generating alerts.

This module contains the core alert evaluation logic that checks metrics
against alert rules and generates alerts when conditions are met.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.alerts.models import Alert, AlertRule
from src.database.database import Database
from src.database.repositories import (
    AlertMuteRepository,
    AlertRepository,
    AlertRuleRepository,
    MetricRepository,
    StatusRepository,
)

logger = logging.getLogger(__name__)


class AlertEngine:
    """
    Alert engine for evaluating rules and generating alerts.

    The engine evaluates all enabled alert rules against current metrics
    and status data, respecting cooldown periods and mute settings.
    """

    def __init__(self, db: Database):
        """
        Initialize alert engine.

        Args:
            db: Database instance
        """
        self.db = db
        self.rule_repo = AlertRuleRepository(db)
        self.alert_repo = AlertRepository(db)
        self.mute_repo = AlertMuteRepository(db)
        self.metric_repo = MetricRepository(db)
        self.status_repo = StatusRepository(db)

    def evaluate_all_rules(self) -> List[Alert]:
        """
        Evaluate all enabled alert rules.

        Returns:
            List of newly created alerts
        """
        logger.info("Starting alert rule evaluation")
        new_alerts = []

        # Get all enabled rules
        rules = self.rule_repo.get_all_enabled()
        logger.debug(f"Evaluating {len(rules)} enabled rules")

        for rule in rules:
            try:
                alerts = self.evaluate_rule(rule)
                new_alerts.extend(alerts)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name} (ID: {rule.id}): {e}")

        logger.info(f"Rule evaluation complete. Generated {len(new_alerts)} new alerts")
        return new_alerts

    def evaluate_rule(self, rule: AlertRule) -> List[Alert]:
        """
        Evaluate a single alert rule.

        Args:
            rule: AlertRule to evaluate

        Returns:
            List of newly created alerts (may be empty)
        """
        if rule.rule_type == "threshold":
            return self._evaluate_threshold_rule(rule)
        elif rule.rule_type == "status_change":
            return self._evaluate_status_change_rule(rule)
        elif rule.rule_type == "custom":
            return self._evaluate_custom_rule(rule)
        else:
            logger.warning(f"Unknown rule type: {rule.rule_type}")
            return []

    def _evaluate_threshold_rule(self, rule: AlertRule) -> List[Alert]:
        """
        Evaluate a threshold-based alert rule.

        Checks if metric values exceed/fall below thresholds.

        Args:
            rule: AlertRule with type='threshold'

        Returns:
            List of newly created alerts
        """
        new_alerts = []

        # Get hosts to check
        if rule.host_id:
            # Check specific host
            hosts = [rule.host_id]
        else:
            # Check all hosts (network-wide rule)
            hosts = self._get_all_host_ids()

        for host_id in hosts:
            # Check if muted
            if self.mute_repo.is_muted(rule.id, host_id):
                logger.debug(f"Rule {rule.name} is muted for host {host_id}")
                continue

            # Check cooldown
            if self._is_in_cooldown(rule, host_id):
                logger.debug(f"Rule {rule.name} is in cooldown for host {host_id}")
                continue

            # Get latest metric value
            metric = self._get_latest_metric(host_id, rule.metric_name)
            if metric is None:
                continue

            # Check threshold
            if self._check_threshold(metric["value"], rule.condition, rule.threshold):
                # Create alert
                alert = self._create_threshold_alert(rule, host_id, metric)
                new_alerts.append(alert)

        return new_alerts

    def _evaluate_status_change_rule(self, rule: AlertRule) -> List[Alert]:
        """
        Evaluate a status change alert rule.

        Detects when host status changes (e.g., goes offline).

        Args:
            rule: AlertRule with type='status_change'

        Returns:
            List of newly created alerts
        """
        new_alerts = []

        # Get hosts to check
        if rule.host_id:
            hosts = [rule.host_id]
        else:
            hosts = self._get_all_host_ids()

        for host_id in hosts:
            # Check if muted
            if self.mute_repo.is_muted(rule.id, host_id):
                continue

            # Check cooldown
            if self._is_in_cooldown(rule, host_id):
                continue

            # Check if status matches alert condition
            status = self._get_latest_status(host_id)
            if status is None:
                continue

            # For status change rules, we typically alert on offline status
            # or other specific status values
            is_offline = not status.get("is_online", True)

            if rule.condition == "eq" and rule.threshold == 0:
                # Alert when device goes offline
                if is_offline:
                    alert = self._create_status_change_alert(
                        rule, host_id, status, "offline"
                    )
                    new_alerts.append(alert)

        return new_alerts

    def _evaluate_custom_rule(self, rule: AlertRule) -> List[Alert]:
        """
        Evaluate a custom alert rule.

        Placeholder for future custom rule logic.

        Args:
            rule: AlertRule with type='custom'

        Returns:
            List of newly created alerts
        """
        logger.warning(f"Custom rules not yet implemented: {rule.name}")
        return []

    def _check_threshold(self, value: float, condition: str, threshold: float) -> bool:
        """
        Check if value meets threshold condition.

        Args:
            value: Current metric value
            condition: Comparison operator
            threshold: Threshold value

        Returns:
            True if condition is met, False otherwise
        """
        if condition == "gt":
            return value > threshold
        elif condition == "gte":
            return value >= threshold
        elif condition == "lt":
            return value < threshold
        elif condition == "lte":
            return value <= threshold
        elif condition == "eq":
            return value == threshold
        elif condition == "ne":
            return value != threshold
        else:
            logger.warning(f"Unknown condition: {condition}")
            return False

    def _is_in_cooldown(self, rule: AlertRule, host_id: str) -> bool:
        """
        Check if rule is in cooldown period for a host.

        Args:
            rule: AlertRule to check
            host_id: Host ID

        Returns:
            True if in cooldown, False otherwise
        """
        if rule.cooldown_minutes <= 0:
            return False

        # Get most recent alert for this rule + host
        alerts = self.alert_repo.get_by_rule(rule.id, limit=100)

        for alert in alerts:
            if alert.host_id == host_id:
                # Check if within cooldown period
                cooldown_end = alert.triggered_at + timedelta(
                    minutes=rule.cooldown_minutes
                )
                if datetime.now() < cooldown_end:
                    return True
                break

        return False

    def _create_threshold_alert(
        self, rule: AlertRule, host_id: str, metric: Dict
    ) -> Alert:
        """
        Create an alert for a threshold breach.

        Args:
            rule: AlertRule that was triggered
            host_id: Host ID
            metric: Metric data with value

        Returns:
            Created Alert
        """
        # Get host name
        host_name = metric.get("host_name", host_id)

        # Create message
        message = (
            f"{host_name}: {rule.metric_name} is {metric['value']:.1f} "
            f"(threshold: {rule.threshold})"
        )

        alert = Alert(
            alert_rule_id=rule.id,
            host_id=host_id,
            host_name=host_name,
            metric_name=rule.metric_name,
            value=metric["value"],
            threshold=rule.threshold,
            severity=rule.severity,
            message=message,
        )

        # Save to database
        created_alert = self.alert_repo.create(alert)
        logger.info(f"Created threshold alert: {message}")

        return created_alert

    def _create_status_change_alert(
        self, rule: AlertRule, host_id: str, status: Dict, status_text: str
    ) -> Alert:
        """
        Create an alert for a status change.

        Args:
            rule: AlertRule that was triggered
            host_id: Host ID
            status: Status data
            status_text: Human-readable status (e.g., 'offline')

        Returns:
            Created Alert
        """
        host_name = status.get("host_name", host_id)
        message = f"{host_name}: Device is {status_text}"

        alert = Alert(
            alert_rule_id=rule.id,
            host_id=host_id,
            host_name=host_name,
            severity=rule.severity,
            message=message,
        )

        # Save to database
        created_alert = self.alert_repo.create(alert)
        logger.info(f"Created status change alert: {message}")

        return created_alert

    def _get_all_host_ids(self) -> List[str]:
        """
        Get all host IDs from the database.

        Returns:
            List of host IDs
        """
        query = "SELECT DISTINCT host_id FROM hosts ORDER BY host_id"
        results = self.db.fetch_all(query)
        return [row["host_id"] for row in results]

    def _get_latest_metric(
        self, host_id: str, metric_name: Optional[str]
    ) -> Optional[Dict]:
        """
        Get latest metric value for a host.

        Args:
            host_id: Host ID
            metric_name: Name of metric to retrieve

        Returns:
            Metric data dict or None if not found
        """
        if not metric_name:
            return None

        # Get latest metric from database
        metrics = self.metric_repo.get_by_host(host_id, limit=1)

        if not metrics:
            return None

        # Extract the specific metric value
        metric = metrics[0]

        # Try to get the metric value from the metric object
        if hasattr(metric, metric_name):
            value = getattr(metric, metric_name)
        else:
            # Fallback: check in a dict representation
            metric_dict = metric.to_dict() if hasattr(metric, "to_dict") else {}
            value = metric_dict.get(metric_name)

        if value is None:
            return None

        return {
            "value": value,
            "host_name": getattr(metric, "host_name", host_id),
            "timestamp": getattr(metric, "timestamp", datetime.now()),
        }

    def _get_latest_status(self, host_id: str) -> Optional[Dict]:
        """
        Get latest status for a host.

        Args:
            host_id: Host ID

        Returns:
            Status data dict or None if not found
        """
        statuses = self.status_repo.get_by_host(host_id, limit=1)

        if not statuses:
            return None

        status = statuses[0]
        return {
            "is_online": getattr(status, "is_online", True),
            "host_name": getattr(status, "host_name", host_id),
            "timestamp": getattr(status, "timestamp", datetime.now()),
        }

    def resolve_stale_alerts(self, hours: int = 24) -> int:
        """
        Auto-resolve alerts that are no longer active.

        For threshold alerts, check if current value is back within bounds.
        For status alerts, check if device is back online.

        Args:
            hours: Look back period for unresolved alerts

        Returns:
            Number of alerts resolved
        """
        logger.info("Checking for stale alerts to auto-resolve")
        resolved_count = 0

        # Get all unresolved alerts
        active_alerts = self.alert_repo.get_active()

        for alert in active_alerts:
            # Skip if too recent
            age = datetime.now() - alert.triggered_at
            if age < timedelta(hours=hours):
                continue

            # Check if alert should be auto-resolved
            should_resolve = False

            # Get the rule
            rule = self.rule_repo.get_by_id(alert.alert_rule_id)
            if not rule:
                continue

            if rule.rule_type == "threshold" and alert.metric_name:
                # Check if metric is back in bounds
                metric = self._get_latest_metric(alert.host_id, alert.metric_name)
                if metric and not self._check_threshold(
                    metric["value"], rule.condition, rule.threshold
                ):
                    should_resolve = True

            elif rule.rule_type == "status_change":
                # Check if device is back online
                status = self._get_latest_status(alert.host_id)
                if status and status.get("is_online", False):
                    should_resolve = True

            if should_resolve:
                self.alert_repo.resolve(alert.id)
                resolved_count += 1
                logger.info(f"Auto-resolved alert: {alert.message}")

        logger.info(f"Auto-resolved {resolved_count} stale alerts")
        return resolved_count
