# EMON36
ESP32-C3-based 36-channel home energy monitor

Features

  - 36 (42) Current Transformer inputs with 3.5 mm jacks
  - Accurate Energy monitoring performed by six (seven) ADE7816
  - ESP32-C3 controller implemented with a ESP32-C3-WROOM-02 or ESP-C3-13 module, providing 
      - Single core RISC-V 160 MHz processor
      - 4 MB flash
      - Wifi, Bluetooth
      - Embedded USB controller
  - 96x64 pixel, 0.96" OLED display
  - 4-key + rotary encoder user controls
  - Dual 9-15VAC inputs for line voltage monitoring and powering the board
  - Micro-USB connector for UART programming and JTAG debugging, and alternate board powering      
  - Integrated DC-DC converter

# Rationale

The EMON36 was developed as personal project for learning all the steps to build an embedded controller project from A to Z, starting from from schematics & layout, online PCB manufacturing, hand soldering of high density SMD devices, an developing the embedded controller software. This includes:

   - Learn KiCAD 6.0 (I have designed and verified many boards with Altium but never did the routing myself before)
   - Use PCBWay or JLCPCB (never done that before)
   - Solder QFN 0.5mm pitch devices (Have done some SMT reworks, but not full assemblies)
   - Learn the internal architecture of the ESP32-C3-based module (first time with this processor; last time was with a 68HC11 20 years ago)
   - Software development tools (Visual Studio Code / Platform IO / ESP IDF/ Micropython etc)

# Status

The board is currently under design and is not ready for production.

 