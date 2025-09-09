# WRB Audio Trigger System

A complete audio playback system using Raspberry Pi Zero with USB audio card and Seeed XIAO ESP32 controllers. Features ESP-NOW wireless communication, serial integration, and hold detection for different audio responses.

## Hardware Requirements

- **Raspberry Pi Zero** (or Pi 3/4) with SD card
- **USB Audio Card/DAC** for audio output
- **2x Seeed XIAO ESP32C3 or ESP32S3** controllers
- **2x Push buttons** (for transmitter XIAO)
- **Jumper wires** for connections
- **Power supply** for Pi
- **MicroSD card** (16GB+ recommended)

## Project Structure

```
WRB/
├── pi_code/                    # Raspberry Pi Python code
│   ├── audio_server.py        # Main audio server with serial integration
│   ├── serial_reader.py       # Serial communication handler
│   ├── usb_manager.py         # USB auto-mounting system
│   ├── status_led.py          # System status LED control
│   ├── install_dependencies.sh # Automated setup script
│   ├── quick_start.sh         # System check and startup script
│   ├── requirements.txt       # Python dependencies
│   └── config.py              # Configuration settings
├── xiao_code/                 # Arduino code for XIAO controllers
│   ├── xiao_transmitter/      # Transmitter XIAO code
│   │   └── xiao_transmitter.ino # ESP-NOW transmission with power management
│   ├── xiao_receiver/         # Receiver XIAO code
│   │   └── xiao_receiver.ino  # ESP-NOW reception + serial to Pi
│   └── xiao_controller/       # Legacy combined code (optional)
├── audio_files/               # Audio files to play
│   ├── button1.wav           # Button 1 press sound
│   ├── button2.wav           # Button 2 press sound
│   ├── hold1.wav             # Button 1 hold sound
│   └── hold2.wav             # Button 2 hold sound
├── docs/                      # Documentation
│   ├── serial_communication_guide.md # Serial setup guide
│   ├── transmitter_receiver_guide.md # XIAO setup guide
│   └── xiao_communication_guide.md   # ESP-NOW guide
├── SETUP_GUIDE.md             # Complete setup instructions
└── README.md                  # This file
```

## Quick Start

### 1. **Clone and Setup on Raspberry Pi:**
   ```bash
   git clone https://github.com/Jallison154/WRB.git
   cd WRB/pi_code
   chmod +x install_dependencies.sh
   ./install_dependencies.sh
   ```

### 2. **Start the Audio Server:**
   ```bash
   chmod +x quick_start.sh
   ./quick_start.sh
   ```

### 3. **Program XIAO Controllers:**
   - **Transmitter**: Upload `xiao_code/xiao_transmitter/xiao_transmitter.ino`
   - **Receiver**: Upload `xiao_code/xiao_receiver/xiao_receiver.ino`
   - See `docs/transmitter_receiver_guide.md` for detailed setup

### 4. **Connect Hardware:**
   - **Transmitter**: Connect 2 buttons to D0 and D1
   - **Receiver**: Connect D6→Pi GPIO14, D7→Pi GPIO15, GND→GND
   - **Pi**: Connect USB audio card to USB port

## Features

- **🚀 ESP-NOW Communication**: Low-latency wireless between XIAO controllers
- **🔌 Serial Integration**: Direct connection from XIAO receiver to Pi
- **🎵 Audio Playback**: Raspberry Pi handles audio with USB audio card
- **⏱️ Hold Detection**: Different sounds for button press vs hold (500ms+)
- **💾 USB Auto-mounting**: Automatic detection and mounting of USB audio files
- **💡 Status LEDs**: Visual feedback on Pi and XIAO controllers
- **🔋 Power Management**: Light/deep sleep modes for battery efficiency
- **🛡️ Security**: MAC address filtering for authorized transmitters only
- **📊 Real-time Monitoring**: Comprehensive logging and status reporting

## How It Works

### ESP-NOW + Serial Communication Flow:
1. **XIAO Transmitter Button Press** → ESP-NOW to XIAO Receiver
2. **XIAO Receiver** → Serial command to Raspberry Pi
3. **Pi Server** → Maps to audio file and plays through USB audio card
4. **LED Indicators** → Show connection status on all devices

### Audio File Mapping:
- Button 1 Press → `button1.wav`
- Button 2 Press → `button2.wav`
- Button 1 Hold → `hold1.wav`
- Button 2 Hold → `hold2.wav`

## System Architecture

### **Communication Flow:**
```
[Button Press] → [XIAO Transmitter] → [ESP-NOW] → [XIAO Receiver] → [Serial] → [Pi Audio Server] → [USB Audio Card] → [Speakers]
```

### **Key Components:**
- **XIAO Transmitter**: Button input, ESP-NOW transmission, power management
- **XIAO Receiver**: ESP-NOW reception, serial forwarding to Pi
- **Pi Audio Server**: Serial reading, audio playback, USB management, status LEDs

## Installation & Setup

### **Automated Setup (Recommended):**
```bash
git clone https://github.com/Jallison154/WRB.git
cd WRB/pi_code
./install_dependencies.sh  # Installs all dependencies
./quick_start.sh          # System check and startup
```

### **Manual Setup:**
```bash
pip3 install -r requirements.txt
python3 audio_server.py
```

## Configuration

### **Audio Files:**
Place your audio files in the `audio_files/` directory:
- `button1.wav` - Button 1 press sound
- `button2.wav` - Button 2 press sound  
- `hold1.wav` - Button 1 hold sound (500ms+)
- `hold2.wav` - Button 2 hold sound (500ms+)

### **XIAO MAC Addresses:**
Update the MAC addresses in `xiao_receiver.ino`:
```cpp
uint8_t ALLOWED_TX_MACS[][6] = {
  { 0x58,0x8C,0x81,0x9F,0x22,0xAC }, // Your transmitter MAC
};
```

## Troubleshooting

### **Common Issues:**
- **No audio**: Check USB audio card connection and `aplay -l`
- **Serial not working**: Verify GPIO connections and permissions
- **ESP-NOW not connecting**: Check MAC addresses and channel settings
- **Dependencies missing**: Run `./install_dependencies.sh`

### **Debug Commands:**
```bash
# Check audio devices
aplay -l

# Monitor serial communication  
screen /dev/ttyUSB0 115200

# Check system status
sudo systemctl status wrb-audio
```

## Documentation

- **📖 [Complete Setup Guide](SETUP_GUIDE.md)** - Detailed installation instructions
- **🔌 [Serial Communication Guide](docs/serial_communication_guide.md)** - Hardware connections
- **📡 [Transmitter/Receiver Guide](docs/transmitter_receiver_guide.md)** - XIAO programming
- **🌐 [ESP-NOW Communication Guide](docs/xiao_communication_guide.md)** - Wireless setup

## License

This project is open source. Feel free to modify and distribute.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
