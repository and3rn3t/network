"""
Alert rule repository for managing alert rules.

Provides CRUD operations for alert_rules table.
"""

from typing import List, Optional

from src.alerts.models import AlertRule
from src.database.repositories.base import BaseRepository


class AlertRuleRepository(BaseRepository):
    """Repository for AlertRule model operations."""

    table_name = "alert_rules"

    def create(self, rule: AlertRule) -> AlertRule:
        """Create new alert rule."""
        query = """
            INSERT INTO alert_rules (
                name, description, rule_type, metric_name, host_id,
                condition, threshold, expected_status, severity, enabled,
                notification_channels, cooldown_minutes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        data = rule.to_dict()
        params = (
            data["name"],
            data.get("description"),
            data["rule_type"],
            data.get("metric_name"),
            data.get("host_id"),
            data["condition"],
            data.get("threshold"),
            data.get("expected_status"),
            data["severity"],
            data["enabled"],
            data["notification_channels"],
            data["cooldown_minutes"],
        )

        with self.db.transaction():
            cursor = self.db.execute(query, params)
            rule.id = cursor.lastrowid

        return rule

    def get_by_id(self, rule_id: int) -> Optional[AlertRule]:
        """Get alert rule by ID."""
        query = "SELECT * FROM alert_rules WHERE id = ?"
        row = self.db.fetch_one(query, (rule_id,))
        if not row:
            return None

        # Convert row to dict
        data = dict(row)
        return AlertRule.from_dict(data)

    def get_all(self, enabled_only: bool = False) -> List[AlertRule]:
        """Get all alert rules."""
        if enabled_only:
            query = "SELECT * FROM alert_rules WHERE enabled = 1 ORDER BY name"
        else:
            query = "SELECT * FROM alert_rules ORDER BY name"

        rows = self.db.fetch_all(query)
        return [AlertRule.from_dict(dict(row)) for row in rows]

    def get_by_host(self, host_id: str) -> List[AlertRule]:
        """Get rules for specific host."""
        query = """
            SELECT * FROM alert_rules
            WHERE (host_id = ? OR host_id IS NULL) AND enabled = 1
            ORDER BY name
        """
        rows = self.db.fetch_all(query, (host_id,))
        return [AlertRule.from_dict(dict(row)) for row in rows]

    def update(self, rule: AlertRule) -> AlertRule:
        """Update existing alert rule."""
        query = """
            UPDATE alert_rules
            SET name = ?, description = ?, rule_type = ?, metric_name = ?,
                host_id = ?, condition = ?, threshold = ?, expected_status = ?,
                severity = ?, enabled = ?, notification_channels = ?,
                cooldown_minutes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """

        data = rule.to_dict()
        params = (
            data["name"],
            data.get("description"),
            data["rule_type"],
            data.get("metric_name"),
            data.get("host_id"),
            data["condition"],
            data.get("threshold"),
            data.get("expected_status"),
            data["severity"],
            data["enabled"],
            data["notification_channels"],
            data["cooldown_minutes"],
            rule.id,
        )

        with self.db.transaction():
            self.db.execute(query, params)

        return rule

    def delete(self, rule_id: int) -> bool:
        """Delete alert rule."""
        return self.delete_by_id(rule_id)
