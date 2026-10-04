""" Defines the EEMON42 menus
"""

import gui
from display import KF, CB, CC, WF  # color codes for blacK/Cyan/White Foreground/Background

async def run_main_menu(gui, app):
    """ Runs the main menu.

    The main menu runs in an infinite loop. It cannot be exited unless the task is cancelled.

    Parameters:

        gui (GUI): GUI instance that will be used to render and operate the menus.
    """
    print('Starting Main menu task')

    items = (
        f"{KF+CB}MAIN MENU",
        ("Monitor", (run_monitor, dict(gui=gui, app=app))),
        ("Calibrate", (run_cal_menu, dict(gui=gui, app=app))),
        ("Network", (run_network_menu, dict(gui=gui, app=app)))
    )

    try:
        while True:
            item = await gui.run_menu(items)
            print(f'Selected top menu item {item}')
    except BaseException as e:
        print(f'Main menu task generated the following exception {e!r}')
        raise
    finally:
        print('Main menu task is terminated')

async def run_monitor(gui, app):
    return 0

async def run_cal_menu(gui, app):
    """ Opens the calibration listbox
    """
    emon = app.emon  # list of energy monitor chip objects
    values = []
    items = []
    chan = []
    last_update = []  # last update number for each chip
    INT24_RANGE = (-2**23, 2**23-1)
    UINT24_RANGE = (0, 2**24-1)

    # values = [NS(emon = e, chip=e.index,  config=e.config) 
    #           for e in emon for j in range(6)]

    # items = [col, col, ...]
    # col = (header_text, row, row ...)
    # header_text = str or lambda(col) returning a str 
    # row = (row_text, eb_format, eb_var)

    def hdrv(values, col, row):
        """ Generate the format string for the header cell of each column (channel) """
        # v = values[col]
        e, chip,cch,ch  = chan[col]
        # print(f'{e.current}{e.active_power} {cch}') 
        s = (f"{WF}CAL CH{chip*6}-{chip*6+5} ({chip})\n"
             f"{KF}V={e.voltage:5.1f}V")
            # f"{KF+CB}I={e.current[cch]:7.3f}A\n" +\
            # f"{KF+CB}P={e.active_power[cch]:7.3f}W\n"
        return s


    # Define the listbox column. All columns are identical, but are parametrized by channel 
    colv = ( 
        # Column header
        hdrv,
        # Row items
        ("Vgain=[{v_gain:6.4f}]", (0,1)), 
        ("VTgain=[{vt_cal:6.4f}]", (0,1)), 
        ("VGAIN=[{VGAIN:+06x}]", INT24_RANGE), 
        ("VRMSOS=[{VRMSOS:7d}]", INT24_RANGE), 
        ("APNOLOAD=[{APNOLOAD:7d}]", INT24_RANGE), 
        ("VARNOLOAD=[{VARNOLOAD:7d}]", INT24_RANGE), 
        # ("[{vgain:4.1f}]", (0,100)),
        # f"{KF+CB}=>{CC} [Yes] [No]",
        # ("Usecal=[{usecal:3s}]", ('Yes', 'No')), 
        # ("Wattcal=[{wattcal:4.1f}]", (-10, 3.33)), 
        # ("Ncyc=[{cyc:3d}]", (0, 255)), 
        # (lambda v,c,r: f"Vrms={v[c].emon.voltage} x=[{{something:1d}}]", (0,1)), 
        # ("hex=[{hex:06x}]", (0, 255)),  # Hex 
    )
    def hdri(values, col, row):
        """ Generate the format string for the header cell of each column (channel) """
        # v = values[col]
        e, chip,cch,ch  = chan[col]
        # print(f'{e.current}{e.active_power} {cch}') 
        s = f"{WF}CAL CH{ch} ({chip}.{cch})\n" +\
            f"{KF}V={e.voltage:5.1f}V\n" +\
            f"{KF}I={e.current[cch]:7.3f}A\n" +\
            f"{KF}P={e.active_power[cch]:7.3f}W\n"
        return s


    coli = ( 
        # Column header
        hdri,
        # Row items
        ("CTgain=[{ct_cal:6.4f}]", (0,1)), 
        ("Wgain=[{energy_cal:6.4f}]", (0,1)), 
        ("IGAIN=[{IGAIN:+07X}]", INT24_RANGE), 
        ("IRMSOS=[{IRMSOS:+07X}]", INT24_RANGE), 
        ("WGAIN=[{WGAIN:+07X}]", INT24_RANGE), 
        ("WATTOS=[{WATTOS:+07X}]", INT24_RANGE), 
        ("VARGAIN=[{VARGAIN:+07X}]", INT24_RANGE), 
        ("VAROS=[{VAROS:+07X}]", INT24_RANGE), 
        ("PCF=[{PCF_COEFF:+07X}]", UINT24_RANGE), 

        # ("[{vgain:4.1f}]", (0,100)),
        # f"{KF+CB}=>{CC} [Yes] [No]",
        # ("Usecal=[{usecal:3s}]", ('Yes', 'No')), 
        # ("Wattcal=[{wattcal:4.1f}]", (-10, 3.33)), 
        # ("Ncyc=[{cyc:3d}]", (0, 255)), 
        # (lambda v,c,r: f"Vrms={v[c].emon.voltage} x=[{{something:1d}}]", (0,1)), 
        # ("hex=[{hex:06x}]", (0, 255)),  # Hex 
    )

    for chip, e in enumerate(emon):
        # print(f'Adding {e.config=}')
        values.append(e.config)
        chan.append((e, chip, None, None))
        items.append(colv)
        last_update.append(e.update_number)
        for cch in range(6):
            chan.append((e, chip, cch, chip*6+cch))
            items.append(coli)
            values.append(e.config.channels[cch])

    # updated_rows = bytes(not isinstance(item, str) for item in col) # we always update the rows that have a dynamic string

    def edit_cb(values, col, row, name, new_value):
        """ Update the energy monitor parameter when the value in the corresponding edit box is changed. """
        e, chip, cch,ch  = chan[col]
        if name.isupper(): # all-uppercase names are assumed to be EMON chip register names
            e.write_reg(name, new_value, cch)  # cch is None for chip-wide values, otherwise will be appended to name
        return new_value

    def update_cb(values, col):
        """ Return a vector indicating which rows of the specified column needs to be re-rendered. 
        Returns None if there are no changes. """
        e, chip, cch, ch  = chan[col]
        if e.update_number == last_update[chip]:
            return None
        last_update[chip] = e.update_number
        return [row for row,item in items[col] if not isinstance(item, str)]

    value =  await gui.run_menu(items, values=values, edit_cb=edit_cb, is_updated_cb=update_cb)
    print(f'Cal menu: selected {value}')
    return value

async def run_network_menu(gui, app):
    """ Opens the network menu
    """
    nic = app.nic
    def mac():
        return app.nic.config("mac").hex(':') if app.nic else "??:??:??:??:??:??"
    def ifinfo(n):
        return app.nic.ifconfig()[n] if app.nic else '?.?.?.?'

    col = (
        "NETWORKING",
        f'ID= {app.client_id}',
        lambda *args: f'MAC={mac():17s}',
        lambda *args: f'IP= {ifinfo(0):15s}',
        lambda *args: f'MSK={ifinfo(1):15s}',
        lambda *args: f'GW= {ifinfo(2):15s}',
        lambda *args: f'NS= {ifinfo(3):15s}',
    )
    return await gui.run_menu(col)
