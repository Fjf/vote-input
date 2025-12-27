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
    pressed_buttons = []
    pressed_mouse_buttons = []

    async with websockets.connect(ws_url) as websocket:
        print(f"Connected to {ws_url}")

        while True:
            msg = await websocket.recv()

            if not backend.is_foreground():
                # Release all buttons if we are tabbed out.
                for button in pressed_buttons:
                    backend.release_key(button)
                for button in pressed_mouse_buttons:
                    backend.release_mouse_button(button)

            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                continue

            buttons = data.get("button")
            mouse_buttons = data.get('mouse_button')
            mouse_movement = data.get('mouse_movement')
            # Check for all buttons we have to release
            for button in pressed_buttons:
                if button not in buttons.split(','):
                    backend.release_key(button)
            for button in pressed_mouse_buttons:
                if button not in mouse_buttons.split(','):
                    backend.release_mouse_button(button)

            if buttons:
                backend.guarded_press_key(buttons)
                pressed_buttons = buttons.split(',')

            if mouse_buttons:
                backend.guarded_press_mouse_button(mouse_buttons)
                pressed_mouse_buttons = mouse_buttons.split(',')

            if mouse_movement:
                dx = mouse_movement.get("x", 0)
                dy = mouse_movement.get("y", 0)
                backend.guarded_move_mouse(dx, dy)


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

    print("Starting input in 0.5 seconds...")
    time.sleep(0.5)

    host = "localhost"
    port = 7790
    websocket_url = f"ws://{host}:{port}/listen"
    start_listener(backend, websocket_url)

if __name__ == "__main__":
    main()
