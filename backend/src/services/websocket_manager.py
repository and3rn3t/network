"""WebSocket connection manager for real-time updates."""

import json
import logging
from typing import Dict, Set, List
from datetime import datetime
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasting.

    Supports room-based broadcasting for targeted updates.
    """

    def __init__(self):
        """Initialize connection manager."""
        # Active connections by client ID
        self.active_connections: Dict[str, WebSocket] = {}

        # Room subscriptions: room_name -> set of client_ids
        self.rooms: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """
        Accept a new WebSocket connection.

        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

        # Send welcome message
        await self.send_personal_message(
            {
                "type": "connection",
                "status": "connected",
                "client_id": client_id,
                "timestamp": datetime.now().isoformat(),
            },
            client_id,
        )

    def disconnect(self, client_id: str) -> None:
        """
        Remove a WebSocket connection.

        Args:
            client_id: Client identifier to disconnect
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")

        # Remove from all rooms
        for room_clients in self.rooms.values():
            room_clients.discard(client_id)

    async def send_personal_message(self, message: dict, client_id: str) -> None:
        """
        Send a message to a specific client.

        Args:
            message: Message data to send
            client_id: Target client identifier
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: dict) -> None:
        """
        Broadcast a message to all connected clients.

        Args:
            message: Message data to send
        """
        disconnected_clients = []

        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    def join_room(self, client_id: str, room: str) -> None:
        """
        Add a client to a room.

        Args:
            client_id: Client identifier
            room: Room name to join
        """
        if room not in self.rooms:
            self.rooms[room] = set()

        self.rooms[room].add(client_id)
        logger.info(f"Client {client_id} joined room '{room}'")

    def leave_room(self, client_id: str, room: str) -> None:
        """
        Remove a client from a room.

        Args:
            client_id: Client identifier
            room: Room name to leave
        """
        if room in self.rooms:
            self.rooms[room].discard(client_id)
            logger.info(f"Client {client_id} left room '{room}'")

    async def broadcast_to_room(self, message: dict, room: str) -> None:
        """
        Broadcast a message to all clients in a room.

        Args:
            message: Message data to send
            room: Target room name
        """
        if room not in self.rooms:
            return

        disconnected_clients = []

        for client_id in self.rooms[room]:
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id} in room {room}: {e}")
                    disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return len(self.active_connections)

    def get_room_members(self, room: str) -> List[str]:
        """
        Get list of clients in a room.

        Args:
            room: Room name

        Returns:
            List of client IDs in the room
        """
        return list(self.rooms.get(room, set()))


# Global connection manager instance
manager = ConnectionManager()
