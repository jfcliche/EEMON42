"""Shared pygame framebuffer blit logic for display simulators."""

import pygame


class PygameDisplay:
    """Mixin for hardware Display subclasses; adds ``surface`` and sim ``update``."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.surface = pygame.surface.Surface((self.WIDTH, self.HEIGHT))
        self._sim_brightness = 0

    def update(self):
        y1 = self.fb_y1
        if y1 < 0:
            return
        y0 = self.fb_y0
        br = self._sim_brightness
        for y in range(y0, y1 + 1):
            a = y * self.BYTES_PER_LINE
            for x in range(self.WIDTH):
                r = self.fb[a] & 0b11111000
                g = ((self.fb[a] & 0b111) << 5) | ((self.fb[a + 1] & 0b11100000) >> 3)
                b = (self.fb[a + 1] & 0b11111) << 3
                self.surface.set_at((x, y), (r * br, g * br, b * br))
                a += 2
        self.fb_y0 = self.HEIGHT - 1
        self.fb_y1 = -1

    def _set_brightness(self, brightness):
        if not brightness:
            self._sim_brightness = 0
        else:
            self._sim_brightness = 0.5 + brightness / 32
        self.update_all()

    def reset(self):
        pass

    def write_command(self, data):
        pass

    def write_data(self, data):
        pass

    def send_command(self, cmd, data=None):
        pass
