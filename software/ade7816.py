import time

# import pyftdi.spi
from machine import Pin

def BIT(x):
    return 1 << x

class ADE7816:
    """ Class allowing operation of the ADE7816 split-phase 6-channel energy monitor chip through a SPI interface.
    """
    STATUS0_LENERGY = BIT(5)

    REGS = {
        'VGAIN' : (0x4380, '32ZPSE'),  #0x000000 Voltage gain adjustment.
        'IAGAIN' : (0x4381, '32ZPSE'),  #0x000000 Current Channel A current gain adjustment.
        'IBGAIN' : (0x4382, '32ZPSE'),  #0x000000 Current Channel B current gain adjustment.
        'ICGAIN' : (0x4383, '32ZPSE'),  #0x000000 Current Channel C current gain adjustment.
        'IDGAIN' : (0x4384, '32ZPSE'),  #0x000000 Current Channel D current gain adjustment.
        'IEGAIN' : (0x4385, '32ZPSE'),  #0x000000 Current Channel E current gain adjustment.
        'IFGAIN' : (0x4386, '32ZPSE'),  #0x000000 Current Channel F current gain adjustment.
        'DICOEFF' : (0x4388, '32ZPSE'),  #0x000000 Register used in the digital integrator algorithm.
        'HPFDIS' : (0x4389, '32ZPSE'),  #0x000000 Disables the high-pass filter for all channels.
        'VRMSOS' : (0x438A, '32ZPSE'),  #0x000000 Voltage rms offset.
        'IARMSOS' : (0x438B, '32ZPSE'),  #0x000000 Current Channel A current rms offset.
        'IBRMSOS' : (0x438C, '32ZPSE'),  #0x000000 Current Channel B current rms offset.
        'ICRMSOS' : (0x438D, '32ZPSE'),  #0x000000 Current Channel C current rms offset.
        'IDRMSOS' : (0x438E, '32ZPSE'),  #0x000000 Current Channel D current rms offset.
        'IERMSOS' : (0x438F, '32ZPSE'),  #0x000000 Current Channel E current rms offset.
        'IFRMSOS' : (0x4390, '32ZPSE'),  #0x000000 Current Channel F current rms offset.
        'AWGAIN' : (0x4391, '32ZPSE'),  #0x000000 Channel A active power gain adjust.
        'AWATTOS' : (0x4392, '32ZPSE'),  #0x000000 Channel A active power offset adjust.
        'BWGAIN' : (0x4393, '32ZPSE'),  #0x000000 Channel B active power gain adjust.
        'BWATTOS' : (0x4394, '32ZPSE'),  #0x000000 Channel B active power offset adjust.
        'CWGAIN' : (0x4395, '32ZPSE'),  #0x000000 Channel C active power gain adjust.
        'CWATTOS' : (0x4396, '32ZPSE'),  #0x000000 Channel C active power offset adjust.
        'DWGAIN' : (0x4397, '32ZPSE'),  #0x000000 Channel D active power gain adjust
        'DWATTOS' : (0x4398, '32ZPSE'),  #0x000000 Channel D active power offset adjust.
        'EWGAIN' : (0x4399, '32ZPSE'),  #0x000000 Channel E active power gain adjust.
        'EWATTOS' : (0x439A, '32ZPSE'),  #0x000000 Channel E active power offset adjust.
        'FWGAIN' : (0x439B, '32ZPSE'),  #0x000000 Channel F active power gain adjust.
        'FWATTOS' : (0x439C, '32ZPSE'),  #0x000000 Channel F active power offset adjust.
        'AVARGAIN' : (0x439D, '32ZPSE'),  #0x000000 Channel A reactive power gain adjust.
        'AVAROS' : (0x439E, '32ZPSE'),  #0x000000 Channel A reactive power offset adjust.
        'BVARGAIN' : (0x439F, '32ZPSE'),  #0x000000 Channel B reactive power gain adjust.
        'BVAROS' : (0x43A0, '32ZPSE'),  #0x000000 Channel B reactive power offset adjust.
        'CVARGAIN' : (0x43A1, '32ZPSE'),  #0x000000 Channel C reactive power gain adjust.
        'CVAROS' : (0x43A2, '32ZPSE'),  #0x000000 Channel C reactive power offset adjust.
        'DVARGAIN' : (0x43A3, '32ZPSE'),  #0x000000 Channel D reactive power gain adjust.
        'DVAROS' : (0x43A4, '32ZPSE'),  #0x000000 Channel D reactive power offset adjust.
        'EVARGAIN' : (0x43A5, '32ZPSE'),  #0x000000 Channel E reactive power gain adjust.
        'EVAROS' : (0x43A6, '32ZPSE'),  #0x000000 Channel E reactive power offset adjust.
        'FVARGAIN' : (0x43A7, '32ZPSE'),  #0x000000 Channel F reactive power gain adjust.
        'FVAROS' : (0x43A8, '32ZPSE'),  #0x000000 Channel F reactive power offset adjust.
        'WTHR1' : (0x43AB, '32ZP'),  #0x000000 Most significant 24 bits of the WTHR[47:0]
        'WTHR0' : (0x43AC, '32ZP'),  #0x000000 Least significant 24 bits of the WTHR[47:0]
        'VARTHR1' : (0x43AD, '32ZP'),  #0x000000 Most significant 24 bits of the VARTHR[47:0]
        'VARTHR0' : (0x43AE, '32ZP'),  #0x000000 Least significant 24 bits of the VARTHR[47:0]
        'APNOLOAD' : (0x43AF, '32ZP'),  #0x000000 No load threshold in the active power datapath.
        'VARNOLOAD' : (0x43B0, '32ZPSE'),  #0x000000 No load threshold in the reactive power
        'PCF_A_COEFF' : (0x43B1, '32ZPSE'),  #0x000000 Phase calibration coefficient for Channel A.
        'PCF_B_COEFF' : (0x43B2, '32ZPSE'),  #0x000000 Phase calibration coefficient for Channel B.
        'PCF_C_COEFF' : (0x43B3, '32ZPSE'),  #0x000000 Phase calibration coefficient for Channel C. 
        'PCF_D_COEFF' : (0x43B4, '32ZPSE'),  #0x000000 Phase calibration coefficientfor Channel D. 
        'PCF_E_COEFF' : (0x43B5, '32ZPSE'),  #0x000000 Phase calibration coefficient for Channel E. 
        'PCF_F_COEFF' : (0x43B6, '32ZPSE'),  #0x000000 Phase calibration coefficient for Channel F.
        'VRMS' : (0x43C0, '32ZP'),  #N/A Voltage rms value.
        'IARMS' : (0x43C1, '32ZP'),  #N/A Current Channel A current rms value.
        'IBRMS' : (0x43C2, '32ZP'),  #N/A Current Channel B current rms value.
        'ICRMS' : (0x43C3, '32ZP'),  #N/A Current Channel C current rms value.
        'IDRMS' : (0x43C4, '32ZP'),  #N/A Current Channel D current rms value.
        'IERMS' : (0x43C5, '32ZP'),  #N/A Current Channel E current rms value.
        'IFRMS' : (0x43C6, '32ZP'),  #N/A Current Channel F current rms value.
        'RUN' : (0xE228, '16U'),  #This register starts and stops the DSP. 16-bit, R/W, unsigned
        'AWATTHR' : (0xE400, '32S'),  #Channel A active energy accumulation.
        'BWATTHR' : (0xE401, '32S'),  #Channel B active energy accumulation.
        'CWATTHR' : (0xE402, '32S'),  #Channel C active energy accumulation.
        'DWATTHR' : (0xE403, '32S'),  #Channel D active energy accumulation.
        'EWATTHR' : (0xE404, '32S'),  #Channel E active energy accumulation.
        'FWATTHR' : (0xE405, '32S'),  #Channel F active energy accumulation.
        'AVARHR' : (0xE406, '32S'),  #Channel A reactive energy accumulation.
        'BVARHR' : (0xE407, '32S'),  #Channel B reactive energy accumulation.
        'CVARHR' : (0xE408, '32S'),  #Channel C reactive energy accumulation.
        'DVARHR' : (0xE409, '32S'),  #Channel D reactive energy accumulation.
        'EVARHR' : (0xE40A, '32S'),  #Channel E reactive energy accumulation.
        'FVARHR' : (0xE40B, '32S'),  #Channel F reactive energy accumulation.
        'IPEAK' : (0xE500, '32U'),  #Current peak register.
        'VPEAK' : (0xE501, '32U'),  #Voltage peak register.
        'STATUS0' : (0xE502, '32U'),  #Interrupt Status Register 0.
        'STATUS1' : (0xE503, '32U'),  #Interrupt Status Register 1.
        'OILVL' : (0xE507, '32ZP'),  #0xFFFFFF Overcurrent threshold.
        'OVLVL' : (0xE508, '32ZP'),  #0xFFFFFF Overvoltage threshold.
        'SAGLVL' : (0xE509, '32ZP'),  #0x000000 Voltage sag level threshold.
        'MASK0' : (0xE50A, '32U'),  #Interrupt Enable Register 0.
        'MASK1' : (0xE50B, '32U'),  #Interrupt Enable Register 1.
        'IAWV_IDWV' : (0xE50C, '32SE'),  #N/A Instantaneous Current Channel A and
        'IBWV_IEWV' : (0xE50D, '32SE'),  #N/A Instantaneous Current Channel B and
        'ICWV_IFWV' : (0xE50E, '32SE'),  #N/A Instantaneous Current Channel C and
        'VWV' : (0xE510, '32SE'),  #N/A Instantaneous voltage.
        'CHECKSUM' : (0xE51F, '32U'),  #Checksum verification (see the Checksum
        'CHSTATUS' : (0xE600, '16U'),  #Channel peak register.
        'ANGLE0' : (0xE601, '16U'),  #Time Delay 0 (see the Angle
        'ANGLE1' : (0xE602, '16U'),  #Time Delay 1 (see the Angle
        'ANGLE2' : (0xE603, '16U'),  #Time Delay 2 (see the Angle
        'PERIOD' : (0xE607, '16U'),  #Line period.
        'CHNOLOAD' : (0xE608, '16U'),  #Channel no load register.
        'LINECYC' : (0xE60C, '16U'),  #Line cycle accumulation mode count.
        'ZXTOUT' : (0xE60D, '16U'),  #Zero-crossing timeout count.
        'COMPMODE' : (0xE60E, '16U'),  #Computation mode register.
        'GAIN' : (0xE60F, '16U'),  #PGA gains at ADC inputs (see Table 22).
        'CHSIGN' : (0xE617, '16U'),  #Power sign register.
        'CONFIG' : (0xE618, '16U'),  #Configuration register.
        'MMODE' : (0xE700, '8U'),  #Measurement mode register.
        'ACCMODE' : (0xE701, '8U'),  #Accumulation mode register.
        'LCYCMODE' : (0xE702, '8U'),  #Line accumulation mode.
        'PEAKCYC' : (0xE703, '8U'),  #Peak detection half line cycles.
        'SAGCYC' : (0xE704, '8U'),  #Sag detection half line cycles.
        'HSDC_CFG' : (0xE706, '8U'),  #HSDC configuration register.
        'VERSION' : (0xE707, '8U'),  #of die.
        'CONFIG2' : (0xEC01, '8U'),  #Configuration register (see Table 29).
        'DUMMY' : (0xEBFF, '8U'),  # used For dummy writes at startup. has no effect.
    }   

    FORMATS = {
        # name: (byte_length, bit_length, is_signed)
        '32U': (4, 32, False),  # unsigned 32-bit value
        '32S': (4, 32, True),  # signed 32-bit value
        '32SE': (4, 32, True), # signed 24-bit value sign-extended to 32 bits
        '32ZP': (4, 32, False), # unsigned 24-bit value zero-padded to 32 bits
        '32ZPSE': (4, 28, False), # signed 24-bit sign extended to 28 bits and then zero-padded to 32 bits
        '16U': (2, 16, False),  # unsigned 16-bit value
        '16S': (2, 16, True),  # signed 16-bit value
        '8U': (1, 8, False),  # unsigned 8-bit value
        '8S': (1, 8, True),  # signed 8-bit value
        }

    CHANNELS = 'ABCDEF'

    def __init__(self, spi, cs_pin, irq_pin, irq_wrapper, index):
        """ Create the energy monitor object, but don't initialize the hardware yet.

        Parameters:

            spi (SPI_with_CS): instance of the SPI_with_CS interface object

            cs_pin (machine.Pin): Pin that controls the display chip select line. Mode must be set by the user.

            index (int): energy monitor number
        """

        self.spi = spi
        self.cs_pin = cs_pin
        self.irq_pin = irq_pin
        self.irq_wrapper = irq_wrapper
        self.cmd = bytearray(3+4)  # command & data bytes
        self.rx_buf = bytearray(4) # reply word
        self.index = index

        self.ct_cal = 0.312/20 # Vrms/Irms # SCT-013 = 1Vrms/20Irms,100 ohm burden, including divider network and its input impedance, Vout=0.436Vp/20Arms, 
        # irq_handler = irq_wrapper(self.irq_handler) if irq_wrapper else self.irq_handler;
        # self.irq_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.irq_handler) 
        self.v_gain = 499/(499+21500)
        self.vt_cal = 10.8/120 # output volts / input volts (use no-load output voltage value since we are far from full load)
        self.t0 = time.time_ns()
        self.total_energy = 0
        self.energy_cal = 1.22155 # J/lsb
        self.energy_count = 0


    def init(self):
        """ Initialize the energy monitor chip
        """
        print(f'Initializing ADE7816 Energy monitor {self.index}')


        # make sure we are in SPI mode by issuing 3 dummy writes as recommended by datasheet. 
        # otherwise we will be in I2C mode
        for _ in range(3):
            self.write_reg('DUMMY',0)
        # lock the SPI serial port choice by writing any value to CONFIG2
        self.write_reg('CONFIG2', 0b00000000) # 


        # Test communications with the chip by writing and reading back values in a register
        for v in (0x00000000, 0x10101010, 0x55555555, 0xDDDDDDDD, 0xFFFFFFFF, 0):
                self.write_reg('MASK0', v) 
                vv = self.read_reg('MASK0') 
                if v != vv:
                    # print(f'EMON{self.index}: SPI Communication error. Wrote {v:08X}, read {vv:08x}.')
                    raise RuntimeError(f'EMON{self.index}: SPI Communication error. Wrote {v:08X}, read {vv:08x}.')
        # set active energy integration threshold
        # A value should be 0x000002_000000 for standard operation. The update rate of the WATTHR rehister is then just below the max of 8 kHz for full scale.  
        self.write_reg('WTHR1', 0x000002)
        self.write_reg('WTHR0', 0x000000)
        # set reactive energy integration threshold
        self.write_reg('VARTHR1', 0x000002)
        self.write_reg('VARTHR0', 0x000000)
        self.write_reg('LINECYC', 120) # capture data every second
        self.write_reg('LCYCMODE', 0b00001011) # Enable zero crossing detector and line accumulation mode

        self.write_reg('MASK0', self.STATUS0_LENERGY) 
        self.write_reg('MASK1', 0 ) 
        # Clear IRQ0
        status0 = self.read_reg('STATUS0')        
        self.write_reg('STATUS0', status0) 
        # Clear IRQ1
        status1 = self.read_reg('STATUS1')        
        self.write_reg('STATUS1', status1) 

        PCF_CAL_VALUE = 0x401235 # 0x401235 for 60 Hz, 0x 400ca4 for 50 Hz
        for ch in self.CHANNELS:
            self.write_reg(f'PCF_{ch}_COEFF', PCF_CAL_VALUE)  

        # repeat last write to ensure the value propagates through the pipeline, as requested in the datasheet
        for i in range(2):
            self.write_reg(f'PCF_{self.CHANNELS[-1]}_COEFF', PCF_CAL_VALUE)

        self.start_dsp()
        self.start_dsp()
        self.start_dsp()
        self.t0 = time.time_ns()
        
    def irq_handler(self, pin):
        status0 = self.read_reg('STATUS0')        
        status1 = self.read_reg('STATUS1')        
        lenergy_irq = bool(status0 & self.STATUS0_LENERGY)
        dt = (time.time_ns() - self.t0) / 1e9
        if True or lenergy_irq:
            energy = self.read_reg('AWATTHR') * self.energy_cal
            self.total_energy += energy
            self.energy_count += 1       
            # print(f'{dt:.3f} IRQ={pin()} LENERGY={lenergy_irq} EMON{self.index}: status0={status0:024b}, status1={status1:016b}, AWATTHR={energy} W, tot = {self.total_energy/3600} kWh')
            print(f'{dt:.3f} EMON{self.index}: {energy} Ws, tot = {self.total_energy/3600} Wh')
            if lenergy_irq: # clear interrupt only if set, otherwise we might cler an interrupt that occured since we last read and we'll miss it
                self.write_reg('STATUS0', self.STATUS0_LENERGY)
        return lenergy_irq
        # Clear IRQ1
        # self.write_reg('STATUS0', status0) 
        # self.write_reg('STATUS1', status1) 



    def read_reg(self, name):
        """Reads a register

        Parameters:

            name (str): name of register to read

        Returns:

            int: value that was read. Will be a signed or unsigned value depending on the register number format. 
        """

        (addr, fmt) = self.REGS[name]
        (byte_length, bit_length, signed) = self.FORMATS[fmt]
        cmd = self.cmd
        rx_buf = self.rx_buf
        cmd[0] = 1
        cmd[1] = addr >> 8
        cmd[2] = addr & 0xff
        self.spi.exchange(self.cs_pin, memoryview(cmd)[:3], memoryview(rx_buf)[:byte_length])
        value = int.from_bytes(rx_buf[:byte_length], 'big')
        if signed and value & (1 << (bit_length - 1)):
            value -= (1 << bit_length)
        return value

    def write_reg(self, name, value):
        """Writes a register

        Parameters:

            name (str): name of register to read

            value (int): value to write

        """

        (addr, fmt) = self.REGS[name]
        (byte_length, bit_length, signed) = self.FORMATS[fmt]
        # print(f"writing {bytes((0, (addr>>8) & 0xFF, addr & 0xFF)) + value.to_bytes(length, 'big')}")
        cmd = self.cmd
        cmd[0] = 0
        cmd[1] = addr >> 8
        cmd[2] = addr & 0xff
        cmd[3:3+byte_length] = value.to_bytes(byte_length, 'big')
        self.spi.exchange(self.cs_pin, memoryview(cmd)[:3+byte_length])
 
    def start_dsp(self):
        self.write_reg('RUN', 1)
        
    def stop_dsp(self):
        self.write_reg('RUN', 0)

    def get_frequency(self):
        """ Return the line frequency

        Returns:

            float: line frequency in Hz. 0 If there is are transitions detected on the line.
        """
        p = self.read_reg('PERIOD')
        return 256e3/p if p else 0;

    def get_current(self, ch):
        """ Get instantaneous RMS current measurement 

        Parameters:

            ch (int): channel number (0-5)
        """
        c = self.CHANNELS[ch]
        # a value of 4191910 (0x3FF6A6) corresponds to a full scale analog voltage of 0.5Vp or 0.5*.707= 0.3535 Vrms. 
        return self.read_reg(f'I{c}RMS')/4191910*0.5*0.707 / self.ct_cal

    def get_voltage(self):
        """ Get instantaneous RMS voltage measurement 

        """
        # a value of 4191910 (0x3FF6A6) corresponds to a full scale analog voltage of 0.5Vp or 0.5*.707= 0.3535 Vrms. 
        return self.read_reg(f'VRMS')/4191910*0.5*0.707 / self.v_gain / self.vt_cal

def test(N=0):
    from machine import Pin
    from e42_spi import SPI_with_CS
    from e42_rotary2 import RotaryEncoder
    import time

    pin_cs0_rota = Pin(10)
    pin_cs1_rotb = Pin(9)
    spi = SPI_with_CS(cs_inout_pins={'EMON0':pin_cs0_rota, 'EMON1': pin_cs1_rotb})
    rot = RotaryEncoder(pin_cs0_rota, pin_cs1_rotb)
    spi.set_pin_irq((pin_cs0_rota, pin_cs1_rotb), rot.process_state)
    p = ADE7816(spi, 'EMON0')
    p.start_dsp()

    # Execute N SPI transaction within the SPI context, which keeps the CS lines in OUT mode and disable pin interrupts.
    # 1000 iterations take 0.648 s. Interrupts are blocked during that whole time.
    t0=time.time_ns()
    with spi:
        for n in range(N):
            p.read_reg('LCYCMODE')
    print(f'loop of {N} SPI transactions WITH context took {(time.time_ns()-t0)/1e9:.3f} s')

    # Execute N SPI transaction without the SPI context. The CS lines
    # directions have to be set and reset on every transaction, but that
    # allows the pin interrupts to be processed between transactions. 
    # 1000 iterations take 1.242 s. (half the rate)
    t0=time.time_ns()
    for n in range(N):
        p.read_reg('LCYCMODE')
    print(f'loop of {N} SPI transactions WITHOUT took {(time.time_ns()-t0)/1e9:.3f} s')
    return spi, p, rot

# if __name__ == "__main__":
#     pass


