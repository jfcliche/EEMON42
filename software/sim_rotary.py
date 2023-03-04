import pygame


class SimRotary:
    def __init__(self):
        self._value = 0
        self._min_val = -100
        self._max_val = 100
        self._cb = None
        self._arg = None

    def value(self):
        return self._value

    def set(self, value, min_val, max_val):
        self._value = value
        self._min_val = min_val
        self._max_val = max_val

    def callback(self, cb, arg=None):
        self._cb = cb
        self._arg = arg

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self._value += event.y
            self._value = max(self._value, self._min_val)
            self._value = min(self._value, self._max_val)
            if self._cb:
                self._cb(self._arg)
