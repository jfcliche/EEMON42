import sys
if sys.implementation.name == 'micropython':
    import uasyncio as asyncio
else:
    import asyncio

# from text_input import TextInput

# Local packages
from display import Display 

class GUI:

    def __init__(self, display, rot_enc, button_rot, button_shift, button_esc, button_enter):
        """ Create GUI instance with its hardware objects, but don't initialize anything yet.

        Parameters:

            display (Display): Object representing the display

            rot_enc (RotaryEncoder): Object representing the rotary encoder knob

            button_rot (Button): Object representing the rotary encoder shaft pushbutton (acting as ENTER)

            button_shift (Button): Object representing the SHIFT/BACKSPACE button

            button_esc (Button): Object representing the ESCAPE button

            button_enter (Button): Object representing the ENTER button
        """
        self.display = display
        self.rot_enc = rot_enc
        self.button_rot = button_rot
        self.button_shift = button_shift
        self.button_esc = button_esc
        self.button_enter = button_enter

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

    async def edit_box(self, x, y, max_nb_characters):
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
        last_rot_enc_shift_value = self.rot_enc.shift_value()
        char = 'A'  # current character
        text = ""
        disp = self.display
        empty = "_" * max_nb_characters
        xx = x
        fg = disp.GREEN
        bg = disp.BLACK


        def draw_char():
            nonlocal xx
            self.display.print(char, x=xx, y=y, fg=fg, bg=bg)
        def draw_inv_char():
            nonlocal xx
            disp.print(char, x=xx, y=y, fg=bg, bg=fg)
        def draw_line():
            nonlocal xx
            self.display.print(text, x=x, y=y, fg=fg, bg=bg)
            self.display.print(empty[len(text):], x=xx, y=y, fg=fg, bg=bg)
            xx = len(text) * disp.font_width
            draw_inv_char()

        disp.print(empty, x=x, y=y)  # clear editing zone
        draw_char()
        while True:
            # Remove current character when SHIFT (here: BACKSPACE) button is released
            if self.button_shift.up():
                disp.set_brightness()
                if len(text) > 0:
                    text = text[:-1]
                    draw_line()
                    # xx -= disp.font_width
                    # draw_inv_char()

            # return the text when ENTER button is pressed
            if self.button_enter.value():
                disp.set_brightness()
                break

            # return the text when ESC is pressed
            if self.button_esc.value():
                disp.set_brightness()
                text = None
                break

            # Add character if encoder button is pressed
            if self.button_rot.value():
                disp.set_brightness()
                if len(text) < max_nb_characters:
                    # draw_char()
                    text += char
                    # x += disp.font_width
                    # draw_inv_char()
                    draw_line()

            rot_enc_shift_value = self.rot_enc.shift_value()
            if  rot_enc_shift_value!= last_rot_enc_shift_value:
                disp.set_brightness()
                incr = rot_enc_value - last_rot_enc_value
                last_rot_enc_value = rot_enc_value
                text = text[:-incr]
                draw_line()


            # Update selected character when rotary encoder moves 
            rot_enc_value = self.rot_enc.value()
            if rot_enc_value != last_rot_enc_value:
                disp.set_brightness()
                incr = rot_enc_value - last_rot_enc_value
                last_rot_enc_value = rot_enc_value
                # print(f'encoder={rot_enc_value}, incr={incr}')
                char = chr(min(max(ord(char) + incr, 32), 127))
                draw_char()
            await asyncio.sleep(0.1)
        # insert display cleanup
        return text

    async def list_box(self, items, x0=0, y0=0, fg=Display.WHITE, bg=Display.BLACK):
        # print('Running listbox {x0=} {y0=}')
        disp = self.display
        disp.set_font(8)
        th = disp.font_height  # text height
        cp = th + 1 # vertical cell pitch (text + line separator)
        last_rot_enc_value = self.rot_enc.value()
        n_items = len(items)
        top_item = 0
        cur_item = 0
        disp.set_fg_color(fg)
        disp.set_bg_color(bg)
        # Print the items
        def draw(i, update=True):
            yy = y0 + 1
            while yy + cp < disp.HEIGHT and i < n_items:
                _fg = Display.BLACK if i == cur_item else fg 
                _bg = Display.YELLOW if i == cur_item else bg 
                # print(f'print {items[i]} @ ({x0+1},{yy}) th={th}')
                disp.print(items[i], x=x0 + 1, y=yy, fg=_fg, bg=_bg, update=False)
                yy += cp
                i += 1
            if update:
                disp.update()
            return i

        x1 = x0 + len(items[0] * disp.font_width) + 1
        disp_items = draw(top_item, update=False) # Number of displayed items
        y1 = y0 + 1 + disp_items * cp
        disp.vline(x0, y0, y1)
        disp.vline(x1, y0, y1)
        for i in range(disp_items + 1):
            disp.hline(x0, x1, y0 + i * cp)
        disp.update()

        while True:
            # Return selected item number button is pressed
            if self.button_rot.value():
                disp.set_brightness()
                break

            #  Button A is pressed (BACKSPACE)
            if self.button_shift.value():
                disp.set_brightness()
                pass

            #  button C is pressed (ENTER)
            if self.button_enter.value():
                disp.set_brightness()
                break

            # Update selected character when rotary encoder moves 
            rot_enc_value = self.rot_enc.value()
            if rot_enc_value != last_rot_enc_value:
                disp.set_brightness()
                incr =  rot_enc_value - last_rot_enc_value   # clockwise = positive increment
                last_rot_enc_value = rot_enc_value
                # print(f'encoder={rot_enc_value}, incr={incr}')
                if incr > 0:
                    cur_item += incr
                    cur_item = min(cur_item, n_items-1)
                    if cur_item >= top_item + disp_items:
                        top_item = cur_item - disp_items + 1
                    draw(top_item)
                    disp.update()
                elif incr < 0:
                    cur_item += incr
                    cur_item = max(cur_item, 0)
                    if cur_item < top_item:
                        top_item = cur_item
                    draw(top_item)
                    disp.update()
            await asyncio.sleep(0.1)

        return cur_item


    async def run(self):
        """ Runs the GUI. This starts the top level interface.
        """

        try:
            while True:
                item = await self.list_box(('allo', 'les ', 'amis', 'de  ', 'la  ', 'terr'), 10, 33)
                print(f'Selected list box item {item}')
                text = await self.edit_box(0, 30, 8)
                print(f'Edit box text: {text}')
                # self.display.print(text, x=0, y=32)
        finally:
            print('GUI is terminated')