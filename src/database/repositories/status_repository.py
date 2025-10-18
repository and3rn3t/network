"""
Status repository for managing host status records.

Provides CRUD operations for host_status table.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from ..models import HostStatus
from .base import BaseRepository


class StatusRepository(BaseRepository):
    """Repository for HostStatus model operations."""

    table_name = "host_status"

    def create(self, status: HostStatus) -> HostStatus:
        """
        Create new status record.

        Args:
            status: HostStatus instance to create

        Returns:
            Created HostStatus instance with ID and timestamp
        """
        query = """
            INSERT INTO host_status (
                host_id, status, is_online, uptime_seconds,
                cpu_usage, memory_usage, temperature,
                last_connection_change, last_backup_time,
                error_message, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self.db.transaction():
            cursor = self.db.execute(query, status.to_db_params())
            status_id = cursor.lastrowid

        # Fetch the created record
        return self.get_by_id(status_id)

    def get_by_id(self, status_id: int) -> Optional[HostStatus]:
        """
        Get status by ID.

        Args:
            status_id: Status record ID

        Returns:
            HostStatus instance or None if not found
        """
        query = "SELECT * FROM host_status WHERE id = ?"
        row = self.db.fetch_one(query, (status_id,))

        if row:
            return HostStatus.from_db_row(row)
        return None

    def get_latest_for_host(self, host_id: str) -> Optional[HostStatus]:
        """
        Get latest status for a host.

        Args:
            host_id: Host identifier

        Returns:
            Latest HostStatus instance or None if not found
        """
        query = """
            SELECT * FROM host_status
            WHERE host_id = ?
            ORDER BY recorded_at DESC
            LIMIT 1
        """
        row = self.db.fetch_one(query, (host_id,))

        if row:
            return HostStatus.from_db_row(row)
        return None

    def get_history_for_host(self, host_id: str, limit: int = 100) -> List[HostStatus]:
        """
        Get status history for a host.

        Args:
            host_id: Host identifier
            limit: Maximum number of records (default: 100)

        Returns:
            List of HostStatus instances ordered by time (newest first)
        """
        query = """
            SELECT * FROM host_status
            WHERE host_id = ?
            ORDER BY recorded_at DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (host_id, limit))
        return [HostStatus.from_db_row(row) for row in rows]

    def get_status_in_timerange(
        self, host_id: str, start_time: str, end_time: str
    ) -> List[HostStatus]:
        """
        Get status records within a time range.

        Args:
            host_id: Host identifier
            start_time: Start time (ISO format)
            end_time: End time (ISO format)

        Returns:
            List of HostStatus instances within range
        """
        query = """
            SELECT * FROM host_status
            WHERE host_id = ?
              AND recorded_at BETWEEN ? AND ?
            ORDER BY recorded_at DESC
        """
        rows = self.db.fetch_all(query, (host_id, start_time, end_time))
        return [HostStatus.from_db_row(row) for row in rows]

    def get_all_latest_status(self) -> List[HostStatus]:
        """
        Get latest status for all hosts.

        Uses a subquery to get only the most recent status per host.

        Returns:
            List of latest HostStatus instances for each host
        """
        query = """
            SELECT hs.* FROM host_status hs
            INNER JOIN (
                SELECT host_id, MAX(id) as max_id
                FROM host_status
                GROUP BY host_id
            ) latest ON hs.id = latest.max_id
            ORDER BY hs.recorded_at DESC
        """
        rows = self.db.fetch_all(query)
        return [HostStatus.from_db_row(row) for row in rows]

    def get_status_changes(self, host_id: str, hours: int = 24) -> List[HostStatus]:
        """
        Get status changes for a host in recent hours.

        Only returns records where status changed from previous record.

        Args:
            host_id: Host identifier
            hours: Number of hours to look back (default: 24)

        Returns:
            List of HostStatus instances where status changed
        """
        # Calculate start time
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        query = """
            SELECT DISTINCT hs1.* FROM host_status hs1
            LEFT JOIN host_status hs2 ON
                hs1.host_id = hs2.host_id AND
                hs2.recorded_at < hs1.recorded_at
            WHERE hs1.host_id = ?
              AND hs1.recorded_at >= ?
              AND (hs2.status IS NULL OR hs1.status != hs2.status)
            ORDER BY hs1.recorded_at DESC
        """
        rows = self.db.fetch_all(query, (host_id, start_time))
        return [HostStatus.from_db_row(row) for row in rows]

    def delete_old_records(self, days: int = 90) -> int:
        """
        Delete status records older than specified days.

        Args:
            days: Number of days to keep (default: 90)

        Returns:
            Number of records deleted
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Count records to delete
        count_query = """
            SELECT COUNT(*) as count FROM host_status
            WHERE recorded_at < ?
        """
        result = self.db.fetch_one(count_query, (cutoff_date,))
        count = result["count"] if result else 0

        # Delete records
        delete_query = "DELETE FROM host_status WHERE recorded_at < ?"

        with self.db.transaction():
            self.db.execute(delete_query, (cutoff_date,))

        return count

    def get_uptime_stats(self, host_id: str) -> dict:
        """
        Get uptime statistics for a host.

        Args:
            host_id: Host identifier

        Returns:
            Dictionary with uptime statistics
        """
        query = """
            SELECT
                COUNT(*) as total_checks,
                SUM(CASE WHEN is_online = 1 THEN 1 ELSE 0 END) as online_count,
                ROUND(AVG(CASE WHEN is_online = 1 THEN 100.0 ELSE 0.0 END), 2) as uptime_percentage,
                MAX(recorded_at) as last_check,
                MIN(recorded_at) as first_check
            FROM host_status
            WHERE host_id = ?
        """
        result = self.db.fetch_one(query, (host_id,))
        return dict(result) if result else {}
