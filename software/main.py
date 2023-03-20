from machine import Pin, SPI, SoftSPI
from display import Display
from button import Button
from e42_spi import SPI_with_CS
from e42_rotary2 import RotaryEncoder
from gui import GUI
import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
import json

config = None
spi = None
display = None
gui = None
client = None

client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'notification'
topic_pub = b'home/sensor1/infojson'

last_message = 0
message_interval = 5
counter = 0


def sub_cb(topic, msg):
    print((topic, msg))
    if topic == b'notification' and msg == b'received':
        print('ESP received hello message')


def connect_and_subscribe():
    client = MQTTClient(
        client_id, config['mqtt_server'], user=config['mqtt_user'], password=config['mqtt_password'])
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' %
          (config['mqtt_server'], topic_sub))
    return client


def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()


def load_config():
    global config
    try:
        with open('config.json') as json_file:
            config = json.load(json_file)
    except:
        return False
    return True


def init():
    pin_sck = Pin(6, Pin.OUT)
    pin_mosi = Pin(7, Pin.OUT)
    pin_miso = Pin(2, Pin.IN)
    pin_cs = Pin(20, Pin.OUT)
    pin_cd = Pin(1, Pin.OUT)
    pin_res = Pin(0, Pin.OUT)

    global spi
    spi = SPI(1, baudrate=5000000, sck=pin_sck, mosi=pin_mosi, miso=pin_miso)
    global display
    display = Display(spi=spi, cs=pin_cs, cd=pin_cd, res=pin_res)


def dispose():
    display.clear()
    global spi
    spi.deinit()
    spi = None


def start_gui():

    global counter
    counter = 0

    pin_cs0_rota = Pin(10)
    pin_cs1_rotb = Pin(9)
    spi = SPI_with_CS(
        cs_inout_pins={'EMON0': pin_cs0_rota, 'EMON1': pin_cs1_rotb})
    rot_enc = RotaryEncoder(pin_cs0_rota, pin_cs1_rotb, verbose=0)
    spi.set_pin_irq((pin_cs0_rota, pin_cs1_rotb), rot_enc.process_state)

    button_rot = Button(Pin(8, Pin.IN, Pin.PULL_UP))
    button_a = Button(Pin(5, Pin.IN, Pin.PULL_UP))
    button_b = Button(Pin(4, Pin.IN, Pin.PULL_UP))
    button_c = Button(Pin(3, Pin.IN, Pin.PULL_UP))

    display.clear()

    global gui
    gui = GUI(display, rot_enc, button_rot, button_a, button_b, button_c)

    gui.draw_text(0, 0, "EEMON42", 255, 255, 0)


def start_client():

    if not load_config():
        print("Unable to load the configuration")
        return

    station = network.WLAN(network.STA_IF)

    if station.isconnected():
        station.disconnect()

    station.active(True)
    station.connect(config['ssid'], config['password'])

    while station.isconnected() == False:
        pass

    print('Connection successful')
    print(station.ifconfig())

    global client
    try:
        client = connect_and_subscribe()
    except OSError as e:
        restart_and_reconnect()


def main_loop():

    global last_message, counter

    while True:
        try:
            counter += 1
            if client:
                client.check_msg()
                if (time.time() - last_message) > message_interval:
                    msg = json.dumps({"counter": counter})
                    client.publish(topic_pub, msg)
                    last_message = time.time()
        except OSError as e:
            restart_and_reconnect()


def run():
    init()
    start_gui()
    # start_client()
    print(gui.show_text_input(0, 1, 8))
    try:
        main_loop()
    except KeyboardInterrupt:
        print('Interrupted')
        dispose()
