class TextInput:

    def __init__(self, gui, x, y, max_nb_characters):
        self._gui = gui
        self._x = x
        self._y = y
        self._max_nb_characters = max_nb_characters
        self._text = ""

    def rot_listener(self, a):
        self._gui.draw_text(self._x, self._y, chr(
            self._gui.rot_enc().value()), 0, 0, 0, 0, 255, 0)

    def button_rot_listener(self, a):
        if len(self._text) < self._max_nb_characters:
            c = chr(self._gui.rot_enc().value())
            self._gui.draw_text(self._x, self._y, c, 0, 255, 0)
            self._text += c
            self._x += 1
            self._gui.draw_text(self._x, self._y, chr(
                self._gui.rot_enc().value()), 0, 0, 0, 0, 255, 0)

    def button_a_listener(self, a):
        if len(self._text) > 0:
            self._text = self._text[:len(self._text)-1]
            self._gui.draw_text(self._x, self._y, " ")
            self._x -= 1
            self._gui.draw_text(self._x, self._y, chr(
                self._gui.rot_enc().value()), 0, 0, 0, 0, 255, 0)

    def button_c_listener(self, a):
        self._done = True

    def show(self):
        self._done = False
        self._gui.rot_enc().set(value=65, min_val=32, max_val=127)
        self._gui.rot_enc().callback(self.rot_listener)
        self._gui.button_rot().callback(self.button_rot_listener)
        self._gui.button_a().callback(self.button_a_listener)
        self._gui.button_c().callback(self.button_c_listener)

        self._gui.draw_text(self._x, self._y, chr(
            self._gui.rot_enc().value()), 0, 0, 0, 0, 255, 0)

        while not self._done:
            self._gui.run_event_loop()

        self._gui.button_c().callback(None)
        self._gui.button_a().callback(None)
        self._gui.button_rot().callback(None)
        self._gui.rot_enc().callback(None)

        return self._text
