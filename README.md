# Raspberry Pi Zero + Seeed XIAO Audio Trigger System

This project creates an audio playback system using a Raspberry Pi Zero with USB audio card and 2 Seeed XIAO controllers, each with 2 buttons to trigger different audio files.

## Hardware Requirements

- Raspberry Pi Zero (with WiFi)
- USB Audio Card/DAC
- 2x Seeed XIAO ESP32C3 or ESP32S3 controllers
- 4x Push buttons (2 per XIAO)
- Jumper wires
- Power supply for Pi

## Project Structure

```
WRB/
├── pi_code/                 # Raspberry Pi Python code
│   ├── audio_server.py     # Main audio server
│   ├── requirements.txt    # Python dependencies
│   └── config.py          # Configuration settings
├── xiao_code/              # Arduino code for XIAO controllers
│   ├── xiao_transmitter/   # Transmitter XIAO code
│   │   └── xiao_transmitter.ino # Button input and transmission
│   ├── xiao_receiver/      # Receiver XIAO code
│   │   └── xiao_receiver.ino # Trigger reception and Pi forwarding
│   ├── xiao_controller/    # Legacy combined code
│   │   ├── xiao_controller.ino # Original combined code
│   │   ├── xiao_controller_v2.ino # Advanced multi-mode
│   │   └── xiao_controller_simple.ino # Simple XIAO-to-XIAO
│   └── libraries/         # Required Arduino libraries
├── audio_files/           # Audio files to play
│   ├── button1_1.wav     # XIAO1 Button1 audio
│   ├── button1_2.wav     # XIAO1 Button2 audio
│   ├── button2_1.wav     # XIAO2 Button1 audio
│   └── button2_2.wav     # XIAO2 Button2 audio
└── docs/                  # Documentation and wiring diagrams
    ├── wiring.md
    ├── setup_guide.md
    ├── xiao_communication_guide.md
    └── transmitter_receiver_guide.md
```

## Quick Start

1. **Setup Raspberry Pi:**
   ```bash
   cd pi_code
   pip install -r requirements.txt
   python audio_server.py
   ```

2. **Upload XIAO Code:**
   - Open Arduino IDE
   - Load `xiao_code/xiao_controller/xiao_controller.ino`
   - Upload to each XIAO controller

3. **Connect Hardware:**
   - See `docs/wiring.md` for detailed connections
   - Connect buttons to XIAO GPIO pins
   - Connect USB audio card to Pi

## Features

- **XIAO-to-XIAO Communication**: Direct communication between XIAO controllers
- **Pi Audio Server**: Raspberry Pi handles audio playback
- **Flexible Communication**: Choose between Pi-only, XIAO-only, or both
- **Button Debouncing**: Reliable button triggering
- **Audio File Management**: Organized audio file system
- **Real-time Status Monitoring**: LED indicators and logging

## How It Works

### XIAO-to-XIAO Communication Flow:
1. **XIAO1 Button Press** → XIAO1 sends HTTP POST to XIAO2
2. **XIAO2 Receives** → XIAO2 forwards request to Pi server
3. **Pi Server** → Maps to audio file and plays through USB audio card
4. **LED Indicators** → Show connection status on both XIAOs

### Audio File Mapping:
- XIAO1 Button1 → `button1_1.wav`
- XIAO1 Button2 → `button1_2.wav`
- XIAO2 Button1 → `button2_1.wav`
- XIAO2 Button2 → `button2_2.wav`

### Communication Options:
- **Transmitter/Receiver Mode**: Dedicated roles (use `xiao_transmitter.ino` + `xiao_receiver.ino`)
- **Simple Mode**: XIAO-to-XIAO only (use `xiao_controller_simple.ino`)
- **Advanced Mode**: Choose Pi-only, XIAO-only, or both (use `xiao_controller_v2.ino`)
