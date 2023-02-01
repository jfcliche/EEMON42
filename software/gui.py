from font import font
from text_input import TextInput


class GUI:

    def __init__(self, display, rot_enc, button_rot, button_a, button_b, button_c, event_loop=None):
        self._display = display
        self._rot_enc = rot_enc
        self._button_rot = button_rot
        self._button_a = button_a
        self._button_b = button_b
        self._button_c = button_c
        self._event_loop = event_loop

        self._display.clear()

    def display(self):
        return self._display

    def rot_enc(self):
        return self._rot_enc

    def button_rot(self):
        return self._button_rot

    def button_a(self):
        return self._button_a

    def button_b(self):
        return self._button_b

    def button_c(self):
        return self._button_c

    def run_event_loop(self):
        if self._event_loop:
            self._event_loop()

    def draw_text(self, x, y, text, r=255, g=255, b=255, bg_r=0, bg_g=0, bg_b=0):
        for c in text:
            self._display.draw_8x8_mono_bitmap(
                x * 8, y * 8, font[ord(c)], r, g, b, bg_r, bg_g, bg_b)
            x += 1

    def show_text_input(self, x, y, max_nb_characters):
        text_input = TextInput(self, x, y, max_nb_characters)
        return text_input.show()
