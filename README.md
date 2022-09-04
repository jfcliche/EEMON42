# EMON36
ESP32-C3-based 36-channel home energy monitor

Features

  - 36 Current Transformer inputs (3.5 mm jacks)
  - Accurate Energy monitoring performed by six ADE7816
  - ESP32-C3-WROOM-02 module (RISC-V single core controller, 4 MB flash, Wifi, Bluetooth)
  - PMOD to support Digilent OLED display
  - 6 key keypad
  - Single phase or split-phase 9 VAC inputs for voltage monitoring (jumper selected)
  - Micro-USB connector for UART programming and JTAG debugging (using the ESP32 embedded USB controller)      
  - Powered by the 9VAC input or the USB port

# Rationale

The EMON36 was developed as personal project to get familiarized with the tools required to build an embedded controller project. This includes:

   - KiCAD 6.0 (I have designed and verified many boards with Altium but never did the routing myself before)
   - Manufacturing using cheap online PCB prototyping fabs (never done that before)
   - Home-made assembly of boards with high density chips (Have done some SMT reworks, but not full assemblies)
   - ESP32-C3-based module (first time with this processor; last time was with a 68HC11 20 years ago)
   - Software development tools (Visual Studio Code / Platform IO / ESP IDF etc)

# Status

The board is currently under design and is not ready for production.

 