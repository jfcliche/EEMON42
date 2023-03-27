STA_IF = 0

class WLAN:
	def __init__(self, *args, **kwargs):
		self.connected = False

	def isconnected(self):
		return self.connected

	def active(self, state):
		pass

	def connect(self, *args, **kwargs):
		self.connected = True

	def ifconfig(self):
		return "simulated WiFi"

