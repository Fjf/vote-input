import asyncio
import json
import threading
import time
from functools import partial
from pathlib import Path
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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
@app.get("/download", response_class=FileResponse)
async def download_input_overlay():
    """Return the Electron installer as a downloadable file."""
    file_path = Path(__file__).parent / "electron" / "dist" / "InputOverlay Setup 1.0.0.exe"
    return FileResponse(
        path=file_path,
        filename="InputOverlay.exe",  # Name shown to the user
        media_type="application/octet-stream"
    )


# ----------------------------------------------------------------------
# Serve JavaScript files located under static/js/
# ----------------------------------------------------------------------
@app.get("/js/{file_path:path}", response_class=FileResponse)
async def get_js(file_path: str):
    """
    Return a JavaScript file from the ``static/js`` directory.

    Example: ``GET /js/app.js`` → ``static/js/app.js``.
    """
    js_path = Path(__file__).parent / "electron" / "js" / file_path
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
        self.emit_interval = 100  # ms
        threading.Thread(target=self._run_emitter_loop, daemon=True).start()

    def _run_emitter_loop(self):
        asyncio.run(self.emit_sporadically())

    async def emit_sporadically(self):
        while True:
            await self.broadcast(str(vote_tally_buttons) + str(vote_tally_mouse_movements))
            await asyncio.sleep(self.emit_interval / 1000)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_listeners.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_listeners.remove(websocket)

    async def broadcast(self, message: str):
        """Send a message to all listening clients."""
        for listener in self.active_listeners:
            await listener.send_text(message)


class MouseUpdate(BaseModel):
    xDelta: float  # Between -1 and 1, 1 is monitor width
    yDelta: float  # Between -1 and 1, 1 io monitor height.

manager = ConnectionManager()
listener_manager = ListenerManager()

# Buttons are all keyboard buttons and the 3 mouse buttons.
vote_tally_buttons: dict[str, str] = {}
# Movement is defined as a difference of xDelta, yDelta
vote_tally_mouse_movements: dict[str, MouseUpdate] = {}


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
            vote_tally_mouse_movements[client_id] = data.get('mouseDelta')
            vote_tally_buttons[client_id] = data.get("key")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        vote_tally_buttons.pop(client_id, None)
        vote_tally_mouse_movements.pop(client_id, None)


# ----------------------------------------------------------------------
# Listening WebSocket – only receives updates about the voting system
# ----------------------------------------------------------------------
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


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=7790, reload=True)