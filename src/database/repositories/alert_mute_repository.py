"""Alert mute repository."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from src.alerts.models import AlertMute

from src.database.repositories.base import BaseRepository


class AlertMuteRepository(BaseRepository):
    """Repository for AlertMute model operations."""

    table_name = "alert_mutes"

    def create(self, mute: "AlertMute") -> "AlertMute":
        """Create new mute."""
        data = mute.to_dict()
        query = """
            INSERT INTO alert_mutes (
                rule_id, host_id, reason, muted_by, expires_at
            ) VALUES (?, ?, ?, ?, ?)
        """
        params = (
            data.get("rule_id"),
            data.get("host_id"),
            data.get("reason"),
            data.get("muted_by"),
            data.get("expires_at"),
        )

        with self.db.transaction():
            cursor = self.db.execute(query, params)
            mute.id = cursor.lastrowid

        return mute

    def get_by_id(self, mute_id: int) -> Optional["AlertMute"]:
        """Get mute by ID."""
        from src.alerts.models import AlertMute

        query = "SELECT * FROM alert_mutes WHERE id = ?"
        row = self.db.fetch_one(query, (mute_id,))
        return AlertMute.from_dict(dict(row)) if row else None

    def get_active(self) -> List["AlertMute"]:
        """Get all active mutes."""
        from src.alerts.models import AlertMute

        query = """
            SELECT * FROM alert_mutes
            WHERE (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            ORDER BY created_at DESC
        """
        rows = self.db.fetch_all(query)
        return [AlertMute.from_dict(dict(row)) for row in rows]

    def get_for_rule(self, rule_id: int) -> List["AlertMute"]:
        """Get active mutes for a rule."""
        from src.alerts.models import AlertMute

        query = """
            SELECT * FROM alert_mutes
            WHERE rule_id = ?
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        """
        rows = self.db.fetch_all(query, (rule_id,))
        return [AlertMute.from_dict(dict(row)) for row in rows]

    def get_for_host(self, host_id: str) -> List["AlertMute"]:
        """Get active mutes for a host."""
        from src.alerts.models import AlertMute

        query = """
            SELECT * FROM alert_mutes
            WHERE host_id = ?
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        """
        rows = self.db.fetch_all(query, (host_id,))
        return [AlertMute.from_dict(dict(row)) for row in rows]

    def delete(self, mute_id: int) -> bool:
        """Delete mute (unmute)."""
        return self.delete_by_id(mute_id)
