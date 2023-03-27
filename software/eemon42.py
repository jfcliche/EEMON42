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
        self.pin_cs3_button_a = Pin(5)
        self.pin_cs4_button_b = Pin(4)
        self.pin_cs5_button_c = Pin(3)
        self.pin_cs6_irq = Pin(21)
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
        self.button_rot = Button(self.pin_cs2_button_rot)
        self.button_a = Button(self.pin_cs3_button_a)
        self.button_b = Button(self.pin_cs4_button_b)
        self.button_c = Button(self.pin_cs5_button_c)

        # Create the 7 energy monitor handlers
        self.emon = [ADE7816(spi=self.spi, cs_pin=cs_pin) for cs_pin in dual_fn_pins]

        # Create the GUI (display + buttons, menu system etc) handler
        self.gui = GUI(self.display, self.rot_enc, self.button_rot, self.button_a, self.button_b, self.button_c)


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

    async def watchdog(self): 
        """ Monitors the system status flags and reset the board if a fatal error is detected
        """
        while True:
            if self.fatal_error:
                self.restart_and_reconnect()
            await asyncio.sleep(1)

    async def main_loop(self):
        print('Starting main loop')


        print('Loading configuration file')
        if not self.load_config():
            print("Unable to load the configuration")
            return

        # Start background tasks
        print('Starting background tasks')
        tasks = (
            # asyncio.create_task(self.watchdog()), # reboots if there is a fatal error
            asyncio.create_task(self.start_wifi_client()), # connect wifi
            asyncio.create_task(self.mqtt_connect_and_subscribe()), # connects MQTT client when wifi is up
            asyncio.create_task(self.process_mqtt_messages()) # sends MQTT messages when MQTT client is connected
            );

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
