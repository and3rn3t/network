"""Notification Channels API endpoints."""

import sys
from pathlib import Path

from fastapi import APIRouter, Body, Depends

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.src.middleware.error_handler import NotFoundError
from backend.src.services.database_service import get_database
from src.alerts.models import NotificationChannel
from src.database.database import Database
from src.database.repositories import NotificationChannelRepository

router = APIRouter()


@router.get("")
async def list_channels(
    db: Database = Depends(get_database),
):
    """
    List all notification channels.

    Returns list of configured notification channels.
    """
    channel_repo = NotificationChannelRepository(db)
    channels = channel_repo.get_all()

    return {
        "channels": [channel.to_dict() for channel in channels],
        "count": len(channels),
    }


@router.get("/{channel_id}")
async def get_channel(
    channel_id: str,
    db: Database = Depends(get_database),
):
    """
    Get channel details by ID.

    Returns complete channel configuration.
    """
    channel_repo = NotificationChannelRepository(db)
    channel = channel_repo.get_by_id(channel_id)

    if not channel:
        raise NotFoundError(f"Channel with ID {channel_id} not found")

    return channel.to_dict()


@router.post("")
async def create_channel(
    channel_data: dict = Body(...),
    db: Database = Depends(get_database),
):
    """
    Create a new notification channel.

    Accepts channel configuration and creates a new notification channel.
    """
    channel_repo = NotificationChannelRepository(db)

    # Convert to NotificationChannel object
    channel = NotificationChannel(**channel_data)
    created_channel = channel_repo.create(channel)

    return {
        "success": True,
        "channel": created_channel.to_dict(),
    }


@router.put("/{channel_id}")
async def update_channel(
    channel_id: str,
    channel_data: dict = Body(...),
    db: Database = Depends(get_database),
):
    """
    Update an existing notification channel.

    Updates channel configuration.
    """
    channel_repo = NotificationChannelRepository(db)
    existing_channel = channel_repo.get_by_id(channel_id)

    if not existing_channel:
        raise NotFoundError(f"Channel with ID {channel_id} not found")

    # Update with new data
    channel_data["id"] = channel_id
    updated_channel = NotificationChannel(**channel_data)
    channel_repo.update(updated_channel)

    return {
        "success": True,
        "channel": updated_channel.to_dict(),
    }


@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: str,
    db: Database = Depends(get_database),
):
    """
    Delete a notification channel.

    Removes the channel from the system.
    """
    channel_repo = NotificationChannelRepository(db)
    success = channel_repo.delete(channel_id)

    if not success:
        raise NotFoundError(f"Channel with ID {channel_id} not found")

    return {
        "success": True,
        "channel_id": channel_id,
    }
