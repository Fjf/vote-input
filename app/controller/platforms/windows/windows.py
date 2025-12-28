import time
import ctypes
from ctypes import wintypes

from app.controller.platforms import Backend
from app.controller.platforms.windows.consts import INPUT_KEYBOARD, INPUT_MOUSE, KEYEVENTF_SCANCODE, KEYEVENTF_KEYUP, \
    MOUSEEVENTF_MOVE, SW_RESTORE, SCANCODES, MOUSE_BUTTONS
from app.controller.platforms.windows.structs import KEYBDINPUT, MOUSEINPUT, INPUT

user32 = ctypes.WinDLL("user32", use_last_error=True)


# -------------------------
# SendInput helpers
# -------------------------
def _send_key(scancode, flags):
    i = INPUT()
    i.type = INPUT_KEYBOARD
    i.ki = KEYBDINPUT(0, scancode, KEYEVENTF_SCANCODE, 0, 0)
    i.ki.dwFlags |= flags
    user32.SendInput(1, ctypes.byref(i), ctypes.sizeof(INPUT))


def _send_mouse(dx=0, dy=0, dwFlags=0):
    inp = INPUT(
        type=INPUT_MOUSE,
        mi=MOUSEINPUT(
            dx=dx,
            dy=dy,
            mouseData=0,
            dwFlags=dwFlags,
            time=0,
            dwExtraInfo=None,
        ),
    )
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

# -------------------------
# Backend
# -------------------------
class WindowsBackend(Backend):
    def list_windows(self):
        windows = []

        @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        def callback(hwnd, _):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    windows.append((hwnd, buf.value))
            return True

        user32.EnumWindows(callback, 0)
        return windows

    def focus_window(self, window_id):
        self.focused_window = window_id
        user32.ShowWindow(window_id, SW_RESTORE)
        user32.SetForegroundWindow(window_id)
        time.sleep(0.2)

    def get_foreground_window(self):
        return user32.GetForegroundWindow()

    def move_mouse(self, dx, dy):
        """
        Move mouse relative to current position
        dx, dy: pixels to move
        """
        _send_mouse(int(dx), int(dy), MOUSEEVENTF_MOVE)


    def press_key(self, key):
        for key in key.split(','):
            _send_key(SCANCODES[key], 0)

    def release_key(self, key):
        for key in key.split(','):
            _send_key(SCANCODES[key], KEYEVENTF_KEYUP)

    def press_mouse_button(self, button, duration=0.05):
        down_flag, up_flag = MOUSE_BUTTONS[button]
        _send_mouse(dwFlags=down_flag)

    def release_mouse_button(self, button):
        down_flag, up_flag = MOUSE_BUTTONS[button]
        _send_mouse(dwFlags=up_flag)
