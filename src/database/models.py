"""
Data models for UniFi Network database.

Provides typed data classes for hosts, status, events, and metrics
with validation and serialization methods.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Host:
    """
    Host/device model representing a UniFi network device.

    Attributes:
        id: UniFi host ID
        hardware_id: Hardware identifier
        type: Device type (console, gateway, switch, ap)
        ip_address: Current IP address
        mac_address: MAC address
        name: Friendly device name
        owner: Is primary owner
        is_blocked: Blocked status
        firmware_version: Current firmware version
        model: Device model
        registration_time: First registration timestamp
        first_seen: First seen in our database
        last_seen: Last seen/updated timestamp
        created_at: Record creation time
        updated_at: Record update time
    """

    id: str
    hardware_id: str
    type: str
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    name: Optional[str] = None
    owner: bool = False
    is_blocked: bool = False
    firmware_version: Optional[str] = None
    model: Optional[str] = None
    registration_time: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Host":
        """
        Create Host from UniFi API response.

        Args:
            data: Raw API response dictionary

        Returns:
            Host instance
        """
        return cls(
            id=data.get("id", ""),
            hardware_id=data.get("hardwareId", ""),
            type=data.get("type", "unknown"),
            ip_address=data.get("ipAddress"),
            mac_address=data.get("mac"),
            name=data.get("name"),
            owner=data.get("owner", False),
            is_blocked=data.get("isBlocked", False),
            firmware_version=data.get("firmwareVersion"),
            model=data.get("model"),
            registration_time=data.get("registrationTime"),
        )

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "Host":
        """
        Create Host from database row.

        Args:
            row: Database row as dictionary

        Returns:
            Host instance
        """
        return cls(
            id=row["id"],
            hardware_id=row["hardware_id"],
            type=row["type"],
            ip_address=row.get("ip_address"),
            mac_address=row.get("mac_address"),
            name=row.get("name"),
            owner=bool(row.get("owner", 0)),
            is_blocked=bool(row.get("is_blocked", 0)),
            firmware_version=row.get("firmware_version"),
            model=row.get("model"),
            registration_time=row.get("registration_time"),
            first_seen=row.get("first_seen"),
            last_seen=row.get("last_seen"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def to_db_params(self) -> tuple:
        """
        Convert to database parameters tuple for INSERT/UPDATE.

        Returns:
            Tuple of values for database operation
        """
        return (
            self.id,
            self.hardware_id,
            self.type,
            self.ip_address,
            self.mac_address,
            self.name,
            int(self.owner),
            int(self.is_blocked),
            self.firmware_version,
            self.model,
            self.registration_time,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def __repr__(self) -> str:
        """String representation."""
        return f"Host(id='{self.id}', " f"name='{self.name}', " f"type='{self.type}')"


@dataclass
class HostStatus:
    """
    Host status model for tracking device status over time.

    Attributes:
        id: Status record ID (auto-increment)
        host_id: Foreign key to hosts table
        status: Status string (online, offline, upgrading, etc.)
        is_online: Boolean online status
        uptime_seconds: Device uptime in seconds
        cpu_usage: CPU usage percentage
        memory_usage: Memory usage percentage
        temperature: Device temperature
        last_connection_change: Last connection state change time
        last_backup_time: Last backup timestamp
        error_message: Error message if any
        raw_data: Full JSON response from API
        recorded_at: When this status was recorded
    """

    host_id: str
    status: str
    id: Optional[int] = None
    is_online: Optional[bool] = None
    uptime_seconds: Optional[int] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    temperature: Optional[float] = None
    last_connection_change: Optional[str] = None
    last_backup_time: Optional[str] = None
    error_message: Optional[str] = None
    raw_data: Optional[str] = None
    recorded_at: Optional[str] = None

    @classmethod
    def from_api_response(cls, host_id: str, data: Dict[str, Any]) -> "HostStatus":
        """
        Create HostStatus from UniFi API response.

        Args:
            host_id: Host identifier
            data: Raw API response dictionary

        Returns:
            HostStatus instance
        """
        # Determine status from API data
        is_online = data.get("isOnline", False)
        status = "online" if is_online else "offline"

        # Extract metrics if available
        cpu_usage = None
        memory_usage = None
        temperature = None

        if "metrics" in data:
            metrics = data["metrics"]
            cpu_usage = metrics.get("cpu")
            memory_usage = metrics.get("memory")
            temperature = metrics.get("temperature")

        return cls(
            host_id=host_id,
            status=status,
            is_online=is_online,
            uptime_seconds=data.get("uptimeSeconds"),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            temperature=temperature,
            last_connection_change=data.get("lastConnectionStateChange"),
            last_backup_time=data.get("latestBackupTime"),
            raw_data=json.dumps(data),
        )

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "HostStatus":
        """
        Create HostStatus from database row.

        Args:
            row: Database row as dictionary

        Returns:
            HostStatus instance
        """
        return cls(
            id=row.get("id"),
            host_id=row["host_id"],
            status=row["status"],
            is_online=(
                bool(row.get("is_online")) if row.get("is_online") is not None else None
            ),
            uptime_seconds=row.get("uptime_seconds"),
            cpu_usage=row.get("cpu_usage"),
            memory_usage=row.get("memory_usage"),
            temperature=row.get("temperature"),
            last_connection_change=row.get("last_connection_change"),
            last_backup_time=row.get("last_backup_time"),
            error_message=row.get("error_message"),
            raw_data=row.get("raw_data"),
            recorded_at=row.get("recorded_at"),
        )

    def to_db_params(self) -> tuple:
        """
        Convert to database parameters tuple for INSERT.

        Returns:
            Tuple of values for database operation
        """
        return (
            self.host_id,
            self.status,
            int(self.is_online) if self.is_online is not None else None,
            self.uptime_seconds,
            self.cpu_usage,
            self.memory_usage,
            self.temperature,
            self.last_connection_change,
            self.last_backup_time,
            self.error_message,
            self.raw_data,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"HostStatus(host_id='{self.host_id}', "
            f"status='{self.status}', "
            f"is_online={self.is_online})"
        )


@dataclass
class Event:
    """
    Event model for tracking significant occurrences.

    Attributes:
        event_type: Type of event (status_change, error, alert, reboot)
        severity: Severity level (info, warning, error, critical)
        title: Event title
        id: Event record ID (auto-increment)
        host_id: Foreign key to hosts table (optional)
        description: Detailed event description
        previous_value: Previous value (for changes)
        new_value: New value (for changes)
        metadata: Additional JSON metadata
        created_at: When event was created
    """

    event_type: str
    severity: str
    title: str
    id: Optional[int] = None
    host_id: Optional[str] = None
    description: Optional[str] = None
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    metadata: Optional[str] = None
    created_at: Optional[str] = None

    @classmethod
    def create_status_change(
        cls, host_id: str, old_status: str, new_status: str, severity: str = "info"
    ) -> "Event":
        """
        Create a status change event.

        Args:
            host_id: Host identifier
            old_status: Previous status
            new_status: New status
            severity: Event severity

        Returns:
            Event instance
        """
        return cls(
            event_type="status_change",
            severity=severity,
            title=f"Status changed: {old_status} → {new_status}",
            host_id=host_id,
            description=f"Host status changed from {old_status} to {new_status}",
            previous_value=old_status,
            new_value=new_status,
        )

    @classmethod
    def create_error(
        cls, host_id: str, title: str, description: str, severity: str = "error"
    ) -> "Event":
        """
        Create an error event.

        Args:
            host_id: Host identifier
            title: Error title
            description: Error description
            severity: Event severity

        Returns:
            Event instance
        """
        return cls(
            event_type="error",
            severity=severity,
            title=title,
            host_id=host_id,
            description=description,
        )

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "Event":
        """
        Create Event from database row.

        Args:
            row: Database row as dictionary

        Returns:
            Event instance
        """
        return cls(
            id=row.get("id"),
            host_id=row.get("host_id"),
            event_type=row["event_type"],
            severity=row["severity"],
            title=row["title"],
            description=row.get("description"),
            previous_value=row.get("previous_value"),
            new_value=row.get("new_value"),
            metadata=row.get("metadata"),
            created_at=row.get("created_at"),
        )

    def to_db_params(self) -> tuple:
        """
        Convert to database parameters tuple for INSERT.

        Returns:
            Tuple of values for database operation
        """
        return (
            self.host_id,
            self.event_type,
            self.severity,
            self.title,
            self.description,
            self.previous_value,
            self.new_value,
            self.metadata,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Event(type='{self.event_type}', "
            f"severity='{self.severity}', "
            f"title='{self.title}')"
        )


@dataclass
class Metric:
    """
    Metric model for time-series data.

    Attributes:
        host_id: Foreign key to hosts table
        metric_name: Name of the metric
        metric_value: Numeric value
        id: Metric record ID (auto-increment)
        unit: Unit of measurement
        recorded_at: When metric was recorded
    """

    host_id: str
    metric_name: str
    metric_value: float
    id: Optional[int] = None
    unit: Optional[str] = None
    recorded_at: Optional[str] = None

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "Metric":
        """
        Create Metric from database row.

        Args:
            row: Database row as dictionary

        Returns:
            Metric instance
        """
        return cls(
            id=row.get("id"),
            host_id=row["host_id"],
            metric_name=row["metric_name"],
            metric_value=row["metric_value"],
            unit=row.get("unit"),
            recorded_at=row.get("recorded_at"),
        )

    def to_db_params(self) -> tuple:
        """
        Convert to database parameters tuple for INSERT.

        Returns:
            Tuple of values for database operation
        """
        return (
            self.host_id,
            self.metric_name,
            self.metric_value,
            self.unit,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def __repr__(self) -> str:
        """String representation."""
        unit_str = f" {self.unit}" if self.unit else ""
        return (
            f"Metric(host_id='{self.host_id}', "
            f"{self.metric_name}={self.metric_value}{unit_str})"
        )


@dataclass
class CollectionRun:
    """
    Collection run model for tracking data collection execution.

    Attributes:
        start_time: When collection started
        status: Run status (running, success, failed)
        id: Run record ID (auto-increment)
        end_time: When collection ended
        hosts_collected: Number of hosts collected
        errors_encountered: Number of errors
        error_message: Error message if failed
        duration_seconds: Run duration
        created_at: Record creation time
    """

    start_time: str
    status: str
    id: Optional[int] = None
    end_time: Optional[str] = None
    hosts_collected: int = 0
    errors_encountered: int = 0
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    created_at: Optional[str] = None

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "CollectionRun":
        """
        Create CollectionRun from database row.

        Args:
            row: Database row as dictionary

        Returns:
            CollectionRun instance
        """
        return cls(
            id=row.get("id"),
            start_time=row["start_time"],
            end_time=row.get("end_time"),
            status=row["status"],
            hosts_collected=row.get("hosts_collected", 0),
            errors_encountered=row.get("errors_encountered", 0),
            error_message=row.get("error_message"),
            duration_seconds=row.get("duration_seconds"),
            created_at=row.get("created_at"),
        )

    def to_db_params(self) -> tuple:
        """
        Convert to database parameters tuple for INSERT.

        Returns:
            Tuple of values for database operation
        """
        return (
            self.start_time,
            self.status,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CollectionRun(status='{self.status}', "
            f"hosts_collected={self.hosts_collected})"
        )
