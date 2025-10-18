"""
Metric repository for managing time-series metric records.

Provides CRUD operations for metrics table.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from ..models import Metric
from .base import BaseRepository


class MetricRepository(BaseRepository):
    """Repository for Metric model operations."""

    table_name = "metrics"

    def create(self, metric: Metric) -> Metric:
        """
        Create new metric record.

        Args:
            metric: Metric instance to create

        Returns:
            Created Metric instance with ID and timestamp
        """
        query = """
            INSERT INTO metrics (
                host_id, metric_name, metric_value, unit
            ) VALUES (?, ?, ?, ?)
        """

        with self.db.transaction():
            cursor = self.db.execute(query, metric.to_db_params())
            metric_id = cursor.lastrowid

        return self.get_by_id(metric_id)

    def create_many(self, metrics: List[Metric]) -> int:
        """
        Create multiple metric records in batch.

        Args:
            metrics: List of Metric instances

        Returns:
            Number of metrics created
        """
        if not metrics:
            return 0

        query = """
            INSERT INTO metrics (
                host_id, metric_name, metric_value, unit
            ) VALUES (?, ?, ?, ?)
        """

        params_list = [m.to_db_params() for m in metrics]

        with self.db.transaction():
            self.db.execute_many(query, params_list)

        return len(metrics)

    def get_by_id(self, metric_id: int) -> Optional[Metric]:
        """
        Get metric by ID.

        Args:
            metric_id: Metric record ID

        Returns:
            Metric instance or None if not found
        """
        query = "SELECT * FROM metrics WHERE id = ?"
        row = self.db.fetch_one(query, (metric_id,))

        if row:
            return Metric.from_db_row(row)
        return None

    def get_for_host(
        self, host_id: str, metric_name: Optional[str] = None, limit: int = 100
    ) -> List[Metric]:
        """
        Get metrics for a host.

        Args:
            host_id: Host identifier
            metric_name: Optional specific metric name
            limit: Maximum number of records (default: 100)

        Returns:
            List of Metric instances ordered by time (newest first)
        """
        if metric_name:
            query = """
                SELECT * FROM metrics
                WHERE host_id = ? AND metric_name = ?
                ORDER BY recorded_at DESC
                LIMIT ?
            """
            rows = self.db.fetch_all(query, (host_id, metric_name, limit))
        else:
            query = """
                SELECT * FROM metrics
                WHERE host_id = ?
                ORDER BY recorded_at DESC
                LIMIT ?
            """
            rows = self.db.fetch_all(query, (host_id, limit))

        return [Metric.from_db_row(row) for row in rows]

    def get_latest_metrics(self, host_id: str) -> List[Metric]:
        """
        Get latest value for each metric type for a host.

        Args:
            host_id: Host identifier

        Returns:
            List of latest Metric instances for each metric name
        """
        query = """
            SELECT m.* FROM metrics m
            INNER JOIN (
                SELECT metric_name, MAX(id) as max_id
                FROM metrics
                WHERE host_id = ?
                GROUP BY metric_name
            ) latest ON m.id = latest.max_id
            ORDER BY m.metric_name
        """
        rows = self.db.fetch_all(query, (host_id,))
        return [Metric.from_db_row(row) for row in rows]

    def get_metric_history(
        self, host_id: str, metric_name: str, hours: int = 24
    ) -> List[Metric]:
        """
        Get metric history for specific time period.

        Args:
            host_id: Host identifier
            metric_name: Metric name
            hours: Number of hours to look back (default: 24)

        Returns:
            List of Metric instances within timerange
        """
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        query = """
            SELECT * FROM metrics
            WHERE host_id = ?
              AND metric_name = ?
              AND recorded_at >= ?
            ORDER BY recorded_at ASC
        """
        rows = self.db.fetch_all(query, (host_id, metric_name, start_time))
        return [Metric.from_db_row(row) for row in rows]

    def get_average(
        self, host_id: str, metric_name: str, hours: int = 24
    ) -> Optional[float]:
        """
        Get average metric value over time period.

        Args:
            host_id: Host identifier
            metric_name: Metric name
            hours: Number of hours to average (default: 24)

        Returns:
            Average value or None if no data
        """
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        query = """
            SELECT AVG(metric_value) as avg_value
            FROM metrics
            WHERE host_id = ?
              AND metric_name = ?
              AND recorded_at >= ?
        """
        result = self.db.fetch_one(query, (host_id, metric_name, start_time))

        if result and result["avg_value"] is not None:
            return float(result["avg_value"])
        return None

    def delete_old_metrics(self, days: int = 30) -> int:
        """
        Delete metrics older than specified days.

        Args:
            days: Number of days to keep (default: 30)

        Returns:
            Number of records deleted
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        count_query = """
            SELECT COUNT(*) as count FROM metrics
            WHERE recorded_at < ?
        """
        result = self.db.fetch_one(count_query, (cutoff_date,))
        count = result["count"] if result else 0

        delete_query = "DELETE FROM metrics WHERE recorded_at < ?"

        with self.db.transaction():
            self.db.execute(delete_query, (cutoff_date,))

        return count

    def get_by_host_id(self, host_id: str, limit: Optional[int] = None) -> List[Metric]:
        """
        Get metrics for a host (alias for get_for_host).

        Args:
            host_id: Host identifier
            limit: Optional maximum number of records

        Returns:
            List of Metric instances
        """
        if limit:
            return self.get_for_host(host_id, limit=limit)
        else:
            return self.get_for_host(host_id, limit=10000)  # Large default

    def get_by_time_range(
        self,
        host_id: str,
        start_time: datetime,
        end_time: datetime,
        metric_name: Optional[str] = None,
    ) -> List[Metric]:
        """
        Get metrics within a time range.

        Args:
            host_id: Host identifier
            start_time: Start of time range
            end_time: End of time range
            metric_name: Optional specific metric name

        Returns:
            List of Metric instances in the time range
        """
        if metric_name:
            query = """
                SELECT * FROM metrics
                WHERE host_id = ?
                  AND metric_name = ?
                  AND recorded_at >= ?
                  AND recorded_at <= ?
                ORDER BY recorded_at ASC
            """
            rows = self.db.fetch_all(
                query,
                (host_id, metric_name, start_time.isoformat(), end_time.isoformat()),
            )
        else:
            query = """
                SELECT * FROM metrics
                WHERE host_id = ?
                  AND recorded_at >= ?
                  AND recorded_at <= ?
                ORDER BY recorded_at ASC
            """
            rows = self.db.fetch_all(
                query, (host_id, start_time.isoformat(), end_time.isoformat())
            )

        return [Metric.from_db_row(row) for row in rows]
