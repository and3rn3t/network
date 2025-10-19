"""
Notification manager for routing alerts to appropriate channels.

Handles delivery to multiple channels, retry logic, and status tracking.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

from src.alerts.models import Alert, NotificationChannel
from src.alerts.notifiers.base import BaseNotifier
from src.database.repositories.alert_repository import AlertRepository
from src.database.repositories.notification_channel_repository import (
    NotificationChannelRepository,
)

logger = logging.getLogger(__name__)


class NotificationManager:
    """
    Manages routing alerts to notification channels.

    Routes alerts based on severity and rule configuration, handles
    parallel delivery, and tracks notification status.
    """

    def __init__(
        self,
        alert_repo: AlertRepository,
        channel_repo: NotificationChannelRepository,
    ):
        """
        Initialize notification manager.

        Args:
            alert_repo: Alert repository for status updates
            channel_repo: Channel repository for channel lookups
        """
        self.alert_repo = alert_repo
        self.channel_repo = channel_repo
        self.notifiers: Dict[str, BaseNotifier] = {}
        self._executor = ThreadPoolExecutor(max_workers=5)

    def register_notifier(self, channel_type: str, notifier: BaseNotifier) -> None:
        """
        Register a notifier implementation for a channel type.

        Args:
            channel_type: Type of channel (email, slack, discord, etc.)
            notifier: Notifier instance
        """
        self.notifiers[channel_type] = notifier
        logger.info(f"Registered notifier for channel type: {channel_type}")

    def send_alert(
        self,
        alert: Alert,
        channel_ids: Optional[List[str]] = None,
    ) -> Dict[str, bool]:
        """
        Send alert to specified channels or all enabled channels.

        Args:
            alert: Alert to send
            channel_ids: Optional list of channel IDs to send to.
                        If None, uses all enabled channels.

        Returns:
            Dictionary mapping channel ID to success status
        """
        # Get channels to send to
        if channel_ids:
            channels = [
                ch
                for cid in channel_ids
                if (ch := self.channel_repo.get_by_id(cid)) is not None
            ]
        else:
            channels = self.channel_repo.get_all_enabled()

        if not channels:
            logger.warning(f"No channels found for alert: {alert.message}")
            return {}

        # Filter channels by severity threshold
        valid_channels = self._filter_by_severity(alert, channels)

        if not valid_channels:
            logger.info(
                f"No channels match severity {alert.severity} for "
                f"alert: {alert.message}"
            )
            return {}

        # Send to all valid channels in parallel
        results = self._send_parallel(alert, valid_channels)

        # Update alert notification status for each channel
        if alert.id:
            for channel_id, success in results.items():
                status = "sent" if success else "failed"
                self.alert_repo.update_notification_status(
                    alert_id=alert.id,
                    channel_id=channel_id,
                    status=status,
                )

        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)

        logger.info(
            f"Sent alert to {success_count}/{total_count} channels: " f"{alert.message}"
        )

        return results

    def _filter_by_severity(
        self, alert: Alert, channels: List[NotificationChannel]
    ) -> List[NotificationChannel]:
        """
        Filter channels by severity threshold.

        Args:
            alert: Alert to send
            channels: List of all channels

        Returns:
            List of channels that should receive this alert
        """
        severity_levels = {"info": 0, "warning": 1, "critical": 2}
        alert_level = severity_levels.get(alert.severity, 0)

        valid_channels = []
        for channel in channels:
            min_severity = channel.config.get("min_severity", "info")
            min_level = severity_levels.get(min_severity, 0)

            if alert_level >= min_level:
                valid_channels.append(channel)

        return valid_channels

    def _send_parallel(
        self, alert: Alert, channels: List[NotificationChannel]
    ) -> Dict[str, bool]:
        """
        Send alert to multiple channels in parallel.

        Args:
            alert: Alert to send
            channels: List of channels to send to

        Returns:
            Dictionary mapping channel ID to success status
        """
        results = {}
        futures = {}

        # Submit all send tasks
        for channel in channels:
            notifier = self.notifiers.get(channel.channel_type)

            if not notifier:
                logger.warning(
                    f"No notifier registered for type: " f"{channel.channel_type}"
                )
                results[channel.id] = False
                continue

            future = self._executor.submit(
                self._send_with_error_handling,
                notifier,
                alert,
                channel,
            )
            futures[future] = channel.id

        # Collect results
        for future in as_completed(futures):
            channel_id = futures[future]
            try:
                success = future.result()
                results[channel_id] = success
            except Exception as e:
                logger.error(f"Unexpected error sending to {channel_id}: {e}")
                results[channel_id] = False

        return results

    def _send_with_error_handling(
        self,
        notifier: BaseNotifier,
        alert: Alert,
        channel: NotificationChannel,
    ) -> bool:
        """
        Send notification with error handling.

        Args:
            notifier: Notifier to use
            alert: Alert to send
            channel: Channel configuration

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Update notifier config if needed
            if hasattr(notifier, "config"):
                notifier.config = channel.config

            return notifier.send(alert)
        except Exception as e:
            logger.error(f"Error sending via {channel.channel_type}: {e}")
            return False

    def close(self) -> None:
        """Shutdown the thread pool executor."""
        self._executor.shutdown(wait=True)
        logger.info("Notification manager shut down")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
