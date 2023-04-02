import random
import time
from font import font

class SSD1331:
    """ Object to operate SSD1331-based OLED displays via its SPI interface

    Parameters:

        spi (SPI_with_CS): SPI_with_CS instance (SPI object with chip select handling)

        cs_pin (machine.Pin): pin that controls the display's chip select line. The pin mode must be set by the user.

        cd_pin (machine.Pin): pin that controls the display's command/data line. The pin mode must be set by the user.

        res_pin (machine.Pin): pin that controls the display's reset line. The pin mode must be set by the user.

    """

    def __init__(self, spi, cs_pin, cd_pin, res_pin):

        self.spi = spi
        self.cs = cs_pin
        self.cd = cd_pin
        self.res = res_pin
        self.fb = memoryview(bytearray(96*64*2)) # command+frame buffer, 2 bytes per pixel, + 6 bytes for the set window function
        self.buf = bytearray((0x15, 0, 95, 0x75, 0, 63))
        self.fb_y0 = 0  # current lowest modified frame buffer line
        self.fb_y1 = 63  # current highest modified frame buffer line
        # self.fg = bytearray(2)
        # self.bg = bytearray(2)
    def init(self):
        self.write_command((
            0xAE,        # Display off
            # Seg remap = 0b01110010 A[7:6]=01:64k color, A[5]=1 COM splip odd-even, A[4]=1 Scan com, A[3]=0, A[2]=0, A[1]=1, A[0]=0
            0xA0, 0b01100000,
            0xA1, 0x00,  # Set Display start line
            0xA2, 0x00,  # Set display offset
            0xA4,        # Normal display
            0xA8, 0x3F,  # Set multiplex
            0xAD, 0x8E,  # Master configure
            0xB0, 0x0B,  # Power save mode
            0xB1, 0x74,  # Phase12 period
            0xB3, 0xD0,  # Clock divider
            0x8A, 0x80,  # Set precharge speed A
            0x8B, 0x80,  # Set precharge speed B
            0x8C, 0x80,  # Set precharge speed C
            0xBB, 0x3E,  # Set pre-charge voltage
            0xBE, 0x3E,  # Set voltage
            0x87, 15))  # Master current control 1 = dim= 35mA, 15=bright=113mA
        self.write_command((0xAF,))  # display ON

        self.write_command((0x26, 1))  # Enable rectangle fill

    def reset(self):

        self.res(0)
        time.sleep(0.01)
        self.res(1)
        time.sleep(0.01)
        # All the display needs to be refreshed
        self.fb_y0 = 0
        self.fb_y1 = 63

    def write_command(self, data):
        """ Writes data bytes

        Parameters: 

            data (list of int or bytes): list of integers representing the
                command bytes to send to the display. Can also be a byte
                string or bytearray.

        """
        self.cd(0)
        self.spi.exchange(self.cs, bytearray(data))

    def _write_command(self, data):
        """ Writes data bytes

        Parameters: 

            data (bytes, bytearray or memoryview): bytes to send to the display.
        """
        self.cd(0)
        self.spi.exchange(self.cs, data)

    def write_data(self, data):
        self.cd(1)
        self.spi.exchange(self.cs, bytearray(data))

    def _write_data(self, data):
        """ Assumes data is already a bytearray or buffer"""
        self.cd(1)
        self.spi.exchange(self.cs, data)

    def write_frame_buffer(self, y0=None, y1=None, cmd=0xAF):
        # sets the window
        self.buf[4] = y0 = y0 if y0 is not None else self.fb_y0
        self.buf[5] = y1 = y1 if y1 is not None else self.fb_y1
        if y1 < 0:
            return
        with self.spi:
            self.write_command((cmd,)) 
            self._write_command(self.buf) # send the window command
            self._write_data(self.fb[y0*96*2: (y1+1)*96*2]) # fb is a memoryview, indexing does not allocate new memory
        self.fb_y0=63
        self.fb_y1=-1 # -1 is faster to check than y0 > y1

    def clear_frame_buffer(self):
        zeros = bytearray(96*2) # preallocate a bunch of zeros for efficiency
        for j in range(64):
            a= 96*2*j
            self.fb[a:a+96*2] = zeros
        self.fb_y0 = 0
        self.fb_y1 = 63

    def set_window(self, x1, y1, x2, y2):
        self.write_command([0x15, x1, x2, 0x75, y1, y2])

    def draw_color_bitmap(self, x, y, width, height, data):
        self.set_window(x, y, x + width - 1, y + height - 1)
        for d in data:
            r = (d >> 11) & 0b11111
            g = (d >> 5) & 0b111111
            b = d & 0b11111
            self.write_data([r << 3 | (g & 0b111), (g & 0b111) | b << 3])

    def draw_8x8_mono_bitmap(self, x: int, y: int, data: list, r: int = 255, g: int = 255, b: int = 255, bg_r: int = 0, bg_g: int = 0, bg_b: int = 0) -> None:
        self.set_window(x, y, x + 7, y + 7)
        index = 0
        rr = r >> 3
        gg = g >> 2
        bb = b >> 3
        bg_rr = bg_r >> 3
        bg_gg = bg_g >> 2
        bg_bb = bg_b >> 3
        cmds_fg = [rr << 3 | (gg & 0b111), (gg & 0b111) | bb << 3]
        cmds_bg = [bg_rr << 3 | (bg_gg & 0b111), (bg_gg & 0b111) | bg_bb << 3]
        for j in range(8):
            d = data[index]
            for i in range(8):
                bit = d & 0x80
                if bit != 0x00:
                    self.write_data(cmds_fg)
                else:
                    self.write_data(cmds_bg)
                d <<= 1
            index += 1

    def draw_8x8_mono_bitmap2(self, x: int, y: int, data: list, r: int = 255, g: int = 255, b: int = 255, bg_r: int = 0, bg_g: int = 0, bg_b: int = 0) -> None:
        """ Writes a 8x8 monochrome bitmap in the frame buffer 


        """
        # t0 = time.ticks_ms()
        fb = self.fb
        fg0 = r & 0b11111000 | (g >> 5) & 0b111
        fg1 = (g << 3) & 0b11100000 | (b >> 3)  & 0b11111
        bg0 = bg_r & 0b11111000 | (bg_g >> 5) & 0b111
        bg1 = (bg_g << 3) & 0b11100000 | (bg_b >> 3) & 0b11111
        addr = (x + y*96)*2
        # ta = time.ticks_cpu()
        for j in range(8):
            d = data[j]
            a = addr
            for i in range(8):
                if (d & (0x80 >> i)):
                    fb[a] = fg0; a +=1
                    fb[a] = fg1; a +=1
                else:
                    fb[a] = bg0; a +=1
                    fb[a] = bg1; a +=1
            addr += 96*2
        # expand the refresh zone to include modified lines
        self.fb_y0 = min(self.fb_y0, y)  
        self.fb_y1 = max(self.fb_y1, y+7)  

        # tb = time.ticks_cpu()
        # t1 = time.ticks_ms()
        # self.write_frame_buffer(y, y+7)
        # t2= time.ticks_ms()
        # print(f'draw={t1-t0} ms, refresh={t2-t1} ms, buf access={tb-ta} cycles')
    # Graphic acceleration commands

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

    def draw_line(self, x1, y1, x2, y2, r=255, g=255, b=255):
        self.write_command((0x21, x1, y1, x2, y2, r, g, b))
        time.sleep(0.001)

    def draw_rect(self, x1, y1, x2, y2, line_r=255, line_g=255, line_b=255, fill_r=0, fill_g=0, fill_b=0):
        self.write_command((0x22, x1, y1, x2, y2, line_r,
                           line_g, line_b, fill_r, fill_g, fill_b))
        time.sleep(0.001)

    def copy(self, src_x1, src_y1, src_x2, src_y2, dest_x, dest_y):
        self.write_command(
            (0x23, src_x1, src_y1, src_x2, src_y2, dest_x, dest_y))
        time.sleep(0.001)

    def dim_rect(self, x1=0, y1=0, x2=95, y2=63):
        """ Reduce the intensity of the pixels in the specified rectangle. Subsequent calls have no effect.
        """
        self.write_command((0x24, x1, y1, x2, y2))
        time.sleep(0.001)

    def set_master_intensity(self, attn=15):
        """ Sets the master display intensity, from 0 to 15.
        """
        self.write_command((0x87, attn & 0x0F))

    def set_dim(self, dim=255):
        """ Sets the display dim level.
        """
        self.write_command((0xAB, 0, dim,dim,dim,31))
        self.write_frame_buffer(0, 63, cmd=0xAC)
        # self.write_command((0xAC, ))

    def clear(self, x1=0, y1=0, x2=95, y2=63):
        self.write_command((0x25, x1, y1, x2, y2))
        time.sleep(0.001)
        # All the display needs to be refreshed
        self.fb_y0 = 0
        self.fb_y1 = 63

    def set_fill(self, ena, rev_copy=False):
        a = 0x00
        if ena:
            a |= 0x01
        if rev_copy:
            a |= 0x10
        self.write_command((0x26, a))

    # Valid time intervals: 6, 10, 100 or 200 frames

    def set_scroll(self, nb_offset_cols, start_row, nb_rows, nb_offset_rows, time_interval=100):
        TIME_INTERVALS = {6: 0x00, 10: 0x01, 100: 0x2, 200: 0x3}
        if time_interval in TIME_INTERVALS:
            self.write_command([0x27, nb_offset_cols, start_row,
                               nb_rows, nb_offset_rows, TIME_INTERVALS[time_interval]])

    def stop_scroll(self):
        self.write_command((0x2E,))

    def start_scroll(self):
        self.write_command((0x2F,))
