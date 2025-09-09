# Complete Setup Guide

## Prerequisites

### Hardware
- Raspberry Pi Zero (with WiFi)
- USB Audio Card/DAC
- 2x Seeed XIAO ESP32C3 or ESP32S3
- 4x Push buttons
- Jumper wires and breadboard
- MicroSD card (16GB+ recommended)
- Power supplies

### Software
- Raspberry Pi OS (latest)
- Arduino IDE
- Python 3.7+

## Step 1: Raspberry Pi Setup

### 1.1 Install Raspberry Pi OS
1. Download Raspberry Pi Imager
2. Flash Raspberry Pi OS to microSD card
3. Enable SSH and WiFi during imaging process
4. Boot Pi and connect via SSH

### 1.2 System Updates
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git
```

### 1.3 Install Audio Dependencies
```bash
# Install audio tools
sudo apt install -y alsa-utils pulseaudio

# Install ffmpeg for audio conversion
sudo apt install -y ffmpeg

# Install Python audio libraries
pip3 install pygame flask requests python-dotenv
```

### 1.4 Configure USB Audio
```bash
# Check if USB audio is detected
aplay -l

# Set USB audio as default (if needed)
sudo nano /etc/asound.conf
```

Add to `/etc/asound.conf`:
```
pcm.!default {
    type hw
    card 1
}
ctl.!default {
    type hw
    card 1
}
```

### 1.5 Setup Project
```bash
# Clone or copy project files
cd /home/pi
mkdir WRB
cd WRB

# Copy all project files to this directory
# Then install Python dependencies
cd pi_code
pip3 install -r requirements.txt
```

### 1.6 Configure Network
```bash
# Set static IP (optional but recommended)
sudo nano /etc/dhcpcd.conf
```

Add to `/etc/dhcpcd.conf`:
```
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1
```

### 1.7 Test Audio System
```bash
# Test audio playback
cd pi_code
python3 audio_manager.py

# Start audio server
python3 audio_server.py
```

## Step 2: XIAO Controller Setup

### 2.1 Install Arduino IDE
1. Download Arduino IDE from arduino.cc
2. Install ESP32 board package:
   - File → Preferences → Additional Board Manager URLs
   - Add: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board → Boards Manager → Search "ESP32" → Install

### 2.2 Install Required Libraries
1. Open Arduino IDE
2. Tools → Manage Libraries
3. Install "ArduinoJson" by Benoit Blanchon

### 2.3 Configure XIAO Code
1. Open `xiao_code/xiao_controller/xiao_controller.ino`
2. Update configuration:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   const char* pi_server = "http://192.168.1.100:8080";
   const int XIAO_ID = 1;  // Change to 2 for second XIAO
   ```

### 2.4 Upload Code to XIAO Controllers
1. Connect XIAO to computer via USB
2. Select correct board:
   - Tools → Board → ESP32 Arduino → XIAO_ESP32C3 (or XIAO_ESP32S3)
3. Select correct port
4. Upload code
5. Repeat for second XIAO (change XIAO_ID to 2)

## Step 3: Hardware Assembly

### 3.1 Wire XIAO Controllers
Follow the wiring diagrams in `docs/wiring.md`:
- Connect Button 1 to D0 and GND
- Connect Button 2 to D1 and GND
- Built-in LED on D2 will show status

### 3.2 Connect USB Audio
- Connect USB audio card to Pi Zero
- Test with: `aplay -l`

### 3.3 Power Everything
- Power Pi Zero with official adapter
- XIAOs can be powered via USB or external supply

## Step 4: Audio Files Setup

### 4.1 Prepare Audio Files
1. Create or obtain audio files
2. Convert to WAV format (44.1kHz, 16-bit):
   ```bash
   ffmpeg -i input.mp3 -ar 44100 -ac 2 -sample_fmt s16 output.wav
   ```

### 4.2 Add Audio Files
1. Copy audio files to `audio_files/` directory
2. Name them according to the mapping:
   - `button1_1.wav` - XIAO1 Button1
   - `button1_2.wav` - XIAO1 Button2
   - `button2_1.wav` - XIAO2 Button1
   - `button2_2.wav` - XIAO2 Button2

### 4.3 Test Audio Files
```bash
cd pi_code
python3 audio_manager.py
```

## Step 5: System Testing

### 5.1 Test Individual Components
```bash
# Test Pi audio server
cd pi_code
python3 audio_server.py

# In another terminal, test HTTP endpoint
curl -X POST http://localhost:8080/status
```

### 5.2 Test XIAO Communication
1. Open Serial Monitor in Arduino IDE
2. Press buttons on XIAO
3. Check for HTTP requests in Pi logs
4. Verify audio playback

### 5.3 Test Complete System
1. Start Pi audio server
2. Power on both XIAO controllers
3. Press buttons and verify audio playback
4. Check LED status indicators

## Step 6: Auto-Start Configuration

### 6.1 Create Systemd Service
```bash
sudo nano /etc/systemd/system/audio-server.service
```

Add:
```ini
[Unit]
Description=WRB Audio Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/WRB/pi_code
ExecStart=/usr/bin/python3 audio_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 6.2 Enable Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable audio-server.service
sudo systemctl start audio-server.service
```

## Troubleshooting

### Common Issues

1. **XIAO not connecting to WiFi**
   - Check SSID and password
   - Verify network range
   - Check Serial Monitor for error messages

2. **Audio not playing**
   - Check USB audio card connection
   - Verify audio file format and location
   - Test with system audio tools

3. **HTTP requests failing**
   - Check IP addresses in configuration
   - Verify Pi server is running
   - Check firewall settings

4. **Buttons not responding**
   - Check wiring connections
   - Verify pull-up resistors
   - Test with multimeter

### Debug Commands

```bash
# Check Pi audio devices
aplay -l

# Check network connectivity
ping 192.168.1.101
ping 192.168.1.102

# Check service status
sudo systemctl status audio-server.service

# View logs
tail -f audio_server.log

# Test audio playback
aplay audio_files/button1_1.wav
```

## Maintenance

### Regular Tasks
1. Check audio file integrity
2. Monitor system logs
3. Update software packages
4. Test button functionality

### Backup
1. Backup audio files
2. Backup configuration files
3. Keep copies of Arduino code

## Support

For issues and questions:
1. Check logs in `audio_server.log`
2. Use Serial Monitor for XIAO debugging
3. Verify network connectivity
4. Test individual components
