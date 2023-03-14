import pygame


class Button:

    def __init__(self, rect):
        self._rect = rect
        self._cb = None
        self._arg = None
        self._value = 0

    def rect(self):
        return self._rect

    def value(self):
        ret_value = self._value
        self._value = 0
        return ret_value

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect.collidepoint(self._rect, event.pos) and event.button == 1:
                self._value += 1
