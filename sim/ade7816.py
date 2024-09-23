import random

class ADE7816:
    def __init__(self, *args, index, **kwargs):
        self.index = index

    def init(self):
        """ Initialize the energy monitor chip
        """
        print(f'Initializing ADE7816 Energy monitor {self.index}')

    def get_rms_current(self, ch):
        """ Get instantaneous RMS current measurement 

        Parameters:

            ch (int): channel number (0-5)
        """
        return 1+ch/10

    def get_frequency(self):
        return 60
