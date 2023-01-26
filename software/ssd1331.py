# import pyftdi.spi
# import pyftdi.gpio
import random, time

class SSD1331:
    """ Interface to control the SPI and control lines of a SSD1331 display"""

    def __init__(self, spi, cs, cd, res):
   
        self.spi = spi
        self.cs = cs
        self.cd = cd
        self.res = res

        self.res(0)
        time.sleep(0.01)
        self.res(1)
        time.sleep(0.01)

        self.write_command([
            0xAE,        # Display off
            0xA0, 0b01100000,  # Seg remap = 0b01110010 A[7:6]=01:64k color, A[5]=1 COM splip odd-even, A[4]=1 Scan com, A[3]=0, A[2]=0, A[1]=1, A[0]=0
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
            0x87, 15])  # Master current control 1 = dim= 35mA, 15=bright=113mA
        self.write_command([0xAF])  # display ON

        self.write_command([0x26, 1])  # Enable rectangle fill


    def write_command(self, data):
        """ Writes data bytes

        Parameters: data (bytes): bytes to write.

        """
        self.cd(0)
        self.res(1)
        self.cs(0)
        self.spi.write(bytearray(data))
        self.cs(1)


    def write_data(self, data):
        self.cd(1)
        self.res(1)
        self.cs(0)
        self.spi.write(bytearray(data))
        self.cs(1)


    def set_window(self, x1, y1, x2, y2):
        self.write_command([0x15, x1, x2, 0x75, y1, y2])


    def draw_color_bitmap(self, x, y, width, height, data):
        self.set_window(x, y, x + width - 1, y + height - 1)
        for d in data:
            r = (d >> 11) & 0b11111
            g = (d >> 5) & 0b111111
            b = d & 0b11111
            self.write_data([r << 3 | (g & 0b111), (g & 0b111) | b << 3]) 


    def draw_8x8_mono_bitmap(self, x, y, data, r=255, g=255, b=255, bg_r=0, bg_g=0, bg_b=0):
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


    # Graphic acceleration commands

    def draw_line(self, x1, y1, x2, y2, r=255, g=255, b=255):
        self.write_command([0x21, x1, y1, x2, y2, r, g, b])
        time.sleep(0.001)


    def draw_rect(self, x1, y1, x2, y2, line_r=255, line_g=255, line_b=255, fill_r=0, fill_g=0, fill_b=0):
        self.write_command([0x22, x1, y1, x2, y2, line_r, line_g, line_b, fill_r, fill_g, fill_b])
        time.sleep(0.001)

    
    def copy(self, src_x1, src_y1, src_x2, src_y2, dest_x, dest_y):
        self.write_command([0x23, src_x1, src_y1, src_x2, src_y2, dest_x, dest_y])
        time.sleep(0.001)

    
    def dim(self, x1=0, y1=0, x2=95, y2=63):
        self.write_command([0x24, x1, y1, x2, y2])
        time.sleep(0.001)


    def clear(self, x1=0, y1=0, x2=95, y2=63):
        self.write_command([0x25, x1, y1, x2, y2])
        time.sleep(0.001)


    def set_fill(self, ena, rev_copy=False):
        a = 0x00
        if ena:
            a |= 0x01
        if rev_copy:
            a |= 0x10
        self.write_command([0x26, a])


    # Valid time intervals: 6, 10, 100 or 200 frames
    def set_scroll(self, nb_offset_cols, start_row, nb_rows, nb_offset_rows, time_interval=100):
        TIME_INTERVALS = {6:0x00, 10:0x01, 100:0x2, 200:0x3}
        if time_interval in TIME_INTERVALS:
            self.write_command([0x27, nb_offset_cols, start_row, nb_rows, nb_offset_rows, TIME_INTERVALS[time_interval]])


    def stop_scroll(self):
        self.write_command([0x2E])


    def start_scroll(self):
        self.write_command([0x2F])


if __name__ == "__main__":
    p = SSD1331()

