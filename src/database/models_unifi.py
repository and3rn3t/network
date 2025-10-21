"""
Data models for UniFi Local Controller integration.

Provides typed data classes for UniFi devices, clients, and their status
with validation and serialization methods compatible with the existing
database schema.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class UniFiDevice:
    """
    UniFi device model representing a network device from local controller.

    Supports switches, access points, gateways, UDM, and other UniFi devices.

    Attributes:
        mac: Device MAC address (primary identifier)
        device_id: UniFi internal device ID
        name: Device name
        type: Device type (usw, uap, ugw, udm, uxg, ubb)
        model: Device model (e.g., US8P150, UAP-AC-PRO)
        version: Firmware version
        ip: IP address
        site_name: Site name
        state: Connection state (1=online, 0=offline)
        adopted: Is device adopted
        disabled: Is device disabled
        uptime: Uptime in seconds
        satisfaction: Client satisfaction (0-100)
        num_sta: Number of connected clients (APs only)
        bytes_total: Total bytes transferred
        led_override: LED override setting
        led_override_color: LED color if overridden
        last_seen: Last seen timestamp
        first_seen: First seen in database
        id: Database record ID (auto-increment)
        created_at: Record creation time
        updated_at: Record update time
    """

    mac: str
    device_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    model: Optional[str] = None
    version: Optional[str] = None
    ip: Optional[str] = None
    site_name: str = "default"
    state: Optional[int] = None
    adopted: bool = False
    disabled: bool = False
    uptime: Optional[int] = None
    satisfaction: Optional[int] = None
    num_sta: int = 0
    bytes_total: int = 0
    led_override: str = "default"
    led_override_color: Optional[str] = None
    last_seen: Optional[str] = None
    first_seen: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_controller_response(
        cls, data: Dict[str, Any], site: str = "default"
    ) -> "UniFiDevice":
        """
        Create UniFiDevice from UniFi Controller API response.

        Args:
            data: Raw API response dictionary
            site: Site name (default: 'default')

        Returns:
            UniFiDevice instance
        """
        return cls(
            mac=data.get("mac", ""),
            device_id=data.get("_id"),
            name=data.get("name"),
            type=data.get("type"),
            model=data.get("model"),
            version=data.get("version"),
            ip=data.get("ip"),
            site_name=site,
            state=data.get("state"),
            adopted=data.get("adopted", False),
            disabled=data.get("disabled", False),
            uptime=data.get("uptime"),
            satisfaction=data.get("satisfaction"),
            num_sta=data.get("num_sta", 0),
            bytes_total=data.get("bytes", 0),
            led_override=data.get("led_override", "default"),
            led_override_color=data.get("led_override_color"),
            last_seen=(
                datetime.fromtimestamp(data["last_seen"]).isoformat()
                if data.get("last_seen")
                else None
            ),
        )

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "UniFiDevice":
        """
        Create UniFiDevice from database row.

        Args:
            row: Database row as dictionary

        Returns:
            UniFiDevice instance
        """
        return cls(
            id=row.get("id"),
            mac=row["mac"],
            device_id=row.get("device_id"),
            name=row.get("name"),
            type=row.get("type"),
            model=row.get("model"),
            version=row.get("version"),
            ip=row.get("ip"),
            site_name=row.get("site_name", "default"),
            state=row.get("state"),
            adopted=bool(row.get("adopted", 0)),
            disabled=bool(row.get("disabled", 0)),
            uptime=row.get("uptime"),
            satisfaction=row.get("satisfaction"),
            num_sta=row.get("num_sta", 0),
            bytes_total=row.get("bytes_total", 0),
            led_override=row.get("led_override", "default"),
            led_override_color=row.get("led_override_color"),
            last_seen=row.get("last_seen"),
            first_seen=row.get("first_seen"),
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
            self.mac,
            self.device_id,
            self.name,
            self.type,
            self.model,
            self.version,
            self.ip,
            self.site_name,
            self.state,
            int(self.adopted),
            int(self.disabled),
            self.uptime,
            self.satisfaction,
            self.num_sta,
            self.bytes_total,
            self.led_override,
            self.led_override_color,
            self.last_seen,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def is_online(self) -> bool:
        """Check if device is online."""
        return self.state == 1

    def __repr__(self) -> str:
        """String representation."""
        status = "online" if self.is_online() else "offline"
        return f"UniFiDevice(mac='{self.mac}', name='{self.name}', type='{self.type}', {status})"


@dataclass
class UniFiDeviceStatus:
    """
    UniFi device status model for tracking device metrics over time.

    Attributes:
        device_mac: Foreign key to unifi_devices.mac
        state: Connection state (1=online, 0=offline)
        uptime: Uptime in seconds
        cpu_usage: CPU usage percentage
        memory_usage: Memory usage percentage
        temperature: Temperature in Celsius
        num_clients: Number of connected clients
        satisfaction: Client satisfaction score
        bytes_rx: Bytes received
        bytes_tx: Bytes transmitted
        port_stats: JSON string with port-level statistics
        raw_data: Full JSON response from API
        recorded_at: When this status was recorded
        id: Database record ID (auto-increment)
    """

    device_mac: str
    state: int
    uptime: Optional[int] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    temperature: Optional[float] = None
    num_clients: int = 0
    satisfaction: Optional[int] = None
    bytes_rx: int = 0
    bytes_tx: int = 0
    port_stats: Optional[str] = None
    raw_data: Optional[str] = None
    recorded_at: Optional[str] = None
    id: Optional[int] = None

    @classmethod
    def from_controller_response(
        cls, device_mac: str, data: Dict[str, Any]
    ) -> "UniFiDeviceStatus":
        """
        Create UniFiDeviceStatus from UniFi Controller API response.

        Args:
            device_mac: Device MAC address
            data: Raw API response dictionary

        Returns:
            UniFiDeviceStatus instance
        """
        # Extract port stats for switches
        port_stats = None
        if "port_table" in data:
            port_stats = json.dumps(data["port_table"])

        # Extract system stats if available
        cpu_usage = data.get("system-stats", {}).get("cpu")
        memory_usage = data.get("system-stats", {}).get("mem")
        temperature = data.get("general_temperature")

        # Calculate bytes
        bytes_rx = data.get("rx_bytes", 0)
        bytes_tx = data.get("tx_bytes", 0)

        return cls(
            device_mac=device_mac,
            state=data.get("state", 0),
            uptime=data.get("uptime"),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            temperature=temperature,
            num_clients=data.get("num_sta", 0),
            satisfaction=data.get("satisfaction"),
            bytes_rx=bytes_rx,
            bytes_tx=bytes_tx,
            port_stats=port_stats,
            raw_data=json.dumps(data),
        )

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "UniFiDeviceStatus":
        """
        Create UniFiDeviceStatus from database row.

        Args:
            row: Database row as dictionary

        Returns:
            UniFiDeviceStatus instance
        """
        return cls(
            id=row.get("id"),
            device_mac=row["device_mac"],
            state=row["state"],
            uptime=row.get("uptime"),
            cpu_usage=row.get("cpu_usage"),
            memory_usage=row.get("memory_usage"),
            temperature=row.get("temperature"),
            num_clients=row.get("num_clients", 0),
            satisfaction=row.get("satisfaction"),
            bytes_rx=row.get("bytes_rx", 0),
            bytes_tx=row.get("bytes_tx", 0),
            port_stats=row.get("port_stats"),
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
            self.device_mac,
            self.state,
            self.uptime,
            self.cpu_usage,
            self.memory_usage,
            self.temperature,
            self.num_clients,
            self.satisfaction,
            self.bytes_rx,
            self.bytes_tx,
            self.port_stats,
            self.raw_data,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def __repr__(self) -> str:
        """String representation."""
        status = "online" if self.state == 1 else "offline"
        return f"UniFiDeviceStatus(mac='{self.device_mac}', {status}, clients={self.num_clients})"


@dataclass
class UniFiClient:
    """
    UniFi client model representing a connected network device.

    Attributes:
        mac: Client MAC address (primary identifier)
        client_id: UniFi internal client ID
        hostname: Client hostname
        name: Friendly name (if set)
        ip: IP address
        site_name: Site name
        is_wired: Wired vs wireless connection
        is_guest: Guest network client
        blocked: Is client blocked
        essid: WiFi SSID (wireless only)
        channel: WiFi channel (wireless only)
        ap_mac: Connected AP MAC (wireless only)
        ap_name: Connected AP name (wireless only)
        sw_mac: Connected switch MAC (wired only)
        sw_port: Connected switch port (wired only)
        network: Network name
        usergroup_id: User group ID
        use_fixedip: Has fixed IP
        oui: Manufacturer (from OUI)
        first_seen: First seen timestamp
        last_seen: Last seen timestamp
        id: Database record ID (auto-increment)
        created_at: Record creation time
        updated_at: Record update time
    """

    mac: str
    client_id: Optional[str] = None
    hostname: Optional[str] = None
    name: Optional[str] = None
    ip: Optional[str] = None
    site_name: str = "default"
    is_wired: bool = False
    is_guest: bool = False
    blocked: bool = False
    essid: Optional[str] = None
    channel: Optional[int] = None
    ap_mac: Optional[str] = None
    ap_name: Optional[str] = None
    sw_mac: Optional[str] = None
    sw_port: Optional[int] = None
    network: Optional[str] = None
    usergroup_id: Optional[str] = None
    use_fixedip: bool = False
    oui: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_controller_response(
        cls, data: Dict[str, Any], site: str = "default"
    ) -> "UniFiClient":
        """
        Create UniFiClient from UniFi Controller API response.

        Args:
            data: Raw API response dictionary
            site: Site name (default: 'default')

        Returns:
            UniFiClient instance
        """
        return cls(
            mac=data.get("mac", ""),
            client_id=data.get("_id"),
            hostname=data.get("hostname"),
            name=data.get("name"),
            ip=data.get("ip"),
            site_name=site,
            is_wired=data.get("is_wired", False),
            is_guest=data.get("is_guest", False),
            blocked=data.get("blocked", False),
            essid=data.get("essid"),
            channel=data.get("channel"),
            ap_mac=data.get("ap_mac"),
            ap_name=data.get("ap_name"),
            sw_mac=data.get("sw_mac"),
            sw_port=data.get("sw_port"),
            network=data.get("network"),
            usergroup_id=data.get("usergroup_id"),
            use_fixedip=data.get("use_fixedip", False),
            oui=data.get("oui"),
            first_seen=(
                datetime.fromtimestamp(data["first_seen"]).isoformat()
                if data.get("first_seen")
                else None
            ),
            last_seen=(
                datetime.fromtimestamp(data["last_seen"]).isoformat()
                if data.get("last_seen")
                else None
            ),
        )

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "UniFiClient":
        """
        Create UniFiClient from database row.

        Args:
            row: Database row as dictionary

        Returns:
            UniFiClient instance
        """
        return cls(
            id=row.get("id"),
            mac=row["mac"],
            client_id=row.get("client_id"),
            hostname=row.get("hostname"),
            name=row.get("name"),
            ip=row.get("ip"),
            site_name=row.get("site_name", "default"),
            is_wired=bool(row.get("is_wired", 0)),
            is_guest=bool(row.get("is_guest", 0)),
            blocked=bool(row.get("blocked", 0)),
            essid=row.get("essid"),
            channel=row.get("channel"),
            ap_mac=row.get("ap_mac"),
            ap_name=row.get("ap_name"),
            sw_mac=row.get("sw_mac"),
            sw_port=row.get("sw_port"),
            network=row.get("network"),
            usergroup_id=row.get("usergroup_id"),
            use_fixedip=bool(row.get("use_fixedip", 0)),
            oui=row.get("oui"),
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
            self.mac,
            self.client_id,
            self.hostname,
            self.name,
            self.ip,
            self.site_name,
            int(self.is_wired),
            int(self.is_guest),
            int(self.blocked),
            self.essid,
            self.channel,
            self.ap_mac,
            self.ap_name,
            self.sw_mac,
            self.sw_port,
            self.network,
            self.usergroup_id,
            int(self.use_fixedip),
            self.oui,
            self.first_seen,
            self.last_seen,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def connection_type(self) -> str:
        """Get connection type description."""
        if self.is_wired:
            return f"Wired (Switch: {self.sw_mac}, Port: {self.sw_port})"
        else:
            return f"Wireless (AP: {self.ap_name}, SSID: {self.essid})"

    def __repr__(self) -> str:
        """String representation."""
        conn = "wired" if self.is_wired else "wireless"
        return f"UniFiClient(mac='{self.mac}', hostname='{self.hostname}', {conn})"


@dataclass
class UniFiClientStatus:
    """
    UniFi client status model for tracking client metrics over time.

    Attributes:
        client_mac: Foreign key to unifi_clients.mac
        ip: IP address at time of recording
        is_wired: Connection type
        signal: Signal strength in dBm (wireless only)
        noise: Noise floor in dBm (wireless only)
        rssi: RSSI value (wireless only)
        tx_bytes: Bytes transmitted
        rx_bytes: Bytes received
        tx_rate: TX rate in Kbps
        rx_rate: RX rate in Kbps
        uptime: Connection uptime in seconds
        satisfaction: Client satisfaction (0-100)
        raw_data: Full JSON response from API
        recorded_at: When this status was recorded
        id: Database record ID (auto-increment)
    """

    client_mac: str
    ip: Optional[str] = None
    is_wired: bool = False
    signal: Optional[int] = None
    noise: Optional[int] = None
    rssi: Optional[int] = None
    tx_bytes: int = 0
    rx_bytes: int = 0
    tx_rate: int = 0
    rx_rate: int = 0
    uptime: Optional[int] = None
    satisfaction: Optional[int] = None
    raw_data: Optional[str] = None
    recorded_at: Optional[str] = None
    id: Optional[int] = None

    @classmethod
    def from_controller_response(
        cls, client_mac: str, data: Dict[str, Any]
    ) -> "UniFiClientStatus":
        """
        Create UniFiClientStatus from UniFi Controller API response.

        Args:
            client_mac: Client MAC address
            data: Raw API response dictionary

        Returns:
            UniFiClientStatus instance
        """
        return cls(
            client_mac=client_mac,
            ip=data.get("ip"),
            is_wired=data.get("is_wired", False),
            signal=data.get("signal"),
            noise=data.get("noise"),
            rssi=data.get("rssi"),
            tx_bytes=data.get("tx_bytes", 0),
            rx_bytes=data.get("rx_bytes", 0),
            tx_rate=data.get("tx_rate", 0),
            rx_rate=data.get("rx_rate", 0),
            uptime=data.get("uptime"),
            satisfaction=data.get("satisfaction"),
            raw_data=json.dumps(data),
        )

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "UniFiClientStatus":
        """
        Create UniFiClientStatus from database row.

        Args:
            row: Database row as dictionary

        Returns:
            UniFiClientStatus instance
        """
        return cls(
            id=row.get("id"),
            client_mac=row["client_mac"],
            ip=row.get("ip"),
            is_wired=bool(row.get("is_wired", 0)),
            signal=row.get("signal"),
            noise=row.get("noise"),
            rssi=row.get("rssi"),
            tx_bytes=row.get("tx_bytes", 0),
            rx_bytes=row.get("rx_bytes", 0),
            tx_rate=row.get("tx_rate", 0),
            rx_rate=row.get("rx_rate", 0),
            uptime=row.get("uptime"),
            satisfaction=row.get("satisfaction"),
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
            self.client_mac,
            self.ip,
            int(self.is_wired),
            self.signal,
            self.noise,
            self.rssi,
            self.tx_bytes,
            self.rx_bytes,
            self.tx_rate,
            self.rx_rate,
            self.uptime,
            self.satisfaction,
            self.raw_data,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def signal_quality(self) -> str:
        """Get signal quality description (wireless only)."""
        if self.is_wired or self.signal is None:
            return "N/A (wired)"

        if self.signal >= -50:
            return "Excellent"
        elif self.signal >= -60:
            return "Good"
        elif self.signal >= -70:
            return "Fair"
        else:
            return "Poor"

    def __repr__(self) -> str:
        """String representation."""
        conn = "wired" if self.is_wired else f"wireless (signal: {self.signal} dBm)"
        return f"UniFiClientStatus(mac='{self.client_mac}', {conn})"


@dataclass
class UniFiEvent:
    """
    UniFi event model for tracking device and client events.

    Attributes:
        event_type: Event type (status_change, connection, disconnection, etc.)
        severity: Event severity (info, warning, error, critical)
        title: Event title
        description: Event description
        device_mac: Related device MAC (if applicable)
        client_mac: Related client MAC (if applicable)
        previous_value: Previous value (for changes)
        new_value: New value (for changes)
        metadata: JSON string with additional data
        created_at: Event creation time
        id: Database record ID (auto-increment)
    """

    event_type: str
    severity: str
    title: str
    description: Optional[str] = None
    device_mac: Optional[str] = None
    client_mac: Optional[str] = None
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    metadata: Optional[str] = None
    created_at: Optional[str] = None
    id: Optional[int] = None

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "UniFiEvent":
        """
        Create UniFiEvent from database row.

        Args:
            row: Database row as dictionary

        Returns:
            UniFiEvent instance
        """
        return cls(
            id=row.get("id"),
            device_mac=row.get("device_mac"),
            client_mac=row.get("client_mac"),
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
            self.device_mac,
            self.client_mac,
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
        return f"UniFiEvent(type='{self.event_type}', severity='{self.severity}', title='{self.title}')"
