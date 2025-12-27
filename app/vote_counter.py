import random
from collections import defaultdict

from pydantic import BaseModel


class MouseUpdate(BaseModel):
    xDelta: float  # Between -1 and 1, 1 is monitor width
    yDelta: float  # Between -1 and 1, 1 io monitor height.


class VoteCounter:
    def __init__(self):
        print("init vote counter")
        # Buttons are all keyboard buttons
        self.buttons: dict[str, str] = {}
        # Left, right, and middle mouse button
        self.mouse_buttons: dict[str, str] = {}
        # Movement is defined as a difference of xDelta, yDelta
        self.mouse_movements: dict[str, MouseUpdate] = {}

    def set(self, user_id, buttons, mouse_buttons, mouse_movements):
        self.buttons[user_id] = buttons
        self.mouse_buttons[user_id] = mouse_buttons
        self.mouse_movements[user_id] = mouse_movements

    def disconnect(self, user_id):
        del self.buttons[user_id]
        del self.mouse_buttons[user_id]
        del self.mouse_movements[user_id]

    def get_current_vote_state(self):
        b_f = defaultdict(int)
        mb_f = defaultdict(int)

        b_max, b_key = 0, None
        mb_max, mb_key = 0, None
        mm_mean = {'x': 0, 'y': 0}

        # Ensure random prioritization in cases of ties is found.
        keys = list(self.buttons.keys())
        random.shuffle(keys)

        for user_id in keys:
            b_f[self.buttons[user_id]] += 1
            if b_f[self.buttons[user_id]] > b_max:
                b_max = b_f[self.buttons[user_id]]
                b_key = self.buttons[user_id]

            mb_f[self.mouse_buttons[user_id]] += 1
            if mb_f[self.mouse_buttons[user_id]] > mb_max:
                mb_max = mb_f[self.mouse_buttons[user_id]]
                mb_key = self.mouse_buttons[user_id]

            mm = self.mouse_movements[user_id]
            mm_mean['x'] += mm['xDelta']
            mm_mean['y'] += mm['yDelta']

        if len(self.buttons) > 0:
            mm_mean['x'] /= len(self.buttons)
            mm_mean['y'] /= len(self.buttons)
        return {'button': b_key, 'mouse_button': mb_key, 'mouse_movement': mm_mean}


# TODO: Make this room-based with user provided rooms (e.g., 5-long random strings).
vote_counter = VoteCounter()