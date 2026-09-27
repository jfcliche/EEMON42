import sys
is_micropython = sys.implementation.name == 'micropython'

# from ssd1331 import SSD1331 as Display  # 96x64 OLED display
from st7735 import ST7735 as Display  # 128x160 LCD display

# Allocate large frame buffer as early as possible before memory is too fragmented
fb = memoryview(bytearray(Display.WIDTH * Display.HEIGHT * Display.BYTES_PER_PIXEL)) # frame buffer, 2 bytes per pixel

# standard packages
from machine import Pin
import time
import machine
import network
import json

import asyncio
import gc


try:
    from asyncio import ThreadSafeFlag
except ImportError:
    from asyncio import Event as ThreadSafeFlag

from ade7816 import ADE7816  # Energy monitor chip
from button import Button  # Pushbutton
from rotary_encoder import RotaryEncoder


# local packages
from spi import SPI_with_CS
from gui import GUI
from namespace import Namespace
from hass import HomeAssistant
import menus

class EEMON42:
    """ EEMON42 main application.
    """

    # topic_sub = b'notification'
    # topic_pub = b'home/sensor1/infojson'

    CONFIG_FOLDER = '/config/'

    def __init__(self):
        """ Create EEMON42 hardware objects
        """
        gc.collect()

        self.config = None
        self.secrets = None
        self.spi = None
        self.display = None
        self.gui = None
        self.client = None # wifi client
        self.fatal_error = False
        self.client_id = machine.unique_id().hex()
        self.nic = None
        self.network_connected = asyncio.Event()

        self.message_interval = 5
        self.screen_saver_timeout = 120

        print('Welcome to EEMON42')
        print('   Creating EEMON42 instance')

        print('   Loading configuration file')
        self.config = self.load_config('config.json')
        self.secrets = self.load_config('secrets.json')

        self.hass = HomeAssistant(
            self.config, self.secrets, network_ready=self.network_connected
        )

        self.irq_flag = ThreadSafeFlag()
        # Pin definitions
        # Pin numbers are GPIO numbers, not package pins numbers
        self.pin_sck = Pin(6, Pin.OUT)  # SPI clock
        self.pin_mosi = Pin(7, Pin.OUT) # SPI MOSI
        self.pin_miso = Pin(2, Pin.IN)  # SPI MISO
        self.pin_cs7_disp = Pin(20, Pin.OUT) # SPI display chip select (not shared)
        self.pin_cd = Pin(1, Pin.OUT) # SPI Display Command/Data line
        self.pin_res = Pin(0, Pin.OUT) # SPI display reset
        # The following pins are dual functions (EMON chip-select and switches or IRQ).
        # Their mode is managed by the SPI module
        self.pin_cs0_rota = Pin(10)
        self.pin_cs1_rotb = Pin(9)
        self.pin_cs2_button_rot = Pin(8) # Rotary encoder pushbutton switch
        self.pin_cs3_button_a = Pin(3) # SW2, bottom switch, usually ENTER
        self.pin_cs4_button_b = Pin(5) # SW3, top switch, usually ESC/BACK
        self.pin_cs5_button_c = Pin(4) # SW4, middle switch, usually SHIFT
        self.pin_cs6_irq = Pin(21)

        # List of pins that are used as ADE7816 chip select outputs. 
        # Those are *ALSO* used for buttton/encoder/irq inputs
        emon_cs_pins = (self.pin_cs0_rota, 
                        self.pin_cs1_rotb,
                        self.pin_cs2_button_rot,
                        self.pin_cs3_button_a,
                        self.pin_cs4_button_b,
                        self.pin_cs5_button_c,
                        self.pin_cs6_irq)

        # Instantiate the SPI controller
        self.spi = SPI_with_CS(
                baudrate=2500000,  # 2.5 MHz clock 
                sck=self.pin_sck,
                mosi=self.pin_mosi,
                miso=self.pin_miso,
                cs_inout_pins=emon_cs_pins  # these pins are set to mode=Pin.OUT during SPI transactions to prevent button operations to enable CS lines 
                )

        # gc.collect()

        # Display handler
        self.display = Display(spi=self.spi, cs_pin=self.pin_cs7_disp, cd_pin=self.pin_cd, res_pin=self.pin_res, fb=fb)

        self.counter = 0

        # Button handlers
        self.button_rot = Button(self.pin_cs2_button_rot, irq_wrapper=self.spi.get_irq)
        self.button_a = Button(self.pin_cs3_button_a, irq_wrapper=self.spi.get_irq)
        self.button_b = Button(self.pin_cs4_button_b, irq_wrapper=self.spi.get_irq)
        self.button_c = Button(self.pin_cs5_button_c, irq_wrapper=self.spi.get_irq)

        # Rotary Encoder handler
        self.rot_enc = RotaryEncoder(
            pin_a=self.pin_cs0_rota, 
            pin_b=self.pin_cs1_rotb,
            button_shift = self.button_c, 
            irq_wrapper=self.spi.get_irq, # provide a IRQ handler that is disabled during SPI transactions
            verbose=0)

        # Create the 7 energy monitor chip handlers
        eemon_conf = self.config.setdefault('emon',[Namespace()]*len(emon_cs_pins)) # Create eemon entry if it does not exists
        self.emon = [ADE7816(
                        spi=self.spi, cs_pin=cs_pin, irq_pin=self.pin_cs6_irq, 
                        irq_wrapper=self.spi.get_irq, 
                        index=ix, 
                        config=eemon_conf[ix]) 
                     for ix, cs_pin in enumerate(emon_cs_pins)]

        # Setup the ADE7816 IRQ line interrupt handler
        self.pin_cs6_irq.irq(handler=self.spi.get_irq(self.emon_irq_handler));
         

        # Create the GUI (display + buttons, menu system etc) handler
        self.gui = GUI(
            self.display, 
            self.rot_enc, 
            self.button_rot, button_enter=self.button_a, button_esc=self.button_b, button_shift=self.button_c)

        print('   Instantiation complete')

    def emon_irq_handler(self, pin):
        """ IRQ handler to process changes on the EMON IRQ line 

        This being called as an IRQ service call in micropython, only thread safe actions must be performed. 
        """
        if not pin.value(): # only set the event if the IRQ line went low
            self.irq_flag.set()

    def init(self):
        """ Initialize hardware

        This function toggles bits and communicates with the external hardware to bring it into known conditions, as opposed to ``__init__``
        which only created the hardware objects.
        """
        # Initialize display
        self.display.init()
        # self.display.print("EEMON42\r\nis\r\nthe\r\nbest\nof\nall", fg=self.display.YELLOW, font_size=5)

        # Initialize Energy Monitor ICs

        for e in self.emon:
            e.init()
        # time.sleep(1)
        # self.display.clear()

        self.gui.init()

    async def wifi_connection(self):
        """Connect to WiFi and signal ``network_connected`` for other tasks."""
        print('Starting WiFi connection Task')
        nic = network.WLAN(network.STA_IF)
        nic.active(True)
        nic.disconnect()
        self.network_connected.clear()
        self.nic = None
        try:
            while True:
                if not nic.isconnected():
                    if self.network_connected.is_set():
                        print('WiFi disconnected')
                    self.network_connected.clear()
                    self.nic = None
                    ssid = self.secrets['ssid']
                    print(f"Waiting for WiFi connection to {ssid}")
                    nic.connect(ssid, self.secrets['password'])
                    while not nic.isconnected():
                        await asyncio.sleep(0.3)
                    print('WiFi connection successful')
                    print(nic.ifconfig())
                    self.nic = nic
                    self.network_connected.set()
                    print('WiFi connection completed')
                await asyncio.sleep(1)
        except BaseException as e:
            print(f'Exception on Wifi task: {e!r}')
            raise
        finally:
            print('Wifi connection task has terminated')
            self.network_connected.clear()
            self.nic = None
            nic.disconnect()


    def load_config(self, filename):
        # If running on-board, always load the config from the '/config' folder, even if the current 
        # working directory is elsewhere (e.g. folder ``/remote`` if we run through ``mpremote mount``)
        # If running on a PC, use the source from the ``software`` folder even if we run from the folder ``sim`` 
        filename = self.CONFIG_FOLDER + filename
        try:
            with open(filename) as json_file:
                config = Namespace(json.load(json_file))
        except OSError:
            print(f'Configuration file "{filename} not found. Loading empty config')
            config = Namespace()  # Create empty config
        return config    

 
    def dispose(self):
        self.display.clear()
        self.spi.deinit()
        self.spi = None

    async def screen_saver(self, timeout=120):
        print('Starting screen saver task')
        try:
            while True:
                dt = int(time.time() - self.display.last_time) 
                if dt > 2*timeout:
                    self.display.set_brightness(0) # turn off display
                elif dt > timeout:
                    self.display.set_brightness(1) # set minimum brightness
                await asyncio.sleep(1)
        except BaseException as e:
            print(f'Exception in screen_saver: {e!r}')
            raise
        finally:
            print('Screen saver task has terminated')
    async def watchdog(self): 
        """ Monitors the system status flags and reset the board if a fatal error is detected
        """
        while True:
            if self.fatal_error:
                self.restart_and_reconnect()
            await asyncio.sleep(1)

    async def scan_emon(self):
        print('Starting EMON scanning task')
        dev = 0  # current energy monitor device number
        n_dev = len(self.emon) # total number of energy monitor devices

        # define local variables for faster access
        emon = self.emon
        irq_pin = self.pin_cs6_irq  
        irq_flag = self.irq_flag
        spi = self.spi
        print(f'IRQ={self.pin_cs6_irq()}')

        try:
            while True:
                # If there is not already an IRQ, wait for the IRQ flag to be set by the pin interrupt, 
                # but continue anyways after a timeout in case the IRQ pin went low without the interrupt being processed
                if irq_pin(): # if no interrupt is pending
                    # print(f'IRQ={irq_pin()}')
                    try:
                        await asyncio.wait_for(irq_flag.wait(), 13)
                        irq_flag.clear()
                    except asyncio.TimeoutError:
                        print(f'Timout while waiting for IRQ, {dev=}, IRQ={irq_pin()}')

                scanned_dev = 0
                while not irq_pin() and not spi.spi_active and scanned_dev < n_dev:
                    emon[dev].irq_handler(irq_pin)
                    dev += 1
                    if dev >= n_dev: 
                        dev = 0
                    scanned_dev += 1
                    # print(f'{dev=} {scanned_dev=}')
                    await asyncio.sleep(0.01)  # be a good neighbor and give back control to the event loop to let the UI respond to user actions 
                # print('---')
                # await asyncio.sleep(0.1)
        except BaseException as e:
            print(f'Exception in EMON scanning: {e!r}')
            raise
        finally:
            print('EMON scanning task has terminated')

    async def publish_task(self):
        """Publish dummy sensor readings to Home Assistant (placeholder for EMON telemetry)."""
        entity_id = 'sensor.eemon42_dummy'
        value = 0
        print('Starting Home Assistant publish task')
        try:
            while True:
                await self.network_connected.wait()
                value += 1
                try:
                    await self.hass.set_state(
                        entity_id,
                        value,
                        {'unit_of_measurement': 'W', 'friendly_name': 'EEMON42 dummy'},
                    )
                except OSError as e:
                    print(f'Home Assistant publish failed: {e!r}')
                await asyncio.sleep(3)
        except asyncio.CancelledError:
            raise
        finally:
            print('Home Assistant publish task has terminated')

    async def main_loop(self, extra_tasks = tuple()):

        self.init()

        print('Starting main loop')

        # Start background tasks
        # print('Starting background tasks')
        task_list = (
            self.screen_saver(timeout=self.screen_saver_timeout), # turn off the display after `timeout`
            self.scan_emon(),
            # self.watchdog(), # reboots if there is a fatal error
            self.wifi_connection(), # connect wifi
            self.hass.run(),
            self.publish_task(),
            # self.mqtt_connect_and_subscribe(), # connects MQTT client when wifi is up
            # self.process_mqtt_messages() # sends MQTT messages when MQTT client is connected
            menus.run_main_menu(self.gui, app=self),
            );
        tasks = tuple(asyncio.create_task(t) for t in task_list) + extra_tasks
        try:
            print('Starting all background tasks')
            results = await asyncio.gather(*tasks, return_exceptions=False)  # return_exceptions=False: will raise an exception as soon as one of the tasks raise one (other tasks won't be cancelled)
        except (KeyboardInterrupt, asyncio.CancelledError):
            print(f'Main loop interrupted by user')
 
        # make sure we cancel all background tasks when exiting
        for t in tasks:
            t.cancel()
        # Wait until all task are completed 
        # return_exceptions=True: Will return only when all tasks are done, with or without exceptions. The ones that had not already failed should stop due to the cancellation. 
        await asyncio.gather(*tasks, return_exceptions=True) 
        print('Disposing EEMON42 resources...')
        self.dispose()
        print('Exiting main loop')
 
    def run(self):
        try:
            asyncio.run(self.main_loop())  # Can't use the parameter debug in micropython
        except (KeyboardInterrupt):
            print('Interrupted')
        except:
            raise
# if __name__ == '__main__':
#     e = EEMON42()
#     d = e.display
#     e.run()