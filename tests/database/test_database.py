"""Tests for database module."""

import sqlite3
from pathlib import Path

import pytest

from src.database import Database


@pytest.fixture
def test_db(tmp_path):
    """Create a temporary test database."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)
    db.initialize()
    yield db
    db.close()


class TestDatabase:
    """Test Database class."""

    def test_init(self, tmp_path):
        """Test database initialization."""
        db_path = tmp_path / "test.db"
        db = Database(db_path)

        assert db.db_path == db_path
        assert not db_path.exists()  # Not created until initialize()

        db.close()

    def test_initialize_creates_schema(self, tmp_path):
        """Test that initialize creates all tables."""
        db_path = tmp_path / "test.db"
        db = Database(db_path)
        db.initialize()

        # Check that database file exists
        assert db_path.exists()

        # Check tables exist
        tables = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [t["name"] for t in tables]

        assert "hosts" in table_names
        assert "host_status" in table_names
        assert "events" in table_names
        assert "metrics" in table_names
        assert "collection_runs" in table_names
        assert "database_metadata" in table_names

        db.close()

    def test_initialize_creates_views(self, tmp_path):
        """Test that initialize creates views."""
        db_path = tmp_path / "test.db"
        db = Database(db_path)
        db.initialize()

        # Check views exist
        views = db.fetch_all("SELECT name FROM sqlite_master WHERE type='view'")
        view_names = [v["name"] for v in views]

        assert "v_latest_host_status" in view_names
        assert "v_host_uptime_stats" in view_names
        assert "v_recent_events" in view_names

        db.close()

    def test_get_connection(self, test_db):
        """Test getting database connection."""
        conn = test_db.get_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)

        # Check row factory is set
        cursor = conn.execute("SELECT 1 as test")
        row = cursor.fetchone()
        assert row["test"] == 1

    def test_execute(self, test_db):
        """Test execute method."""
        # Insert test data
        cursor = test_db.execute(
            "INSERT INTO hosts (id, hardware_id, type) VALUES (?, ?, ?)",
            ("test1", "hw1", "switch"),
        )
        assert cursor.rowcount == 1

    def test_fetch_one(self, test_db):
        """Test fetch_one method."""
        # Insert test data
        test_db.execute(
            "INSERT INTO hosts (id, hardware_id, type) VALUES (?, ?, ?)",
            ("test1", "hw1", "switch"),
        )

        # Fetch it back
        row = test_db.fetch_one("SELECT * FROM hosts WHERE id = ?", ("test1",))

        assert row is not None
        assert row["id"] == "test1"
        assert row["hardware_id"] == "hw1"
        assert row["type"] == "switch"

    def test_fetch_one_not_found(self, test_db):
        """Test fetch_one returns None when not found."""
        row = test_db.fetch_one("SELECT * FROM hosts WHERE id = ?", ("nonexistent",))
        assert row is None

    def test_fetch_all(self, test_db):
        """Test fetch_all method."""
        # Insert test data
        test_db.execute(
            "INSERT INTO hosts (id, hardware_id, type) VALUES (?, ?, ?)",
            ("test1", "hw1", "switch"),
        )
        test_db.execute(
            "INSERT INTO hosts (id, hardware_id, type) VALUES (?, ?, ?)",
            ("test2", "hw2", "ap"),
        )

        # Fetch all
        rows = test_db.fetch_all("SELECT * FROM hosts ORDER BY id")

        assert len(rows) == 2
        assert rows[0]["id"] == "test1"
        assert rows[1]["id"] == "test2"

    def test_fetch_all_empty(self, test_db):
        """Test fetch_all returns empty list when no results."""
        rows = test_db.fetch_all("SELECT * FROM hosts")
        assert rows == []

    def test_transaction_commit(self, test_db):
        """Test transaction commits on success."""
        with test_db.transaction():
            test_db.execute(
                "INSERT INTO hosts (id, hardware_id, type) VALUES (?, ?, ?)",
                ("test1", "hw1", "switch"),
            )

        # Verify data was committed
        row = test_db.fetch_one("SELECT * FROM hosts WHERE id = ?", ("test1",))
        assert row is not None

    def test_transaction_rollback(self, test_db):
        """Test transaction rolls back on error."""
        with pytest.raises(sqlite3.IntegrityError):
            with test_db.transaction():
                test_db.execute(
                    "INSERT INTO hosts (id, hardware_id, type) VALUES (?, ?, ?)",
                    ("test1", "hw1", "switch"),
                )
                # Try to insert duplicate (should fail)
                test_db.execute(
                    "INSERT INTO hosts (id, hardware_id, type) VALUES (?, ?, ?)",
                    ("test1", "hw1", "switch"),
                )

        # Verify no data was committed
        row = test_db.fetch_one("SELECT * FROM hosts WHERE id = ?", ("test1",))
        assert row is None

    def test_get_schema_version(self, test_db):
        """Test getting schema version."""
        version = test_db.get_schema_version()
        assert version == "1.0"

    def test_get_stats(self, test_db):
        """Test getting database stats."""
        # Insert some test data
        test_db.execute(
            "INSERT INTO hosts (id, hardware_id, type) VALUES (?, ?, ?)",
            ("test1", "hw1", "switch"),
        )

        stats = test_db.get_stats()

        assert "database_path" in stats
        assert "database_size_bytes" in stats
        assert "schema_version" in stats
        assert "hosts_count" in stats

        assert stats["schema_version"] == "1.0"
        assert stats["hosts_count"] == 1

    def test_vacuum(self, test_db):
        """Test vacuum operation."""
        # Insert and delete data to create fragmentation
        test_db.execute(
            "INSERT INTO hosts (id, hardware_id, type) VALUES (?, ?, ?)",
            ("test1", "hw1", "switch"),
        )
        test_db.execute("DELETE FROM hosts WHERE id = ?", ("test1",))

        # Vacuum should complete without error
        test_db.vacuum()

    def test_backup(self, test_db, tmp_path):
        """Test database backup."""
        # Insert test data
        test_db.execute(
            "INSERT INTO hosts (id, hardware_id, type) VALUES (?, ?, ?)",
            ("test1", "hw1", "switch"),
        )

        # Create backup
        backup_path = tmp_path / "backup.db"
        test_db.backup(backup_path)

        assert backup_path.exists()

        # Verify backup contains data
        backup_db = Database(backup_path)
        row = backup_db.fetch_one("SELECT * FROM hosts WHERE id = ?", ("test1",))
        assert row is not None
        backup_db.close()

    def test_context_manager(self, tmp_path):
        """Test database as context manager."""
        db_path = tmp_path / "test.db"

        with Database(db_path) as db:
            db.initialize()
            db.execute(
                "INSERT INTO hosts (id, hardware_id, type) VALUES (?, ?, ?)",
                ("test1", "hw1", "switch"),
            )

        # Database should be closed after context
        # Verify data persists
        db2 = Database(db_path)
        row = db2.fetch_one("SELECT * FROM hosts WHERE id = ?", ("test1",))
        assert row is not None
        db2.close()
