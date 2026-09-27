"""Pygame-backed ST7735 for host simulation (shadows ``software/st7735.py``)."""
from pygame_display import PygameDisplay
from software.st7735 import ST7735 as ST7735_HW # shadowed module; use package import for hardware

class ST7735(PygameDisplay, ST7735_HW):
    pass

