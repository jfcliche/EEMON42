# PyPi packages
import pygame

# local packages
import display

class SSD1331(display.Display):

    WIDTH = 96
    HEIGHT = 64
    BYTES_PER_PIXEL = 2

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.surface = pygame.surface.Surface((self.WIDTH, self.HEIGHT))
        self._sim_brightness = 0

    def reset(self):
        pass

    def init(self):
        super().init()

    def clear(self, x1: int = 0, y1: int = 0, x2: int = 95, y2: int = 63) -> None:
        self.surface.fill((0, 0, 0), (x1, y1, x2, y2))

    def write_frame_buffer(self, y0=0, y1=HEIGHT-1):
        y0 = y0 if y0 is not None else self.fb_y0
        y1 = y1 if y1 is not None else self.fb_y1
        if y1 < 0: # indicates that no refresh is necessary
            return
        br = self._sim_brightness
        if 1 or br<1:
            print(f'br={br}, self.brightness={self._sim_brightness}')
        for y in range(y0, y1 + 1):
            a = y * self.BYTES_PER_LINE
            for x in range(self.WIDTH):
                r = self.fb[a] & 0b11111000
                g = ((self.fb[a] & 0b111) << 5) | ((self.fb[a + 1] & 0b11100000) >> 3)
                b = (self.fb[a + 1] & 0b11111) << 3
                # print(f'({x},{y})=({r},{g},{b})')
                self.surface.set_at((x, y), (r * br, g* br, b * br))
                a += 2
        self.fb_y0 = self.HEIGHT - 1
        self.fb_y1 = -1 # -1 is faster to check than y0 > y1

    def _set_brightness(self, brightness):
        print(f'Sim _set_brightness({brightness})')
        # A fractional brightness of 0.5 looks like an OLED brightness of 1 (out of 15)
        if not brightness:
            self._sim_brightness = 0
        else:
            self._sim_brightness = 0.5 + brightness/32
        self.write_frame_buffer()
