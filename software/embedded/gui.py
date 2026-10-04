import sys
if sys.implementation.name == 'micropython':
    import uasyncio as asyncio
else:
    import asyncio

# from text_input import TextInput

# Local packages
from display import Display
from namespace import Namespace


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

            eemon42 (EEMON42): EEMON42 object that will use to access system status, energy monitor chips etc.
        """
        self.display = display
        self.rot_enc = rot_enc
        self.button_rot = button_rot
        self.button_shift = button_shift
        self.button_esc = button_esc
        self.button_enter = button_enter
        self.loop_delay = 0.1  # sleep time in seconds between UI polling. Should be fast enough to provide a responsive UI, but not too fast in order to leave time for other async process to complete with minimum latency   

    def init(self):
        """ Initializes the display and the GUI.
        """

        # initialize display
        # self.display.reset() # resets the display control lines
        # self.display.init()  # initializes display operations
        # self.clear() # clear the display

        # Display is assumed initialzed and cleared
        # get latest rotary encoder positions to use as a starting point
        self.last_rot_enc_value = self.rot_enc.value()
        self.last_shift_rot_enc_value = self.rot_enc.shift_value()

    def clear(self, update=True):
        """ Clear the display (all black)
        """
        self.display.clear(update=update)

    # def draw_text(self, *args, **kwargs):
    #     self.display.print(*args, **kwargs)

    def shift_pressed(self):
        v = self.button_shift.value()
        if v:
            self.display.set_brightness()
        return v

    def shift_released(self):
        v = self.button_shift.up()
        if v:
            self.display.set_brightness()
        return v

    def rot_pressed(self):
        v = self.button_rot.value()
        if v:
            self.display.set_brightness()
        return v

    def enter_pressed(self):
        v = self.button_enter.value()
        if v:
            self.display.set_brightness()
        return v

    def esc_pressed(self):
        v = self.button_esc.value()
        if v:
            self.display.set_brightness()
        return v

    def rot(self):
        rot_enc_value = self.rot_enc.value()
        if rot_enc_value == self.last_rot_enc_value:
            return 0
        self.display.set_brightness()
        incr =  rot_enc_value - self.last_rot_enc_value   # clockwise = positive increment
        self.last_rot_enc_value = rot_enc_value
        return incr

    def shift_rot(self):
        shift_rot_enc_value = self.rot_enc.shift_value()
        if shift_rot_enc_value == self.last_shift_rot_enc_value:
            return 0
        self.display.set_brightness()
        incr =  shift_rot_enc_value - self.last_shift_rot_enc_value   # clockwise = positive increment
        self.last_shift_rot_enc_value = shift_rot_enc_value
        return incr

    async def run_menu(self, items, **kwargs):
        """ DIsplay and operate a menu, which is a list box with optional selectable and/or editable fields.

        Parameters:

            items (tuple): List of menu items.

            kwargs (dict): all other parameters passed to the Menu object. 
                Arguments not used by the Menu object are passed to the sub-menu function calls. 
                See Menu class documentation.

        Returns:

            -1: Menu was exited using ESCAPE
            (col, row, field): Menu was exited by selecting a cell or a non-editable field.   
        """
        return await Menu(self, items, **kwargs).run()

    def update_status_bar(self):
        wifi = chr(1)
        mqtt = chr(10)
        self.disp.print(f'{wifi} {mqtt}         ')

 

class Menu:

    def __init__(self, gui, 
                 items, values=({},), 
                 x0=0, y0=8, 
                 fg=Display.WHITE, bg=Display.BLACK, frame_color=Display.DARKCYAN, 
                 edit_cb=None, 
                 is_updated_cb=None, **kwargs):

        """ Displays a menu, which is implemented as a multi-column list box in which cells that can contain 
        optional selectable and editable fields.

        Columns of items are shown one at a time. 
        
        Controls in selection mode:

        - Knob rotation:
        
            - If SHIFT is pressed, cwitches between columns
            - otherwise navigate between items and fields in the current column. 

        - ENTER button or Knob push button: 
        
            - if the selected object is an editable field, the field edition mode will be started.
            - Otherwise, if the selected cell/field has a select function, that function will be called. This function can start a sub-menu.  
            - Otherwise, this method returns the selected (col, row, field) tuple. 

        - ESCAPE button: returns with the value -1

        Controls in edit mode:

        - Knob rotation:

            - if SHIFT is pressed, move position of cursor (if available)
            - otherwise, increase/decrease digit/character/field at the cursor position

        - know push button: select character and move cursor to next

        - ENTER or ESCAPE buttons: exit edit mode


        Parameters:

            items (list/tuple): ``col`` object for single column menu, or ``(col1, col2, col3)`` tuple describing multi-column menu, where
            ``col = (header, item1, item2, item3...)`` is a tuple that describes the items to be shown in each menu column. It contains:
                 - ``header``: a ``fmt_str`` (see below) used to produce the text contents of the header cell. **Cannot** be a tuple.  
                 - ``item``:is cell item, and can be one of the following:
                    - fmt_str (str or func): format string (see below) not containing any ``[]`` field. Menu closes when the cell selected.
                    - (fmt_str, (func, kwargs)): format string containing not containing any ``[]`` field. ``func(**kwargs)`` is called when cell is selected
                    - (fmt_str, field_info1, field_info2): format string containing fields, with a field_info tuple for each field     

                 - ``field_info`` describes the field:
                 
                    - ``(func, kwargs)`` . If field is not editable, ``func(**kwargs)`` is called when field is selected
                    - ``(float, float)`` sets the min/max values of an editable float field (type 'f')
                    - ``(int, int)`` sets the min/max values of an editable integer field (type 'd' or 'x')
                    - ``(str, str, ...)``: lists the possible string values that could be selected in editable string field (type 's')
                    - ``"az"``: string containg the first and last allowable characters for editable string fields (type 's') 

                 - ``fmt_str`` (string or function) is format string used to generate the item text 
                   or a function that returns such a format string. Cell text is generated using the standard ``.format`` method on this string
                   by calling ``fmt_str.format(*cell_values)`` or ``fmt_str.format(**cell_values)``

            values (list/tuple): values that are accessed by format strings or that are updated by edit boxes.
               - ``values = (col1_val, col2_val, col3_val...)``
               - ``col{n}_val: values for each column::
                  - ``col{n}_val = dict``: dict common to all rows (format string ``{key:03d}``)
                  - ``col{n}_val = list``: list common to all rows (format string ``{numeric_index:03d}``)
                  - ``col{n}_val = tuple: (row1_val, row2_val, ...)``:list or dict for each row 

            x0 (int): x coordinate of upper left corner of the list box

            y0 (int): y coordinate of upper left corner of list box

            fg (int): foreground color for frame and also text unless the format strings contain specific colors

            bg (int): background color for text unless the format strings contain specific colors

            edit_cb (func): function that is called when a new value is set on a variable by the edit box

            is_updated_cb (func): function that indicates if text needs to be updated for rows of the specified column 

            kwargs (dict): extra parameters that ar epassed to the cell/field selection functions.

        format strings:
            `hdr_str`  are format string used as follows:
                - if `hdr_str` is a function, it is first replaced by the format string returned by that function as ``hdr_str = hdr_str(values, column, row)``
                - the cell text is ``hdr_str.format(values[col])`` if ``col{n}_val`` is a dict or list
                - the cell text is ``hdr_str.format(values[col][row])`` if ``col{n}_val`` is a tuple (**not a list**).
            
            The same processing is applied to ``row_str``.

            In `row_str`, replacement fields placed between square brackets (e.g. ``"[{name:0.5s}]"``) indicate a value that can be 
            edited in an edit box. The contents of the replacement field is parsed to determine the name and type of the variable, 
            so some constraints ar eplaced in these fields to simplify parsing:

                - There should be no spaces anywhere inside the square brackets (including within the replacement field)
                - The square brackets are used to determine the position and width of the edit box after the format string has been parsed.
                - The name of the variable lies between [{ and :, e.g. "[{my_name:5d}]". 
                - A fixed-width format string preceded by ':' must be specified. Empty format field is not allowed. 
                - As the value is being edited, the updated value is stored in the appropriate numeric format in the `values` array:
                    - If ``values[col]`` is a dict, the edited value is stored in ``values[col][name]`` (i.e all editable values in all rows are stored in one dict)
                    - if ``values[col]`` is a list or tuple, the edited value is stored in ``values[col][row][name]`` (i.e each row has its own unique dict)
                    - If name is numeric, the edited value is stored in values[col][row][int(name)] if values[col][row] is a list, otherwise it is stored in values[col][int(name)]
                    - When values is updated, the callback ``edit_cb(values, row, col, name, value)`` is called with the new value. The final value is the one returned by edit_cb. 
                - The following types are allowed:
                    'd': integer values.
                        - lim = (min, max), where min and max are integers: Edits a numeric value limited between the specified range
                        - lim = (s1, s2, s3, ...): where s1, s2... are strings: choose between the specified strings, with the stored value being the index of the string
                    'f', 'n': floating point value in the range set by lim=(min, max)
                    's': string with characters limited by lim:
                        - lim="xy" where x and y are the lower and upper allowable char
                        - lim=(s1, s2, s3...) is a list of allowable strings.

        Examples:

            - Top menu: header, one column, with non-editable cells
            - Yes/no: Either a menu with ('Exit?', 'Yes', 'No'), or a menu with ('Exit?', '[Yes] [No]')
        """
        # print('Running listbox {x0=} {y0=}')
        self.gui = gui
        self.disp = gui.display
        self.x0 = x0
        self.y0 = y0
        self.fg = fg
        self.bg = bg
        self.frame_color = frame_color
        self.items = items if isinstance(items[0], tuple) else (items,)  # allow just a (header, item, item ...) tuple for single column menu
        self.values = values
        self.edit_cb = edit_cb
        self.is_updated_cb = is_updated_cb
        self.kwargs = kwargs

        # Static Edit box attributes
        self.eb_fg = self.disp.GREEN
        self.eb_bg = self.disp.BLACK

        self.disp.set_font(5)

        # List box params
        self.set_col(0)


    def set_col(self, col):
        self.col = col
        self.row = self.top_row = 1
        # identify fields in the current row
        self.ebs = self.get_field_info(self.row)
        self.eb = 0
        # Disable edit box
        self.eb_type = None # indicates if field editing is active and what type of field it is
        self.eb_pos = None # current position of the cursor in the edit field

        self.menu_width = max(self.disp.print_width(self.get_text(r)) for r in range(len(self.items[col]))) 
        self.menu_width = min(self.menu_width, (self.disp.WIDTH-self.x0-2) // self.disp.font_width) # Limit to the number of characters that fit within the frame
        # print(f'Menu width = {self.menu_width}')  # debug
        self.clear() # clear display to make sure the previous menu does not show
        # draw initial Listbox, and capture its geometry for future updates 
        self.disp_items, self.header_y = self.draw(draw_lines=True, update=True)

    def get_values(self, row):
        # print(f'{self.values=} {self.col=}')
        values = self.values[self.col]
        if isinstance(values, (dict, list)):
            return values
        else: # if a tuple
            return values[row]

    def get_format_string(self, row):
        col = self.col
        # print(f'{self.items[self.col]=}')
        fmt = self.items[col][row]
        if isinstance(fmt, tuple):
            fmt = fmt[0]
        if not isinstance(fmt, str):
            fmt = fmt(self.values, col, row)
        return fmt

    def get_text(self, row, fmt=None):
        if not fmt:
            fmt = self.get_format_string(row)

        values = self.get_values(row)
        # print(f'{fmt=} {row=} {values=}')
        if isinstance(values, dict):
            text = fmt.format(**values)
        else:
            text = fmt.format(*values)
        return text

    def get_field_info(self, row):
        """ Extract the position of each field in the selected cell along with the corresponding format string if the field is editable

        Returns:

            tuple or None:  None if no edit box, or a list of tuples ``(start_pos, end_pos, fmt)`` describing each edit box:
                - start_pos (int): position of first character after '[' in the final text
                - end_pos (int): position of last character before ']' in the final text
                - fmt (str): format string that renders the contents of an editable field. Is None if the field is not editable. 
        """
        edit_boxes = []
        fmt = self.get_format_string(row)
        text = self.get_text(row, fmt)
        start = fstart = 0
        while (fstart := fmt.find('[', fstart)) >= 0:
            fend = fmt.find(']', fstart)
            start = text.find('[', start)
            end = text.find(']', start)
            # print(f'{fstart=} {fend=} {start=} {end=}')
            fstr = fmt[fstart + 1: fend]
            if fstr.startswith('{'):
                edit_boxes.append((start + 1, end - 1, fstr))
            else:
                edit_boxes.append((start + 1, end - 1, None))

            fstart = fend + 1
            start = end + 1
        # print(f'found edit boxes {edit_boxes} in {fmt=} {text=}')
        return edit_boxes

    def clear(self, update=False):
        self.disp.clear(update=update)

    def draw(self, draw_lines=False, row=None, rows = None, update=True, clear=False):
        """ Redraws the menu, highlighting the currently selected row, selected field, or actively edited field as needed.

        Parameters:

            draw_lines (bool): if True, the edit box lines will be redrawn. Usually necessary only on the first draw.

            update (bool): If True, the frame buffer will be sent to the display after the list box is drawn

            row (int): row to redraw. If None, all rows that fit in the window are redrawn.

            rows (None or list): list of rows should be redrawn. If None, all rows that fit in the window are redrawn. 

        Returns: (n_display_lines, y_first_line) tuple where:

            - n_display_lines (int): Number if cells that were displayed below the header
            - y_first_line (int): y coordinate of the first line (just below the header separator)

            Also updates self.row_text with the text that was printed on the last selected row
        """
        disp = self.gui.display
        if clear:
            disp.clear()
            draw_lines = True

        x0 = self.x0
        y0 = self.y0
        dy = disp.font_height + 1 # vertical cell pitch (text + line separator)
        items = self.items[self.col]
        n_items = len(items)
        xx = x0 + 1
        yy = y0 + 1
        disp.set_colors(fg=self.fg, bg=self.frame_color, hl_fg=self.eb_fg, hl_bg=self.eb_bg)
        # Print header
        for text in self.get_text(0).splitlines(): 
            if draw_lines:
                disp.print(text, x=xx, y=yy, width=self.menu_width, update=False)
            yy += disp.font_height
        yh = yy # coordinate of horizontal line
        yy += 1 # skip separator line

        disp.set_colors(bg=self.bg)

        n_disp = 0
        r = self.top_row
        while yy + dy < disp.HEIGHT and r < n_items:
            if (rows is None or r in rows) and (row is None or r == row):
                hl_start = hl_stop = None  # No highlighting by default
                if r == self.row: # if row is currently selected
                    if self.ebs: # if current row has fields
                        field_info = self.ebs[self.eb]  # (start_pos, stop_pos, format_string)
                        if self.eb_type: # if field editing is active
                            # text = self.get_text(row=self.row, fmt=self.eb_fmt)
                            hl_start = field_info[0]
                            hl_stop = field_info[1]
                            if self.eb_type == 'S': # Editing list field: highligt and invert whole field
                                inv_start = field_info[0]
                                inv_stop = field_info[1]
                            else: # Editing non-list field: highlight field, invert selected character
                                inv_start = inv_stop = field_info[0] + self.eb_pos
                            # self.disp.print(text, x=self.eb_x0, y=self.eb_y0, fg=self.eb_fg, bg=self.eb_bg, inv_start=inv_start, inv_stop=inv_stop, update=False)
                        else: # Not edited field: invert field
                            # print(f'{self.ebs=}[{self.eb=}]')
                            inv_start = field_info[0]-1
                            inv_stop = field_info[1]+1
                    else: # no-field row, invert whole cell
                        inv_start = 0
                        inv_stop = None
                else: # Row not selected
                    inv_start = inv_stop = None
                text = self.row_text = self.get_text(r)
                # print(f'print {items[i]} @ ({x0+1},{yy}) th={th}')
                # disp.print(text, x=x0 + 1, y=yy, fg=self.fg, bg=self.bg, update=False, inv_start=inv_start, inv_stop=inv_stop)
                disp.print(text, x=x0 + 1, y=yy, width=self.menu_width, hl_start=hl_start, hl_stop=hl_stop, inv_start=inv_start, inv_stop=inv_stop, update=False)
            yy += dy
            r += 1
            n_disp += 1
        if draw_lines:
            x1 = min(disp.WIDTH-1, x0 + self.menu_width * disp.font_width + 1)
            y1 = yy - 1  # yy was after the final separator line
            # print(f'lines are at {x0,x1,y0,y1,yh}')
            disp.vline(x0, y0, y1, color=self.frame_color)
            disp.vline(x1, y0, y1, color=self.frame_color)
            disp.hline(x0, x1, y0, color=self.frame_color)
            yy = yh
            for j in range(n_disp + 1):
                disp.hline(x0, x1, yy, color=self.frame_color)
                yy += dy
        if update:
            disp.update()
        return n_disp, yh


    async def loop_poll(self):
        """ Called on every iteration of the GUI polling loop to check for display updates and implement a loop delay
        """ 
        # Redraw cells if needed
        if self.is_updated_cb and (updated_rows := self.is_updated_cb(self.values, self.col)):
            self.draw(rows=updated_rows)

        await asyncio.sleep(self.gui.loop_delay)

    async def run(self):
        return await self.run_list_box()

    async def run_list_box(self):
        """ Process buttons when selecting items in a list box.
        Will update:
        - self.row : currently selected item
        - self.top_row: top item is the displayed list

        Also:

        - Display brightness will be reset whenever a control is actuated

        Returns:

            int: -1: escape, 0: no action, 1: enter 

        """

        while True:

            # ROT BUTTON or ENTER is pressed
            if self.gui.rot_pressed() or self.gui.enter_pressed():
                # print(f'ENTER: {self.ebs=}')
                item = self.items[self.col][self.row]
                if self.ebs : # if the cell contains edit boxes
                    field_info = self.ebs[self.eb] # (start_pos, stop_pos, fmt)
                    field_params = item[1 + self.eb]
                    if field_info[2]: # if the field is editable
                        await self.run_edit_box()
                        self.draw()
                        continue
                    elif isinstance(field_params, tuple): # non editable field with tuple
                        meth, kwargs = field_params
                        v = await meth(**kwargs, **self.kwargs)
                        self.draw(clear=True)
                    else: # non-editable field without tuple
                        return (self.col, self.row, self.eb)  # return the selection including the field
                else: # we have no fields
                    if isinstance(item, tuple) and len(item) >=2: # if we have cell parameters
                        cell_params = item[1]
                        if isinstance(cell_params, tuple): # cell_params are a tuple 
                            meth, kwargs = cell_params
                            v = await meth(**kwargs, **self.kwargs)
                            self.draw(clear=True)
                        else: # info element not tuple, return it as 3rd param
                            v = cell_params
                        if v is not None:
                            return (self.col, self.row, v)
                    else: # there is no info, just a format string
                        v = None
                    if v is not None:
                        return (self.col, self.row, v)

            #  ESCAPE is pressed 
            if self.gui.esc_pressed():
                return None

            if incr := self.gui.shift_rot(): 
                self.set_col(max(0, min(len(self.items) - 1, self.col + incr)))

            # Update field & cell selection when the knob is rotated 
            incr = self.gui.rot()
            old_row = self.row
            old_top_row = self.top_row
            if incr:
                if incr > 0:
                    if self.ebs:
                        self.eb += incr
                        if incr :=  self.eb - len(self.ebs) + 1 > 0:
                            self.eb = len(self.ebs) - 1
                        else:
                            incr = 0    

                    # if there is any movement beyong field selection, increase the row number
                    if incr > 0:
                        self.row = min(self.row + incr, len(self.items[self.col])-1)
                        self.ebs = self.get_field_info(self.row)
                        if self.ebs: # if the cell contains edit boxes
                            self.eb = 0
                            # print(f'There are edit boxes: {self.ebs}')
                        # update top row if needed
                        if self.row >= self.top_row + self.disp_items:
                            self.top_row = self.row - self.disp_items + 1
                elif incr < 0:
                    if self.ebs:
                        self.eb += incr
                        if self.eb >= 0:
                            incr = 0
                    if incr:
                        self.row = max(1, self.row + incr)
                        self.ebs = self.get_field_info(self.row)
                        if self.ebs: # if the cell contains edit boxes
                            self.eb = len(self.ebs) - 1
                            # print(f'There are edit boxes: {self.ebs}')

                        self.top_row = min(self.top_row, self.row)
                # Redraw rows
                if self.top_row != old_top_row:
                    self.draw() # we changed top row, so redraw the whole menu
                else:
                    self.draw(rows=(old_row, self.row)) # just redraw the affected cells

            await self.loop_poll()

    async def run_edit_box(self):
        """ Edit a field

        Parameters:

            x0, y0 (int): position of the upper-left corner of the edit zone 
            fmt (str): format string used to render the edit box text
            lims (tuple): limits / parameters affecting the list box
            values (list or dict): object containing the value of the field. Is used as ``fmt.format(values)`` to render the field. 
            update_cb (func): function that sets (and optionally modify) the value of the field. Normally ``values[name] = value``. 
                Called as ``modified_new_value = update_cb(col, row, field, new_value)``

        Controls:
            - Rotary encoder: scroll through characters / options / values
            - Rotary encoder button: selects character and moves to the next
            - Button A: Backspace (deletes previous character)
            - Button B: Not used
            - Button C: ENTER: accepts and returns string

        Parameters:


        Requires fhe following instance attribute:
        - self.ebs: list of fields in the current cell
        - self.eb: index of field currently selected
        - self.row: current active row
        - self.col: current active column

        Returns:

            (str): text that was entered

        """
       # Edit box attributes

        gui = self.gui
        start, stop, fmt = self.ebs[self.eb]
        values = self.get_values(self.row)
        lims = self.items[self.col][self.row][1+self.eb]   

        # extract field name & type form format string "{name:x.xt}"
        # - name (str or int): name of the field or integer index (between '[{' and ':' in the format string)
        # - type (str): type of the variable (last character of the format string before '}]'
        colon_pos = fmt.find(':')
        type = fmt[-2]
        name = fmt[1:colon_pos]
        if name.isdigit():
            name = int(name)
        
        # indicate that the Edit box is active and with what type highlighting it should be rentered
        # - None: edit field is inactive
        # - 'S': highlight and invert whole field (a list of item is being selected)
        # - others: highlight whole field but invert only at cursor position self.eb_pos 
        self.eb_type = 'S' if type == 's' and isinstance(lims, tuple) else type

        def update_values(value):
            values[name] = self.edit_cb(self.values, self.col, self.row, name, value)
            # todo: call update functon
        def draw():
            self.draw(row=self.row)


        text = self.get_text(self.row)[start: stop + 1]
        width = len(text)
        dot_pos = text.find('.') if '.' in text else width  # position of the decimal point, if any
        self.eb_pos = width + (-2 if width -1 == dot_pos else -1) 

        draw()

        while True:
               
            if gui.enter_pressed(): # ENTER
                self.eb_type = None
                return 1
            if gui.esc_pressed(): # ESC
                self.eb_type = None
                return -1

            # Edit string character by character
            if type == 's' and isinstance(lims, str):
                text = values[name]
                if gui.shift_released(): # SHIFT button is released without rotation (i.e BACKSPACE)
                    if len(value) > 0:
                        update_values(text[:-1])
                        self.eb_pos = len(text) - 1 
                        draw()
                if gui.rot_pressed(): # Add character if encoder button is pressed
                    if self.eb_pos < width - 1:
                        self.eb_pos += 1
                        draw()
                if incr := self.shift_rot():
                    self.eb_pos = max(0, min(width-1, self.eb_pos + incr))
                    draw()

                # Update selected character when rotary encoder moves 
                if incr := self.rot():
                    # print(f'encoder={rot_enc_value}, incr={incr}')
                    text[self.eb_pos] = chr(min(max(ord(text[self.eb_pos]) + incr, ord(lim[0])), ord(lim(1))))
                    update_values(text)
                    self.draw

            # Select string from list
            elif type == 's' and isinstance(lims, tuple):
                text = values[name]
                if incr := gui.rot():
                    # print(f'{incr=} {lims=}')
                    i = max(0, min(len(lims)-1, (lims.index(text) if text in lims else 0) + incr)) 
                    update_values(lims[i])
                    draw()

            # Edit integer, hex or float, lims = (min, max)
            elif type in 'fFdnxX':
                value = values[name]
                base = 16 if (type == 'x' or type == 'X') else 10 
                if incr := gui.shift_rot():
                    exp = self.eb_pos - (self.eb_pos > dot_pos) # Position from the left skipping the decimal point
                    exp2 = max(0, min(width - 1 - (dot_pos <= width), exp + incr))
                    # print(f'{incr=} {self.eb_pos=} {dot_pos=} {exp=} {exp2=} {width=} new pos={exp2 + (exp2 >= dot_pos)}')
                    self.eb_pos = exp2 + (exp2 >= dot_pos) 
                    draw()
                if incr := gui.rot():
                    exp = dot_pos - self.eb_pos - (self.eb_pos < dot_pos) # exponent at position
                    incr = (base ** exp) * incr
                    # print(f'adding {incr=} {exp=} {base=} {self.eb_pos=} {dot_pos=}')
                    if lims[0] <= (value + incr) <= lims[1]:
                        value =  value + incr
                        value = float(value) if type == 'f' else int(value) 
                        # print(f'new value = {value}')
                        update_values(value)
                        # print(f'new value = {values[name]}')
                        draw()
            else:
                raise RuntimeError(f'Unknown edit field type {type}')

            await self.loop_poll()
