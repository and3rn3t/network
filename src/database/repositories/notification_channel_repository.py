"""Notification channel repository."""

from typing import List, Optional

from src.alerts.models import NotificationChannel
from src.database.repositories.base import BaseRepository


class NotificationChannelRepository(BaseRepository):
    """Repository for NotificationChannel model operations."""

    table_name = "notification_channels"

    def create(self, channel: NotificationChannel) -> NotificationChannel:
        """Create new notification channel."""
        data = channel.to_dict()
        query = """
            INSERT INTO notification_channels (
                id, name, channel_type, config, enabled, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data["id"],
            data["name"],
            data["channel_type"],
            data["config"],
            data["enabled"],
            data["created_at"],
            data["updated_at"],
        )

        with self.db.transaction():
            self.db.execute(query, params)

        return channel

    def get_by_id(self, channel_id: int) -> Optional[NotificationChannel]:
        """Get channel by ID."""
        query = "SELECT * FROM notification_channels WHERE id = ?"
        row = self.db.fetch_one(query, (channel_id,))
        return NotificationChannel.from_dict(dict(row)) if row else None

    def get_all(self, enabled_only: bool = False) -> List[NotificationChannel]:
        """Get all notification channels."""
        if enabled_only:
            query = "SELECT * FROM notification_channels WHERE enabled = 1"
        else:
            query = "SELECT * FROM notification_channels"

        rows = self.db.fetch_all(query)
        return [NotificationChannel.from_dict(dict(row)) for row in rows]

    def update(self, channel: NotificationChannel) -> NotificationChannel:
        """Update notification channel."""
        data = channel.to_dict()
        query = """
            UPDATE notification_channels
            SET name = ?, channel_type = ?, config = ?,
                enabled = ?, min_severity = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (
            data["name"],
            data["channel_type"],
            data["config"],
            data["enabled"],
            data.get("min_severity"),
            channel.id,
        )

        with self.db.transaction():
            self.db.execute(query, params)

        return channel

    def delete(self, channel_id: int) -> bool:
        """Delete notification channel."""
        return self.delete_by_id(channel_id)
