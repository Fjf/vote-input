import time
import os
from Xlib import X, display
from Xlib.ext import xtest

from app.controller.platforms import Backend
from app.controller.platforms.linux.consts import KEYSYM, MOUSE_BUTTONS

if "WAYLAND_DISPLAY" in os.environ:
    raise RuntimeError("Wayland detected: input injection is blocked by design")

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
