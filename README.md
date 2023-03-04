# EEMON42
ESP32-C3-based 42-channel home energy monitor using the Analog Device ADE7816 emergy monitor chip

Features

  - 42 Current monitoring inputs with 3.5 mm jacks for current transformers
  - Single board, 10x10 cm design with OLED screen with a OLED/switch/rotary encoder user interface
  - Two AC voltage for split phase voltage monitoring and board powering
  - Micropython control software with MQTT telemetry streamed over WiFi

# Status

  V0 Hardware
    - Board is built. 
    - Hardware validation:
      - Switcher works. Board can be powered via USB or AC jacks. 
      - Can operate the ESP32 via the USB and micropython. 
      - All buttons work.
      - OLED display works
      - Only one ADE7816 is populated so far, but we can read registers.
    - Todo: 
      - Check analog inputs of ADE7816. Populate rest of the board. Calibrate all inputs.

  Software
    - Building basic micropyton modules
    - Todo: 
      - Implement main loop and monitoring/GUI tasks as coroutines. Improve display functions. Integrate with Home Assistant.


# Design Details:
- Accurate Energy monitoring performed by seven ADE7816
  - ESP32-C3 controller implemented with a Espressif ESP32-C3-WROOM-02 or AI Thinker ESP-C3-13 module, providing 
      - Single core RISC-V 160 MHz processor
      - 4 MB flash
      - Wifi, Bluetooth
      - Embedded USB controller
  - 96x64 pixel, 0.96" OLED display
  - 3 pushbutton keys 
  - Rotary encoder with integrated push button
  - Dual 9-15VAC inputs for line voltage monitoring and powering the board
  - Micro-USB connector for UART programming and JTAG debugging, and alternate board powering      
  - Integrated DC-DC converter for wide input voltage range

# Rationale

The EEMON42 was developed as personal project for learning all the steps to build an embedded controller project from A to Z, starting from from schematics & layout, online PCB manufacturing, hand soldering of high density SMD devices, an developing the embedded controller software. More specifically, this includes:

   - Learn KiCAD 6.0 and learn to place and route designs
   - Use PCBWay or JLCPCB to manufacture the PCB
   - Learn SMD soldering techniques for sizes down to 0603 and QFN 0.5mm pitch devices
   - Learn the internal architecture of the ESP32-C3-based module
   - Software development tools (Visual Studio Code / Platform IO / ESP IDF/ Micropython etc)

# History

2022/06: Design start
2022/12: Board was manufactured by PCBJLC. Board is assembled. Preliminary hardware verification is performed: power, ESP32, buttons and OLED display works with Micropython. Discovered bug in esptool that prevent the flashing stub to operate when USB-enabled micropython has booted first.
2023/03: ADE7816 is installed. Successful communication with it. Implement Python object for it. Implement SPI object to handle SPI CS pins shared with buttons and pin interrupts.

# Known bugs & gotcha's:

v1 hardware:
  - GPIO9 can be pull down and prevent micropython boot if encoder is left in mid-position
  - Missing GPIO2 & GPIO8 pullup (but still works without those)
  - A reset swwitch would be nice, but is becoming les and less necessary as hardware matures
  - A power LED would prevent accidental soldering on a powered board...
  - Pad and copper pour cleareaces too small close to USB connector: rookie solderers might cause shorts when applying too much solder...
  - serial number chip (or some GPIO strapping) might be useful for software to identify the hardware automatically. rev2 GPIOs assignments will change.  
  - encoder is a bit too close to screen for big fingers. Buttons should be spread out more.
  - Find socket with proper height for screen.

# Changelog:

 v2 hardware (in development):
  - OLED CS7 is now on FSPICS0 for native hardware-enabled CS toggling (if possible)
  - Encoder Button CS2 is on GPIO9 to prevent unwanted boot mode and allow user-controlled to force downnloader boot (although USB interface does not need it except for esptool bug)
  - CS0 and CS1 moved to other GPIOs
  - Added weak pullups on GPIO2 and GPIO8 to be sure

