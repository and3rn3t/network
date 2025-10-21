"""Alert repository for managing triggered alerts."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from src.alerts.models import Alert

from src.database.repositories.base import BaseRepository


class AlertRepository(BaseRepository):
    """Repository for Alert model operations."""

    table_name = "alert_history"

    def create(self, alert: "Alert") -> "Alert":
        """Create new alert."""
        data = alert.to_dict()
        query = """
            INSERT INTO alert_history (
                rule_id, host_id, metric_name, value, threshold,
                severity, status, message, notification_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data["rule_id"],
            data.get("host_id"),
            data.get("metric_name"),
            data.get("value"),
            data.get("threshold"),
            data["severity"],
            data["status"],
            data["message"],
            data["notification_status"],
        )

        with self.db.transaction():
            cursor = self.db.execute(query, params)
            alert.id = cursor.lastrowid

        return alert

    def get_by_id(self, alert_id: int) -> Optional["Alert"]:
        """Get alert by ID."""
        from src.alerts.models import Alert

        query = "SELECT * FROM alert_history WHERE id = ?"
        row = self.db.fetch_one(query, (alert_id,))
        return Alert.from_dict(dict(row)) if row else None

    def get_active(self) -> List["Alert"]:
        """Get all active (unresolved) alerts."""
        from src.alerts.models import Alert

        query = """
            SELECT * FROM alert_history
            WHERE resolved_at IS NULL
            ORDER BY triggered_at DESC
        """
        rows = self.db.fetch_all(query)
        return [Alert.from_dict(dict(row)) for row in rows]

    def get_by_rule(self, rule_id: int) -> List["Alert"]:
        """Get all alerts for a rule."""
        from src.alerts.models import Alert

        query = """
            SELECT * FROM alert_history
            WHERE rule_id = ?
            ORDER BY triggered_at DESC
        """
        rows = self.db.fetch_all(query, (rule_id,))
        return [Alert.from_dict(dict(row)) for row in rows]

    def get_recent(self, hours: int = 24, limit: int = 100) -> List["Alert"]:
        """Get recent alerts."""
        from src.alerts.models import Alert

        query = """
            SELECT * FROM alert_history
            WHERE triggered_at >= datetime('now', '-' || ? || ' hours')
            ORDER BY triggered_at DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (hours, limit))
        return [Alert.from_dict(dict(row)) for row in rows]

    def update(self, alert: "Alert") -> "Alert":
        """Update alert."""
        data = alert.to_dict()
        query = """
            UPDATE alert_history
            SET status = ?, acknowledged_at = ?, acknowledged_by = ?,
                resolved_at = ?, notification_status = ?
            WHERE id = ?
        """
        params = (
            data["status"],
            data.get("acknowledged_at"),
            data.get("acknowledged_by"),
            data.get("resolved_at"),
            data["notification_status"],
            alert.id,
        )

        with self.db.transaction():
            self.db.execute(query, params)

        return alert
