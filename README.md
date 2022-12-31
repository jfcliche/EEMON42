# EMON42
ESP32-C3-based 42-channel home energy monitor using the Analog Device ADE7816 emergy monitor chip

Features

  - Single board, 10x10 cm design with OLED screen with a OLED/switch/rotary encoder user interface
  - Two AC voltage for split phase voltage monitoring and board powering
  - 42 Current monitoring inputs with 3.5 mm jacks for current transformers

Details:
- Accurate Energy monitoring performed by seven ADE7816
  - ESP32-C3 controller implemented with a ESP32-C3-WROOM-02 or ESP-C3-13 module, providing 
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

# Status

2022/06: Design start
2022/12: Board was manufactured by PCBJLC. Board is assembled. Preliminary hardware verification is performed.

 
