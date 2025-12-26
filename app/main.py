import asyncio
import json
import threading
import time
from collections import defaultdict
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
            json_data = json.dumps(vote_counter.get_current_vote_state())

            await self.broadcast(json_data)
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


class VoteCounter:
    def __init__(self):
        # Buttons are all keyboard buttons
        self.buttons: dict[str, str] = {}
        # Left, right, and middle mouse button
        self.mouse_buttons: dict[str, str] = {}
        # Movement is defined as a difference of xDelta, yDelta
        self.mouse_movements: dict[str, MouseUpdate] = {}

    def set(self, user_id, buttons, mouse_buttons, mouse_movements):
        self.buttons[user_id] = buttons
        self.mouse_buttons[user_id] = mouse_buttons
        self.mouse_movements[user_id] = mouse_movements

    def disconnect(self, user_id):
        del self.buttons[user_id]
        del self.mouse_buttons[user_id]
        del self.mouse_movements[user_id]

    def get_current_vote_state(self):
        b_f = defaultdict(int)
        mb_f = defaultdict(int)

        b_max, b_key = 0, None
        mb_max, mb_key = 0, None
        mm_mean = {'x': 0, 'y': 0}
        for user_id in self.buttons.keys():
            b_f[self.buttons[user_id]] += 1
            if b_f[self.buttons[user_id]] > b_max:
                b_max = b_f[self.buttons[user_id]]
                b_key = self.buttons[user_id]

            mb_f[self.mouse_buttons[user_id]] += 1
            if mb_f[self.mouse_buttons[user_id]] > mb_max:
                mb_max = mb_f[self.mouse_buttons[user_id]]
                mb_key = self.mouse_buttons[user_id]

            mm = self.mouse_movements[user_id]
            mm_mean['x'] += mm['xDelta']
            mm_mean['y'] += mm['yDelta']

        if len(self.buttons) > 0:
            mm_mean['x'] /= len(self.buttons)
            mm_mean['y'] /= len(self.buttons)
        return {'button': b_key, 'mouse_button': mb_key, 'mouse_movement': mm_mean}


# TODO: Make this room-based with user provided rooms (e.g., 5-long random strings).
vote_counter = VoteCounter()


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
            vote_counter.set(
                client_id,
                data.get('key'),
                data.get('mouseButton'),
                data.get('mouseDelta')
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        vote_counter.disconnect(client_id)


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
