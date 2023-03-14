# Debounced Button
# Ref: https://gist.github.com/SpotlightKid/0a0aac56606286a80f860b116423c94f

# inspired by: https://forum.micropython.org/viewtopic.php?t=1938#p10931

import micropython

try:
    from machine import Timer
    def timer_init(t, p, cb): return t.init(period=p, callback=cb)
except ImportError:
    from pyb import Timer
    def timer_init(t, p, cb): return t.init(freq=1000 // p, callback=cb)


class Button:
    def __init__(self, sw, delay=50, tid=4):
        self.sw = sw
        # Create references to bound methods beforehand
        # http://docs.micropython.org/en/latest/pyboard/library/micropython.html#micropython.schedule
        self._sw_cb = self._sw_cb
        self._tim_cb = self._tim_cb
        self._set_cb = getattr(self.sw, 'callback', None) or self.sw.irq
        self._value = 0
        self._delay = delay
        self._tim = Timer(tid)
        self._set_callback(self._callback, None)

    def _sw_cb(self, pin=None):
        self._set_cb(None)
        timer_init(self._tim, self._delay, self._tim_cb)

    def _tim_cb(self, tim):
        tim.deinit()
        if self.sw():
            micropython.schedule(self.cb, self.arg)
        self._set_cb(self._sw_cb if self.cb else None)

    def _set_callback(self, cb, arg=None):
        self._tim.deinit()
        self.cb = cb
        self.arg = arg
        self._set_cb(self._sw_cb if cb else None)

    def _callback(self, a):
        self._value += 1

    def value(self):
        ret_value = self._value
        self._value = 0
        return ret_value
