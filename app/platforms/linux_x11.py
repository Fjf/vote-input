import time
import os
from Xlib import X, display
from Xlib.ext import xtest

from . import Backend

if "WAYLAND_DISPLAY" in os.environ:
    raise RuntimeError("Wayland detected: input injection is blocked by design")

# Full X11 key mapping for US QWERTY
KEYSYM = {
    # Letters
    "KeyA": 0x61,
    "KeyB": 0x62,
    "KeyC": 0x63,
    "KeyD": 0x64,
    "KeyE": 0x65,
    "KeyF": 0x66,
    "KeyG": 0x67,
    "KeyH": 0x68,
    "KeyI": 0x69,
    "KeyJ": 0x6a,
    "KeyK": 0x6b,
    "KeyL": 0x6c,
    "KeyM": 0x6d,
    "KeyN": 0x6e,
    "KeyO": 0x6f,
    "KeyP": 0x70,
    "KeyQ": 0x71,
    "KeyR": 0x72,
    "KeyS": 0x73,
    "KeyT": 0x74,
    "KeyU": 0x75,
    "KeyV": 0x76,
    "KeyW": 0x77,
    "KeyX": 0x78,
    "KeyY": 0x79,
    "KeyZ": 0x7a,

    # Numbers (top row)
    "Digit0": 0x30,
    "Digit1": 0x31,
    "Digit2": 0x32,
    "Digit3": 0x33,
    "Digit4": 0x34,
    "Digit5": 0x35,
    "Digit6": 0x36,
    "Digit7": 0x37,
    "Digit8": 0x38,
    "Digit9": 0x39,

    # Enter / Escape / Backspace / Tab / Space
    "Enter": 0xff0d,
    "Escape": 0xff1b,
    "Backspace": 0xff08,
    "Tab": 0xff09,
    "Space": 0x20,

    # Modifiers
    "ShiftLeft": 0xffe1,
    "ShiftRight": 0xffe2,
    "ControlLeft": 0xffe3,
    "ControlRight": 0xffe4,
    "AltLeft": 0xffe9,
    "AltRight": 0xffea,
    "MetaLeft": 0xffe7,
    "MetaRight": 0xffe8,
    "CapsLock": 0xffe5,

    # Function keys
    "F1": 0xffbe,
    "F2": 0xffbf,
    "F3": 0xffc0,
    "F4": 0xffc1,
    "F5": 0xffc2,
    "F6": 0xffc3,
    "F7": 0xffc4,
    "F8": 0xffc5,
    "F9": 0xffc6,
    "F10": 0xffc7,
    "F11": 0xffc8,
    "F12": 0xffc9,

    # Symbols
    "Minus": 0x2d,        # -
    "Equal": 0x3d,        # =
    "BracketLeft": 0x5b,  # [
    "BracketRight": 0x5d, # ]
    "Backslash": 0x5c,    # \
    "Semicolon": 0x3b,    # ;
    "Quote": 0x27,        # '
    "Backquote": 0x60,    # `
    "Comma": 0x2c,        # ,
    "Period": 0x2e,       # .
    "Slash": 0x2f,        # /

    # Arrow keys
    "ArrowLeft": 0xff51,
    "ArrowUp": 0xff52,
    "ArrowRight": 0xff53,
    "ArrowDown": 0xff54,

    # Home / End / PageUp / PageDown / Insert / Delete
    "Insert": 0xff63,
    "Delete": 0xffff,
    "Home": 0xff50,
    "End": 0xff57,
    "PageUp": 0xff55,
    "PageDown": 0xff56,

    # Numpad
    "Numpad0": 0xffb0,
    "Numpad1": 0xffb1,
    "Numpad2": 0xffb2,
    "Numpad3": 0xffb3,
    "Numpad4": 0xffb4,
    "Numpad5": 0xffb5,
    "Numpad6": 0xffb6,
    "Numpad7": 0xffb7,
    "Numpad8": 0xffb8,
    "Numpad9": 0xffb9,
    "NumpadEnter": 0xff8d,
    "NumpadAdd": 0xffab,
    "NumpadSubtract": 0xffad,
    "NumpadMultiply": 0xffaa,
    "NumpadDivide": 0xffaf,
    "NumpadDecimal": 0xffae,
}


# JS-style mouse button mapping
MOUSE_BUTTONS = {
    "LeftMouseButton": 1,
    "MiddleMouseButton": 2,
    "RightMouseButton": 3,
}

class LinuxX11Backend(Backend):
    def __init__(self):
        self.display = display.Display()
        self.root = self.display.screen().root

    # -------------------------
    # Window methods
    # -------------------------
    def list_windows(self):
        windows = []
        for win in self.root.query_tree().children:
            try:
                name = win.get_wm_name()
                if name:
                    windows.append((win.id, name))
            except Exception:
                pass
        return windows

    def _get_top_level_window(self, win):
        while True:
            parent = win.query_tree().parent
            if parent.id == self.root.id:
                return win
            win = parent

    def focus_window(self, window_id):
        self.focused_window = window_id
        win = self.display.create_resource_object("window", window_id)
        win.set_input_focus(X.RevertToParent, X.CurrentTime)
        self.display.sync()
        time.sleep(0.2)

    def is_foreground(self):
        focus = self.display.get_input_focus().focus
        if not focus:
            return False

        focused_top = self._get_top_level_window(focus)
        selected = self.display.create_resource_object(
            "window", self.focused_window
        )
        selected_top = self._get_top_level_window(selected)

        return focused_top.id == selected_top.id

    def get_foreground_window(self):
        focus = self.display.get_input_focus()
        return focus.focus.id if focus.focus else None

    # -------------------------
    # Keyboard input
    # -------------------------
    def press_key(self, key, duration=0.05):
        keysym = KEYSYM[key]
        keycode = self.display.keysym_to_keycode(keysym)

        xtest.fake_input(self.display, X.KeyPress, keycode)
        self.display.sync()
        time.sleep(duration)
        xtest.fake_input(self.display, X.KeyRelease, keycode)
        self.display.sync()

    # -------------------------
    # Mouse input
    # -------------------------
    def move_mouse(self, x, y):
        """
        Move the mouse relative to the current position.

        x, y: relative delta in pixels
        """
        pointer = self.root.query_pointer()
        current_x = pointer.root_x
        current_y = pointer.root_y

        new_x = current_x + x
        new_y = current_y + y

        # Keep mouse on the screen (assume fullscreen window)
        # TODO: Take windowed-game into account
        screen = self.display.screen()
        new_x = max(0, min(screen.width_in_pixels - 1, new_x))
        new_y = max(0, min(screen.height_in_pixels - 1, new_y))

        xtest.fake_input(self.display, X.MotionNotify, x=new_x, y=new_y)
        self.display.sync()

    def press_mouse_button(self, button, duration=0.05):
        """Press a JS-style mouse button ('left', 'middle', 'right')"""
        btn = MOUSE_BUTTONS.get(button.lower())
        if not btn:
            raise ValueError(f"Unknown mouse button: {button}")

        xtest.fake_input(self.display, X.ButtonPress, btn)
        self.display.sync()
        time.sleep(duration)
        xtest.fake_input(self.display, X.ButtonRelease, btn)
        self.display.sync()
