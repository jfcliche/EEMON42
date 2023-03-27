import sys
if sys.implementation.name == 'micropython':
    import uasyncio as asyncio
else:
    import asyncio

from font import font
from text_input import TextInput


class GUI:

    def __init__(self, display, rot_enc, button_rot, button_a, button_b, button_c):
        self._display = display
        self._rot_enc = rot_enc
        self._button_rot = button_rot
        self._button_a = button_a
        self._button_b = button_b
        self._button_c = button_c

        # self._display.clear()

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

    def draw_text(self, x, y, text, r=255, g=255, b=255, bg_r=0, bg_g=0, bg_b=0):
        for c in text:
            self._display.draw_8x8_mono_bitmap(
                x * 8, y * 8, font[ord(c)], r, g, b, bg_r, bg_g, bg_b)
            x += 1

    async def text_input(self, x, y, max_nb_characters):
        """ Allows the user to enter a string

        Controls:
            - Rotary encoder: scroll through characters
            - Rotary encoder button: selects character and moves to the next
            - Button A: Backspace (deletes previous character)
            - Button B: Not used
            - Button C: ENTER: accepts and returns string

        Parameters:

            x,y (int): initial position 

            max_nb_characters (int): maximum number of characters to enter

        Returns:

            (str): text that was entered

        """
        last_rot_enc_value = self.rot_enc().value()
        char = 'A'  # current character
        text = ""
        def draw_char():
            self.draw_text(x,y, char, 0, 255, 0)
        def draw_inv_char():
            self.draw_text(x,y, char, 0, 0, 0, 0, 255, 0)

        self.draw_text(x, y, "_" * max_nb_characters)  # clear editing zone
        draw_char()
        while True:
            # Add character if encoder button is pressed
            if self.button_rot().value() > 0 and len(text) < max_nb_characters:
                draw_char()
                text += char
                x += 1
                draw_inv_char()

            # Remove current character when button a is pressed (BACKSPACE)
            if self.button_a().value() > 0 and len(text) > 0:
                text = text[:-1]
                self.draw_text(x, y, " ")
                x -= 1
                draw_inv_char()

            # return the text when button C is pressed (ENTER)
            if self.button_c().value() > 0:
                break

            # Update selected character when rotary encoder moves 
            rot_enc_value = self.rot_enc().value()
            if rot_enc_value != last_rot_enc_value:
                incr = rot_enc_value - last_rot_enc_value
                last_rot_enc_value = rot_enc_value
                print(f'encoder={rot_enc_value}, incr={incr}')
                char = chr(min(max(ord(char) + incr, 32), 127))
                draw_char()
            await asyncio.sleep(0.1)
        # insert display cleanup
        return text

    # def show_text_input(self, x, y, max_nb_characters):
    #     text_input = TextInput(self, x, y, max_nb_characters)
    #     return text_input.show()

    async def run(self):
        """ Runs the GUI. This starts the top level interface.
        """

        self._display.clear()
        self.draw_text(0, 0, "EEMON42", 255, 255, 0)

        # Create status bar
        # start task to update status bar
        # Create background
        # start first menu
        try:
            while True:
                print(await self.text_input(0, 1, 8))
        finally:
            print('GUI is terminated')