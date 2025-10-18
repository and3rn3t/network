"""
Event repository for managing event records.

Provides CRUD operations for events table.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..models import Event
from .base import BaseRepository


class EventRepository(BaseRepository):
    """Repository for Event model operations."""

    table_name = "events"

    def create(self, event: Event) -> Event:
        """
        Create new event record.

        Args:
            event: Event instance to create

        Returns:
            Created Event instance with ID and timestamp
        """
        query = """
            INSERT INTO events (
                host_id, event_type, severity, title,
                description, previous_value, new_value, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        with self.db.transaction():
            cursor = self.db.execute(query, event.to_db_params())
            event_id = cursor.lastrowid

        return self.get_by_id(event_id)

    def get_by_id(self, event_id: int) -> Optional[Event]:
        """
        Get event by ID.

        Args:
            event_id: Event record ID

        Returns:
            Event instance or None if not found
        """
        query = "SELECT * FROM events WHERE id = ?"
        row = self.db.fetch_one(query, (event_id,))

        if row:
            return Event.from_db_row(row)
        return None

    def get_for_host(self, host_id: str, limit: int = 100) -> List[Event]:
        """
        Get events for a specific host.

        Args:
            host_id: Host identifier
            limit: Maximum number of events (default: 100)

        Returns:
            List of Event instances ordered by time (newest first)
        """
        query = """
            SELECT * FROM events
            WHERE host_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (host_id, limit))
        return [Event.from_db_row(row) for row in rows]

    def get_by_type(self, event_type: str, limit: int = 100) -> List[Event]:
        """
        Get events by type.

        Args:
            event_type: Event type (status_change, error, alert, etc.)
            limit: Maximum number of events (default: 100)

        Returns:
            List of Event instances ordered by time (newest first)
        """
        query = """
            SELECT * FROM events
            WHERE event_type = ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (event_type, limit))
        return [Event.from_db_row(row) for row in rows]

    def get_by_severity(self, severity: str, limit: int = 100) -> List[Event]:
        """
        Get events by severity level.

        Args:
            severity: Severity level (info, warning, error, critical)
            limit: Maximum number of events (default: 100)

        Returns:
            List of Event instances ordered by time (newest first)
        """
        query = """
            SELECT * FROM events
            WHERE severity = ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (severity, limit))
        return [Event.from_db_row(row) for row in rows]

    def get_recent(self, hours: int = 24, limit: int = 100) -> List[Event]:
        """
        Get recent events.

        Args:
            hours: Number of hours to look back (default: 24)
            limit: Maximum number of events (default: 100)

        Returns:
            List of recent Event instances
        """
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        query = """
            SELECT * FROM events
            WHERE created_at >= ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (start_time, limit))
        return [Event.from_db_row(row) for row in rows]

    def get_errors(self, limit: int = 100) -> List[Event]:
        """
        Get error and critical events.

        Args:
            limit: Maximum number of events (default: 100)

        Returns:
            List of error/critical Event instances
        """
        query = """
            SELECT * FROM events
            WHERE severity IN ('error', 'critical')
            ORDER BY created_at DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (limit,))
        return [Event.from_db_row(row) for row in rows]

    def delete_old_events(self, days: int = 365) -> int:
        """
        Delete events older than specified days.

        Args:
            days: Number of days to keep (default: 365)

        Returns:
            Number of records deleted
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        count_query = """
            SELECT COUNT(*) as count FROM events
            WHERE created_at < ?
        """
        result = self.db.fetch_one(count_query, (cutoff_date,))
        count = result["count"] if result else 0

        delete_query = "DELETE FROM events WHERE created_at < ?"

        with self.db.transaction():
            self.db.execute(delete_query, (cutoff_date,))

        return count

    def get_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        limit: Optional[int] = None,
    ) -> List[Event]:
        """
        Get events within a time range.

        Args:
            start_time: Start of time range
            end_time: End of time range
            limit: Optional limit on number of events

        Returns:
            List of Event instances in the time range
        """
        if limit:
            query = """
                SELECT * FROM events
                WHERE created_at >= ? AND created_at <= ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            rows = self.db.fetch_all(
                query, (start_time.isoformat(), end_time.isoformat(), limit)
            )
        else:
            query = """
                SELECT * FROM events
                WHERE created_at >= ? AND created_at <= ?
                ORDER BY created_at DESC
            """
            rows = self.db.fetch_all(
                query, (start_time.isoformat(), end_time.isoformat())
            )

        return [Event.from_db_row(row) for row in rows]

    def get_event_counts(
        self, start_time: datetime, end_time: datetime
    ) -> Dict[str, int]:
        """
        Get counts of events by type within a time range.

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Dictionary mapping event types to counts
        """
        query = """
            SELECT event_type, COUNT(*) as count
            FROM events
            WHERE created_at >= ? AND created_at <= ?
            GROUP BY event_type
        """
        rows = self.db.fetch_all(query, (start_time.isoformat(), end_time.isoformat()))

        return {row["event_type"]: row["count"] for row in rows}

    def get_by_host_id(self, host_id: str, limit: Optional[int] = None) -> List[Event]:
        """
        Get events for a specific host (alias for get_for_host).

        Args:
            host_id: Host identifier
            limit: Optional maximum number of events

        Returns:
            List of Event instances
        """
        if limit:
            return self.get_for_host(host_id, limit)
        else:
            return self.get_for_host(host_id, limit=10000)  # Large default
