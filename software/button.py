# Debounced Button

import time  # using functions not compatible with Cpython

class Button:
    def __init__(self, sw, delay=50, irq_wrapper=None):
        self.sw = sw
        self._delay = delay
        self.last_time_0 = 0
        self.last_time_1 = 0
        self._value = 0
        if irq_wrapper:
            self.sw.irq(irq_wrapper(self.process_irq))
        else:
            self.sw.irq(self.process_irq)

    def process_irq(self, pin):
        t = time.ticks_ms()
        if not pin.value(): # 0 when button is pressed
            if time.ticks_diff(t, self.last_time_1) > self._delay and time.ticks_diff(t, self.last_time_0) > (self._delay << 1):
                self._value += 1
                print(f'Button {pin}={pin.value()} value={self._value}, dt0={time.ticks_diff(t, self.last_time_0)} dt1={time.ticks_diff(t, self.last_time_1)}')
            self.last_time_0 = t
        else:
            self.last_time_1 = t            

    def value(self):
        ret_value = self._value
        self._value = 0
        return ret_value
