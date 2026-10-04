
# PyPi packages
import time

# Local packages
from display import Display


class ST7735(Display):
    """ Object to operate SST7735-based LCD displays via its SPI interface

    Parameters:

        spi (SPI_with_CS): SPI_with_CS instance (SPI object with chip select handling)

        cs_pin (machine.Pin): pin that controls the display's chip select line. The pin mode must be set by the user.

        cd_pin (machine.Pin): pin that controls the display's command/data line. The pin mode must be set by the user.

        res_pin (machine.Pin): pin that controls the display's reset line. The pin mode must be set by the user.

    """

    WIDTH = 128
    HEIGHT = 160
    BYTES_PER_PIXEL = 2

 
    # Registers
    NOP = 0x00
    SWRESET = 0x01
    RDDID = 0x04
    RDDST = 0x09

    SLPIN = 0x10
    SLPOUT = 0x11
    PTLON = 0x12
    NORON = 0x13

    INVOFF = 0x20
    INVON = 0x21
    DISPOFF = 0x28
    DISPON = 0x29

    CASET = 0x2A
    RASET = 0x2B
    RAMWR = 0x2C
    RAMRD = 0x2E

    PTLAR = 0x30
    MADCTL = 0x36
    COLMOD = 0x3A

    FRMCTR1 = 0xB1
    FRMCTR2 = 0xB2
    FRMCTR3 = 0xB3
    INVCTR = 0xB4
    DISSET5 = 0xB6


    PWCTR1 = 0xC0
    PWCTR2 = 0xC1
    PWCTR3 = 0xC2
    PWCTR4 = 0xC3
    PWCTR5 = 0xC4
    VMCTR1 = 0xC5

    RDID1 = 0xDA
    RDID2 = 0xDB
    RDID3 = 0xDC
    RDID4 = 0xDD

    GMCTRP1 = 0xE0
    GMCTRN1 = 0xE1

    PWCTR6 = 0xFC

    def __init__(self, spi, cs_pin, cd_pin, res_pin, fb=None):
        import gc
        gc.collect()
        super().__init__(fb=fb)
        self.spi = spi
        self.cs_pin = cs_pin
        self.cd_pin = cd_pin
        self.rst_pin = res_pin
        self.cmd = bytearray((0x15, 0, 95, 0x75, 0, 63)) # command bytes. The last two bytes are updated as needed
        

    def init(self):
        """ Initializes the display controller to the desired display mode
        """
        self.reset()
        time.sleep(.150)

        self.send_command(self.SWRESET)    # Software reset
        time.sleep(0.150)               # delay 150 ms. Datasheet days to wait 120 ms.

        self.send_command(self.SLPOUT)     # Out of sleep mode
        time.sleep(0.150)               # delay 500 ms. Datasheet says to wait 120 ms.

        print('Out of sleep mode')
        self.send_command(self.COLMOD, b'\x05')     # set color mode
        # byte 1: 0x05                 # 16-bit color

        # Frame rate ctrl - normal mode (full color)
        #   Byte 1: RTNA 1-line period
        #   Byte 2: FPA: front porch, 
        #   Byte 3: BPA: back porch
        # Rate = fosc/(1x2+40) * (LINE+2C+2D)
        self.send_command(self.FRMCTR1, b'\x00\x06\x03')  # '\x01\x2c\x2d' for red tab'    

        # *** debug
        # # Frame rate ctrl - idle mode (8-colors)
        # # Rate = fosc/(1x2+40) * (LINE+2C+2D)
        self.send_command(self.FRMCTR2, b'\x00\x06\x03' )    # Frame rate ctrl - idle mode
        # was (0x01, 0x2c, 0x2d)

        # *** debug
        # # Frame rate ctrl - partial mode + full color
        # # ( Dot inversion mode, _, _, Line inversion mode, _ , _)
        self.send_command(self.FRMCTR3, b'\x00\x06\x03\x00\x06\x03' )    
        #was (0x01, 0x2c, 0x2d, 0x01, 0x2c, 0x2d)

        # Memory access control (directions)
        #   Byte 1: row addr/col addr, bottom to top refresh; RGB/BGR encoding
        #       Bit 7: MY: Row address order
        #       Bit 6: MX: Column address order
        #       Bit 5: MV: Row/column exchange
        #       Bit 4: ML: Vertical refresh order; 0=top to bot, 1= Bot to Top
        #       Bit 3: RGB: RGB-BGR order; 0=RGB, 1=BGR
        #       Bit 2: MH: Horizontal refesh order; 0=Lest to Right, 1= Right to Left 
        self.send_command(self.MADCTL, b'\x00')     
            #0xC8,))            # row addr/col addr, bottom to top refresh; Set D3 RGB Bit to 1 for format BGR
            # 0xC0,))             # row addr/col addr, bottom to top refresh; Set D3 RGB Bit to 0 for format RGB

        # Display settings
        #   Byte 1: NO, SDT (source delay), EQ (EQ period). 0x15 = 1 clk nonoverlap, 2 cycle gate rise, 3 cyc osc, equualize.
        #   Byte 2: PTG, PT (Display area source/VCOM/Gate output control) 0x02: Fix on VTL
        self.send_command(self.DISSET5, b'\x15\x02')    # ( 1 clk cycle nonoverlap, fix on VTL)

        # Display inversion ctrl
        #   Byte 1: NL
        self.send_command(self.INVCTR, b'\x07') # No inversion  . 'b\07' for red tab   

        # Power control 
        #   Byte 1: VRH
        #   Byte 2: IB-SEL
        self.send_command(self.PWCTR1, b'\x02\x70')  # Power control (4.7V, 1uA) (b'\xA2\x02\x84' for ST7735S)

        # Power control
        #   Byte 1: BT (sets VGH/VGL voltage)
        self.send_command(self.PWCTR2, b'\x05')     # Power control (VGH=14.7V, VGL=-7.35V)
            # 0x0A,                 # Opamp current small
            # 0x00))                 # Boost frequency

        # Power control in normal mode (full colors)
        #   Byte 1: APA (opamp adjust)
        #   Byte 2: DCA (booster voltage)
        self.send_command(self.PWCTR3, b'\x01\x02') # Opamp current small, Boost frequency

        # Power control in idle mode (8 colors)
        # self.send_command(self.PWCTR4,(     # Power control
        #     0x8A,                 # BCLK/2, Opamp current small & Medium low
        #     0x2A))

        # Power control in partial mode (Full colors)
        # self.send_command(self.PWCTR5, (     # Power control
        #     0x8A,
        #     0xEE))


        # VCOM control
        #   Byte 1: VMH (VCOMH voltage)
        #   Byte 2: VML (VCOML voltage)
        self.send_command(self.VMCTR1, b'\x3c\x38')  # VCOMH = 4V, VCOML= -1.1V 

        # Power control in partial mode + Idle
        #   Byte 1: Sapa, Sapb
        #   Byte 2: Sapc, DCD
        self.send_command(self.PWCTR6, b'\x11\x15')  # VCOMH = 4V, VCOML= -1.1V 





        # Set Gamma
        # Bytes 1-16: Gamma adjustment + polarity
        self.send_command(self.GMCTRP1, b'\x02\x1c\x07\x12\x37\x32\x29\x2d\x29\x25\x2B\x39\x00\x01\x03\x10')         

        # Set Gamma    
        # Bytes 1-16: Gamma adjustment - polarity
        self.send_command(self.GMCTRN1, b'\x03\x1d\x07\x06\x2E\x2C\x29\x2D\x2E\x2E\x37\x3F\x00\x00\x02\x10') 

        # Column addr set
        # Bytes 1-2: 16-bit X addr start (big endian) 
        # Bytes 3-4: 16-bit X addr end (big endian) 
        x0 = 2
        x1 = x0 + self.WIDTH -1
        self.send_command(self.CASET, ((x0 << 16) + x1).to_bytes(4, 'big'))     

        # Row addr set
        # Bytes 1-2: 16-bit Y addr start (big endian) 
        # Bytes 3-4: 16-bit Y addr end (big endian) 
        y0 = 1
        y1 = y0 + self.HEIGHT -1
        self.send_command(self.RASET, ((y0 << 16) + y1).to_bytes(4, 'big'))     
   
            

        self.send_command(self.INVOFF)  # Don't invert display



 
        # self.send_command(self.SLPOUT)      

        self.send_command(self.NORON)      # Normal display on
        time.sleep(0.010)                # 10 ms

        self.send_command(self.DISPON)
        time.sleep(0.100)               # 100 ms. Datasheet says 120ms vefore DISPOFF

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
        self.fb_y1 = self.HEIGHT - 1

    def send_command(self, cmd, data=None):
        """ Sends 1-byte command followed by its arguments

        Parameters: 

            data (memoryview or list/tuple/bytes/bytearray): list of integers representing the
                command bytes to send to the display. Can also be a byte
                string or bytearray.

        """
        self.cd_pin(0)
        self.spi.exchange(self.cs_pin, bytes((cmd,)))
        if data:
            self.cd_pin(1)
            if isinstance(data, (memoryview, bytes, bytearray)):
                return self.spi.exchange(self.cs_pin, data)
            else:
                return self.spi.exchange(self.cs_pin, bytearray(data))

    # def _write_command(self, data):
    #     """ Writes data bytes

    #     Parameters: 

    #         data (bytes, bytearray or memoryview): bytes to send to the display.
    #     """
    #     self.cd_pin(0)
    #     self.spi.exchange(self.cs_pin, data)

    # def write_data(self, data):
    #     self.cd_pin(1)
    #     self.spi.exchange(self.cs_pin, bytearray(data))

    # def _write_data(self, data):
    #     """ Assumes data is already a bytearray or buffer"""
    #     self.cd_pin(1)
    #     self.spi.exchange(self.cs_pin, data)


    def display_on(self):
        self.send_command(self.DISPON)

    def display_off(self):
        self.send_command(self.DISPOFF)

    def _set_brightness(self, brightness):
        if not brightness:
            self.display_off()
        else:
            self.display_on()
            # self.send_command((0xAF, 0x87, min(15, brightness-1))) # dislay ON, set brightness

    def _update(self, y0, y1):
        """ Sends the specified lines of the frame buffer to the hardware display. 

        If no lines are specified, only the block of lines that were modified since the last call are updated. 

        Parameters:

            y0, y1 (int): first and last line of the block to be updated. If None, the higest/lowest line modified since the last call is used.  

        """
        # sets the window
        with self.spi:
            # Column & row addr set
            # self.send_command(self.CASET, (0, 0, (self.WIDTH -1) >> 8, (self.WIDTH -1) & 0xFF))
            self.send_command(self.RASET, (((y0+1) << 16) + y1 + 1).to_bytes(4, 'big'))
            # self.send_command(self.RAMWR)       # write to RAM
            # Send the frame buffer
            # print(f'Sending lines {y0}-{y1}')
            self.send_command(self.RAMWR, self.fb[y0 * self.BYTES_PER_LINE: (y1+1) * self.BYTES_PER_LINE]) # fb is a memoryview, indexing does not allocate new memory

 
    # def set_window(self, x1, y1, x2, y2):
    #     self.write_command((0x15, x1, x2, 0x75, y1, y2))

    # def draw_color_bitmap(self, x, y, width, height, data):
    #     self.set_window(x, y, x + width - 1, y + height - 1)
    #     for d in data:
    #         r = (d >> 11) & 0b11111
    #         g = (d >> 5) & 0b111111
    #         b = d & 0b11111
    #         self.write_data([r << 3 | (g & 0b111), (g & 0b111) | b << 3])

    # # def draw_8x8_mono_bitmap(self, x: int, y: int, data: list, r: int = 255, g: int = 255, b: int = 255, bg_r: int = 0, bg_g: int = 0, bg_b: int = 0) -> None:
    # #     self.set_window(x, y, x + 7, y + 7)
    # #     index = 0
    # #     rr = r >> 3
    # #     gg = g >> 2
    # #     bb = b >> 3
    # #     bg_rr = bg_r >> 3
    # #     bg_gg = bg_g >> 2
    # #     bg_bb = bg_b >> 3
    # #     cmds_fg = [rr << 3 | (gg & 0b111), (gg & 0b111) | bb << 3]
    # #     cmds_bg = [bg_rr << 3 | (bg_gg & 0b111), (bg_gg & 0b111) | bg_bb << 3]
    # #     for j in range(8):
    # #         d = data[index]
    # #         for i in range(8):
    # #             bit = d & 0x80
    # #             if bit != 0x00:
    # #                 self.write_data(cmds_fg)
    # #             else:
    # #                 self.write_data(cmds_bg)
    # #             d <<= 1
    # #         index += 1



    # def draw_line(self, x1, y1, x2, y2, r=255, g=255, b=255):
    #     self.write_command((0x21, x1, y1, x2, y2, r, g, b))
    #     time.sleep(0.001)

    # def draw_rect(self, x1, y1, x2, y2, line_r=255, line_g=255, line_b=255, fill_r=0, fill_g=0, fill_b=0):
    #     self.write_command((0x22, x1, y1, x2, y2, line_r,
    #                        line_g, line_b, fill_r, fill_g, fill_b))
    #     time.sleep(0.001)

    # def copy(self, src_x1, src_y1, src_x2, src_y2, dest_x, dest_y):
    #     self.write_command(
    #         (0x23, src_x1, src_y1, src_x2, src_y2, dest_x, dest_y))
    #     time.sleep(0.001)

    # def dim_rect(self, x1=0, y1=0, x2=95, y2=63):
    #     """ Reduce the intensity of the pixels in the specified rectangle. Subsequent calls have no effect.
    #     """
    #     self.write_command((0x24, x1, y1, x2, y2))
    #     time.sleep(0.001)

    # def set_master_intensity(self, attn=15):
    #     """ Sets the master display intensity, from 0 to 15.
    #     """
    #     self.write_command((0x87, attn & 0x0F))

    # def set_dim(self, dim=255):
    #     """ Sets the display dim level.

    #     The dim command seems to erase the display memory, so the frame buffer has to be sent back.
    #     This causes flicker.
    #     We cannot completely extinguish the pixels with dim=0.
    #     """
    #     self.write_command((0xAB, 0, dim,dim,dim,31))
    #     self.write_frame_buffer(0, 63, cmd=0xAC)
    #     # self.write_command((0xAC, ))

    # def clear_display(self, x1=0, y1=0, x2=WIDTH-1, y2=HEIGHT-1):
    #     """ Clears the display's pixels in the specified rectangle coordinates.

    #     This operates on the display directly, using the hardware clear command. 
    #     The frame buffer is unaffected.
    #     If no arguments are provided, the whole display is cleared. 

    #     Parameters:

    #         x1, y1, x2, y2 (int): coordinates of the rectangles to be cleared 
    #     """
    #     self.write_command((0x25, x1, y1, x2, y2))
    #     time.sleep(0.001)
    #     # All the display needs to be refreshed
    #     self.fb_y0 = 0
    #     self.fb_y1 = 63

    # def set_fill(self, ena, rev_copy=False):
    #     a = 0x00
    #     if ena:
    #         a |= 0x01
    #     if rev_copy:
    #         a |= 0x10
    #     self.write_command((0x26, a))

    # # Valid time intervals: 6, 10, 100 or 200 frames

    # def set_scroll(self, nb_offset_cols, start_row, nb_rows, nb_offset_rows, time_interval=100):
    #     TIME_INTERVALS = {6: 0x00, 10: 0x01, 100: 0x2, 200: 0x3}
    #     if time_interval in TIME_INTERVALS:
    #         self.write_command([0x27, nb_offset_cols, start_row,
    #                            nb_rows, nb_offset_rows, TIME_INTERVALS[time_interval]])

    # def stop_scroll(self):
    #     self.write_command((0x2E,))

    # def start_scroll(self):
    #     self.write_command((0x2F,))
