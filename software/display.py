import font


class Display:
    WIDTH = None
    HEIGHT = None
    BYTES_PER_PIXEL = None
    WHITE = 0b11111_111111_11111 # R_G_B
    BLACK = 0b00000_000000_00000
    YELLOW = 0b11111_111111_00000
    GREEN = 0b00000_111111_00000
    BLUE = 0b00000_000000_11111

    def __init__(self):
        self.BYTES_PER_LINE = self.WIDTH * self.BYTES_PER_PIXEL
        self.fb = memoryview(bytearray(self.BYTES_PER_LINE * self.HEIGHT)) # command+frame buffer, 2 bytes per pixel
        self.fb_y0 = 0  # current lowest modified frame buffer line
        self.fb_y1 = self.HEIGHT-1  # current highest modified frame buffer line

        self.set_font(5)
        self.text_x = 0
        self.text_y = 0
        self.fg = self.WHITE
        self.bg = self.BLACK

    def init(self):
        pass



    def write_frame_buffer(self, y0=None, y1=None):
        """ Sends the specified lines of the frame buffer to the hardware display.

            This method should be provided by the hardware-specific subclass.
        """ 
        raise NotImplementedError()


    def clear(self, update=True):
        zeros = bytearray(self.BYTES_PER_LINE) # preallocate a bunch of zeros for efficiency
        addr = 0
        for j in range(self.HEIGHT):
            self.fb[addr: addr + self.BYTES_PER_LINE] = zeros
        self.fb_y0 = 0
        self.fb_y1 = self.HEIGHT - 1
        if update:
            self.write_frame_buffer()

    @classmethod
    def encode_color(cls, r, g, b):
        """ Convert a RGB value into a color code that is easily usable by the display

        Format: 16-bit color code: RRRRRGGGGGGBBBBB (i.e. R5G6B5)

        Parameters:
            r,g,b (int): values between 0-255

        """ 
        return (r & 0b11111000) << 8 | (g & 0b11111100) << 3 | (b >> 3)

    def draw_8x8_mono_bitmap(self, x: int, y: int, data: list, fg=WHITE,  bg=BLACK) -> None:
        """ Writes a 8x8 monochrome bitmap in the frame buffer.

        The routine is optimized to be efficient in micropython. 
        As currently written, it works only for BYTES_PER_PIXEL=2, with R=5 bits, G=6 bits and  B=5 bits.

        Parameters:

            x, y (int): coordinate of the upper-left corner of the bitmap

            r, g, b (int): foreground color (0-255)

            bg_r, bg_g, bg_b: background color (0-255)
        """
        # t0 = time.ticks_ms()
        fb = self.fb
        addr = (x + y * self.WIDTH) * self.BYTES_PER_PIXEL
        # ta = time.ticks_cpu()
        for j in range(8): # scan rows
            d = data[j]
            a = addr
            for i in range(8): # scan columns
                if (d & (0x80 >> i)):
                    fb[a] = fg >> 8; a +=1
                    fb[a] = fg & 0xFF; a +=1
                else:
                    fb[a] = bg >> 8; a +=1
                    fb[a] = bg & 0xFF; a +=1
            addr += self.BYTES_PER_LINE

        # expand the refresh zone to include modified lines
        self.fb_y0 = min(self.fb_y0, y)  
        self.fb_y1 = max(self.fb_y1, y + self.HEIGHT-1)  

    def draw_5x7_mono_bitmap(self, x: int, y: int, data: list, fg=WHITE, bg=BLACK) -> None:
        """ Writes a 5x7 monochrome bitmap in the frame buffer. Data bytes represent columns.

        Parameters:

            x, y (int): coordinate of the upper-left corner of the bitmap

            r, g, b (int): foreground color (0-255)

            bg_r, bg_g, bg_b: background color (0-255)
        """
        # t0 = time.ticks_ms()
        fb = self.fb
        addr = (x + y * self.WIDTH) * self.BYTES_PER_PIXEL
        # ta = time.ticks_cpu()
        for col in range(5): # scan columns
            d = data[col]
            a = addr
            for row in range(7): # scan rows
                if (d & (1 << row)):
                    fb[a] = fg >> 8;
                    fb[a + 1] = fg & 0xFF; 
                else:
                    fb[a] = bg >> 8; 
                    fb[a + 1] = bg & 0xFF; 
                a += self.BYTES_PER_LINE
            addr += self.BYTES_PER_PIXEL

        # expand the refresh zone to include modified lines
        self.fb_y0 = min(self.fb_y0, y)  
        self.fb_y1 = max(self.fb_y1, y + self.HEIGHT -1)  

    def set_font(self, font_size):
        if font_size==8:
            self.font = font.font8x8
            self.font_width = 8
            self.font_height = 8
        else:
            self.font = font.font5x7
            self.font_width = 5
            self.font_height = 7

    def set_fg_color(self, color):
        if isinstance(color, tuple):
            self.fg = self.encode_color(color)
        else:
            self.fg = color

    def set_bg_color(self, color):
        if isinstance(color, tuple):
            self.bg = self.encode_color(color)
        else:
            self.bg = color

    def print(self, text, x=None, y=None, fg=None, bg=None, update=True, font_size=None):
        """ Displays a single line of text"""
        if font_size:
            self.set_font(font_size)
        if x is not None:
            self.text_x = x
        if y is not None:
            self.text_y = y
        if fg is not None:
            self.set_fg_color(fg)
        if bg is not None:
            self.set_bg_color(bg)

        for c in text:
            if c == '\r':
                self.text_x = 0
                continue
            elif c == '\n':
                self.text_y += self.font_height
                continue

            if self.font_width == 8: # implied 8x8 font with row-wise encoding
                cc = ord(c) * self.font_height # x8
                bitmap = font.font8x8[cc: cc + self.font_height]
                self.draw_8x8_mono_bitmap(self.text_x, self.text_y, bitmap, self.fg, self.bg)
            else: # implied 5x7 font with column-wise encoding
                cc = ord(c) * self.font_width
                bitmap = font.font5x7[cc: cc + self.font_width]
                self.draw_5x7_mono_bitmap(self.text_x, self.text_y, bitmap, self.fg, self.bg)
            self.text_x += self.font_width

            # wrap text
            if self.text_x >= self.WIDTH:
                self.text_x = 0
                self.text_y += self.font_height

        if update:
            self.write_frame_buffer()
