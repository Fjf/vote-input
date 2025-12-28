import json

from starlette.websockets import WebSocket, WebSocketDisconnect

from app.webserver.main import app
from app.webserver.managers import manager, listener_manager
from app.webserver.vote_counter import vote_counter


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Receive votes from a client and update the voting system."""
    await manager.connect(websocket)
    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            vote_counter.set(
                client_id,
                data.get('key'),
                data.get('mouseButton'),
                data.get('mouseDelta')
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        vote_counter.disconnect(client_id)


@app.websocket("/listen")
async def listening_endpoint(websocket: WebSocket):
    """Register a listener and push the current voting state whenever it changes."""
    await listener_manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive; we don't expect incoming messages.
            await websocket.receive_text()
    except WebSocketDisconnect:
        listener_manager.disconnect(websocket)
