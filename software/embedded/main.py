#!/usr/bin/env -S uv run

import sys
import os

# If we are not running native micropython, enable the paths to the emulated modules
if sys.implementation.name != 'micropython':
    _embedded_dir = os.path.dirname(os.path.abspath(__file__))
    _software_dir = os.path.normpath(os.path.join(_embedded_dir, "..")) 
    _sim_dir = os.path.join(_software_dir, "sim")  
    sys.path.insert(0, _sim_dir)  # sim dir modules will shadow the software dir modules
    sys.path.insert(0, _software_dir)  # include root dir to allow simulated modules to access embedded modules through absolute path imports
    print(f'{_sim_dir=}')
    sys.pycache_prefix = os.path.join(_sim_dir, ".pycache")  #  put all .pyc in sim's .pycache so we don't pollute the embedded folder
    print('This is a ***simulated*** EEMON42')

from eemon42 import EEMON42


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
