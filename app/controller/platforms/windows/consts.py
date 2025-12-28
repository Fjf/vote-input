INPUT_KEYBOARD = 1
INPUT_MOUSE = 0
KEYEVENTF_SCANCODE = 0x8
KEYEVENTF_KEYUP = 0x0002
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_MOVE_NOCOALESCE = 0x2000
SW_RESTORE = 9
SCANCODES = {
    # Letters
    "KeyA": 0x1E,
    "KeyB": 0x30,
    "KeyC": 0x2E,
    "KeyD": 0x20,
    "KeyE": 0x12,
    "KeyF": 0x21,
    "KeyG": 0x22,
    "KeyH": 0x23,
    "KeyI": 0x17,
    "KeyJ": 0x24,
    "KeyK": 0x25,
    "KeyL": 0x26,
    "KeyM": 0x32,
    "KeyN": 0x31,
    "KeyO": 0x18,
    "KeyP": 0x19,
    "KeyQ": 0x10,
    "KeyR": 0x13,
    "KeyS": 0x1F,
    "KeyT": 0x14,
    "KeyU": 0x16,
    "KeyV": 0x2F,
    "KeyW": 0x11,
    "KeyX": 0x2D,
    "KeyY": 0x15,
    "KeyZ": 0x2C,

    # Numbers (top row)
    "Digit1": 0x02,
    "Digit2": 0x03,
    "Digit3": 0x04,
    "Digit4": 0x05,
    "Digit5": 0x06,
    "Digit6": 0x07,
    "Digit7": 0x08,
    "Digit8": 0x09,
    "Digit9": 0x0A,
    "Digit0": 0x0B,

    # Enter, Escape, Backspace, Tab, Space
    "Enter": 0x1C,
    "Escape": 0x01,
    "Backspace": 0x0E,
    "Tab": 0x0F,
    "Space": 0x39,

    # Modifiers
    "ShiftLeft": 0x2A,
    "ShiftRight": 0x36,
    "ControlLeft": 0x1D,
    "ControlRight": 0x1D | 0xE000,  # extended
    "AltLeft": 0x38,
    "AltRight": 0x38 | 0xE000,      # extended
    "MetaLeft": 0x5B | 0xE000,
    "MetaRight": 0x5C | 0xE000,
    "CapsLock": 0x3A,

    # Function keys
    "F1": 0x3B,
    "F2": 0x3C,
    "F3": 0x3D,
    "F4": 0x3E,
    "F5": 0x3F,
    "F6": 0x40,
    "F7": 0x41,
    "F8": 0x42,
    "F9": 0x43,
    "F10": 0x44,
    "F11": 0x57,
    "F12": 0x58,

    # Symbols
    "Minus": 0x0C,
    "Equal": 0x0D,
    "BracketLeft": 0x1A,
    "BracketRight": 0x1B,
    "Backslash": 0x2B,
    "Semicolon": 0x27,
    "Quote": 0x28,
    "Backquote": 0x29,
    "Comma": 0x33,
    "Period": 0x34,
    "Slash": 0x35,

    # Arrow keys (extended)
    "ArrowLeft": 0x4B | 0xE000,
    "ArrowUp": 0x48 | 0xE000,
    "ArrowRight": 0x4D | 0xE000,
    "ArrowDown": 0x50 | 0xE000,

    # Navigation (extended)
    "Insert": 0x52 | 0xE000,
    "Delete": 0x53 | 0xE000,
    "Home": 0x47 | 0xE000,
    "End": 0x4F | 0xE000,
    "PageUp": 0x49 | 0xE000,
    "PageDown": 0x51 | 0xE000,

    # Numpad
    "Numpad0": 0x52,
    "Numpad1": 0x4F,
    "Numpad2": 0x50,
    "Numpad3": 0x51,
    "Numpad4": 0x4B,
    "Numpad5": 0x4C,
    "Numpad6": 0x4D,
    "Numpad7": 0x47,
    "Numpad8": 0x48,
    "Numpad9": 0x49,
    "NumpadEnter": 0x1C | 0xE000,
    "NumpadAdd": 0x4E,
    "NumpadSubtract": 0x4A,
    "NumpadMultiply": 0x37,
    "NumpadDivide": 0x35 | 0xE000,
    "NumpadDecimal": 0x53,
}

MOUSE_BUTTONS = {
    "LeftMouseButton": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
    "RightMouseButton": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
    "MiddleMouseButton": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
}
