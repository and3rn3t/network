"""Database service for dependency injection."""

from pathlib import Path
from typing import Generator

from backend.src.config import get_settings

# Import from project root src (sys.path set up in startup.py)
from src.database.database import Database

settings = get_settings()

# Global database instance
_db_instance: Database | None = None


def get_database() -> Generator[Database, None, None]:
    """
    Get database instance for dependency injection.

    Yields:
        Database instance
    """
    global _db_instance

    if _db_instance is None:
        db_path = Path(settings.database_path).resolve()
        _db_instance = Database(str(db_path))

    yield _db_instance


def close_database() -> None:
    """Close database connection."""
    global _db_instance
    if _db_instance:
        _db_instance.close()
        _db_instance = None
