import uuid

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

	def disconnect(self, *args, **kwargs):
		self.connected = False

	def ifconfig(self):
		return "simulated WiFi"

	def config(self, key):
		if key == 'mac':
			return uuid.getnode().to_bytes(6,'big')  

