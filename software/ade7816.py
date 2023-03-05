# import pyftdi.spi

class ADE7816:
    """ Class allowing operation of the ADE7816 split-phase 6-channel energy monitor chip through a SPI interface.
    """

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
        'PCF_A_COEFF' : (0x43B1, '32ZPSE'),  #0x000000 Phase calibration coefficient for Channel A. Set
        'PCF_B_COEFF' : (0x43B2, '32ZPSE'),  #0x000000 Phase calibration coefficient for Channel B. Set
        'PCF_C_COEFF' : (0x43B3, '32ZPSE'),  #0x000000 Phase calibration coefficient for Channel C. Set
        'PCF_D_COEFF' : (0x43B4, '32ZPSE'),  #0x000000 Phase calibration coefficientfor Channel D. Set
        'PCF_E_COEFF' : (0x43B5, '32ZPSE'),  #0x000000 Phase calibration coefficient for Channel E. Set to
        'PCF_F_COEFF' : (0x43B6, '?'),  #0x000000 Phase calibration coefficient for Channel F. Set to
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
        # name: (number_of_bytes_transferred, is_signed_value)
        '32U': (4, False),  # unsigned 32-bit value
        '32S': (4, True),  # signed 32-bit value
        '32SE': (4, True), # signed 24-bit value sign-extended to 32 bits
        '32ZP': (4, False), # unsigned 24-bit value zero-padded to 32 bits
        '16U': (2, False),  # unsigned 16-bit value
        '16S': (2, True),  # signed 16-bit value
        '8U': (1, False),  # unsigned 8-bit value
        '8S': (1, True),  # signed 8-bit value
        }

    def __init__(self, spi, cs_name):
        """
        Parameters:

            spi (SPI_with_CS): instance of the SPI_with_CS interface object

            cs_name (str): name of the SPI device as found in the `spi` object.

        """

        self.spi = spi
        self.cs_name = cs_name

        # make sure we are in SPI mode by issuing 3 dummy writes as recommended by datasheet. 
        # otherwise we will be in I2C mode

        for _ in range(3):
            # self.write_reg8(0xEBFF,0)
            self.write_reg('DUMMY',0)

    def read_reg(self, name):
        """Reads a register

        Parameters:

            name (str): name of register to read

        Returns:

            int: value that was read. Will be a signed or unsigned value depending on the register number format. 
        """

        (addr, fmt) = self.REGS[name]
        (length, signed) = self.FORMATS[fmt]
        return int.from_bytes(self.spi.exchange(self.cs_name, (1, (addr>>8) & 0xFF, addr & 0xFF), read_length=length), 'big') - signed*(1 << 8 * length)

    def write_reg(self, name, value):
        """Writes a register

        Parameters:

            name (str): name of register to read

            value (int): value to write

        """

        (addr, fmt) = self.REGS[name]
        (length, signed) = self.FORMATS[fmt]
        # print(f"writing {bytes((0, (addr>>8) & 0xFF, addr & 0xFF)) + value.to_bytes(length, 'big')}")
        self.spi.exchange(self.cs_name, bytes((0, (addr>>8) & 0xFF, addr & 0xFF)) + value.to_bytes(length, 'big'))
 
    def start_dsp(self):
        self.write_reg('RUN', 1)
        
    def stop_dsp(self):
        self.write_reg('RUN', 0)

    def get_frequency(self):
        """ Return the line frequency

        Returns:

            float: line frequency in Hz
        """
        return 256e3/self.read_reg('PERIOD')


def test(N=0):
    from machine import Pin
    from e42_spi import SPI_with_CS
    from e42_rotary2 import RotaryEncoder
    import time

    pin_cs0_rota = Pin(10)
    pin_cs1_rotb = Pin(9)
    spi = SPI_with_CS(cs_inout_pins={'EMON0':pin_cs0_rota, 'EMON1': pin_cs1_rotb})
    rot = RotaryEncoder(pin_cs0_rota, pin_cs1_rotb)
    spi.set_cs_pin_irq('EMON0', rot.process_state)
    spi.set_cs_pin_irq('EMON1', rot.process_state)
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


