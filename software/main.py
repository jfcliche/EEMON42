#!/usr/bin/env python 

import sys
import os
import time
import asyncio

is_micropython = sys.implementation.name == 'micropython'

# If we are not running micropython, we are presumably running on a computer, so se setup the python path for running simulated modules
if not is_micropython:
    _software_dir = os.path.dirname(os.path.abspath(__file__))
    _root_dir = os.path.normpath(os.path.join(_software_dir, "..")) # include root dir to allow simulated modules to access embedded modules through absolute path imports
    _sim_dir = os.path.normpath(os.path.join(_root_dir, "sim")) # sim dir modules will shadow the software dir modules
    sys.path.insert(0, _sim_dir)
    sys.path.insert(0, _root_dir)
    print('This is a ***simulated*** EEMON42')


from eemon42 import EEMON42

# import hass


print(f'Running {os.getcwd()}/main.py')


print('Hold button C while booting to start the GUI')

print(f'Creating EEMON42 object from main')
e = EEMON42()
d = e.display

def run():
    e.run()


def f():
    import asyncio
    e.load_config()
    asyncio.run(e.wifi_connection())


# Make attributes from this module accessible directly in the __main__ module

if __name__ == '__main__' or not e.pin_cs5_button_c.value():
    e.run()
else:
    # Export variables defined in this module to the interpreter namespace 
    # to facilitate interactive debugging
    print('Copying "main" module attributes to current context for interactive debugging')
    import __main__  # The interpreter namespace is __main__
    for k,v in list(locals().items()):
        if not k.startswith('_'):
            setattr(__main__, k, v)
