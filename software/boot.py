# boot.py -- run on boot-up
# a=10
# from e42_spi import SPI_with_CS
# def spi_test():
# from ade7816 import ADE7816, test
# import time
# from eemon42 import EEMON42
# e = EEMON42()
# print('EEMON42')
# print('Press button C while booting to start the GUI')
# if not e.pin_cs5_button_c.value():
# 	print('Starting GUI')
# 	e.run()
# m = e.emon[0]
# m.init()
a=1
# spi, p, rot = test(1000)
 
# def shift_test():
# 	N=1000000
# 	x=3
# 	print("Bit shift:")
# 	start = time.time_ns()
# 	for i in range(N):
# 	    x<<1
# 	end = time.time_ns()
# 	print(end - start)

# 	print("Multiplication by 2:")
# 	start = time.time_ns()
# 	for i in range(N):
# 	    x*2
# 	end = time.time_ns()
# 	print(end - start)

# 	print("Multiplication by 3:")
# 	start = time.time_ns()
# 	for i in range(N):
# 	    x*3
# 	end = time.time_ns()
# 	print(end - start)

# def timeit(f, *args, **kwargs):
#     t = time.ticks_us()
#     result = f(*args, **kwargs)
#     delta = time.ticks_diff(time.ticks_us(), t)
#     print(f'Time = {delta/1000:6.3f}ms')
#     return result

# cmd = bytearray(2)
# def fn1(x):
#     cmd[0]=x>>8; cmd[1]=x & 0xff;

# def fn2(x):
#     cmd[0:1] = x.to_bytes(2,'big')
