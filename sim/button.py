import pygame


class Button:

    def __init__(self, *args, rect=None, **kwargs):
        self._rect = rect
        self._cb = None
        self._arg = None
        self._up = 0
        self._down = 0

    def rect(self):
        return self._rect

    def set_rect(self, rect):
        self._rect = rect

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect.collidepoint(self._rect, event.pos) and event.button == 1:
                self._down += 1
        elif event.type == pygame.MOUSEBUTTONUP:
            if pygame.Rect.collidepoint(self._rect, event.pos) and event.button == 1:
                self._up += 1

    def value(self):
        """ Same as down()
        """
        ret_value = self._down
        self._down = self._up = 0
        return ret_value

    def is_down(self):
        return self._rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]

    def down(self):
        ret_value = self._down
        self._down = self._up = 0
        return ret_value

    def up(self):
        ret_value = self._up
        self._down = self._up = 0
        return ret_value

    def clear(self):
        self._down = self._up = 0

