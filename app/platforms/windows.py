import time
import ctypes
from ctypes import wintypes

from . import Backend

user32 = ctypes.WinDLL("user32", use_last_error=True)

# -------------------------
# Win32 constants
# -------------------------
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
SW_RESTORE = 9

VK = {
    "w": 0x57,
    "a": 0x41,
    "s": 0x53,
    "d": 0x44,
    "enter": 0x0D,
    "esc": 0x1B,
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

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("ki", KEYBDINPUT),
    ]

# -------------------------
# Backend
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

    def press_key(self, key, duration=0.05):
        vk = VK[key]
        _send_key(vk, 0)
        time.sleep(duration)
        _send_key(vk, KEYEVENTF_KEYUP)