
# PyPi packages
import time

# Local packages
from display import Display


class SSD1331(Display):
    """ Object to operate SSD1331-based OLED displays via its SPI interface

    Parameters:

        spi (SPI_with_CS): SPI_with_CS instance (SPI object with chip select handling)

        cs_pin (machine.Pin): pin that controls the display's chip select line. The pin mode must be set by the user.

        cd_pin (machine.Pin): pin that controls the display's command/data line. The pin mode must be set by the user.

        res_pin (machine.Pin): pin that controls the display's reset line. The pin mode must be set by the user.

    """

    WIDTH = 96
    HEIGHT = 64
    BYTES_PER_PIXEL = 2

    def __init__(self, spi, cs_pin, cd_pin, res_pin):

        super().__init__()
        self.spi = spi
        self.cs_pin = cs_pin
        self.cd_pin = cd_pin
        self.rst_pin = res_pin
        self.cmd = bytearray((0x15, 0, 95, 0x75, 0, 63)) # command bytes. The last two bytes are updated as needed
        

    def init(self):
        """ Initializes the display controller to the desired display mode
        """
        self.reset()
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

        super().init()

    def reset(self):
        """ Pulses the hardware reset line of the display
        """

        self.rst_pin(0)
        time.sleep(0.01)
        self.rst_pin(1)
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
        self.cd_pin(0)
        self.spi.exchange(self.cs_pin, bytearray(data))

    def _write_command(self, data):
        """ Writes data bytes

        Parameters: 

            data (bytes, bytearray or memoryview): bytes to send to the display.
        """
        self.cd_pin(0)
        self.spi.exchange(self.cs_pin, data)

    def write_data(self, data):
        self.cd_pin(1)
        self.spi.exchange(self.cs_pin, bytearray(data))

    def _write_data(self, data):
        """ Assumes data is already a bytearray or buffer"""
        self.cd_pin(1)
        self.spi.exchange(self.cs_pin, data)

    def write_frame_buffer(self, y0=None, y1=None):
        """ Sends the specified lines of the frame buffer to the hardware display. 

        If no lines are specified, only the block of lines that were modified since the last call are updated. 

        Parameters:

            y0, y1 (int): first and last line of the block to be updated. If None, the higest/lowest line modified since the last call is used.  

        """
        # sets the window
        self.cmd[4] = y0 = y0 if y0 is not None else self.fb_y0
        self.cmd[5] = y1 = y1 if y1 is not None else self.fb_y1
        if y1 < 0:
            return
        with self.spi:
            self._write_command(self.cmd) # send the window command
            self._write_data(self.fb[y0 * self.BYTES_PER_LINE: (y1+1) * self.BYTES_PER_LINE]) # fb is a memoryview, indexing does not allocate new memory
        self.fb_y0 = self.HEIGHT - 1
        self.fb_y1 = -1 # -1 is faster to check than y0 > y1

        # tb = time.ticks_cpu()
        # t1 = time.ticks_ms()
        # self.write_frame_buffer(y, y+7)
        # t2= time.ticks_ms()
        # print(f'draw={t1-t0} ms, refresh={t2-t1} ms, buf access={tb-ta} cycles')

    def display_on(self):
        self.write_command((0xAF,))

    def display_off(self):
        self.write_command((0xAE,))

    def _set_brightness(self, brightness):
        if not brightness:
            self.write_command((0xAE,))  # display OFF
        else:
            self.write_command((0xAF, 0x87, min(15, brightness-1))) # dislay ON, set brightness


    def set_window(self, x1, y1, x2, y2):
        self.write_command((0x15, x1, x2, 0x75, y1, y2))

    def draw_color_bitmap(self, x, y, width, height, data):
        self.set_window(x, y, x + width - 1, y + height - 1)
        for d in data:
            r = (d >> 11) & 0b11111
            g = (d >> 5) & 0b111111
            b = d & 0b11111
            self.write_data([r << 3 | (g & 0b111), (g & 0b111) | b << 3])

    # def draw_8x8_mono_bitmap(self, x: int, y: int, data: list, r: int = 255, g: int = 255, b: int = 255, bg_r: int = 0, bg_g: int = 0, bg_b: int = 0) -> None:
    #     self.set_window(x, y, x + 7, y + 7)
    #     index = 0
    #     rr = r >> 3
    #     gg = g >> 2
    #     bb = b >> 3
    #     bg_rr = bg_r >> 3
    #     bg_gg = bg_g >> 2
    #     bg_bb = bg_b >> 3
    #     cmds_fg = [rr << 3 | (gg & 0b111), (gg & 0b111) | bb << 3]
    #     cmds_bg = [bg_rr << 3 | (bg_gg & 0b111), (bg_gg & 0b111) | bg_bb << 3]
    #     for j in range(8):
    #         d = data[index]
    #         for i in range(8):
    #             bit = d & 0x80
    #             if bit != 0x00:
    #                 self.write_data(cmds_fg)
    #             else:
    #                 self.write_data(cmds_bg)
    #             d <<= 1
    #         index += 1



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

        The dim command seems to erase the display memory, so the frame buffer has to be sent back.
        This causes flicker.
        We cannot completely extinguish the pixels with dim=0.
        """
        self.write_command((0xAB, 0, dim,dim,dim,31))
        self.write_frame_buffer(0, 63, cmd=0xAC)
        # self.write_command((0xAC, ))

    def clear_display(self, x1=0, y1=0, x2=WIDTH-1, y2=HEIGHT-1):
        """ Clears the display's pixels in the specified rectangle coordinates.

        This operates on the display directly, using the hardware clear command. 
        The frame buffer is unaffected.
        If no arguments are provided, the whole display is cleared. 

        Parameters:

            x1, y1, x2, y2 (int): coordinates of the rectangles to be cleared 
        """
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
