class Pin:
	OUT = 1
	IN = 2
	PULL_UP = 3
	def __init__(self, *args, **kwargs):
		self._value = 0
	def init(self, *args, **kwargs):
		pass
	def value(self, val=None):
		if val is not None:
			self._value = val
		return self._value
	def irq(self, fn):
		pass

class SPI:
	def __init__(self, *args, **kwargs):
		pass

	def deinit(self, *args, **kwargs):
		pass

	def write(self, *args, **kwargs):
		pass

	def readinto(self, *args, **kwargs):
		pass



def unique_id():
	return b'beefface'