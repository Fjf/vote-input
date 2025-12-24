import json
from pathlib import Path
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount the static directory for generic assets (CSS, images, etc.)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)


# ----------------------------------------------------------------------
# Serve the main HTML page at the root URL
# ----------------------------------------------------------------------
@app.get("/", response_class=FileResponse)
async def get_root():
    """Return the static HTML page."""
    html_path = Path(__file__).parent / "static" / "index.html"
    return FileResponse(html_path)


# ----------------------------------------------------------------------
# Serve the listening HTML page
# ----------------------------------------------------------------------
@app.get("/listening", response_class=FileResponse)
async def get_listening():
    """Return the listening page."""
    html_path = Path(__file__).parent / "static" / "listening.html"
    return FileResponse(html_path)


# ----------------------------------------------------------------------
# Serve JavaScript files located under static/js/
# ----------------------------------------------------------------------
@app.get("/js/{file_path:path}", response_class=FileResponse)
async def get_js(file_path: str):
    """
    Return a JavaScript file from the ``static/js`` directory.

    Example: ``GET /js/app.js`` → ``static/js/app.js``.
    """
    js_path = Path(__file__).parent / "static" / "js" / file_path
    if not js_path.is_file():
        raise HTTPException(status_code=404, detail="JavaScript file not found")
    return FileResponse(js_path, media_type="application/javascript")


class ConnectionManager:
    """Manages active voting WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)


class ListenerManager:
    """Manages active listening WebSocket connections."""

    def __init__(self):
        self.active_listeners: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_listeners.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_listeners.remove(websocket)

    async def broadcast(self, message: str):
        """Send a message to all listening clients."""
        for listener in self.active_listeners:
            await listener.send_text(message)


manager = ConnectionManager()
listener_manager = ListenerManager()
voting_system: dict[str, str] = {}


# ----------------------------------------------------------------------
# Voting WebSocket – receives votes and updates the shared state
# ----------------------------------------------------------------------
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Receive votes from a client and update the voting system."""
    await manager.connect(websocket)
    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            voting_system[client_id] = data.get("key")
            # Notify all listeners about the new voting state
            await listener_manager.broadcast(str(voting_system))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        voting_system.pop(client_id, None)


# ----------------------------------------------------------------------
# Listening WebSocket – only receives updates about the voting system
# ----------------------------------------------------------------------
@app.websocket("/listen")
async def listening_endpoint(websocket: WebSocket):
    """Register a listener and push the current voting state whenever it changes."""
    await listener_manager.connect(websocket)
    try:
        # Send the current state immediately upon connection
        await websocket.send_text(str(voting_system))
        while True:
            # Keep the connection alive; we don't expect incoming messages.
            await websocket.receive_text()
    except WebSocketDisconnect:
        listener_manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=7790, reload=True)