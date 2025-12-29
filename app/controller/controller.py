import asyncio
import json
import os
import sys
import time
import platform

import websockets

from app.controller.available_key_mapping_list import AVAILABLE_JS_KEYS


def load_backend():
    system = platform.system()

    if system == "Windows":
        from app.controller.platforms.windows.windows import WindowsBackend
        return WindowsBackend()

    if system == "Linux":
        from app.controller.platforms.linux.linux_x11 import LinuxX11Backend
        return LinuxX11Backend()

    raise RuntimeError(f"Unsupported OS: {system}")


class KeyValidator:
    def __init__(self):
        self.valid_keys = AVAILABLE_JS_KEYS

    def filter_key_csv(self, key_csv):
        return ','.join(key for key in key_csv.split(',') if key in self.valid_keys)

validator = KeyValidator()

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
                if not buttons or button not in buttons.split(','):
                    backend.release_key(button)
            for button in pressed_mouse_buttons:
                if not mouse_buttons or button not in mouse_buttons.split(','):
                    backend.release_mouse_button(button)

            if buttons:
                buttons = validator.filter_key_csv(buttons)

                for button in buttons.split(','):
                    if button in pressed_buttons:
                        continue
                    backend.guarded_press_key(button)
                pressed_buttons = buttons.split(',')

            if mouse_buttons:

                for button in mouse_buttons.split(','):
                    if button in pressed_mouse_buttons:
                        continue
                    backend.guarded_press_mouse_button(button)

                pressed_mouse_buttons = mouse_buttons.split(',')

            if mouse_movement:
                dx = mouse_movement.get("x", 0)
                dy = mouse_movement.get("y", 0)

                # Convert to pixels from -1,+1 range
                dx *= 1280
                dy *= 1280
                backend.guarded_move_mouse(dx, dy)


def start_listener(backend, ws_url):
    asyncio.run(listen_for_input(backend, ws_url))


# -------------------------
# Main controller
# -------------------------
def main():
    print("Attempting to load keymap button whitelist from file: whitelist.txt")
    if os.path.exists('whitelist.txt'):
        with open('whitelist.txt', 'r') as f:
            whitelisted_keys = f.readlines()

        validated_whitelisted_keys = []
        for whitelisted_key in whitelisted_keys:
            if whitelisted_key in AVAILABLE_JS_KEYS:
                validated_whitelisted_keys.append(whitelisted_key)

        print("Current whitelisting keys applied:")
        print(json.dumps(validated_whitelisted_keys))

        validator.valid_keys = validated_whitelisted_keys
    else:
        print(
            "File not found. Create a file with list of valid JS key names separated by newlines to function as available keys.")

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
