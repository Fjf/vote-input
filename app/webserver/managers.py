import asyncio
import json
import threading

from starlette.websockets import WebSocket

from app.webserver.vote_counter import vote_counter


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
        self.emit_interval = 10  # ms

    def init_app(self):
        print('starting background thread!')
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


manager = ConnectionManager()
listener_manager = ListenerManager()
