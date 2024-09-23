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
        # self.surface = None  # will be defined by set_surface() call.
        pass

    def reset(self):
        pass

    def init(self):
        pass

    def set_surface(self, surface):
        self.surface = surface

    def clear(self, x1: int = 0, y1: int = 0, x2: int = 95, y2: int = 63) -> None:
        self.surface.fill((0, 0, 0), (x1, y1, x2, y2))

    def write_frame_buffer(self, y0=0, y1=63):
        y0 = y0 if y0 is not None else self.fb_y0
        y1 = y1 if y1 is not None else self.fb_y1
        if y1 < 0: # indicates that no refresh is necessary
            return
        for y in range(y0, y1 + 1):
            a = y * self.BYTES_PER_LINE
            for x in range(self.WIDTH):
                r = self.fb[a] & 0b11111000
                g = ((self.fb[a] & 0b111) << 5) | ((self.fb[a + 1] & 0b11100000) >> 3)
                b = (self.fb[a + 1] & 0b11111) << 3
                # print(f'({x},{y})=({r},{g},{b})')
                self.surface.set_at((x, y), (r, g, b))
                a += 2
        self.fb_y0 = self.HEIGHT - 1
        self.fb_y1 = -1 # -1 is faster to check than y0 > y1

    # def draw_8x8_mono_bitmap(self, x: int, y: int, data: list, r: int = 255, g: int = 255, b: int = 255, bg_r: int = 0, bg_g: int = 0, bg_b: int = 0) -> None:
    #     xx = x
    #     yy = y
    #     index = 0
    #     for j in range(8):
    #         d = data[index]
    #         for i in range(8):
    #             bit = d & 0x80
    #             if bit != 0x00:
    #                 self.surface.set_at((xx, yy), (r, g, b))
    #             else:
    #                 self.surface.set_at((xx, yy), (bg_r, bg_g, bg_b))
    #             d <<= 1
    #             xx += 1
    #         index += 1
    #         yy += 1
    #         xx = x
