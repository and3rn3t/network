"""
Base notifier class for alert notifications.

Defines the interface that all notification channel implementations must follow.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from src.alerts.models import Alert

logger = logging.getLogger(__name__)


class BaseNotifier(ABC):
    """
    Abstract base class for notification channels.

    All notifier implementations (email, Slack, Discord, etc.) must
    inherit from this class and implement the send() method.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize notifier with configuration.

        Args:
            config: Channel-specific configuration dictionary
        """
        self.config = config
        self.name = self.__class__.__name__

    @abstractmethod
    def send(self, alert: Alert) -> bool:
        """
        Send alert notification.

        Args:
            alert: Alert to send

        Returns:
            True if notification sent successfully, False otherwise
        """
        pass

    def validate_config(self) -> bool:
        """
        Validate notifier configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        # Override in subclasses if specific validation is needed
        return True

    def format_message(self, alert: Alert) -> str:
        """
        Format alert as plain text message.

        Args:
            alert: Alert to format

        Returns:
            Formatted message string
        """
        severity_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🔴",
        }

        emoji = severity_emoji.get(alert.severity, "📢")
        lines = [
            f"{emoji} **{alert.severity.upper()} ALERT**",
            "",
            f"**Message:** {alert.message}",
            f"**Triggered:** {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        if alert.host_name:
            lines.append(f"**Host:** {alert.host_name}")

        if alert.metric_name:
            lines.append(f"**Metric:** {alert.metric_name}")

        if alert.value is not None:
            lines.append(f"**Current Value:** {alert.value:.2f}")

        if alert.threshold is not None:
            lines.append(f"**Threshold:** {alert.threshold:.2f}")

        return "\n".join(lines)

    def _log_success(self, alert: Alert, channel_info: str = "") -> None:
        """
        Log successful notification delivery.

        Args:
            alert: Alert that was sent
            channel_info: Additional channel information
        """
        info = f" ({channel_info})" if channel_info else ""
        logger.info(
            f"Sent {alert.severity} alert via {self.name}{info}: " f"{alert.message}"
        )

    def _log_error(self, alert: Alert, error: Exception) -> None:
        """
        Log notification delivery failure.

        Args:
            alert: Alert that failed to send
            error: Exception that occurred
        """
        logger.error(
            f"Failed to send alert via {self.name}: {alert.message}. " f"Error: {error}"
        )
