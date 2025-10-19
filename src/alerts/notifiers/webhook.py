"""
Webhook notifier for sending alerts to external services.

Supports generic webhooks and specific integrations for Slack and Discord.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import requests

from src.alerts.models import Alert
from src.alerts.notifiers.base import BaseNotifier

logger = logging.getLogger(__name__)


class WebhookNotifier(BaseNotifier):
    """
    Generic webhook notifier with platform-specific formatting.

    Supports Slack, Discord, and generic JSON webhooks.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize webhook notifier.

        Args:
            config: Configuration dictionary with keys:
                - webhook_url: URL to send webhook to (required)
                - platform: Platform type ('slack', 'discord', 'generic')
                - timeout: Request timeout in seconds (default: 10)
                - verify_ssl: Whether to verify SSL certificates (default: True)
        """
        super().__init__(config)
        self.webhook_url = config.get("webhook_url")
        self.platform = config.get("platform", "generic")
        self.timeout = config.get("timeout", 10)
        self.verify_ssl = config.get("verify_ssl", True)

    def validate_config(self) -> bool:
        """
        Validate webhook configuration.

        Returns:
            True if configuration is valid
        """
        if not self.webhook_url:
            logger.error("Webhook URL is required")
            return False

        if self.platform not in ["slack", "discord", "generic"]:
            logger.error(
                f"Unsupported platform: {self.platform}. "
                f"Use 'slack', 'discord', or 'generic'"
            )
            return False

        return True

    def send(self, alert: Alert) -> bool:
        """
        Send alert via webhook.

        Args:
            alert: Alert to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.validate_config():
            return False

        try:
            # Format payload based on platform
            payload = self._format_payload(alert)

            # Send webhook
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )

            response.raise_for_status()

            self._log_success(alert, f"{self.platform} webhook")
            return True

        except requests.exceptions.Timeout:
            logger.error(f"Webhook request timed out after {self.timeout}s")
            return False
        except requests.exceptions.RequestException as e:
            self._log_error(alert, e)
            return False
        except Exception as e:
            self._log_error(alert, e)
            return False

    def _format_payload(self, alert: Alert) -> Dict[str, Any]:
        """
        Format alert as webhook payload.

        Args:
            alert: Alert to format

        Returns:
            Payload dictionary
        """
        if self.platform == "slack":
            return self._format_slack(alert)
        elif self.platform == "discord":
            return self._format_discord(alert)
        else:
            return self._format_generic(alert)

    def _format_slack(self, alert: Alert) -> Dict[str, Any]:
        """
        Format alert for Slack webhook.

        Args:
            alert: Alert to format

        Returns:
            Slack-compatible payload
        """
        # Color coding by severity
        colors = {
            "info": "#2196F3",
            "warning": "#FF9800",
            "critical": "#F44336",
        }
        color = colors.get(alert.severity, "#757575")

        # Build fields
        fields = [
            {
                "title": "Severity",
                "value": alert.severity.upper(),
                "short": True,
            },
            {
                "title": "Triggered",
                "value": alert.triggered_at.strftime("%Y-%m-%d %H:%M:%S"),
                "short": True,
            },
        ]

        if alert.host_name:
            fields.append(
                {
                    "title": "Host",
                    "value": alert.host_name,
                    "short": True,
                }
            )

        if alert.metric_name:
            fields.append(
                {
                    "title": "Metric",
                    "value": alert.metric_name,
                    "short": True,
                }
            )

        if alert.value is not None:
            fields.append(
                {
                    "title": "Current Value",
                    "value": f"{alert.value:.2f}",
                    "short": True,
                }
            )

        if alert.threshold is not None:
            fields.append(
                {
                    "title": "Threshold",
                    "value": f"{alert.threshold:.2f}",
                    "short": True,
                }
            )

        return {
            "attachments": [
                {
                    "color": color,
                    "title": "UniFi Network Alert",
                    "text": alert.message,
                    "fields": fields,
                    "footer": "UniFi Network Monitoring",
                    "ts": int(alert.triggered_at.timestamp()),
                }
            ]
        }

    def _format_discord(self, alert: Alert) -> Dict[str, Any]:
        """
        Format alert for Discord webhook.

        Args:
            alert: Alert to format

        Returns:
            Discord-compatible payload
        """
        # Color coding by severity
        colors = {
            "info": 0x2196F3,
            "warning": 0xFF9800,
            "critical": 0xF44336,
        }
        color = colors.get(alert.severity, 0x757575)

        # Build fields
        fields = [
            {
                "name": "Severity",
                "value": alert.severity.upper(),
                "inline": True,
            },
            {
                "name": "Triggered",
                "value": alert.triggered_at.strftime("%Y-%m-%d %H:%M:%S"),
                "inline": True,
            },
        ]

        if alert.host_name:
            fields.append(
                {
                    "name": "Host",
                    "value": alert.host_name,
                    "inline": True,
                }
            )

        if alert.metric_name:
            fields.append(
                {
                    "name": "Metric",
                    "value": alert.metric_name,
                    "inline": True,
                }
            )

        if alert.value is not None:
            fields.append(
                {
                    "name": "Current Value",
                    "value": f"{alert.value:.2f}",
                    "inline": True,
                }
            )

        if alert.threshold is not None:
            fields.append(
                {
                    "name": "Threshold",
                    "value": f"{alert.threshold:.2f}",
                    "inline": True,
                }
            )

        return {
            "embeds": [
                {
                    "title": "🔔 UniFi Network Alert",
                    "description": alert.message,
                    "color": color,
                    "fields": fields,
                    "footer": {
                        "text": "UniFi Network Monitoring",
                    },
                    "timestamp": alert.triggered_at.isoformat(),
                }
            ]
        }

    def _format_generic(self, alert: Alert) -> Dict[str, Any]:
        """
        Format alert as generic JSON payload.

        Args:
            alert: Alert to format

        Returns:
            Generic JSON payload
        """
        # Determine status from alert properties
        if alert.resolved_at:
            status = "resolved"
        elif alert.acknowledged_at:
            status = "acknowledged"
        else:
            status = "active"

        payload = {
            "alert_id": alert.id,
            "severity": alert.severity,
            "message": alert.message,
            "triggered_at": alert.triggered_at.isoformat(),
            "status": status,
        }

        if alert.host_name:
            payload["host_name"] = alert.host_name

        if alert.metric_name:
            payload["metric_name"] = alert.metric_name

        if alert.value is not None:
            payload["value"] = alert.value

        if alert.threshold is not None:
            payload["threshold"] = alert.threshold

        if alert.acknowledged_at:
            payload["acknowledged_at"] = alert.acknowledged_at.isoformat()
            if alert.acknowledged_by:
                payload["acknowledged_by"] = alert.acknowledged_by

        if alert.resolved_at:
            payload["resolved_at"] = alert.resolved_at.isoformat()

        return payload
