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

        baudrate (int or float): SPI baud rate, in bps. Default is 2.5 MHz.

        sck (Pin): pin associated to the SPI clock. Mode must be set by the user.

        miso (Pin): pin associated to the SPI MISO signal. Mode must be set by the user.

        mosi (Pin): pin associated to the SPI MOSI signal. Mode must be set by the user.

        cs_inout_pins (tuple or list): list of dual-function machine.PIN
            objects that should be in IN and PULL_UP mode except during SPI transactions
            where they *must* be in OUT mode. The pins are set to the IN mode with
            PULL_UP at initialization.

        cs_out_pins (tuple or list): List of Pin objects to be set in the OUT
            mode at initialization. This is for convenience; this parameter
            does not have to be specified  if the pin modes are handled by the
            user.


        kwargs: all other keywords arguments are passed to the machine.SPI class

    """
    def __init__(self, baudrate=2.5e6, sck=None, mosi=None, miso=None, cs_out_pins=tuple(), cs_inout_pins=tuple()):
        SPI(1).deinit() # need to deinitialize so we can initialize again
        super().__init__(1, int(baudrate))
        # self.init(baudrate=int(baudrate), sck=sck, mosi=mosi, miso=miso)
        self.cs_inout_pins = cs_inout_pins  # list of input-output (dual function) CS pins
 
        # Initialize output-only CS pins. This is done only once here. The mode of this pin is not changed during SPI transactions.
        for pin in cs_out_pins: 
            pin.init(Pin.OUT)
 
        # Initialize input-output CS pins. The mode of these pins are changed during SPI transactions.
        for pin in cs_inout_pins: 
            pin.init(Pin.IN, Pin.PULL_UP)

        self.spi_active = False
        self.context_active = False

    def get_irq(self, irq_handler):
        """ Return a Pin interrupt handler that will call `irq_handler` 
        only if the SPI port is not active.

        Interrupt handlers for pins that have a shared function with the SPI
        CS lines should be obtained through this method to prevent unwanted
        interrupts to be caused by SPI transactions. 

        Parameters:

            cs_pin (machine.Pin): One or multiple pins for which the
                interrupt routine should be applied.

            irq_handler (fn): Interrupt routine that will be called on changes
                on the specified pins, only when the SPI port is inactive.

            kwargs: Additional arguments passed to the Pin.irq() call.
        """
        def wrapped_irq_handler(pin):
            """ Calls the IRQ handler only if SPI is not active"""
            if not self.spi_active:
                irq_handler(pin)
            # else:
            #     print('blocked IRQ')
 
        return wrapped_irq_handler

    def enable_spi(self):
        self.spi_active = True  # block pin interrupts
        # put dual-function pins in OUT mode to prevent CS lines from being activated by their dual-function devices (e.g. switches)
        # print('settint to OUT')
        for pin in self.cs_inout_pins:
            pin.init(mode=Pin.OUT, value=1)

    def disable_spi(self):
        # print('settint to IN')
        for pin in self.cs_inout_pins:
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

    def exchange(self, cs_pin, data, read_buf=None):
        """ Writes `data` to the SPI port and then read bytes into `read_buf`while the chip select pin `cs_pin` is activated
        and ensuring that all dual-function pins are temporarily set to the OUT mode to prevent unwanted activation during the transaction. 

        IRQ handlers created through the `set_pin_irq()` method are disabled during the transaction.

        Use the context manager ``with spi:`` wo wrap a group of
        transactions to avoid the overhead of setting the dual-function pins on each
        transaction.


        Parameters:
            cs_pin (machine.Pin): chip-select pin to be activated (LOW) during the transaction

            data (bytes): Data to write.

            read_buf (buffer): read ``len(read_buf)`` into `read_buf` if not `None`.

        Returns:
            None

        Note: Using pre-allocated bytearrays and memoryview made the call slower, not faster... But we were still copying `data`
        """ 
        # if not isinstance(data, bytes):
        #     data = bytes(data)
        # din = bytearray(len(data) + read_length)
        # din = bytearray(read_length)
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

    # def write(self, cs_pin, data):
    #     self.exchange(cs_pin, data)  # write method just calls exchange
