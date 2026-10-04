"""Pygame-backed SSD1331 for host simulation (shadows ``embedded/ssd1331.py``)."""

from pygame_display import PygameDisplay
from embedded.ssd1331 import SSD1331 as SSD1331_HW

class SSD1331(PygameDisplay, SSD1331_HW):
    pass