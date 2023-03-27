import pygame


class SSD1331:


    def __init__(self, *args, **kwargs):
        self.surface = None  # will be defined by set_surface() call.



    def set_surface(self, surface):
        self.surface = surface

    def clear(self, x1: int = 0, y1: int = 0, x2: int = 95, y2: int = 63) -> None:
        self.surface.fill((0, 0, 0), (x1, y1, x2, y2))

    def draw_8x8_mono_bitmap(self, x: int, y: int, data: list, r: int = 255, g: int = 255, b: int = 255, bg_r: int = 0, bg_g: int = 0, bg_b: int = 0) -> None:
        xx = x
        yy = y
        index = 0
        for j in range(8):
            d = data[index]
            for i in range(8):
                bit = d & 0x80
                if bit != 0x00:
                    self.surface.set_at((xx, yy), (r, g, b))
                else:
                    self.surface.set_at((xx, yy), (bg_r, bg_g, bg_b))
                d <<= 1
                xx += 1
            index += 1
            yy += 1
            xx = x
