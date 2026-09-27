
SSDP_PORT = 1900
nic = None
def connect_wifi():
    global nic  # we need to assign
    if nic:
        return
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    nic.disconnect()
    nic.connect('igloot', 'fifafoiot')
    while not nic.isconnected():
        pass
    print(f'Connected to Wifi')

print(f'{__name__=}, {locals()}')



def get_state(cmd='sensor.service_meter_power'):
    # HASS_URL = 'http://homeassistant.local:8123'
    HASS_URL = 'http://10.0.7.3:8123'
    HASS_LLAT = e.secrets.hass_api_token

    # from homeassistant import HomeAssistant
    # hass=HomeAssistant('http://10.0.7.3:8123', e.secrets.hass_api_token)
    # return hass
    import requests

    headers = {
        'Authorization': f'Bearer {HASS_LLAT}',
        # 'content-type': 'application/json',
    }
    # print(f'{headers=}')
    response = requests.get(HASS_URL+'/api/states/'+cmd, headers=headers)
    return response.json()['state']
    print(response.text)	

def set_state(cmd='sensor.eemon42_ch0_power', value='23'):
    # from homeassistant import HomeAssistant
    # hass=HomeAssistant('http://10.0.7.3:8123', e.secrets.hass_api_token)
    # return hass
    import requests

    headers = {
        'Authorization': f'Bearer {HASS_LLAT}',
        'content-type': 'application/json',
    }
    # print(f'{headers=}')
    response = requests.post(HASS_URL+'/api/states/'+cmd, headers=headers, json={'state':value})
    return response
    print(response.text)	

def scan():
    import ujson
    import usocket


    addr = usocket.getaddrinfo('homeassistant.local', 8123)
    print(f'{addr=}')
    return addr

    MCAST_IP = "224.0.0.123"
    MCAST_PORT = 38123
    TIMEOUT = 5

    QUERY = 'Home Assistants Assemble!'.encode('utf-8')
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
    try:
        if hasattr(sock, 'settimeout'):
            sock.settimeout(TIMEOUT)

        addrs = usocket.getaddrinfo(MCAST_IP, MCAST_PORT)
        sock.sendto(QUERY, addrs[0][4])
        data, addr = sock.recvfrom(1024)
        return ujson.loads(data.decode('utf-8'))
    finally:
        sock.close()


class x:
    def __init__(self):
        self.x=0
        timeit(self.f1)
        self.f2()

    def f1(self):
        self.x += 1

    def f2(self):
        y = 0
        def f3():
            nonlocal y
            y += 1
        timeit(f3)

async def cancelme():
    try:
        while True:
            await asyncio.sleep(0)
    except BaseException as e:
        print(f'oh my me got exsheption {e!r}')
        raise

async def canceller():
    task = asyncio.create_task(cancelme())
    await asyncio.sleep(0.5)
    task.cancel()
    await asyncio.sleep(0.5)

def timeit(fn, n=10000):
    t0 = utime.ticks_us()
    for _ in range(n):
        fn()
    t1 = utime.ticks_us()
    print(f'Function took {(t1-t0)/n:0.1f} us / iteration')



def get_instance(api_password=None):
    info = scan()
    return HomeAssistant(info.get('host'),
                         info.get('api_password', api_password))

