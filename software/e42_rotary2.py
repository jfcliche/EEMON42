class RotaryEncoder():
	""" Implement rotary encoder decoding.

	The rotary encoder sequence for the two encoder pins is 11, 01, 00, 10, 11 for clockwise rotation, 
	and the sequence is in the opposite direction for counterclockwise rotation.
	The detent (stable state) is on 11.

	The encoder position is stored in `self.counter`. We increment or
	decrement the counter when the last 3 bit patterns of the encoder end
	up in the final detent position.

	Parameters:

		pin_a, pin_b (machine.Pin): Pins connected to the rotary encoder.
			These pins must already have been configured properly, and an
			interrupt pointing to `process_state` must have been set on both pins.
		"""
	def __init__(self, pin_a, pin_b):
		self.pin_a = pin_a
		self.pin_b = pin_b
		self.counter = 0
		self.state = 0b111111

	def process_state(self, pin):
		""" Encoder state processing method, meant to be used as an pin interrupt routine.

		Parameters:

			pin (machine.Pin): Pin that caused the interrupt, as passed by the pin interrupt handler. This is not used.

		"""
		pins = (self.pin_a.value() << 1) | self.pin_b.value() # get the two encoder pin values
		if pins == self.state & 0b11: # do nothing if they have not changed
			return
		self.state = ((self.state & 0b1111) << 2) | pins  # shift left the 2 bits into the state register
		old_counter = self.counter  # debug
		if self.state == 0b001011: # last 3 values are the clockwise sequence ending on a detent (00, 10, 11)
			self.counter += 1
		elif self.state == 0b000111: # last 3 values are the counterclockwise sequence ending on a detent (00, 01, 11)
			self.counter -= 1
		if self.counter != old_counter: # debug
			print(f'counter={self.counter}')
