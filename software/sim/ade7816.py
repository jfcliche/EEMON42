from embedded.ade7816 import ADE7816 as ADE7816_HW


class ADE7816(ADE7816_HW):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._regs = {r: 0 for r in self.REGS}

    def get_rms_current(self, ch):
        return 1 + ch / 10

    def write_reg(self, name, value, ch=None):
        if ch is not None:
            name += "012345"[ch]
        if self.verbose:
            print(f'Writing reg {name} = {value}')
        self._regs[name] = value

    def read_reg(self, name, ch=None):
        if ch is not None:
            name += "012345"[ch]
        value = self._regs[name]
        if self.verbose:
            print(f'Reading reg {name} = {value}')
        return value

    def get_frequency(self):
        return 60

    def irq_handler(self, pin):
        pass
