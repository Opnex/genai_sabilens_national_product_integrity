"""WebSocket connection manager"""
from typing import List, Dict
from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, client_id: str, websocket: WebSocket):
        """Connect a new WebSocket"""
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)
    
    def disconnect(self, client_id: str, websocket: WebSocket):
        """Disconnect a WebSocket"""
        self.active_connections[client_id].remove(websocket)
    
    async def broadcast(self, client_id: str, message: str):
        """Broadcast message to all connections for a client"""
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    pass
    
    async def send_personal(self, websocket: WebSocket, message: str):
        """Send message to a specific connection"""
        try:
            await websocket.send_text(message)
        except Exception:
            pass


# Global instance
ws_manager = ConnectionManager()
