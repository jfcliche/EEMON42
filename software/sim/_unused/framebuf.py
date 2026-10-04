""" Emulates micropython framebuffer module """

import font

class FrameBuffer:

    RGB565 = 1 # this is the only supported color mode

    def __init__(self, buf, width, height, color_mode):
        self.fb = buf
        self.width = width
        self.height = height



    def text(s,x,y,c=1):
        """ Draws string `s` starting at position ``(x,y)`` using color `c`.
        """
        for c in s:
            cc = ord(c) * 8
            bitmap = font.font8x8[cc: cc + 8]
            self.draw_col_wise_mono_bitmap(x,y, bitmap, width=8, height=8, fg=1, bg=None)
            x += 8

