import uuid

STA_IF = 0

_country = "XX"


def country(code=None):
    """MicroPython regulatory country code; no-op in sim except storing for get."""
    global _country
    if code is None:
        return _country
    _country = code


class WLAN:
    PM_NONE = 0

    def __init__(self, *args, **kwargs):
        self.connected = False

    def isconnected(self):
        return self.connected

    def active(self, state=None):
        if state is None:
            return True
        return None

    def connect(self, *args, **kwargs):
        self.connected = True

    def disconnect(self, *args, **kwargs):
        self.connected = False

    def ifconfig(self, *args, **kwargs):
        if args or kwargs:
            return None
        return ("192.168.0.100", "255.255.255.0", "192.168.0.1", "8.8.8.8")

    def config(self, *args, **kwargs):
        if args and not kwargs:
            key = args[0]
            if key == "mac":
                return uuid.getnode().to_bytes(6, "big")
        return None
