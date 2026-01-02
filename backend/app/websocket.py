from typing import Dict, List
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for different client types."""
    
    def __init__(self):
        # Active staff connections
        self.staff_connections: List[WebSocket] = []
        
        # Active display connections: {device_id: WebSocket}
        self.display_connections: Dict[str, WebSocket] = {}
        
        # Active client connections: {token: WebSocket}
        self.client_connections: Dict[str, WebSocket] = {}
    
    async def connect_staff(self, websocket: WebSocket):
        """Connect a staff client."""
        await websocket.accept()
        self.staff_connections.append(websocket)
        logger.info(f"Staff connected. Total staff: {len(self.staff_connections)}")
    
    async def connect_display(self, device_id: str, websocket: WebSocket):
        """Connect a display device."""
        await websocket.accept()
        self.display_connections[device_id] = websocket
        logger.info(f"Display {device_id} connected. Total displays: {len(self.display_connections)}")
    
    async def connect_client(self, token: str, websocket: WebSocket):
        """Connect a client tracker."""
        await websocket.accept()
        self.client_connections[token] = websocket
        logger.info(f"Client {token} connected. Total clients: {len(self.client_connections)}")
    
    def disconnect_staff(self, websocket: WebSocket):
        """Disconnect a staff client."""
        if websocket in self.staff_connections:
            self.staff_connections.remove(websocket)
            logger.info(f"Staff disconnected. Total staff: {len(self.staff_connections)}")
    
    def disconnect_display(self, device_id: str):
        """Disconnect a display device."""
        if device_id in self.display_connections:
            del self.display_connections[device_id]
            logger.info(f"Display {device_id} disconnected. Total displays: {len(self.display_connections)}")
    
    def disconnect_client(self, token: str):
        """Disconnect a client tracker."""
        if token in self.client_connections:
            del self.client_connections[token]
            logger.info(f"Client {token} disconnected. Total clients: {len(self.client_connections)}")
    
    async def broadcast_to_staff(self, message: dict):
        """Broadcast message to all staff connections."""
        disconnected = []
        for connection in self.staff_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to staff: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect_staff(conn)
    
    async def send_to_display(self, device_id: str, message: dict):
        """Send message to a specific display."""
        if device_id in self.display_connections:
            try:
                await self.display_connections[device_id].send_json(message)
                logger.info(f"Sent to display {device_id}: {message.get('type')}")
            except Exception as e:
                logger.error(f"Error sending to display {device_id}: {e}")
                self.disconnect_display(device_id)
        else:
            logger.warning(f"Display {device_id} not connected")
    
    async def send_to_client(self, token: str, message: dict):
        """Send message to a specific client."""
        if token in self.client_connections:
            try:
                await self.client_connections[token].send_json(message)
                logger.info(f"Sent to client {token}: {message.get('type')}")
            except Exception as e:
                logger.error(f"Error sending to client {token}: {e}")
                self.disconnect_client(token)
        else:
            logger.debug(f"Client {token} not connected (will receive update when connects)")


# Global connection manager instance
manager = ConnectionManager()
