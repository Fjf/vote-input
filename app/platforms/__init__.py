import sys
import abc

class Backend(abc.ABC):
    def is_foreground(self):
        return self.get_foreground_window() == self.focused_window

    @abc.abstractmethod
    def list_windows(self):
        raise NotImplementedError

    focused_window = None
    @abc.abstractmethod
    def focus_window(self, window_id):
        """
        Platform-specific implementation should set the focused_window property to the same value that we would get
        from `get_foreground_window()`.
        :param window_id:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def press_key(self, key, duration=0.05):
        raise NotImplementedError

    @abc.abstractmethod
    def get_foreground_window(self):
        raise NotImplementedError

    def guarded_press_key(self, key, duration=0.05):
        if not self.is_foreground():
            return
        self.press_key(key, duration)