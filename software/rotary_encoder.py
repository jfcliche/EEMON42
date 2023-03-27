class RotaryEncoder():
    """ Creates a rotary encoder decoding object connected to `pin_a` and `pin_b` and sets the interrupt on these pins
    to continuously keep track of the encoder movements.

    The rotary encoder sequence for the two encoder pins is 11, 01, 00, 10, 11 for clockwise rotation, 
    and the sequence is in the opposite direction for counterclockwise rotation.
    The detent (stable state) is on 11.

    The encoder position is stored in `self._value` and is accessed with `self.value()`. 

    The decoding is performed by the Pin interrupt handler `process_state()` which should be called when the state of
    either of the encoder pin changes.

    Principle of operation: each each time we call `process_state()`, we increment the `sub_incr` counter by the direction of
    movement (+1, -1) obtained from the previous and current encoder state. If the current encoder lands in its detent
    position ('11'), we add `sub_incr//4` to the counter, i.e. it will add +1 or -1 only if we have detected +4 or -4
    subincrements since the last detent landing.

    Invalid transition (skipping 2 encoder phases states) are problematic as we can't tell which direction we went. We
    try to salvage some of those those events and increase our accuracy by keeping track of these missed counts and
    adding later with the direction of the other valid increments. We don't use the missed counts if increment count is
    null. Of course this won't help if we miss too many states between `process_state()` calls.

    Parameters:

        pin_a, pin_b (machine.Pin): Pins connected to the rotary encoder.
            These pins must already have been configured properly.

        irq_wrapper (fn): If specified, wraps the Pin interrupt handler that tracks
            encoder movements. 

        verbose (int): verbose level for testing

    """

    # Direction table: maps the previous and current encoder pin values (Aprev Bprev Acur Bcur) to the direction of the
    # rotation. Values in parentheses indicate invalid changes (2 phase jumps = > ambiguous sign).
    dir_table = [
        0, -1, 1, (0), 1, 0, (0), -1,  # 0000, 0001, 0010, 0011, 0100, 0101, 0110, 0111
        -1, (0), 0, 1, (0), 1, -1, 0  # 1000, 1001, 1010, 1011, 1100, 1101, 1110, 1111
        ]
    def __init__(self, pin_a, pin_b, irq_wrapper=None, verbose=2):
        self.pin_a = pin_a
        self.pin_b = pin_b
        self._value = 0  # final encoder position 
        self.prev_pins = 0b11  # stores the previous encoder pin state
        self.sub_incr = 0  # tracks cumulative phase increments between detents
        self.invalid = 0  # number of invalid state changes
        self.verbose = verbose

        # Set rotary encoder pins IRQ callback to the encoder handler so it can keep track of pin level changes. 
        # Use process_state() unless a custom handler is provided 

        irq_handler = irq_wrapper(self.process_state) if irq_wrapper else self.process_state;
        self.pin_a.irq(irq_handler) 
        self.pin_b.irq(irq_handler)

    def value(self):
        return self._value

    def reset(self):
        self._value = 0

    def process_state(self, pin):
        """ Encoder state processing method, meant to be used as an pin interrupt routine.

        Parameters:

            pin (machine.Pin): Pin that caused the interrupt, as passed by the pin interrupt handler to *both* encoder pins. This parameter is not used since we already know the two pins we need to probe.

        """
        pins = (self.pin_a.value() << 1) | self.pin_b.value() # get the two encoder pin values
        # Do nothing if the encoder pins have not changed. This happens often, 
        # so let's save some CPU cycles by stopping right here. 
        if pins == self.prev_pins: 
            return
        incr = self.dir_table[(self.prev_pins << 2) | pins] # get direction of rotation from previous and current state
        self.sub_incr += incr  # increment with direction between 
        self.invalid += not incr # count the number of invalid transition; we'll handle them later in the final detent tally
        if self.verbose:
            if self.verbose > 1:
                print(f'pins {self.prev_pins:02b}=>{pins:02b}, dir={self.dir_table[(self.prev_pins << 2) | pins]}, sub_incr={self.sub_incr}, invalid={self.invalid}')
            if not incr: 
                print(f'Missed a count!')
        self.prev_pins = pins
        old_counter = self._value  # debug
        if pins == 0b11: # we landed on the detent position. Assess our increment.
            # add sub_incr/4, after adding invalid counts as jumps of 2 in the direction of the valid ones
            self._value += (self.sub_incr + (self.invalid << 1 if self.sub_incr > 0 else -self.invalid << 1 if self.sub_incr < 0 else 0)) >> 2
            self.sub_incr = self.invalid = 0 # start anew
        if self.verbose and self._value != old_counter: 
            print(f'value={self._value}')
