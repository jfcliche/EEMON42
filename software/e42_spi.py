from machine import Pin, SPI
import time

class SPI_with_CS(SPI):
    """ Hardware SPI interface with dual-function chip-select (CS) pin handling.

    Dual function pins can be used both as SPI chip-select output lines or as input lines (e.g. to read switches).

    By default, CS pins are in IN mode with a weak pullup so the pins can read the line status and trigger associated interrupts.
    When a SPI transaction (`exchange()`) is performed:

        1) all the dual function CS pins are set to OUT mode to prevent switches from enabling the CS lines during the transaction
        2) the dual-function pin interrups are disabled to prevent interrupts being called when the CS lines are toggled during the SPI transaction 
        3) The CS pin for the selected device is activated. 

    The pins and interrupts are restored after the SPI transaction is completed.

    Parameters:

        cs_out_pins (dict): dict mapping the SPI device name with the Pin handling its chip select (CS) line for pins used in output mode only. 

        cs_inout_pins (dict): same as `cs_out_pins`, except that the specified pins are dual function: they are in IN mode but are all set to OUT mode  during SPI transactions.

        baud_rate (int or float): SPI baud rate, in bps. Default is 2.5 MHz.

    """
    def __init__(self, cs_out_pins={}, cs_inout_pins={}, baud_rate=2.5e6):
        super().__init__(1, int(baud_rate))
        self.cs_pins = {}  # Map of all CS pins (both output-only and in/out)
        self.cs_inout_pins = {}  # Map of input-output (dual function) CS pins
 
        # Initialize output-only CS pins
        for cs_name, pin in cs_out_pins.items(): 
            pin.init(Pin.OUT)
            self.cs_pins[cs_name] = pin
 
        # Initialize input-output CS pins
        for cs_name, pin in cs_inout_pins.items(): 
            pin.init(Pin.IN, Pin.PULL_UP)
            self.cs_pins[cs_name] = pin
            self.cs_inout_pins[cs_name] = pin

        self.spi_active = False
        self.context_active = False

    def set_pin_irq(self, cs_pin, irq_handler, **kwargs):
        """ Sets the interrupt handler of a CS pin such that it will not be
        called if the CS pins toggle due to a SPI operation.

        Parameters:

            cs_pin (machine.Pin, str or list/tuple): One or multiple pins,
                provided as a Pin object or a SPI device name, for which the
                interrupt routine should be applied.

            irq_handler (fn): Interrupt routine that will be called on changes
                on the specified pins, only when the SPI port is inactive.

            kwargs: Additional arguments passed to the Pin.irq() call.
        """
        def wrapped_irq_handler(pin):
            if not self.spi_active:
                irq_handler(pin)
            # else:
            #     print('blobkerd IRQ')
        if not isinstance(cs_pin, (list, tuple)):
            cs_pin = (cs_pin,)
        for pin in cs_pin:
            if isinstance(pin, str):
                pin = self.cs_pins[pin] 
            pin.irq(wrapped_irq_handler, **kwargs)

    def enable_spi(self):
        self.spi_active = True  # block pin interrupts
        # put dual-function pins in OUT mode to prevent CS lines from being activated by their dual-function devices (e.g. switches)
        # print('settint to OUT')
        for pin in self.cs_inout_pins.values():
            pin.init(mode=Pin.OUT, value=1)

    def disable_spi(self):
        # print('settint to IN')
        for pin in self.cs_inout_pins.values():
            pin.init(mode=Pin.IN)

        # print('enabling irq')
        time.sleep(0) # let the interrupt thread process the pending pin interrupts
        self.spi_active = False # enable pin interrupts
        # time.sleep(.00005)
        # print()
    def __enter__(self):
        self.context_active = True
        self.enable_spi()
    def __exit__(self, e1,e2,e3):
        self.disable_spi()
        self.context_active = False

    def exchange(self, cs_name, data, read_buf=None):
        """ Writes `data` to the SPI port and then read `read_length` bytes of the device specified by `cs_name` while
        ensuring the .

        Parameters:

            data (bytes): Data to write.

        Returns:
            `read_length` bytes.

        Note: Using pre-allocated bytearrays and memoryview made the call slower, not faster... But we were still copying `data`
        """ 
        # if not isinstance(data, bytes):
        #     data = bytes(data)
        # din = bytearray(len(data) + read_length)
        # din = bytearray(read_length)
        cs_pin = self.cs_pins[cs_name]
        if not self.context_active:
            self.enable_spi()

        cs_pin.value(0) # enable target CS line
        # self.write_readinto(data+b'\x00'*read_length, din) # perform SPI transaction
        self.write(data) # perform SPI transaction
        self.readinto(read_buf) if read_buf else [] # perform SPI transaction
        cs_pin.value(1) # disable target CS line
        if not self.context_active:
            self.disable_spi()
        # return din