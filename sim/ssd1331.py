"""Pygame-backed SSD1331 for host simulation (shadows ``software/ssd1331.py``)."""

from pygame_display import PygameDisplay
from software.ssd1331 import SSD1331 as SSD1331_HW  # shadowed module; use package import for hardware

class SSD1331(PygameDisplay, SSD1331_HW):
    pass