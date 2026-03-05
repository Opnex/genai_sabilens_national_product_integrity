"""WebSocket routes."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.websocket import ws_manager

router = APIRouter()


async def _handle_socket(websocket: WebSocket, client_id: str):
    await ws_manager.connect(client_id, websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await ws_manager.send_personal(websocket, f"ack:{message}")
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id, websocket)
    except Exception:
        ws_manager.disconnect(client_id, websocket)


@router.websocket("/ws/ws")
async def websocket_bridge(websocket: WebSocket):
    """Compatibility WebSocket endpoint used by frontend clients."""
    await _handle_socket(websocket, "default")


@router.websocket("/api/ws/ws")
async def websocket_bridge_api(websocket: WebSocket):
    """Compatibility WebSocket endpoint used by frontend clients."""
    await _handle_socket(websocket, "default")
