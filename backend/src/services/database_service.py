"""Database service for dependency injection."""

import sys
from pathlib import Path
from typing import Generator

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.config import get_settings
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
