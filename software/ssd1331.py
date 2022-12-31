import pyftdi.spi
import pyftdi.gpio
import random

class SSD1331:
    """ Interface to control the SPI and control lines of a SSD1331 display using the ESP-Prog FTDI board

    This class offers standardized read/write interface.

    JTAG connector (configured as a SPI interface)
        pin 1: VDD (set jumper to select 3.3V!)
        pin 2: CS (TMS)
        pin 4: SCK (TCK)
        pin 6: MISO (TDO)
        pin 8: MOSI (TDI)
        pin 3,5,7,9 - GND

    UART connector (configured ad GPIO)
        pin 1: (EN): cannot use, see note
        pin 2: VDD (set jumper to select 3.3V!)
        pin 3: GPIO1- RES (TXD)
        pin 4: GND
        pin 5: GPIO0 - C/D  (RXD)
        pin 6: (IO0): cannot use see note

        NOTE: GPIO 2 & 4 must stay at 1 to enable EN, which enables JTAG connector outputs

    """
    DC_GPIO_MASK = 0b00001  # D/C# Data/command on GPIO0
    RES_GPIO_MASK = 0b00010  # RES# on GPIO1
    RTS_DTR_GPIO_MASK = 0b10100 # RTS and DTR bits, used to set EN and IO0

    # From : https://github.com/adafruit/Adafruit_CircuitPython_SSD1331/blob/main/adafruit_ssd1331.py

    _INIT_SEQUENCE = (
        b"\xAE\x00"  # _DISPLAYOFF
        b"\xA0\x01\x72"  # _SETREMAP (RGB)
        b"\xA1\x01\x00"  # _STARTLINE
        b"\xA2\x01\x00"  # _DISPLAYOFFSET
        b"\xA4\x00"  # _NORMALDISPLAY
        b"\xA8\x01\x3F"  # _SETMULTIPLEX (1/64 duty)
        b"\xAD\x01\x8E"  # _SETMASTER
        b"\xB0\x01\x0B"  # _POWERMODE
        b"\xB1\x01\x31"  # _PRECHARGE
        b"\xB3\x01\xF0"  # _CLOCKDIV 7:4 = Osc Freq, 3:0 = CLK Div Ratio
        b"\x8A\x01\x64"  # _PRECHARGEA
        b"\x8B\x01\x78"  # _PRECHARGEB
        b"\x8C\x01\x64"  # _PRECHARGEC
        b"\xBB\x01\x3A"  # _PRECHARGELEVEL
        b"\xBE\x01\x3E"  # _VCOMH
        b"\x87\x01\x06"  # _MASTERCURRENT
        b"\x81\x01\x91"  # _CONTRASTA
        b"\x82\x01\x50"  # _CONTRASTB
        b"\x83\x01\x7D"  # _CONTRASTC
        b"\xAF\x00"  # _DISPLAYON
    )


    def __init__(self, url1='ftdi://ftdi:2232h/1', url2='ftdi://ftdi:2232h/2', freq=10e6):

        self.spi_ctrl = pyftdi.spi.SpiController()
        self.spi_ctrl.configure(url1)

        self.spi = self.spi_ctrl.get_port(cs=0, freq=freq, mode=0)

        self.gpio = pyftdi.gpio.GpioAsyncController()
        self.gpio.configure(url2)
        self.gpio.set_direction(0xFF, 0xFF)  # all 8 bits of port BD are outputs

        # reset the display by pulsing the reset line low
        # self.gpio.write(self.RTS_DTR_GPIO_MASK) # DC=0, RES=0, RTS/DTR=1
        # time.sleep(0.3)
        # self.gpio.write(self.RTS_DTR_GPIO_MASK | self.RES_GPIO_MASK) # DC=0, RES=1, RTS/DTR=1


        # Initialize the display
        # self.write_command(self._INIT_SEQUENCE)
        # self.write_command([0xAF,0])  # display ON
        # self.write_command(b"\xA0\x01\x72")

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
        # debug
        rand = random.randint
        while True:
            self.write_command([0x21, rand(0,95), rand(0,63), rand(0,95), rand(0,63), rand(0,63), rand(0,63), rand(0,63)])
            self.write_command([0x22,1,1,16,16, 35,0,0, 0,0,40])
            # time.sleep(0.2)
            self.write_command([0x22,1,1,16,16, 0,35,0, 0,40,0])
            # time.sleep(0.2)
    def write_command(self, data):
        """ Writes data bytes

        Parameters: data (bytes): bytes to write.

        """
        self.gpio.write(self.RTS_DTR_GPIO_MASK | self.RES_GPIO_MASK) # DC=0, RES=1, RTS/DTR=1

        self.spi.exchange(data)



if __name__ == "__main__":
    p = SSD1331()


