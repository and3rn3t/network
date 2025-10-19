"""WebSocket API endpoints."""

import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.database.database import Database
from backend.src.services.database_service import get_database
from backend.src.services.websocket_manager import manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for real-time updates.

    Clients can subscribe to different update streams:
    - metrics: Real-time device metrics
    - alerts: Alert notifications
    - devices: Device status changes
    - health: Network health updates

    Example connection:
        ws://localhost:8000/ws?client_id=dashboard-123
    """
    # Generate client ID if not provided
    if not client_id:
        client_id = f"client-{datetime.now().timestamp()}"

    await manager.connect(websocket, client_id)

    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message_type = data.get("type")

            # Handle subscription requests
            if message_type == "subscribe":
                room = data.get("room")
                if room:
                    manager.join_room(client_id, room)
                    await manager.send_personal_message(
                        {
                            "type": "subscription",
                            "status": "subscribed",
                            "room": room,
                            "timestamp": datetime.now().isoformat(),
                        },
                        client_id,
                    )

            # Handle unsubscribe requests
            elif message_type == "unsubscribe":
                room = data.get("room")
                if room:
                    manager.leave_room(client_id, room)
                    await manager.send_personal_message(
                        {
                            "type": "subscription",
                            "status": "unsubscribed",
                            "room": room,
                            "timestamp": datetime.now().isoformat(),
                        },
                        client_id,
                    )

            # Handle ping requests
            elif message_type == "ping":
                await manager.send_personal_message(
                    {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat(),
                    },
                    client_id,
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")

    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics.

    Returns current connection count and room information.
    """
    rooms_info = {}
    for room, members in manager.rooms.items():
        rooms_info[room] = {
            "member_count": len(members),
            "members": list(members),
        }

    return {
        "total_connections": manager.get_connection_count(),
        "rooms": rooms_info,
        "timestamp": datetime.now().isoformat(),
    }


# Background task for broadcasting metrics
async def broadcast_metrics_task(db: Database):
    """
    Background task to broadcast metrics updates.

    Periodically queries for new metrics and broadcasts to subscribers.
    """
    logger.info("Starting metrics broadcast task")

    while True:
        try:
            # Get recent metrics (last minute)
            since = datetime.now() - timedelta(minutes=1)
            query = """
                SELECT m.host_id, h.name, m.metric_type, m.value, m.timestamp
                FROM metrics m
                JOIN hosts h ON m.host_id = h.id
                WHERE m.timestamp >= ?
                ORDER BY m.timestamp DESC
                LIMIT 100
            """

            rows = db.execute(query, (since.isoformat(),)).fetchall()

            if rows:
                metrics_data = [
                    {
                        "host_id": row[0],
                        "host_name": row[1],
                        "metric_type": row[2],
                        "value": row[3],
                        "timestamp": row[4],
                    }
                    for row in rows
                ]

                # Broadcast to metrics room
                await manager.broadcast_to_room(
                    {
                        "type": "metrics_update",
                        "data": metrics_data,
                        "count": len(metrics_data),
                        "timestamp": datetime.now().isoformat(),
                    },
                    "metrics",
                )

            # Wait before next broadcast
            await asyncio.sleep(30)  # Broadcast every 30 seconds

        except Exception as e:
            logger.error(f"Error in metrics broadcast task: {e}")
            await asyncio.sleep(60)  # Wait longer on error


async def broadcast_alert_update(alert_data: dict):
    """
    Broadcast an alert update to all subscribers.

    Args:
        alert_data: Alert information to broadcast
    """
    await manager.broadcast_to_room(
        {
            "type": "alert_update",
            "data": alert_data,
            "timestamp": datetime.now().isoformat(),
        },
        "alerts",
    )


async def broadcast_device_update(device_data: dict):
    """
    Broadcast a device status update to all subscribers.

    Args:
        device_data: Device information to broadcast
    """
    await manager.broadcast_to_room(
        {
            "type": "device_update",
            "data": device_data,
            "timestamp": datetime.now().isoformat(),
        },
        "devices",
    )


async def broadcast_health_update(health_data: dict):
    """
    Broadcast a health score update to all subscribers.

    Args:
        health_data: Health information to broadcast
    """
    await manager.broadcast_to_room(
        {
            "type": "health_update",
            "data": health_data,
            "timestamp": datetime.now().isoformat(),
        },
        "health",
    )
