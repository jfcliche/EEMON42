import pygame


class RotaryEncoder:
    def __init__(self):
        self._value = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self._value += event.y

    def value(self):
        return self._value
