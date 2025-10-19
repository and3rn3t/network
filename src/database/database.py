"""
Database connection and management for UniFi Network API.

This module provides the Database class for managing SQLite connections,
executing queries, and handling transactions.
"""

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class Database:
    """
    SQLite database manager for UniFi network data.

    Handles connection management, query execution, and schema initialization.
    Uses context managers for safe transaction handling.

    Example:
        >>> db = Database("data/unifi_network.db")
        >>> db.initialize()
        >>> with db.transaction() as conn:
        ...     db.execute("INSERT INTO hosts ...", params)
    """

    def __init__(self, db_path: str = "data/unifi_network.db"):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[sqlite3.Connection] = None

        logger.info(f"Database initialized at {self.db_path}")

    def get_connection(self) -> sqlite3.Connection:
        """
        Get or create database connection.

        Returns:
            SQLite connection with row factory enabled
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            )
            # Enable row factory for dict-like access
            self._connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
            logger.debug("Database connection established")

        return self._connection

    def close(self):
        """Close database connection if open."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.debug("Database connection closed")

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        Automatically commits on success or rolls back on error.

        Example:
            >>> with db.transaction() as conn:
            ...     db.execute("INSERT INTO hosts ...", params)
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
            logger.debug("Transaction committed")
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise

    def execute(self, query: str, params: Optional[Tuple] = None) -> sqlite3.Cursor:
        """
        Execute a single SQL query.

        Args:
            query: SQL query string
            params: Query parameters (optional)

        Returns:
            Cursor with query results
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            logger.debug(f"Executed query: {query[:100]}...")
            return cursor
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            raise

    def execute_many(self, query: str, params_list: List[Tuple]) -> sqlite3.Cursor:
        """
        Execute query with multiple parameter sets (batch insert/update).

        Args:
            query: SQL query string
            params_list: List of parameter tuples

        Returns:
            Cursor with query results
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.executemany(query, params_list)
            logger.debug(f"Executed batch query with {len(params_list)} rows")
            return cursor
        except sqlite3.Error as e:
            logger.error(f"Batch query execution failed: {e}")
            raise

    def fetch_one(
        self, query: str, params: Optional[Tuple] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch single row as dictionary.

        Args:
            query: SQL query string
            params: Query parameters (optional)

        Returns:
            Single row as dict or None if no results
        """
        cursor = self.execute(query, params)
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def fetch_all(
        self, query: str, params: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows as list of dictionaries.

        Args:
            query: SQL query string
            params: Query parameters (optional)

        Returns:
            List of rows as dictionaries
        """
        cursor = self.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def initialize(self):
        """
        Initialize database with schema.

        Reads schema.sql and creates all tables, indexes, and views.
        """
        schema_path = Path(__file__).parent / "schema.sql"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        logger.info("Initializing database schema...")

        with open(schema_path, "r") as f:
            schema_sql = f.read()

        # Use executescript for multiple statements
        conn = self.get_connection()
        with self.transaction():
            conn.executescript(schema_sql)

        logger.info("Database schema initialized successfully")

    def initialize_alerts(self):
        """
        Initialize alert system schema.

        Reads schema_alerts.sql and creates alert-related tables, indexes, and views.
        This is a separate migration to support phased rollout.
        """
        schema_path = Path(__file__).parent / "schema_alerts.sql"

        if not schema_path.exists():
            raise FileNotFoundError(f"Alert schema file not found: {schema_path}")

        logger.info("Initializing alert system schema...")

        with open(schema_path, "r") as f:
            schema_sql = f.read()

        # Use executescript for multiple statements
        conn = self.get_connection()
        with self.transaction():
            conn.executescript(schema_sql)

        logger.info("Alert system schema initialized successfully")

    def get_schema_version(self) -> str:
        """
        Get current database schema version.

        Returns:
            Schema version string
        """
        result = self.fetch_one(
            "SELECT value FROM database_metadata WHERE key = 'schema_version'"
        )
        return result["value"] if result else "unknown"

    def vacuum(self):
        """
        Optimize database by running VACUUM.

        Reclaims unused space and defragments database file.
        """
        logger.info("Running VACUUM to optimize database...")
        conn = self.get_connection()
        conn.execute("VACUUM")
        logger.info("Database optimization complete")

    def backup(self, backup_path: Optional[str] = None) -> Path:
        """
        Create database backup.

        Args:
            backup_path: Custom backup path (optional)

        Returns:
            Path to backup file
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/backups/unifi_network_{timestamp}.db"

        backup_file = Path(backup_path)
        backup_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating database backup: {backup_file}")

        # Use SQLite backup API
        source_conn = self.get_connection()
        backup_conn = sqlite3.connect(str(backup_file))

        with backup_conn:
            source_conn.backup(backup_conn)

        backup_conn.close()

        logger.info(f"Backup created successfully: {backup_file}")
        return backup_file

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with table counts and database info
        """
        stats = {
            "database_path": str(self.db_path),
            "database_size_bytes": (
                self.db_path.stat().st_size if self.db_path.exists() else 0
            ),
            "schema_version": self.get_schema_version(),
        }

        # Get table counts
        tables = ["hosts", "host_status", "events", "metrics", "collection_runs"]

        for table in tables:
            try:
                result = self.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                stats[f"{table}_count"] = result["count"] if result else 0
            except sqlite3.Error:
                stats[f"{table}_count"] = 0

        return stats

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation."""
        return f"Database(db_path='{self.db_path}')"
