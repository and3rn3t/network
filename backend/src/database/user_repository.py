"""User repository for database operations."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.database.database import Database


class User:
    """User model."""

    def __init__(
        self,
        id: int,
        username: str,
        email: Optional[str],
        full_name: Optional[str],
        hashed_password: str,
        is_active: bool,
        is_superuser: bool,
        created_at: datetime,
        last_login: Optional[datetime] = None,
    ):
        """Initialize user."""
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.created_at = created_at
        self.last_login = last_login


class UserRepository:
    """Repository for user database operations."""

    def __init__(self, db: Database):
        """Initialize repository."""
        self.db = db
        self._ensure_tables()

    def _ensure_tables(self):
        """Ensure user tables exist."""
        schema_file = Path(__file__).parent / "auth_schema.sql"
        if schema_file.exists():
            with open(schema_file, "r") as f:
                schema = f.read()
                # Use executescript for multi-statement SQL
                try:
                    conn = self.db.get_connection()
                    conn.executescript(schema)
                    conn.commit()
                except Exception as e:
                    # Tables might already exist
                    pass

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: Username to search for

        Returns:
            User object or None if not found
        """
        query = """
            SELECT id, username, email, full_name, hashed_password,
                   is_active, is_superuser, created_at, last_login
            FROM users
            WHERE username = ?
        """
        row = self.db.fetch_one(query, (username,))

        if row:
            return User(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                full_name=row["full_name"],
                hashed_password=row["hashed_password"],
                is_active=bool(row["is_active"]),
                is_superuser=bool(row["is_superuser"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                last_login=(
                    datetime.fromisoformat(row["last_login"])
                    if row["last_login"]
                    else None
                ),
            )
        return None

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID to search for

        Returns:
            User object or None if not found
        """
        query = """
            SELECT id, username, email, full_name, hashed_password,
                   is_active, is_superuser, created_at, last_login
            FROM users
            WHERE id = ?
        """
        row = self.db.fetch_one(query, (user_id,))

        if row:
            return User(
                id=row["id"],
                username=row["username"],
                email=row["email"],
                full_name=row["full_name"],
                hashed_password=row["hashed_password"],
                is_active=bool(row["is_active"]),
                is_superuser=bool(row["is_superuser"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                last_login=(
                    datetime.fromisoformat(row["last_login"])
                    if row["last_login"]
                    else None
                ),
            )
        return None

    def create_user(
        self,
        username: str,
        hashed_password: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        is_superuser: bool = False,
    ) -> User:
        """
        Create a new user.

        Args:
            username: Username
            hashed_password: Hashed password
            email: Optional email
            full_name: Optional full name
            is_superuser: Whether user is superuser

        Returns:
            Created user object
        """
        query = """
            INSERT INTO users (
                username, email, full_name, hashed_password, is_superuser
            )
            VALUES (?, ?, ?, ?, ?)
        """
        cursor = self.db.execute(
            query, (username, email, full_name, hashed_password, int(is_superuser))
        )
        self.db.get_connection().commit()

        user_id = cursor.lastrowid
        user = self.get_by_id(user_id)
        if not user:
            raise Exception("Failed to create user")
        return user

    def update_last_login(self, user_id: int):
        """
        Update user's last login timestamp.

        Args:
            user_id: User ID to update
        """
        query = "UPDATE users SET last_login = ? WHERE id = ?"
        self.db.execute(query, (datetime.utcnow().isoformat(), user_id))

    def update_password(self, user_id: int, hashed_password: str):
        """
        Update user's password.

        Args:
            user_id: User ID
            hashed_password: New hashed password
        """
        query = "UPDATE users SET hashed_password = ? WHERE id = ?"
        self.db.execute(query, (hashed_password, user_id))

    def deactivate_user(self, user_id: int):
        """
        Deactivate a user.

        Args:
            user_id: User ID to deactivate
        """
        query = "UPDATE users SET is_active = 0 WHERE id = ?"
        self.db.execute(query, (user_id,))

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        List all users.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user objects
        """
        query = """
            SELECT id, username, email, full_name, hashed_password,
                   is_active, is_superuser, created_at, last_login
            FROM users
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        rows = self.db.fetch_all(query, (limit, skip))

        users = []
        for row in rows:
            users.append(
                User(
                    id=row["id"],
                    username=row["username"],
                    email=row["email"],
                    full_name=row["full_name"],
                    hashed_password=row["hashed_password"],
                    is_active=bool(row["is_active"]),
                    is_superuser=bool(row["is_superuser"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    last_login=(
                        datetime.fromisoformat(row["last_login"])
                        if row["last_login"]
                        else None
                    ),
                )
            )

        return users
