# standard packages
from machine import Pin
import time
from umqttsimple import MQTTClient
import ubinascii
import machine
# import micropython
import network
# import esp
import json

import sys
if sys.implementation.name == 'micropython':
    import uasyncio as asyncio
else:
    import asyncio

# local packages
from ssd1331 import SSD1331  # OLED display
from ade7816 import ADE7816  # Energy monitor
from button import Button
from spi import SPI_with_CS
from rotary_encoder import RotaryEncoder
from gui import GUI



class EEMON42:
    """ EEMON42 main application.
    """

    topic_sub = b'notification'
    topic_pub = b'home/sensor1/infojson'



    def __init__(self):
        """ Create EEMON42 hardware objects
        """

        self.config = None
        self.spi = None
        self.display = None
        self.gui = None
        self.client = None # wifi client
        self.fatal_error = False
        self.client_id = ubinascii.hexlify(machine.unique_id())  # too bad the bytes.hex() function is not supported.
        self.station = None

        self.message_interval = 5

        self.pin_sck = Pin(6, Pin.OUT)  # SPI clock
        self.pin_mosi = Pin(7, Pin.OUT) # SPI MOSI
        self.pin_miso = Pin(2, Pin.IN)  # SPI MISO
        self.pin_cs7_disp = Pin(20, Pin.OUT) # SPI display chip select (not shared)
        self.pin_cd = Pin(1, Pin.OUT) # SPI Display Command/Data line
        self.pin_res = Pin(0, Pin.OUT) # SPI display reset
        # The following pins are dual functions (EMON chip-select and switches or IRQ).
        # Teir mode is managed by the SPI module
        self.pin_cs0_rota = Pin(10)
        self.pin_cs1_rotb = Pin(9)
        self.pin_cs2_button_rot = Pin(8)
        self.pin_cs3_button_a = Pin(3)
        self.pin_cs4_button_b = Pin(5)
        self.pin_cs5_button_c = Pin(4)
        self.pin_cs6_irq = Pin(21)

        # List of pins that are used *both* for buttton/encoder/irq inputs and energy monitor chip select outputs
        dual_fn_pins = (self.pin_cs0_rota, 
                        self.pin_cs1_rotb,
                        self.pin_cs2_button_rot,
                        self.pin_cs3_button_a,
                        self.pin_cs4_button_b,
                        self.pin_cs5_button_c,
                        self.pin_cs6_irq)

        self.spi = SPI_with_CS(
                baudrate=2500000,  # 2.5 MHz clock 
                sck=self.pin_sck,
                mosi=self.pin_mosi,
                miso=self.pin_miso,
                cs_inout_pins=dual_fn_pins  # these pins are set to mode=Pin.OUT during SPI transactions to prevent button operations to enable CS lines 
                )

        # Display handler
        self.display = SSD1331(spi=self.spi, cs_pin=self.pin_cs7_disp, cd_pin=self.pin_cd, res_pin=self.pin_res)

        self.counter = 0

        # Rotary Encoder handler
        self.rot_enc = RotaryEncoder(
            pin_a=self.pin_cs0_rota, 
            pin_b=self.pin_cs1_rotb, 
            irq_wrapper=self.spi.get_irq, # provide a IRQ handler that is disabled during SPI transactions
            verbose=0)

        # Button handlers
        self.button_rot = Button(self.pin_cs2_button_rot, irq_wrapper=self.spi.get_irq)
        self.button_a = Button(self.pin_cs3_button_a, irq_wrapper=self.spi.get_irq)
        self.button_b = Button(self.pin_cs4_button_b, irq_wrapper=self.spi.get_irq)
        self.button_c = Button(self.pin_cs5_button_c, irq_wrapper=self.spi.get_irq)

        # Create the 7 energy monitor handlers
        self.emon = [ADE7816(spi=self.spi, cs_pin=cs_pin, irq_pin=self.pin_cs6_irq, irq_wrapper=self.spi.get_irq, index=ix) 
                     for ix, cs_pin in enumerate(dual_fn_pins)]

        self.pin_cs6_irq.irq(handler=self.spi.get_irq(self.emon_irq_handler));
         


        # Create the GUI (display + buttons, menu system etc) handler
        self.gui = GUI(self.display, self.rot_enc, self.button_rot, self.button_a, self.button_b, self.button_c)


        print('Loading configuration file')
        if not self.load_config():
            print("Unable to load the configuration")
            return

    def emon_irq_handler(self, pin):
        print(f'Got pin IRQ!')
        if False:
            for e in self.emon:
                e.irq_handler()

    def init(self):
        self.display.print("EEMON42\r\nis\r\nthe\r\nbest\nof\nall", fg=self.display.YELLOW, font_size=5)
        for e in self.emon:
            e.init()
        time.sleep(1)
        self.display.clear()



    async def start_wifi_client(self):
        """ Connect to the Wifi Access point

        Todo: continuously test connection, and loop to attempt reconnection
        """
        try:
            print(f'Starting WiFi connection')
            station = network.WLAN(network.STA_IF)

            if station.isconnected():
                station.disconnect()

            station.active(True)

            ssid = self.config['ssid']
            print(f"Waiting for WiFi connection to {ssid}")
            station.connect(ssid, self.config['password'])

            # Wait for connection to the AP
            while not station.isconnected():
                await asyncio.sleep(.3)

            print('WiFi connection successful')
            print(station.ifconfig())
            self.station = station  # store wifi object, which signals wifi is ready
            print('WiFi connection completed')
        except Exception as e:
            print(f'Wifi exception was raised: {e}')
            raise

    async def mqtt_connect_and_subscribe(self):


        def sub_cb(topic, msg):
            print((topic, msg))
            if topic == b'notification' and msg == b'received':
                print('ESP received hello message')


        try:
            print(f'Starting MQTT connection')
            config = self.config

            # Make sure wifi link is ready
            while not self.station:
                print('MQTT client waiting for WiFi connection')
                await asyncio.sleep(1)
            print(f'Creating MQTT object')

            client = MQTTClient(self.client_id, 
                config['mqtt_server'], 
                user=config['mqtt_user'], 
                password=config['mqtt_password'])
            print('MQTT object created. Connecting...')
            client.set_callback(sub_cb)
            client.connect()
            print('MQTT connection complete. Subscribing...')
            client.subscribe(self.topic_sub)
            print('Connected to %s MQTT broker, subscribed to %s topic' %
                  (config['mqtt_server'], topic_sub))
            self.client = client  # Store MQTT client object, which also indicates it is fully ready 
        except Exception as e:
            print(f'Error while connecting to MQTT server: {repr(e)}')
            # self.fatal_error = True
            raise

    async def process_mqtt_messages(self):
        """ Continuously look for new data to send and sent it when available 
        """
        counter = 0
        while True:
            try:
                counter += 1
                if self.client: # don't do anything unless the MQTT client is up and running
                    self.client.check_msg()  # what does that do? messages from server?
                    msg = json.dumps({"counter": counter})
                    self.client.publish(self.topic_pub, msg)
                await asyncio.sleep(self.message_interval)
            except OSError as e:
                self.fatal_error = True


    def restart_and_reconnect(self):
        print('Failed to connect to MQTT broker. Reconnecting...')
        time.sleep(10)
        machine.reset()


    def load_config(self):
        try:
            with open('config.json') as json_file:
                self.config = json.load(json_file)
        except:
            return False
        return True
 
    def dispose(self):
        self.display.clear()
        self.spi.deinit()
        self.spi = None

    async def screen_saver(self, timeout=10):
        while True:
            t = time.time() - self.rot_enc.last_time - timeout
            if t > 0:
                self.display.clear()
            # elif t > 0:
            #     self.display.set_master_intensity(0)
            await asyncio.sleep(1)


    async def watchdog(self): 
        """ Monitors the system status flags and reset the board if a fatal error is detected
        """
        while True:
            if self.fatal_error:
                self.restart_and_reconnect()
            await asyncio.sleep(1)

    async def scan_emon(self):
        ch = 0;
        ch_max = len(self.emon) - 1
        while True:
            try:
                # for ix, e in enumerate(self.emon):
                #     f = e.get_frequency()
                #     print(f'CH{ix} = {f} Hz')

                #     for ch in range(1):
                #         i = e.get_rms_current(ch)
                #         print(f'CH{ix}.{ch} = {i:.3f} A RMS')
                #         if not ch:
                #             self.display.print(f'CH{ix} = {i:.3f} A RMS', x=0, y=ix*self.display.font_height)
                while not self.pin_cs6_irq():
                    if self.emon[ch].irq_handler(self.pin_cs6_irq):
                        ch = ch + 1 if ch < ch_max else 0
                    await asyncio.sleep(0) 
                print('.', end='')
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f'scan_emon exception {e}')
                raise
    async def main_loop(self):

        self.init()

        print('Starting main loop')


 
        # Start background tasks
        print('Starting background tasks')
        task_list = (
            self.screen_saver(timeout=10), # turn off the display after `timeout`
            self.scan_emon(),
            # self.watchdog(), # reboots if there is a fatal error
            # self.start_wifi_client(), # connect wifi
            # self.mqtt_connect_and_subscribe(), # connects MQTT client when wifi is up
            # self.process_mqtt_messages() # sends MQTT messages when MQTT client is connected
            );
        tasks = [asyncio.create_task(t) for t in task_list]

        # Start GUI
        print('Starting GUI')
        try:
            await self.gui.run()  # run the GUI
        finally:
            # make sure we cancel all background tasks when exiting
            for t in tasks:
                t.cancel()
            self.dispose()
        print('Exiting main loop')
 
    def run(self):
        # init()
        # start_gui()
        # start_client()

        try:
            asyncio.run(self.main_loop())
        except KeyboardInterrupt:
            print('Interrupted')
