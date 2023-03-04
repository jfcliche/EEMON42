# boot.py -- run on boot-up
a=10
from machine import Pin, SPI
from ade7816 import ADE7816, test
spi, p = test(1000)