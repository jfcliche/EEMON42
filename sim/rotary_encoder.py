import pygame


class RotaryEncoder:
    def __init__(self, button_shift, *args, **kwargs):
        self.button_shift = button_shift
        self._value = 0
        self._shift_value = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            if self.button_shift.is_down():
                self._shift_value += event.y
            else:
                self._value += event.y

    def value(self):
        return self._value
    def shift_value(self):
        return self._shift_value
