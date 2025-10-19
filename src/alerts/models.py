"""
Alert system data models.

This module defines the data models for the alerting system including
alert rules, alerts, notification channels, and mutes.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AlertRule:
    """
    Alert rule definition.

    An alert rule defines the conditions that trigger an alert and how
    notifications should be delivered.

    Attributes:
        id: Unique identifier (None for new rules)
        name: Unique human-readable name
        description: Optional detailed description
        rule_type: Type of rule ('threshold', 'status_change', 'custom')
        metric_name: Name of metric to monitor (for threshold rules)
        host_id: Specific host ID to monitor (None for network-wide)
        condition: Comparison operator ('gt', 'lt', 'eq', 'ne', 'gte', 'lte')
        threshold: Threshold value (for threshold rules)
        severity: Alert severity ('info', 'warning', 'critical')
        enabled: Whether rule is active
        notification_channels: List of notification channel IDs
        cooldown_minutes: Minutes to wait before re-alerting
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    name: str
    rule_type: str
    condition: str
    severity: str
    notification_channels: List[str]
    id: Optional[int] = None
    description: Optional[str] = None
    metric_name: Optional[str] = None
    host_id: Optional[str] = None
    threshold: Optional[float] = None
    enabled: bool = True
    cooldown_minutes: int = 60
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate rule configuration."""
        # Validate rule type
        valid_types = ["threshold", "status_change", "custom"]
        if self.rule_type not in valid_types:
            raise ValueError(f"rule_type must be one of {valid_types}")

        # Validate severity
        valid_severities = ["info", "warning", "critical"]
        if self.severity not in valid_severities:
            raise ValueError(f"severity must be one of {valid_severities}")

        # Validate condition
        valid_conditions = ["gt", "lt", "eq", "ne", "gte", "lte"]
        if self.condition not in valid_conditions:
            raise ValueError(f"condition must be one of {valid_conditions}")

        # Threshold rules require metric_name and threshold
        if self.rule_type == "threshold":
            if not self.metric_name:
                raise ValueError("threshold rules require metric_name")
            if self.threshold is None:
                raise ValueError("threshold rules require threshold value")

        # Validate cooldown
        if self.cooldown_minutes < 0:
            raise ValueError("cooldown_minutes must be >= 0")

        # Ensure notification_channels is a list
        if not isinstance(self.notification_channels, list):
            raise ValueError("notification_channels must be a list")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        # Convert datetime to ISO format string
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        # Convert list to JSON string for SQLite
        data["notification_channels"] = json.dumps(self.notification_channels)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlertRule":
        """Create from dictionary (database row)."""
        # Parse datetime strings
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        # Parse JSON string to list
        if isinstance(data.get("notification_channels"), str):
            data["notification_channels"] = json.loads(data["notification_channels"])

        # Convert enabled from int to bool
        if isinstance(data.get("enabled"), int):
            data["enabled"] = bool(data["enabled"])

        return cls(**data)


@dataclass
class Alert:
    """
    Alert instance (triggered rule).

    Represents a single occurrence of an alert being triggered.

    Attributes:
        alert_rule_id: ID of the rule that triggered this alert
        severity: Alert severity ('info', 'warning', 'critical')
        message: Human-readable alert message
        triggered_at: When the alert was triggered
        id: Unique identifier (None for new alerts)
        host_id: ID of affected host (if applicable)
        host_name: Name of affected host (for display)
        metric_name: Name of metric that triggered (for threshold alerts)
        value: Current metric value
        threshold: Threshold that was breached
        acknowledged_at: When alert was acknowledged (None if not ack'd)
        acknowledged_by: Who acknowledged the alert
        resolved_at: When alert was resolved (None if active)
        notification_status: Delivery status per channel
    """

    alert_rule_id: int
    severity: str
    message: str
    triggered_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
    host_id: Optional[str] = None
    host_name: Optional[str] = None
    metric_name: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    notification_status: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate alert data."""
        valid_severities = ["info", "warning", "critical"]
        if self.severity not in valid_severities:
            raise ValueError(f"severity must be one of {valid_severities}")

    def is_active(self) -> bool:
        """Check if alert is currently active (not resolved)."""
        return self.resolved_at is None

    def is_acknowledged(self) -> bool:
        """Check if alert has been acknowledged."""
        return self.acknowledged_at is not None

    def acknowledge(self, user: str) -> None:
        """Acknowledge this alert."""
        self.acknowledged_at = datetime.now()
        self.acknowledged_by = user

    def resolve(self) -> None:
        """Resolve this alert."""
        self.resolved_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        # Convert datetime to ISO format string
        for field_name in ["triggered_at", "acknowledged_at", "resolved_at"]:
            if data[field_name] is not None:
                data[field_name] = data[field_name].isoformat()
        # Convert dict to JSON string for SQLite
        data["notification_status"] = json.dumps(self.notification_status)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Alert":
        """Create from dictionary (database row)."""
        # Parse datetime strings
        for field_name in ["triggered_at", "acknowledged_at", "resolved_at"]:
            if isinstance(data.get(field_name), str):
                data[field_name] = datetime.fromisoformat(data[field_name])

        # Parse JSON string to dict
        if isinstance(data.get("notification_status"), str):
            try:
                data["notification_status"] = json.loads(data["notification_status"])
            except json.JSONDecodeError:
                data["notification_status"] = {}

        return cls(**data)


@dataclass
class NotificationChannel:
    """
    Notification channel configuration.

    Defines how to deliver notifications through a specific channel.

    Attributes:
        id: Unique channel identifier (e.g., 'email_primary')
        name: Human-readable channel name
        channel_type: Type of channel ('email', 'slack', 'discord', 'webhook', 'sms')
        config: Channel-specific configuration (SMTP details, webhook URLs, etc.)
        enabled: Whether channel is active
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: str
    name: str
    channel_type: str
    config: Dict[str, Any]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate channel configuration."""
        valid_types = ["email", "slack", "discord", "webhook", "sms"]
        if self.channel_type not in valid_types:
            raise ValueError(f"channel_type must be one of {valid_types}")

        if not isinstance(self.config, dict):
            raise ValueError("config must be a dictionary")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        # Convert datetime to ISO format string
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        # Convert dict to JSON string for SQLite
        data["config"] = json.dumps(self.config)
        # Convert enabled to int
        data["enabled"] = int(self.enabled)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NotificationChannel":
        """Create from dictionary (database row)."""
        # Parse datetime strings
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        # Parse JSON string to dict
        if isinstance(data.get("config"), str):
            data["config"] = json.loads(data["config"])

        # Convert enabled from int to bool
        if isinstance(data.get("enabled"), int):
            data["enabled"] = bool(data["enabled"])

        return cls(**data)


@dataclass
class AlertMute:
    """
    Alert mute/snooze configuration.

    Temporarily suppresses alerts for a specific rule and optionally host.

    Attributes:
        alert_rule_id: ID of the rule to mute
        muted_by: Who muted the alert
        muted_at: When the mute was created
        id: Unique identifier (None for new mutes)
        host_id: Specific host to mute (None for all hosts)
        expires_at: When mute expires (None for indefinite)
        reason: Optional reason for muting
    """

    alert_rule_id: int
    muted_by: str
    muted_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None
    host_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    reason: Optional[str] = None

    def is_active(self) -> bool:
        """Check if mute is currently active (not expired)."""
        if self.expires_at is None:
            return True  # Indefinite mute
        return datetime.now() < self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        data = asdict(self)
        # Convert datetime to ISO format string
        data["muted_at"] = self.muted_at.isoformat()
        if self.expires_at is not None:
            data["expires_at"] = self.expires_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlertMute":
        """Create from dictionary (database row)."""
        # Parse datetime strings
        if isinstance(data.get("muted_at"), str):
            data["muted_at"] = datetime.fromisoformat(data["muted_at"])
        if isinstance(data.get("expires_at"), str):
            data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        return cls(**data)
