"""
Host repository for managing host/device records.

Provides CRUD operations for hosts table.
"""

from typing import List, Optional

from ..models import Host
from .base import BaseRepository


class HostRepository(BaseRepository):
    """Repository for Host model operations."""

    table_name = "hosts"

    def create(self, host: Host) -> Host:
        """
        Create new host record.

        Args:
            host: Host instance to create

        Returns:
            Created Host instance with timestamps
        """
        query = """
            INSERT INTO hosts (
                id, hardware_id, type, ip_address, mac_address,
                name, owner, is_blocked, firmware_version, model,
                registration_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self.db.transaction():
            self.db.execute(query, host.to_db_params())

        # Fetch the created record with timestamps
        return self.get_by_id(host.id)

    def get_by_id(self, host_id: str) -> Optional[Host]:
        """
        Get host by ID.

        Args:
            host_id: Host identifier

        Returns:
            Host instance or None if not found
        """
        query = "SELECT * FROM hosts WHERE id = ?"
        row = self.db.fetch_one(query, (host_id,))

        if row:
            return Host.from_db_row(row)
        return None

    def get_by_hardware_id(self, hardware_id: str) -> Optional[Host]:
        """
        Get host by hardware ID.

        Args:
            hardware_id: Hardware identifier

        Returns:
            Host instance or None if not found
        """
        query = "SELECT * FROM hosts WHERE hardware_id = ?"
        row = self.db.fetch_one(query, (hardware_id,))

        if row:
            return Host.from_db_row(row)
        return None

    def get_all(self, limit: Optional[int] = None) -> List[Host]:
        """
        Get all hosts.

        Args:
            limit: Optional limit on number of results

        Returns:
            List of Host instances
        """
        query = "SELECT * FROM hosts ORDER BY name, id"
        if limit:
            query += f" LIMIT {limit}"

        rows = self.db.fetch_all(query)
        return [Host.from_db_row(row) for row in rows]

    def get_by_type(self, device_type: str) -> List[Host]:
        """
        Get hosts by device type.

        Args:
            device_type: Device type (console, gateway, switch, ap)

        Returns:
            List of Host instances
        """
        query = "SELECT * FROM hosts WHERE type = ? ORDER BY name"
        rows = self.db.fetch_all(query, (device_type,))
        return [Host.from_db_row(row) for row in rows]

    def update(self, host: Host) -> Host:
        """
        Update existing host record.

        Args:
            host: Host instance with updated data

        Returns:
            Updated Host instance
        """
        query = """
            UPDATE hosts SET
                hardware_id = ?,
                type = ?,
                ip_address = ?,
                mac_address = ?,
                name = ?,
                owner = ?,
                is_blocked = ?,
                firmware_version = ?,
                model = ?,
                registration_time = ?,
                last_seen = datetime('now'),
                updated_at = datetime('now')
            WHERE id = ?
        """

        # to_db_params includes id, so skip it (id, hw_id, type, ...)
        # For UPDATE, we need (hw_id, type, ..., id)
        all_params = host.to_db_params()
        params = all_params[1:] + (all_params[0],)  # Move id to end

        with self.db.transaction():
            self.db.execute(query, params)

        return self.get_by_id(host.id)

    def upsert(self, host: Host) -> Host:
        """
        Insert or update host record.

        Args:
            host: Host instance

        Returns:
            Upserted Host instance
        """
        if self.exists(host.id):
            return self.update(host)
        else:
            return self.create(host)

    def update_last_seen(self, host_id: str) -> bool:
        """
        Update last_seen timestamp for a host.

        Args:
            host_id: Host identifier

        Returns:
            True if updated, False if not found
        """
        if not self.exists(host_id):
            return False

        query = """
            UPDATE hosts
            SET last_seen = datetime('now'),
                updated_at = datetime('now')
            WHERE id = ?
        """

        with self.db.transaction():
            self.db.execute(query, (host_id,))

        return True

    def get_online_hosts(self) -> List[Host]:
        """
        Get hosts that are currently online.

        Uses the v_latest_host_status view to determine online status.

        Returns:
            List of online Host instances
        """
        query = """
            SELECT h.* FROM hosts h
            INNER JOIN v_latest_host_status v ON h.id = v.id
            WHERE v.is_online = 1
            ORDER BY h.name
        """
        rows = self.db.fetch_all(query)
        return [Host.from_db_row(row) for row in rows]

    def get_offline_hosts(self) -> List[Host]:
        """
        Get hosts that are currently offline.

        Uses the v_latest_host_status view to determine online status.

        Returns:
            List of offline Host instances
        """
        query = """
            SELECT h.* FROM hosts h
            INNER JOIN v_latest_host_status v ON h.id = v.id
            WHERE v.is_online = 0
            ORDER BY h.name
        """
        rows = self.db.fetch_all(query)
        return [Host.from_db_row(row) for row in rows]

    def search(self, search_term: str) -> List[Host]:
        """
        Search hosts by name, IP, or MAC address.

        Args:
            search_term: Search term (case-insensitive)

        Returns:
            List of matching Host instances
        """
        search_pattern = f"%{search_term}%"
        query = """
            SELECT * FROM hosts
            WHERE name LIKE ?
               OR ip_address LIKE ?
               OR mac_address LIKE ?
            ORDER BY name
        """
        rows = self.db.fetch_all(
            query, (search_pattern, search_pattern, search_pattern)
        )
        return [Host.from_db_row(row) for row in rows]
