import asyncio
import json
import sys
import time
import platform

import websockets


# -------------------------
# Backend selection
# -------------------------
def load_backend():
    system = platform.system()

    if system == "Windows":
        from platforms.windows import WindowsBackend
        return WindowsBackend()

    if system == "Linux":
        from platforms.linux_x11 import LinuxX11Backend
        return LinuxX11Backend()

    raise RuntimeError(f"Unsupported OS: {system}")



async def listen_for_input(backend, ws_url):
    async with websockets.connect(ws_url) as websocket:
        print(f"Connected to {ws_url}")

        while True:
            msg = await websocket.recv()

            try:
                data = json.loads(msg)
                print("received:", data)
            except json.JSONDecodeError:
                continue

            if data.get("button"):
                backend.guarded_press_key(data["button"])

            if data.get("mouse_button"):
                backend.press_mouse_button(data["mouse_button"])

            if data.get("mouse_movement"):
                dx = data["mouse_movement"].get("x", 0)
                dy = data["mouse_movement"].get("y", 0)
                backend.move_mouse(dx, dy)


def start_listener(backend, ws_url):
    asyncio.run(listen_for_input(backend, ws_url))

# -------------------------
# Main controller
# -------------------------
def main():
    backend = load_backend()

    windows = backend.list_windows()
    if not windows:
        print("No windows found")
        sys.exit(1)

    print("Running applications:")
    for i, (_, title) in enumerate(windows, start=1):
        print(f"{i}. {title}")

    try:
        idx = int(input("Select window: ")) - 1
        window_id, title = windows[idx]
    except (ValueError, IndexError):
        print("Invalid selection")
        sys.exit(1)

    print(f"Focusing: {title}")
    backend.focus_window(window_id)

    print("Starting input in 2 seconds...")
    time.sleep(2)

    host = "localhost"
    port = 7790
    websocket_url = f"ws://{host}:{port}/listen"
    start_listener(backend, websocket_url)

if __name__ == "__main__":
    main()
