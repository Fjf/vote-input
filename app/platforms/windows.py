import time
import ctypes
from ctypes import wintypes

from . import Backend

user32 = ctypes.WinDLL("user32", use_last_error=True)

# -------------------------
# Win32 constants
# -------------------------
INPUT_KEYBOARD = 1
INPUT_MOUSE = 0
KEYEVENTF_KEYUP = 0x0002
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
SW_RESTORE = 9

VK = {
    "w": 0x57,
    "a": 0x41,
    "s": 0x53,
    "d": 0x44,
    "enter": 0x0D,
    "esc": 0x1B,
}

MOUSE_BUTTONS = {
    "left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
    "right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
    "middle": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
}

# -------------------------
# Win32 structures
# -------------------------
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT)]
    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("_input", _INPUT),
    ]

# -------------------------
# SendInput helpers
# -------------------------
def _send_key(vk, flags):
    inp = INPUT(
        type=INPUT_KEYBOARD,
        ki=KEYBDINPUT(
            wVk=vk,
            wScan=0,
            dwFlags=flags,
            time=0,
            dwExtraInfo=None,
        ),
    )
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

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

    # -------------------------
    # Keyboard
    # -------------------------
    def press_key(self, key, duration=0.05):
        vk = VK[key]
        _send_key(vk, 0)
        time.sleep(duration)
        _send_key(vk, KEYEVENTF_KEYUP)

    # -------------------------
    # Mouse
    # -------------------------
    def move_mouse(self, dx, dy):
        """
        Move mouse relative to current position
        dx, dy: pixels to move
        """
        # Convert relative movement to absolute coordinates in 0..65535
        # Get screen size
        screen_x = user32.GetSystemMetrics(0)
        screen_y = user32.GetSystemMetrics(1)

        # Get current cursor position
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        new_x = int((pt.x + dx) * 65535 / (screen_x - 1))
        new_y = int((pt.y + dy) * 65535 / (screen_y - 1))

        _send_mouse(new_x, new_y, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE)

    def press_mouse_button(self, button, duration=0.05):
        """
        Press and release a JS-style mouse button: 'left', 'right', 'middle'
        """
        if button.lower() not in MOUSE_BUTTONS:
            raise ValueError(f"Unknown mouse button: {button}")
        down_flag, up_flag = MOUSE_BUTTONS[button.lower()]
        _send_mouse(dwFlags=down_flag)
        time.sleep(duration)
        _send_mouse(dwFlags=up_flag)
