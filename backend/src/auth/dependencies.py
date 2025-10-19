"""Authentication dependencies for FastAPI."""

import sys
from pathlib import Path
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.services.auth_service import decode_access_token
from backend.src.services.database_service import get_database
from backend.src.database.user_repository import UserRepository, User
from backend.src.middleware.error_handler import AuthenticationError

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db=Depends(get_database),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP authorization credentials
        db: Database instance

    Returns:
        User object

    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    if not credentials:
        raise AuthenticationError("Not authenticated")

    token = credentials.credentials

    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise AuthenticationError("Invalid or expired token")

    username = payload.get("sub")
    if username is None:
        raise AuthenticationError("Invalid token payload")

    # Get user from database
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(username)

    if user is None:
        raise AuthenticationError("User not found")

    if not user.is_active:
        raise AuthenticationError("User account is inactive")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current user from token

    Returns:
        User object

    Raises:
        AuthenticationError: If user is not active
    """
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current superuser.

    Args:
        current_user: Current user from token

    Returns:
        User object

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db=Depends(get_database),
) -> Optional[User]:
    """
    Optional authentication - returns user if authenticated, None otherwise.

    Args:
        credentials: HTTP authorization credentials
        db: Database instance

    Returns:
        User object or None
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = decode_access_token(token)

        if payload is None:
            return None

        username = payload.get("sub")
        if username is None:
            return None

        user_repo = UserRepository(db)
        user = user_repo.get_by_username(username)

        if user and user.is_active:
            return user

    except Exception:
        pass

    return None
