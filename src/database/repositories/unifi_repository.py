"""
UniFi repositories for managing UniFi Controller data.

Provides CRUD operations for UniFi devices, clients, events, and metrics.
"""

from typing import Dict, List, Optional, Tuple

from ..models_unifi import (
    UniFiClient,
    UniFiClientStatus,
    UniFiDevice,
    UniFiDeviceStatus,
    UniFiEvent,
)
from .base import BaseRepository


class UniFiDeviceRepository(BaseRepository):
    """Repository for UniFi device operations."""

    table_name = "unifi_devices"

    def create(self, device: UniFiDevice) -> UniFiDevice:
        """
        Create new UniFi device record.

        Args:
            device: UniFiDevice instance to create

        Returns:
            Created UniFiDevice instance with timestamps
        """
        query = """
            INSERT INTO unifi_devices (
                mac, device_id, name, type, model, version, ip, site_name,
                state, adopted, disabled, uptime, satisfaction, num_sta,
                bytes_total, led_override, led_override_color, last_seen
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self.db.transaction():
            self.db.execute(query, device.to_db_params())

        # Fetch the created record with timestamps
        return self.get_by_mac(device.mac)

    def get_by_mac(self, mac: str) -> Optional[UniFiDevice]:
        """
        Get device by MAC address.

        Args:
            mac: Device MAC address

        Returns:
            UniFiDevice instance or None if not found
        """
        query = "SELECT * FROM unifi_devices WHERE mac = ?"
        row = self.db.fetch_one(query, (mac,))

        if row:
            return UniFiDevice.from_db_row(row)
        return None

    def get_by_id(self, device_id: int) -> Optional[UniFiDevice]:
        """
        Get device by database ID.

        Args:
            device_id: Database record ID

        Returns:
            UniFiDevice instance or None if not found
        """
        query = "SELECT * FROM unifi_devices WHERE id = ?"
        row = self.db.fetch_one(query, (device_id,))

        if row:
            return UniFiDevice.from_db_row(row)
        return None

    def get_all(
        self, site_name: Optional[str] = None, limit: Optional[int] = None
    ) -> List[UniFiDevice]:
        """
        Get all devices, optionally filtered by site.

        Args:
            site_name: Optional site name filter
            limit: Optional limit on number of results

        Returns:
            List of UniFiDevice instances
        """
        if site_name:
            query = "SELECT * FROM unifi_devices WHERE site_name = ? ORDER BY name, mac"
            rows = self.db.fetch_all(query, (site_name,))
        else:
            query = "SELECT * FROM unifi_devices ORDER BY name, mac"
            rows = self.db.fetch_all(query)

        if limit:
            rows = rows[:limit]

        return [UniFiDevice.from_db_row(row) for row in rows]

    def get_by_type(
        self, device_type: str, site_name: Optional[str] = None
    ) -> List[UniFiDevice]:
        """
        Get devices by type.

        Args:
            device_type: Device type (usw, uap, ugw, udm, etc.)
            site_name: Optional site name filter

        Returns:
            List of UniFiDevice instances
        """
        if site_name:
            query = """
                SELECT * FROM unifi_devices
                WHERE type = ? AND site_name = ?
                ORDER BY name
            """
            rows = self.db.fetch_all(query, (device_type, site_name))
        else:
            query = "SELECT * FROM unifi_devices WHERE type = ? ORDER BY name"
            rows = self.db.fetch_all(query, (device_type,))

        return [UniFiDevice.from_db_row(row) for row in rows]

    def get_online_devices(self, site_name: Optional[str] = None) -> List[UniFiDevice]:
        """
        Get all online devices.

        Args:
            site_name: Optional site name filter

        Returns:
            List of online UniFiDevice instances
        """
        if site_name:
            query = """
                SELECT * FROM unifi_devices
                WHERE state = 1 AND site_name = ?
                ORDER BY name
            """
            rows = self.db.fetch_all(query, (site_name,))
        else:
            query = "SELECT * FROM unifi_devices WHERE state = 1 ORDER BY name"
            rows = self.db.fetch_all(query)

        return [UniFiDevice.from_db_row(row) for row in rows]

    def update(self, device: UniFiDevice) -> UniFiDevice:
        """
        Update existing device record.

        Args:
            device: UniFiDevice instance with updated data

        Returns:
            Updated UniFiDevice instance
        """
        query = """
            UPDATE unifi_devices SET
                device_id = ?,
                name = ?,
                type = ?,
                model = ?,
                version = ?,
                ip = ?,
                site_name = ?,
                state = ?,
                adopted = ?,
                disabled = ?,
                uptime = ?,
                satisfaction = ?,
                num_sta = ?,
                bytes_total = ?,
                led_override = ?,
                led_override_color = ?,
                last_seen = ?,
                updated_at = datetime('now')
            WHERE mac = ?
        """

        # to_db_params: (mac, device_id, name, ..., last_seen)
        # For UPDATE: (device_id, name, ..., last_seen, mac)
        all_params = device.to_db_params()
        params = all_params[1:] + (all_params[0],)  # Move mac to end

        with self.db.transaction():
            self.db.execute(query, params)

        return self.get_by_mac(device.mac)

    def upsert(self, device: UniFiDevice) -> UniFiDevice:
        """
        Insert or update device record.

        Args:
            device: UniFiDevice instance

        Returns:
            Upserted UniFiDevice instance
        """
        existing = self.get_by_mac(device.mac)
        if existing:
            return self.update(device)
        else:
            return self.create(device)

    def update_state(self, mac: str, state: int) -> bool:
        """
        Update device state (online/offline).

        Args:
            mac: Device MAC address
            state: Connection state (1=online, 0=offline)

        Returns:
            True if updated, False if not found
        """
        if not self.get_by_mac(mac):
            return False

        query = """
            UPDATE unifi_devices
            SET state = ?,
                last_seen = datetime('now'),
                updated_at = datetime('now')
            WHERE mac = ?
        """

        with self.db.transaction():
            self.db.execute(query, (state, mac))

        return True

    def exists_by_mac(self, mac: str) -> bool:
        """
        Check if device exists by MAC address.

        Args:
            mac: Device MAC address

        Returns:
            True if device exists, False otherwise
        """
        query = "SELECT 1 FROM unifi_devices WHERE mac = ? LIMIT 1"
        result = self.db.fetch_one(query, (mac,))
        return result is not None


class UniFiDeviceStatusRepository(BaseRepository):
    """Repository for UniFi device status history."""

    table_name = "unifi_device_status"

    def create(self, status: UniFiDeviceStatus) -> UniFiDeviceStatus:
        """
        Create new device status record.

        Args:
            status: UniFiDeviceStatus instance to create

        Returns:
            Created UniFiDeviceStatus instance
        """
        query = """
            INSERT INTO unifi_device_status (
                device_mac, state, uptime, cpu_usage, memory_usage,
                temperature, num_clients, satisfaction, bytes_rx,
                bytes_tx, port_stats, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self.db.transaction():
            cursor = self.db.execute(query, status.to_db_params())
            status.id = cursor.lastrowid

        return status

    def get_latest_by_device(self, device_mac: str) -> Optional[UniFiDeviceStatus]:
        """
        Get latest status for a device.

        Args:
            device_mac: Device MAC address

        Returns:
            Latest UniFiDeviceStatus or None
        """
        query = """
            SELECT * FROM unifi_device_status
            WHERE device_mac = ?
            ORDER BY recorded_at DESC
            LIMIT 1
        """
        row = self.db.fetch_one(query, (device_mac,))

        if row:
            return UniFiDeviceStatus.from_db_row(row)
        return None

    def get_history(
        self,
        device_mac: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: Optional[int] = 100,
    ) -> List[UniFiDeviceStatus]:
        """
        Get status history for a device.

        Args:
            device_mac: Device MAC address
            start_time: Optional start time (ISO format)
            end_time: Optional end time (ISO format)
            limit: Maximum number of records to return

        Returns:
            List of UniFiDeviceStatus instances
        """
        query = "SELECT * FROM unifi_device_status WHERE device_mac = ?"
        params = [device_mac]

        if start_time:
            query += " AND recorded_at >= ?"
            params.append(start_time)

        if end_time:
            query += " AND recorded_at <= ?"
            params.append(end_time)

        query += " ORDER BY recorded_at DESC"

        if limit:
            query += f" LIMIT {limit}"

        rows = self.db.fetch_all(query, tuple(params))
        return [UniFiDeviceStatus.from_db_row(row) for row in rows]

    def get_uptime_stats(
        self, device_mac: str, days: int = 7
    ) -> Optional[Dict[str, float]]:
        """
        Calculate uptime statistics for a device.

        Args:
            device_mac: Device MAC address
            days: Number of days to analyze

        Returns:
            Dictionary with uptime statistics or None
        """
        query = """
            SELECT
                COUNT(*) as total_checks,
                SUM(CASE WHEN state = 1 THEN 1 ELSE 0 END) as online_checks,
                AVG(CASE WHEN state = 1 THEN uptime ELSE 0 END) as avg_uptime,
                MAX(uptime) as max_uptime
            FROM unifi_device_status
            WHERE device_mac = ?
                AND recorded_at >= datetime('now', '-' || ? || ' days')
        """

        row = self.db.fetch_one(query, (device_mac, days))

        if row and row["total_checks"] > 0:
            uptime_pct = (row["online_checks"] / row["total_checks"]) * 100
            return {
                "uptime_percentage": uptime_pct,
                "total_checks": row["total_checks"],
                "online_checks": row["online_checks"],
                "offline_checks": row["total_checks"] - row["online_checks"],
                "avg_uptime_seconds": row["avg_uptime"],
                "max_uptime_seconds": row["max_uptime"],
            }

        return None


class UniFiClientRepository(BaseRepository):
    """Repository for UniFi client operations."""

    table_name = "unifi_clients"

    def create(self, client: UniFiClient) -> UniFiClient:
        """
        Create new UniFi client record.

        Args:
            client: UniFiClient instance to create

        Returns:
            Created UniFiClient instance with timestamps
        """
        query = """
            INSERT INTO unifi_clients (
                mac, client_id, hostname, name, ip, site_name,
                is_wired, is_guest, blocked, essid, channel,
                ap_mac, ap_name, sw_mac, sw_port, network,
                usergroup_id, use_fixedip, oui, first_seen, last_seen
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self.db.transaction():
            self.db.execute(query, client.to_db_params())

        # Fetch the created record with timestamps
        return self.get_by_mac(client.mac)

    def get_by_mac(self, mac: str) -> Optional[UniFiClient]:
        """
        Get client by MAC address.

        Args:
            mac: Client MAC address

        Returns:
            UniFiClient instance or None if not found
        """
        query = "SELECT * FROM unifi_clients WHERE mac = ?"
        row = self.db.fetch_one(query, (mac,))

        if row:
            return UniFiClient.from_db_row(row)
        return None

    def get_all(
        self, site_name: Optional[str] = None, limit: Optional[int] = None
    ) -> List[UniFiClient]:
        """
        Get all clients, optionally filtered by site.

        Args:
            site_name: Optional site name filter
            limit: Optional limit on number of results

        Returns:
            List of UniFiClient instances
        """
        if site_name:
            query = """
                SELECT * FROM unifi_clients
                WHERE site_name = ?
                ORDER BY last_seen DESC, hostname
            """
            rows = self.db.fetch_all(query, (site_name,))
        else:
            query = "SELECT * FROM unifi_clients ORDER BY last_seen DESC, hostname"
            rows = self.db.fetch_all(query)

        if limit:
            rows = rows[:limit]

        return [UniFiClient.from_db_row(row) for row in rows]

    def get_by_connection_type(
        self, is_wired: bool, site_name: Optional[str] = None
    ) -> List[UniFiClient]:
        """
        Get clients by connection type (wired/wireless).

        Args:
            is_wired: True for wired, False for wireless
            site_name: Optional site name filter

        Returns:
            List of UniFiClient instances
        """
        if site_name:
            query = """
                SELECT * FROM unifi_clients
                WHERE is_wired = ? AND site_name = ?
                ORDER BY last_seen DESC
            """
            rows = self.db.fetch_all(query, (int(is_wired), site_name))
        else:
            query = """
                SELECT * FROM unifi_clients
                WHERE is_wired = ?
                ORDER BY last_seen DESC
            """
            rows = self.db.fetch_all(query, (int(is_wired),))

        return [UniFiClient.from_db_row(row) for row in rows]

    def get_by_ap(self, ap_mac: str) -> List[UniFiClient]:
        """
        Get clients connected to a specific AP.

        Args:
            ap_mac: Access Point MAC address

        Returns:
            List of UniFiClient instances
        """
        query = """
            SELECT * FROM unifi_clients
            WHERE ap_mac = ?
            ORDER BY last_seen DESC
        """
        rows = self.db.fetch_all(query, (ap_mac,))
        return [UniFiClient.from_db_row(row) for row in rows]

    def get_by_switch(self, sw_mac: str) -> List[UniFiClient]:
        """
        Get clients connected to a specific switch.

        Args:
            sw_mac: Switch MAC address

        Returns:
            List of UniFiClient instances
        """
        query = """
            SELECT * FROM unifi_clients
            WHERE sw_mac = ?
            ORDER BY sw_port, last_seen DESC
        """
        rows = self.db.fetch_all(query, (sw_mac,))
        return [UniFiClient.from_db_row(row) for row in rows]

    def get_recently_seen(
        self, hours: int = 24, site_name: Optional[str] = None
    ) -> List[UniFiClient]:
        """
        Get clients seen within the last N hours.

        Args:
            hours: Number of hours to look back
            site_name: Optional site name filter

        Returns:
            List of UniFiClient instances
        """
        if site_name:
            query = """
                SELECT * FROM unifi_clients
                WHERE last_seen >= datetime('now', '-' || ? || ' hours')
                    AND site_name = ?
                ORDER BY last_seen DESC
            """
            rows = self.db.fetch_all(query, (hours, site_name))
        else:
            query = """
                SELECT * FROM unifi_clients
                WHERE last_seen >= datetime('now', '-' || ? || ' hours')
                ORDER BY last_seen DESC
            """
            rows = self.db.fetch_all(query, (hours,))

        return [UniFiClient.from_db_row(row) for row in rows]

    def update(self, client: UniFiClient) -> UniFiClient:
        """
        Update existing client record.

        Args:
            client: UniFiClient instance with updated data

        Returns:
            Updated UniFiClient instance
        """
        query = """
            UPDATE unifi_clients SET
                client_id = ?,
                hostname = ?,
                name = ?,
                ip = ?,
                site_name = ?,
                is_wired = ?,
                is_guest = ?,
                blocked = ?,
                essid = ?,
                channel = ?,
                ap_mac = ?,
                ap_name = ?,
                sw_mac = ?,
                sw_port = ?,
                network = ?,
                usergroup_id = ?,
                use_fixedip = ?,
                oui = ?,
                first_seen = ?,
                last_seen = ?,
                updated_at = datetime('now')
            WHERE mac = ?
        """

        # to_db_params: (mac, client_id, hostname, ..., last_seen)
        # For UPDATE: (client_id, hostname, ..., last_seen, mac)
        all_params = client.to_db_params()
        params = all_params[1:] + (all_params[0],)  # Move mac to end

        with self.db.transaction():
            self.db.execute(query, params)

        return self.get_by_mac(client.mac)

    def upsert(self, client: UniFiClient) -> UniFiClient:
        """
        Insert or update client record.

        Args:
            client: UniFiClient instance

        Returns:
            Upserted UniFiClient instance
        """
        existing = self.get_by_mac(client.mac)
        if existing:
            return self.update(client)
        else:
            return self.create(client)

    def exists_by_mac(self, mac: str) -> bool:
        """
        Check if client exists by MAC address.

        Args:
            mac: Client MAC address

        Returns:
            True if client exists, False otherwise
        """
        query = "SELECT 1 FROM unifi_clients WHERE mac = ? LIMIT 1"
        result = self.db.fetch_one(query, (mac,))
        return result is not None


class UniFiClientStatusRepository(BaseRepository):
    """Repository for UniFi client status history."""

    table_name = "unifi_client_status"

    def create(self, status: UniFiClientStatus) -> UniFiClientStatus:
        """
        Create new client status record.

        Args:
            status: UniFiClientStatus instance to create

        Returns:
            Created UniFiClientStatus instance
        """
        query = """
            INSERT INTO unifi_client_status (
                client_mac, ip, is_wired, signal, noise, rssi,
                tx_bytes, rx_bytes, tx_rate, rx_rate, uptime,
                satisfaction, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self.db.transaction():
            cursor = self.db.execute(query, status.to_db_params())
            status.id = cursor.lastrowid

        return status

    def get_latest_by_client(self, client_mac: str) -> Optional[UniFiClientStatus]:
        """
        Get latest status for a client.

        Args:
            client_mac: Client MAC address

        Returns:
            Latest UniFiClientStatus or None
        """
        query = """
            SELECT * FROM unifi_client_status
            WHERE client_mac = ?
            ORDER BY recorded_at DESC
            LIMIT 1
        """
        row = self.db.fetch_one(query, (client_mac,))

        if row:
            return UniFiClientStatus.from_db_row(row)
        return None

    def get_history(
        self,
        client_mac: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: Optional[int] = 100,
    ) -> List[UniFiClientStatus]:
        """
        Get status history for a client.

        Args:
            client_mac: Client MAC address
            start_time: Optional start time (ISO format)
            end_time: Optional end time (ISO format)
            limit: Maximum number of records to return

        Returns:
            List of UniFiClientStatus instances
        """
        query = "SELECT * FROM unifi_client_status WHERE client_mac = ?"
        params = [client_mac]

        if start_time:
            query += " AND recorded_at >= ?"
            params.append(start_time)

        if end_time:
            query += " AND recorded_at <= ?"
            params.append(end_time)

        query += " ORDER BY recorded_at DESC"

        if limit:
            query += f" LIMIT {limit}"

        rows = self.db.fetch_all(query, tuple(params))
        return [UniFiClientStatus.from_db_row(row) for row in rows]

    def get_signal_stats(
        self, client_mac: str, hours: int = 24
    ) -> Optional[Dict[str, float]]:
        """
        Calculate signal statistics for a wireless client.

        Args:
            client_mac: Client MAC address
            hours: Number of hours to analyze

        Returns:
            Dictionary with signal statistics or None
        """
        query = """
            SELECT
                AVG(signal) as avg_signal,
                MIN(signal) as min_signal,
                MAX(signal) as max_signal,
                AVG(rssi) as avg_rssi,
                AVG(tx_rate) as avg_tx_rate,
                AVG(rx_rate) as avg_rx_rate
            FROM unifi_client_status
            WHERE client_mac = ?
                AND is_wired = 0
                AND signal IS NOT NULL
                AND recorded_at >= datetime('now', '-' || ? || ' hours')
        """

        row = self.db.fetch_one(query, (client_mac, hours))

        if row and row["avg_signal"] is not None:
            return {
                "avg_signal_dbm": row["avg_signal"],
                "min_signal_dbm": row["min_signal"],
                "max_signal_dbm": row["max_signal"],
                "avg_rssi": row["avg_rssi"],
                "avg_tx_rate_kbps": row["avg_tx_rate"],
                "avg_rx_rate_kbps": row["avg_rx_rate"],
            }

        return None


class UniFiEventRepository(BaseRepository):
    """Repository for UniFi events."""

    table_name = "unifi_events"

    def create(self, event: UniFiEvent) -> UniFiEvent:
        """
        Create new event record.

        Args:
            event: UniFiEvent instance to create

        Returns:
            Created UniFiEvent instance with timestamp
        """
        query = """
            INSERT INTO unifi_events (
                device_mac, client_mac, event_type, severity,
                title, description, previous_value, new_value, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self.db.transaction():
            cursor = self.db.execute(query, event.to_db_params())
            event.id = cursor.lastrowid

        # Fetch with created_at timestamp
        return self.get_by_id(event.id)

    def get_by_id(self, event_id: int) -> Optional[UniFiEvent]:
        """
        Get event by ID.

        Args:
            event_id: Event ID

        Returns:
            UniFiEvent instance or None
        """
        query = "SELECT * FROM unifi_events WHERE id = ?"
        row = self.db.fetch_one(query, (event_id,))

        if row:
            return UniFiEvent.from_db_row(row)
        return None

    def get_recent(
        self,
        limit: int = 100,
        severity: Optional[str] = None,
        event_type: Optional[str] = None,
    ) -> List[UniFiEvent]:
        """
        Get recent events with optional filtering.

        Args:
            limit: Maximum number of events to return
            severity: Optional severity filter (info, warning, error, critical)
            event_type: Optional event type filter

        Returns:
            List of UniFiEvent instances
        """
        query = "SELECT * FROM unifi_events WHERE 1=1"
        params = []

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        rows = self.db.fetch_all(query, tuple(params))
        return [UniFiEvent.from_db_row(row) for row in rows]

    def get_by_device(self, device_mac: str, limit: int = 50) -> List[UniFiEvent]:
        """
        Get events for a specific device.

        Args:
            device_mac: Device MAC address
            limit: Maximum number of events to return

        Returns:
            List of UniFiEvent instances
        """
        query = """
            SELECT * FROM unifi_events
            WHERE device_mac = ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (device_mac, limit))
        return [UniFiEvent.from_db_row(row) for row in rows]

    def get_by_client(self, client_mac: str, limit: int = 50) -> List[UniFiEvent]:
        """
        Get events for a specific client.

        Args:
            client_mac: Client MAC address
            limit: Maximum number of events to return

        Returns:
            List of UniFiEvent instances
        """
        query = """
            SELECT * FROM unifi_events
            WHERE client_mac = ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (client_mac, limit))
        return [UniFiEvent.from_db_row(row) for row in rows]

    def get_by_time_range(
        self,
        start_time: str,
        end_time: str,
        severity: Optional[str] = None,
    ) -> List[UniFiEvent]:
        """
        Get events within a time range.

        Args:
            start_time: Start time (ISO format)
            end_time: End time (ISO format)
            severity: Optional severity filter

        Returns:
            List of UniFiEvent instances
        """
        query = """
            SELECT * FROM unifi_events
            WHERE created_at >= ? AND created_at <= ?
        """
        params = [start_time, end_time]

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        query += " ORDER BY created_at DESC"

        rows = self.db.fetch_all(query, tuple(params))
        return [UniFiEvent.from_db_row(row) for row in rows]


class UniFiMetricsRepository(BaseRepository):
    """Repository for UniFi metrics (time-series data)."""

    def create_device_metric(
        self, device_mac: str, metric_name: str, metric_value: float, unit: str
    ) -> int:
        """
        Create a device metric record.

        Args:
            device_mac: Device MAC address
            metric_name: Metric name
            metric_value: Metric value
            unit: Unit of measurement

        Returns:
            Record ID
        """
        query = """
            INSERT INTO unifi_device_metrics (
                device_mac, metric_name, metric_value, unit
            ) VALUES (?, ?, ?, ?)
        """

        with self.db.transaction():
            cursor = self.db.execute(
                query, (device_mac, metric_name, metric_value, unit)
            )
            return cursor.lastrowid

    def create_client_metric(
        self, client_mac: str, metric_name: str, metric_value: float, unit: str
    ) -> int:
        """
        Create a client metric record.

        Args:
            client_mac: Client MAC address
            metric_name: Metric name
            metric_value: Metric value
            unit: Unit of measurement

        Returns:
            Record ID
        """
        query = """
            INSERT INTO unifi_client_metrics (
                client_mac, metric_name, metric_value, unit
            ) VALUES (?, ?, ?, ?)
        """

        with self.db.transaction():
            cursor = self.db.execute(
                query, (client_mac, metric_name, metric_value, unit)
            )
            return cursor.lastrowid

    def get_device_metrics(
        self,
        device_mac: str,
        metric_name: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Tuple[str, str, float, str]]:
        """
        Get device metrics.

        Args:
            device_mac: Device MAC address
            metric_name: Optional metric name filter
            start_time: Optional start time (ISO format)
            end_time: Optional end time (ISO format)
            limit: Maximum number of records

        Returns:
            List of tuples (recorded_at, metric_name, metric_value, unit)
        """
        query = "SELECT recorded_at, metric_name, metric_value, unit FROM unifi_device_metrics WHERE device_mac = ?"
        params = [device_mac]

        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)

        if start_time:
            query += " AND recorded_at >= ?"
            params.append(start_time)

        if end_time:
            query += " AND recorded_at <= ?"
            params.append(end_time)

        query += f" ORDER BY recorded_at DESC LIMIT {limit}"

        rows = self.db.fetch_all(query, tuple(params))
        return [
            (r["recorded_at"], r["metric_name"], r["metric_value"], r["unit"])
            for r in rows
        ]

    def get_client_metrics(
        self,
        client_mac: str,
        metric_name: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Tuple[str, str, float, str]]:
        """
        Get client metrics.

        Args:
            client_mac: Client MAC address
            metric_name: Optional metric name filter
            start_time: Optional start time (ISO format)
            end_time: Optional end time (ISO format)
            limit: Maximum number of records

        Returns:
            List of tuples (recorded_at, metric_name, metric_value, unit)
        """
        query = "SELECT recorded_at, metric_name, metric_value, unit FROM unifi_client_metrics WHERE client_mac = ?"
        params = [client_mac]

        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)

        if start_time:
            query += " AND recorded_at >= ?"
            params.append(start_time)

        if end_time:
            query += " AND recorded_at <= ?"
            params.append(end_time)

        query += f" ORDER BY recorded_at DESC LIMIT {limit}"

        rows = self.db.fetch_all(query, tuple(params))
        return [
            (r["recorded_at"], r["metric_name"], r["metric_value"], r["unit"])
            for r in rows
        ]


class UniFiCollectionRunRepository(BaseRepository):
    """Repository for UniFi collection run tracking."""

    table_name = "unifi_collection_runs"

    def create_run(self, controller_host: str) -> int:
        """
        Create a new collection run record.

        Args:
            controller_host: Controller hostname or IP

        Returns:
            Run ID
        """
        query = """
            INSERT INTO unifi_collection_runs (
                controller_host, start_time, status
            ) VALUES (?, datetime('now'), 'running')
        """

        with self.db.transaction():
            cursor = self.db.execute(query, (controller_host,))
            return cursor.lastrowid if cursor.lastrowid is not None else 0

    def complete_run(
        self,
        run_id: int,
        devices_collected: int,
        clients_collected: int,
        errors_encountered: int = 0,
        error_message: Optional[str] = None,
    ) -> bool:
        """
        Mark a collection run as completed.

        Args:
            run_id: Run ID
            devices_collected: Number of devices collected
            clients_collected: Number of clients collected
            errors_encountered: Number of errors
            error_message: Optional error message

        Returns:
            True if updated successfully
        """
        query = """
            UPDATE unifi_collection_runs SET
                end_time = datetime('now'),
                status = ?,
                devices_collected = ?,
                clients_collected = ?,
                errors_encountered = ?,
                error_message = ?,
                duration_seconds = (
                    julianday(datetime('now')) - julianday(start_time)
                ) * 86400
            WHERE id = ?
        """

        status = "completed" if errors_encountered == 0 else "completed_with_errors"

        with self.db.transaction():
            self.db.execute(
                query,
                (
                    status,
                    devices_collected,
                    clients_collected,
                    errors_encountered,
                    error_message,
                    run_id,
                ),
            )

        return True

    def fail_run(self, run_id: int, error_message: str) -> bool:
        """
        Mark a collection run as failed.

        Args:
            run_id: Run ID
            error_message: Error message

        Returns:
            True if updated successfully
        """
        query = """
            UPDATE unifi_collection_runs SET
                end_time = datetime('now'),
                status = 'failed',
                error_message = ?,
                duration_seconds = (
                    julianday(datetime('now')) - julianday(start_time)
                ) * 86400
            WHERE id = ?
        """

        with self.db.transaction():
            self.db.execute(query, (error_message, run_id))

        return True

    def get_recent_runs(self, limit: int = 20) -> List[Dict[str, any]]:
        """
        Get recent collection runs.

        Args:
            limit: Maximum number of runs to return

        Returns:
            List of run dictionaries
        """
        query = """
            SELECT * FROM unifi_collection_runs
            ORDER BY start_time DESC
            LIMIT ?
        """
        return self.db.fetch_all(query, (limit,))

    def get_run_stats(self, hours: int = 24) -> Optional[Dict[str, any]]:
        """
        Get collection run statistics.

        Args:
            hours: Number of hours to analyze

        Returns:
            Dictionary with statistics or None
        """
        query = """
            SELECT
                COUNT(*) as total_runs,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_runs,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_runs,
                AVG(duration_seconds) as avg_duration,
                SUM(devices_collected) as total_devices,
                SUM(clients_collected) as total_clients
            FROM unifi_collection_runs
            WHERE start_time >= datetime('now', '-' || ? || ' hours')
        """

        row = self.db.fetch_one(query, (hours,))

        if row and row["total_runs"] > 0:
            return dict(row)

        return None
