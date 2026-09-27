import pygame


class RotaryEncoder:
    def __init__(self, button_shift, *args, **kwargs):
        self.button_shift = button_shift
        self._value = 0
        self._shift_value = 0

    def handle_event(self, event):
        shift = pygame.key.get_mods() & pygame.KMOD_SHIFT
        if event.type == pygame.MOUSEWHEEL:
            if shift:
                self._shift_value -= event.y
            else:
                self._value -= event.y
        elif event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_UP and shift) or event.key == pygame.K_LEFT:
                    self._shift_value -= 1
            elif (event.key == pygame.K_DOWN and shift) or event.key == pygame.K_RIGHT:
                    self._shift_value += 1
            elif event.key == pygame.K_UP: # shift must be disabled here
                self._value -= 1
            elif event.key == pygame.K_DOWN:
                self._value += 1

    def value(self):
        return self._value
    def shift_value(self):
        return self._shift_value
