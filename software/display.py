import time

import font


# In-string color code
# Colors are encoded as R2G2B2 values. 
# Foreground color codes are ASCII character 128-191, background color codes are ASCII characters 192-255 
WF = chr(0b10_111111) # White foreground
RF = chr(0b10_110000) # Red foreground
GF = chr(0b10_001100) # Green foreground
BF = chr(0b10_000011) # Blue foreground
YF = chr(0b10_111100) # Yellow foreground
CF = chr(0b10_001111) # Cyan foreground
KF = chr(0b10_000000)  # Black foreground

WB = chr(0b11_111111) # White background
RB = chr(0b11_110000) # Red background
GB = chr(0b11_001100) # Green background
BB = chr(0b11_000011) # Blue background
YB = chr(0b11_111100) # Yellow background
CB = chr(0b11_001111) # Cyan background
KB = chr(0b11_000000)  # Black background
cB = chr(0b11_000101) # Dark Cyan background

CC = chr(31) # clear color

class Display:
    """ Frame buffer for R5G5B5 displays. 
  
    """
    # Display geometry
    WIDTH = None
    HEIGHT = None
    BYTES_PER_PIXEL = None

    # Basic colors
    WHITE = 0b11111_111111_11111 # R5_G6_B5 format
    BLACK = 0b00000_000000_00000
    YELLOW = 0b11111_111111_00000
    GREEN = 0b00000_111111_00000
    BLUE = 0b00000_000000_11111
    CYAN = 0b00000_111111_11111
    DARKCYAN = 0b00000_011111_01111

 

    def __init__(self, fb=None):
        self.BYTES_PER_LINE = self.WIDTH * self.BYTES_PER_PIXEL

        # initialize the frame buffer if one is not alreadyprovided
        if fb:
            self.fb  =fb
        else:
            self.fb = memoryview(bytearray(self.BYTES_PER_LINE * self.HEIGHT)) # frame buffer, 2 bytes per pixel

        self.zeros = memoryview(bytearray(self.BYTES_PER_LINE)) # preallocate a line of zeros for efficiency


        self.fb_y0 = 0  # current lowest modified frame buffer line
        self.fb_y1 = self.HEIGHT-1  # current highest modified frame buffer line
        self.cl_y0 = 0
        self.cl_y1 = self.HEIGHT-1

        self.brightness = 0 # dim level: 0= display off, 1: min brightness, 16: max brightness
        self.last_time = time.time()

        # current font information
        self.font = None  # Font bitmap table
        self.font_width = None  # font horizontal pitch in pixels
        self.font_height = None # font vertical pitch in pixels

        self.set_font(5)
        self.text_x = 0
        self.text_y = 0
        self.fg = self.WHITE
        self.bg = self.BLACK

    def init(self):
        self.set_brightness(16)
        self.clear(update=True)


    def set_brightness(self, brightness=16):
        if brightness == 16:
            self.last_time = time.time()
        if self.brightness == brightness:
            return 
        self._set_brightness(brightness)
        self.brightness = brightness

    def update(self):
        """ Sends the invalidated lines of the frame buffer to the display.

            This method should be provided by the hardware-specific subclass.
        """ 
        raise NotImplementedError()

    def _set_brightness(self, brightness):
        """ Set the brightness of the display.

        Parameters:
            brightness (int): brightness value between 0 and 16
        """
        raise NotImplementedError()

    def update_all(self):
        self.fb_y0 = 0
        self.fb_y1 = self.HEIGHT - 1
        self.update()

    # def update(self, y0=None, y1=None):
    #     self.write_frame_buffer(y0=y0, y1=y1)

    def clear(self, update=False, force=False):
        fb = self.fb
        if force:
            self.fb_y0 = 0
            self.fb_y1 = self.HEIGHT - 1
        else:
            self.fb_y0 = self.cl_y0
            self.fb_y1 = self.cl_y1
            if self.cl_y1 < 0:
                return

        addr = self.fb_y0 * self.BYTES_PER_LINE
        for j in range(self.fb_y1 - self.fb_y0 + 1):
            fb[addr: addr + self.BYTES_PER_LINE] = self.zeros
            addr += self.BYTES_PER_LINE
        self.text_x = self.text_y = 0
        if update:
            self.update()
        self.cl_y0 = self.HEIGHT - 1
        self.cl_y1 = -1

    def fill(self, x0, y0, x1, y1, color, update=False):
        fb = self.fb
        addr = (x0 + y0 * self.WIDTH) * self.BYTES_PER_PIXEL
        for j in range(y1 - y0 + 1):
            a = addr
            for i in range(x1 - x0 + 1):
                fb[a] = color >> 8; a +=1
                fb[a] = color & 0xFF; a +=1
            addr += self.BYTES_PER_LINE
        self.fb_y0 = min(self.fb_y0, y0)  
        self.fb_y1 = max(self.fb_y1, y1) 
        if update:
            self.update()

    @classmethod
    def encode_color(cls, r, g, b):
        """ Convert a RGB value into an integer color code that is easily usable by the display

        Format: 16-bit color code: RRRRRGGGGGGBBBBB (i.e. R5G6B5)

        Parameters:
            r,g,b (int): values between 0-255

        Returns:
            int: 16-bit color code
        """ 
        return (r & 0b11111000) << 8 | (g & 0b11111100) << 3 | (b >> 3)

    @classmethod
    def convert_R2G2B2_color(cls, c):
        """ Convert R2G2B2 color into R5G6B5 color 
        """
        return ((0, 0b01010_000000_00000, 0b10100_000000_00000, 0b11111_000000_00000)[(c >> 4) & 0b11] |
                (0, 0b010101_00000, 0b101010_00000, 0b111111_00000)[(c >> 2) & 0b11] |
                (0, 0b01010, 0b10100, 0b11111)[c & 0b11])

    def hline(self, x0, x1, y, color = WHITE):
        """ Draws an horizontal line in the frame buffer

        Parameters:

            x0, x1, y (int): coordinates of the line. Line will be drawn between (x0,y) and (x1,y).

        """
        fb = self.fb
        a = (x0 + y * self.WIDTH) * self.BYTES_PER_PIXEL
        for i in range(x1 - x0 + 1):
            fb[a] = color >> 8; a +=1
            fb[a] = color & 0xFF; a +=1
        self.fb_y0 = min(self.fb_y0, y)  
        self.fb_y1 = max(self.fb_y1, y) 

    def vline(self, x, y0, y1, color = WHITE):
        """ Draws an vertical line in the frame buffer

        Parameters:

            x, y0, y1 (int): coordinates of the line. Line will be drawn between (x,y0) and (x,y1).

        """
        fb = self.fb
        a = (x + y0 * self.WIDTH) * self.BYTES_PER_PIXEL
        for i in range(y1 - y0 + 1):
            fb[a] = color >> 8
            fb[a+1] = color & 0xFF
            a += self.BYTES_PER_LINE
        self.fb_y0 = min(self.fb_y0, y0)  
        self.fb_y1 = max(self.fb_y1, y1) 

    # def draw_row_wise_mono_bitmap(self, x: int, y: int, data: list, width=8, height=8, fg=WHITE,  bg=BLACK) -> None:
    #     """ Writes a 8x8 monochrome bitmap in the frame buffer.

    #     The routine is optimized to be efficient in micropython. 
    #     As currently written, it works only for BYTES_PER_PIXEL=2, with R=5 bits, G=6 bits and  B=5 bits.

    #     Parameters:

    #         x, y (int): coordinate of the upper-left corner of the bitmap

    #         r, g, b (int): foreground color (0-255)

    #         bg_r, bg_g, bg_b: background color (0-255)
    #     """
    #     # t0 = time.ticks_ms()
    #     fb = self.fb
    #     addr = (x + y * self.WIDTH) * self.BYTES_PER_PIXEL
    #     # ta = time.ticks_cpu()
    #     for j in range(height): # scan rows
    #         d = data[j]
    #         a = addr
    #         for i in range(width): # scan columns
    #             if (d & (0x80 >> i)):
    #                 fb[a] = fg >> 8; a +=1
    #                 fb[a] = fg & 0xFF; a +=1
    #             else:
    #                 fb[a] = bg >> 8; a +=1
    #                 fb[a] = bg & 0xFF; a +=1
    #         addr += self.BYTES_PER_LINE

    #     # expand the refresh zone to include modified lines
    #     self.fb_y0 = min(self.fb_y0, y)  
    #     self.fb_y1 = max(self.fb_y1, y + height -1)  


    def draw_col_wise_mono_bitmap(self, x: int, y: int, data: list, width=5, height=7, fg=WHITE, bg=BLACK) -> None:
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
        for col in range(width): # scan columns
            d = data[col]
            a = addr
            for row in range(height): # scan rows
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
        self.fb_y1 = max(self.fb_y1, y + height -1)  

    def set_font(self, font_size):
        if font_size is None:
            return
        if font_size==8:
            self.font = font.font8x8
            self.font_width = 8
            self.font_height = 8
            self.font_is_row_wise = False
        else:
            self.font = font.font5x7
            self.font_width = 5
            self.font_height = 7
            self.font_is_row_wise = False

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

    def set_colors(self, fg=None, bg=None, hl_fg=None, hl_bg=None):
        if fg is not None:
            self.set_fg_color(fg)
        if bg is not None:
            self.set_bg_color(bg)
        if hl_fg is not None:
            self.hl_fg = self.encode_color(hl_fg) if isinstance(hl_fg, tuple) else hl_fg;
        if hl_bg is not None:
            self.hl_bg = self.encode_color(hl_bg) if isinstance(hl_bg, tuple) else hl_bg;

    def print_width(self, text):
        """ Return the maximum length of the text lines in ``text``, excluding non-printable characters 
        """
        return max(sum(not(c == '\r' or c == '\n' or c==CC or ord(c)>=128) 
                   for c in line) 
                   for line in text.splitlines()) 

    def print(self, text, x=None, y=None, width = None, fg=None, bg=None, font_size=None, hl_start=None, hl_stop=None, inv_start=None, inv_stop=None, wrap=False, update=False ):
        """ Print text in the frame buffer

        Parameters:

            text (str): string to print

            x, y (int): coordinate of where to start to print. If not specified, continues from last current location.

            fg, bg (int): sets the foreground and background color by calling ``set_fg_color()`` and ``set_bg_color`` . If not specified, the current colors are used.

            update (bool): if True, the the frame buffer is sent to the display after the print is complete.

            font_size (int): Indicates which font to use by calling ``set_font()``. If not specified, the current font is used. 

            inv_start, inv_stop (int): position between which the text colors are inverted
        """
        if x is not None:
            self.text_x = x
        if y is not None:
            self.text_y = y
        self.set_font(font_size)
        self.set_colors(fg=fg, bg=bg)

        font = self.font
        font_width = self.font_width
        font_height = self.font_height
        fg = self.fg
        bg = self.bg
        # font_is_row_wise = self.font_is_row_wise 

        # print(f'Printing {text} at {self.text_x=}, {self.text_y=}')
        highlight = False
        invert = False
        x1 = min(self.WIDTH-1, self.text_x + width*font_width - 1) if width is not None else self.WIDTH-1

        def pad():
            if self.text_x > x1:
                return
            # print(f'Fill {self.text_x, self.text_y, x1, self.text_y + font_height-1}')
            self.fill(self.text_x, self.text_y, x1, self.text_y + font_height - 1, fg if invert else bg)

        def newline():
            pad()
            self.text_x = 0
            self.text_y += font_height

        for pos, c in enumerate(text):
            # cc = ord(c)
            # Process special characters
            if c == '\r': # carriage return
                pad()
                self.text_x = 0
                continue
            elif c == '\n': # newline (carriage return + linefeed)
                newline()
                continue
            elif c == CC: # clear color codes
                fg = self.fg
                bg = self.bg 
                continue
            elif (cc := ord(c)) >= 192: # background color codes
                bg = self.convert_R2G2B2_color(cc)   
                continue
            elif cc >= 128: # foreground color codes
                fg = self.convert_R2G2B2_color(cc)
                continue
            # wrap line if current character won't fit   
            if self.text_x + font_width - 1 > x1:
                if wrap:
                    newline()
                else:
                    continue # don't print character. Will have room after next newline.
            # print(f'print {c!r} ({ord(c)}) at {self.text_x, self.text_y}')
            cc = ord(c) * self.font_width
            bitmap = font[cc: cc + font_width]
            if pos == hl_start:
                highlight = True
            if pos == inv_start:
                invert = True
            fg_ = self.hl_fg if highlight else fg
            bg_ = self.hl_bg if highlight else bg
            self.draw_col_wise_mono_bitmap(
                self.text_x, self.text_y, bitmap, 
                width=font_width, height=font_height, 
                fg=bg_ if invert else fg_, 
                bg=fg_ if invert else bg_)
            self.text_x += font_width
            if pos == hl_stop:
                highlight = False
            if pos == inv_stop:
                invert = False
            # # wrap text
            # if wrap and self.text_x > x1:
            #     if wrap:
            #         self.text_x = 0
            #         self.text_y += font_height
        pad()

        # print(f' {self.fb_y0=}, {self.fb_y1=}')
 
        if update:
            self.update()

    def test_text(self,r=255, g=255, b=255):
        self.clear_frame_buffer()
        self.write_frame_buffer()
        t0 = time.ticks_ms()
        for x in range(96):
            c = 8*(x+32)
            self.draw_8x8_mono_bitmap2((x % 12) * 8, x//12 * 8, font[c: c+8], r, g, b)
        t1 = time.ticks_ms()
        self.write_frame_buffer()
        t2 = time.ticks_ms()
        print(f'draw={t1-t0} ms, refresh={t2-t1} ms')
