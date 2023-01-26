from machine import Pin, SPI, SoftSPI
from ssd1331 import SSD1331
from rotary_irq_esp import RotaryIRQ
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
oled = None
gui = None
client = None

rot_enc = None

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
    client = MQTTClient(client_id, config['mqtt_server'], user=config['mqtt_user'], password=config['mqtt_password'])
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (config['mqtt_server'], topic_sub))
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
    pin_sck=Pin(6, Pin.OUT)
    pin_mosi=Pin(7, Pin.OUT)
    pin_miso=Pin(2, Pin.IN)
    pin_cs=Pin(20, Pin.OUT)
    pin_cd=Pin(1, Pin.OUT)
    pin_res=Pin(0, Pin.OUT)

    global spi
    spi = SPI(1, baudrate=5000000, sck=pin_sck, mosi=pin_mosi, miso=pin_miso)
    global oled
    oled = SSD1331(spi=spi, cs=pin_cs, cd=pin_cd, res=pin_res)

    global rot_enc
    rot_enc = RotaryIRQ(pin_num_clk=9, pin_num_dt=10, pull_up=True)


def dispose():
    oled.clear()
    global spi
    spi.deinit()
    spi = None


def update():
    gui.draw_text(3, 4, "        ")
    gui.draw_text(3, 4, str(counter), 0, 255, 0)


def rot_enc_changed():
    global counter
    counter = rot_enc.value()
    update()


def start_gui():

    global counter
    counter = 0

    # p3=Pin(3, Pin.IN, Pin.PULL_UP)
    # p3.irq(lambda p:print(p, p.value()))
    # p4=Pin(4, Pin.IN, Pin.PULL_UP)
    # p4.irq(lambda p:print(p, p.value()))
    # p5=Pin(5, Pin.IN, Pin.PULL_UP)
    # p5.irq(lambda p:print(p, p.value()))
    # p8=Pin(8, Pin.IN, Pin.PULL_UP)
    # p8.irq(lambda p:print(p, p.value()))

    oled.clear()

    global gui
    gui = GUI(oled)
 
    gui.draw_text(0, 0, "EEMON42", 255, 255, 0)
    gui.draw_text(1, 3, "Counter: ")
    update()

    rot_enc.add_listener(rot_enc_changed)


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

    global last_message

    while True:
        try:
            counter = rot_enc.value()
            client.check_msg()
            if (time.time() - last_message) > message_interval:
                msg = json.dumps({"counter":counter})
                client.publish(topic_pub, msg)
                last_message = time.time()
        except OSError as e:
            restart_and_reconnect()


def run():
    init()
    start_gui()
    start_client()
    try:
        main_loop()
    except KeyboardInterrupt:
        print('Interrupted')
        dispose()
