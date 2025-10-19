"""Authentication API endpoints."""

import sys
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.auth.dependencies import get_current_superuser, get_current_user
from backend.src.database.user_repository import User, UserRepository
from backend.src.middleware.error_handler import AuthenticationError, ValidationError
from backend.src.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserResponse,
)
from backend.src.services.auth_service import (
    create_token_response,
    get_password_hash,
    verify_password,
)
from backend.src.services.database_service import get_database

router = APIRouter()


def user_to_response(user: User) -> UserResponse:
    """Convert User model to UserResponse schema."""
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db=Depends(get_database),
):
    """
    Login with username and password.

    Returns JWT access token on success.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(login_data.username)

    # Check user exists and password is correct
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise AuthenticationError("Incorrect username or password")

    # Check user is active
    if not user.is_active:
        raise AuthenticationError("User account is inactive")

    # Update last login
    user_repo.update_last_login(user.id)

    # Create token
    token_data = create_token_response(user.id, user.username)

    return LoginResponse(
        access_token=token_data["access_token"],
        token_type=token_data["token_type"],
        expires_in=token_data["expires_in"],
        user=user_to_response(user),
    )


@router.post("/logout")
async def logout(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Logout current user.

    Note: With JWT tokens, logout is handled client-side by discarding the token.
    This endpoint is provided for consistency and future session management.
    """
    return {
        "message": "Successfully logged out",
        "username": current_user.username,
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get current user information."""
    return user_to_response(current_user)


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db=Depends(get_database),
):
    """Change current user's password."""
    user_repo = UserRepository(db)

    # Verify current password
    if not verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        raise AuthenticationError("Incorrect current password")

    # Hash and update new password
    new_hashed = get_password_hash(password_data.new_password)
    user_repo.update_password(current_user.id, new_hashed)

    return {"message": "Password changed successfully"}


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: Annotated[User, Depends(get_current_superuser)],
    db=Depends(get_database),
):
    """
    Create a new user.

    Requires superuser permissions.
    """
    user_repo = UserRepository(db)

    # Check if username already exists
    existing = user_repo.get_by_username(user_data.username)
    if existing:
        raise ValidationError(f"Username '{user_data.username}' already exists")

    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user = user_repo.create_user(
        username=user_data.username,
        hashed_password=hashed_password,
        email=user_data.email,
        full_name=user_data.full_name,
        is_superuser=user_data.is_superuser,
    )

    return user_to_response(user)


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: Annotated[User, Depends(get_current_superuser)],
    db=Depends(get_database),
    skip: int = 0,
    limit: int = 100,
):
    """
    List all users.

    Requires superuser permissions.
    """
    user_repo = UserRepository(db)
    users = user_repo.list_users(skip=skip, limit=limit)
    return [user_to_response(user) for user in users]
