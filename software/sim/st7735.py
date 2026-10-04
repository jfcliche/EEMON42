"""Pygame-backed ST7735 for host simulation (shadows ``embedded/st7735.py``)."""
from pygame_display import PygameDisplay
from embedded.st7735 import ST7735 as ST7735_HW

class ST7735(PygameDisplay, ST7735_HW):
    pass

