from eemon42 import EEMON42
import utime
import __main__ 

e = EEMON42()
d = e.display

def run():
    e.run()

print('Press button C while booting to start the GUI')
if not e.pin_cs5_button_c.value():
	print('Starting GUI')
	run()


def timeit(fn, n=1000):
	t0 = utime.ticks_us()
	for _ in range(n):
		fn()
	t1 = utime.ticks_us()
	print(f'Function took {(t1-t0)/n:0.1f} us / iteration')

# Make attributes from this module accessible directly in the __main__ module
import main
for k,v in main.__dict__.items():
	if not k.startswith('_'):
		setattr(__main__, k, v)

# e.run() 