import sys
if sys.implementation.name == 'micropython':
    import uasyncio as asyncio
else:
    import asyncio


class TextInput:

    def __init__(self, gui, x, y, max_nb_characters):
        self._gui = gui
        self._x = x
        self._y = y
        self._max_nb_characters = max_nb_characters
        self._text = ""

    def _rot_action(self, c):
        self._gui.draw_text(self._x, self._y, c, 0, 0, 0, 0, 255, 0)

    def _button_rot_action(self, c):
        if len(self._text) < self._max_nb_characters:
            self._gui.draw_text(self._x, self._y, c, 0, 255, 0)
            self._text += c
            self._x += 1
            self._gui.draw_text(self._x, self._y, c, 0, 0, 0, 0, 255, 0)

    def _button_a_action(self, c):
        if len(self._text) > 0:
            self._text = self._text[:len(self._text)-1]
            self._gui.draw_text(self._x, self._y, " ")
            self._x -= 1
            self._gui.draw_text(self._x, self._y, c, 0, 0, 0, 0, 255, 0)

    def _button_c_action(self):
        self._done = True

    async def _run(self):
        last_rot_enc_value = self._gui.rot_enc().value()
        relative_value = 65
        first_pass = True
        while not self._done:
            self._gui.run_event_loop()
            if self._gui.button_rot().value() > 0:
                self._button_rot_action(chr(relative_value))
            if self._gui.button_a().value() > 0:
                self._button_a_action(chr(relative_value))
            if self._gui.button_c().value() > 0:
                self._button_c_action()
            rot_enc_value = self._gui.rot_enc().value()
            if rot_enc_value != last_rot_enc_value or first_pass:
                first_pass = False
                relative_value += rot_enc_value - last_rot_enc_value
                last_rot_enc_value = rot_enc_value
                relative_value = max(relative_value, 32)
                relative_value = min(relative_value, 127)
                self._rot_action(chr(relative_value))
            await asyncio.sleep(0)

    def show(self):
        self._done = False

        asyncio.run(self._run())

        return self._text
