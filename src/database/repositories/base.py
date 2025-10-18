"""
Base repository class for common database operations.

Provides shared functionality for all repository classes.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar

from ..database import Database

T = TypeVar("T")


class BaseRepository:
    """
    Base repository with common CRUD operations.

    Subclasses should specify their table_name and model_class.
    """

    table_name: str = ""

    def __init__(self, db: Database):
        """
        Initialize repository with database connection.

        Args:
            db: Database instance
        """
        self.db = db

    def exists(self, id_value: Any) -> bool:
        """
        Check if record exists by ID.

        Args:
            id_value: ID value to check

        Returns:
            True if record exists, False otherwise
        """
        query = f"SELECT 1 FROM {self.table_name} WHERE id = ? LIMIT 1"
        result = self.db.fetch_one(query, (id_value,))
        return result is not None

    def count(self) -> int:
        """
        Get total count of records.

        Returns:
            Number of records in table
        """
        query = f"SELECT COUNT(*) as count FROM {self.table_name}"
        result = self.db.fetch_one(query)
        return result["count"] if result else 0

    def delete_by_id(self, id_value: Any) -> bool:
        """
        Delete record by ID.

        Args:
            id_value: ID value to delete

        Returns:
            True if deleted, False if not found
        """
        if not self.exists(id_value):
            return False

        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        with self.db.transaction():
            self.db.execute(query, (id_value,))

        return True

    def delete_all(self) -> int:
        """
        Delete all records from table.

        Returns:
            Number of records deleted
        """
        count = self.count()
        query = f"DELETE FROM {self.table_name}"

        with self.db.transaction():
            self.db.execute(query)

        return count
