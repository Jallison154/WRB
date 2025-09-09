# WRB Audio System Setup Guide

## Overview
This system is designed to run on a **Raspberry Pi Zero** with **Seeed XIAO ESP32C3/S3** controllers. The Python code cannot run on Windows - it needs to be deployed to your Raspberry Pi.

## Prerequisites

### Hardware Required:
- Raspberry Pi Zero (or Pi 3/4)
- 2x Seeed XIAO ESP32C3 or ESP32S3
- USB Audio Card (for Pi)
- MicroSD card (16GB+ recommended)
- USB-C cable (for XIAO programming)
- Jumper wires for connections

### Software Required:
- Raspberry Pi OS (Lite recommended)
- Arduino IDE (for XIAO programming)
- SD Card formatter

## Step 1: Prepare Raspberry Pi

### 1.1 Flash Raspberry Pi OS
1. Download [Raspberry Pi Imager](https://www.raspberrypi.org/downloads/)
2. Flash Raspberry Pi OS Lite to your SD card
3. Enable SSH and set WiFi credentials during imaging

### 1.2 First Boot Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install audio dependencies
sudo apt install alsa-utils pulseaudio -y

# Install GPIO library
sudo apt install python3-rpi.gpio -y
```

## Step 2: Deploy Code to Raspberry Pi

### 2.1 Copy Files to Pi
You can use SCP, SFTP, or copy files via USB drive:

```bash
# From your Windows machine, copy the pi_code directory to Pi
scp -r pi_code/ pi@<PI_IP_ADDRESS>:/home/pi/

# Or use FileZilla/SFTP to copy the entire project
```

### 2.2 Install Python Dependencies on Pi
```bash
# SSH into your Pi
ssh pi@<PI_IP_ADDRESS>

# Navigate to pi_code directory
cd pi_code

# Install requirements
pip3 install -r requirements.txt
```

## Step 3: Configure Raspberry Pi

### 3.1 Enable Serial Communication
```bash
# Enable serial port
sudo raspi-config
# Navigate to: Interfacing Options → Serial
# Enable serial port, disable login shell

# Reboot
sudo reboot
```

### 3.2 Set Up Audio
```bash
# Test audio output
speaker-test -t wav -c 2

# Set default audio device (if using USB audio card)
sudo nano /etc/asound.conf
```

### 3.3 Configure GPIO (if using physical buttons)
```bash
# Add user to gpio group
sudo usermod -a -G gpio pi
```

## Step 4: Program XIAO Controllers

### 4.1 Install Arduino IDE
1. Download [Arduino IDE](https://www.arduino.cc/en/software)
2. Install ESP32 board support:
   - File → Preferences → Additional Board Manager URLs
   - Add: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board → Boards Manager → Search "ESP32" → Install

### 4.2 Configure XIAO Boards
1. Tools → Board → ESP32 Arduino → XIAO_ESP32C3 (or XIAO_ESP32S3)
2. Tools → Port → Select your XIAO's COM port
3. Tools → Upload Speed → 921600

### 4.3 Upload Code
1. **Transmitter**: Open `xiao_code/xiao_transmitter/xiao_transmitter.ino`
   - Update MAC addresses in receiver code
   - Upload to first XIAO
2. **Receiver**: Open `xiao_code/xiao_receiver/xiao_receiver.ino`
   - Update allowed transmitter MACs
   - Upload to second XIAO

## Step 5: Hardware Connections

### 5.1 XIAO Transmitter
```
XIAO Transmitter
┌─────────────┐
│      D0     │──────── Button 1 (with pull-up resistor)
│      D1     │──────── Button 2 (with pull-up resistor)
│     GND     │──────── Button grounds
│    3.3V     │──────── Button power (if needed)
└─────────────┘
```

### 5.2 XIAO Receiver to Pi
```
XIAO Receiver          Raspberry Pi
┌─────────────┐        ┌─────────────┐
│      D6     │────────│   GPIO 14   │ (TXD)
│      D7     │────────│   GPIO 15   │ (RXD)
│     GND     │────────│     GND     │
│    3.3V     │────────│    3.3V     │ (optional)
└─────────────┘        └─────────────┘
```

### 5.3 Pi Audio Output
```
USB Audio Card → Pi USB Port
Audio Output → Speakers/Headphones
```

## Step 6: Test the System

### 6.1 Test Pi Audio Server
```bash
# On Pi, start the audio server
cd pi_code
python3 audio_server.py

# You should see:
# - "Audio Server started on port 8080"
# - "Serial reader started successfully"
# - "Status LED set to ready state"
```

### 6.2 Test XIAO Communication
1. Power on XIAO transmitter
2. Power on XIAO receiver
3. Check Pi logs for serial communication
4. Press buttons on transmitter
5. Verify audio plays on Pi

## Step 7: Auto-Start (Optional)

### 7.1 Create Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/wrb-audio.service
```

```ini
[Unit]
Description=WRB Audio Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pi_code
ExecStart=/usr/bin/python3 audio_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable wrb-audio.service
sudo systemctl start wrb-audio.service

# Check status
sudo systemctl status wrb-audio.service
```

## Troubleshooting

### Common Issues:

1. **"No module named 'pygame'"**
   ```bash
   pip3 install pygame
   ```

2. **"Permission denied" for serial**
   ```bash
   sudo usermod -a -G dialout pi
   sudo reboot
   ```

3. **No audio output**
   ```bash
   # Check audio devices
   aplay -l
   
   # Test audio
   speaker-test -t wav -c 2
   ```

4. **XIAO not connecting**
   - Check MAC addresses in code
   - Verify ESP-NOW channel (both on channel 1)
   - Check power supply

5. **Serial communication fails**
   ```bash
   # Check serial devices
   ls /dev/tty*
   
   # Test serial connection
   screen /dev/ttyUSB0 115200
   ```

## Next Steps

1. **Deploy to Pi**: Copy the `pi_code` directory to your Raspberry Pi
2. **Install Dependencies**: Run `pip3 install -r requirements.txt` on Pi
3. **Program XIAOs**: Upload the transmitter and receiver code
4. **Connect Hardware**: Wire everything according to the diagrams
5. **Test System**: Start the audio server and test button presses

The system is designed to run on Raspberry Pi, not Windows. Once deployed to Pi, you'll have a fully functional audio trigger system! 🎉
