# boot.py -- run on boot-up
# a=10
# from e42_spi import SPI_with_CS
from ade7816 import ADE7816, test
spi, p, rot = test(1000)