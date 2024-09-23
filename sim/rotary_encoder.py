import pygame


class RotaryEncoder:
    def __init__(self, *args, **kwargs):
        self._value = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            # print(f'{event.y}')
            self._value += event.y

    def value(self):
        return self._value
