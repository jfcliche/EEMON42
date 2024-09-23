import sys
if sys.implementation.name == 'micropython':
    import uasyncio as asyncio
else:
    import asyncio

from text_input import TextInput


class GUI:

    def __init__(self, display, rot_enc, button_rot, button_a, button_b, button_c):
        """ Create GUI instance with its hardware objects, but don't initialize anything yet.

        Parameters:

            display (Display): Object representing the display

            rot_enc (RotaryEncoder): Object representing the rotary encoder knob

            button_rot (Button): Object representing the rotary encoder shaft pushbutton (acting as ENTER)

            button_a (Button): Object representing button A (acting as BACKSPACE)

            button_b (Button): Object representing button B (acting as )

            button_c (Button): Object representing button C (acting as ESCAPE/BACK)
        """
        self.display = display
        self.rot_enc = rot_enc
        self.button_rot = button_rot
        self.button_a = button_a
        self.button_b = button_b
        self.button_c = button_c

        # default text print position
        self.text_x = 0
        self.text_y = 0
        # self.display.clear()

    def init(self):
        """ Initializes the display and the GUI.
        """

        # initialize display
        self.display.reset() # resets the display control lines
        self.display.init()  # initializes display operations
        self.clear() # clear the display

    def clear(self):
        """ Clear the display (all black)
        """
        self.display.clear()
        self.text_x = 0
        self.text_y = 0
    def draw_text(self, *args, **kwargs):
        self.display.print(*args, **kwargs)

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
        last_rot_enc_value = self.rot_enc.value()
        char = 'A'  # current character
        text = ""
        def draw_char():
            self.display.print(char, x,y, fg=self.display.GREEN, bg=self.display.BLACK)
        def draw_inv_char():
            self.display.print(char, x,y, fg=self.dispay.BLACK, bg=self.display.GREEN)

        self.display.print("_" * max_nb_characters, x=x, y=y)  # clear editing zone
        draw_char()
        while True:
            # Add character if encoder button is pressed
            if self.button_rot.value() > 0 and len(text) < max_nb_characters:
                draw_char()
                text += char
                x += self.display.font_width
                draw_inv_char()

            # Remove current character when button a is pressed (BACKSPACE)
            if self.button_a.value() > 0 and len(text) > 0:
                text = text[:-1]
                self.display.print(" ", x, y)
                x -= self.display.font_width
                draw_inv_char()

            # return the text when button C is pressed (ENTER)
            if self.button_c.value() > 0:
                break

            # Update selected character when rotary encoder moves 
            rot_enc_value = self.rot_enc.value()
            if rot_enc_value != last_rot_enc_value:
                incr = rot_enc_value - last_rot_enc_value
                last_rot_enc_value = rot_enc_value
                # print(f'encoder={rot_enc_value}, incr={incr}')
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
        # self.display.clear()
        # self.draw_text(0, 0, "EEMON42", 255, 255, 0)

        # Create status bar
        # start task to update status bar
        # Create background
        # start first menu
        try:
            while True:
                print(await self.text_input(0, 10, 8))
        finally:
            print('GUI is terminated')