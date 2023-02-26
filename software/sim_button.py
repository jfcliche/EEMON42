import pygame


class SimButton:

    def __init__(self, rect):
        self._rect = rect
        self._cb = None
        self._arg = None

    def callback(self, cb, arg=None):
        self._cb = cb
        self._arg = arg

    def rect(self):
        return self._rect

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.Rect.collidepoint(self._rect, event.pos) and event.button == 1 and self._cb:
                self._cb(self._arg)
