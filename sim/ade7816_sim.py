import random
import ade7816

class ADE7816(ade7816.ADE7816):
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.index = index


        # self.voltage = 240
        # self.current = (2.2,)*6
        # self.active_power = (100,) * 6
        # self.update_number = 0
        # self.config = config
        self._regs = {r:0 for r in self.REGS}

    # def init(self):
    #     """ Initialize the energy monitor chip
    #     """
    #     print(f'Initializing ADE7816 Energy monitor {self.index}')

    def get_rms_current(self, ch):
        """ Get instantaneous RMS current measurement 

        Parameters:

            ch (int): channel number (0-5)
        """
        return 1+ch/10

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
