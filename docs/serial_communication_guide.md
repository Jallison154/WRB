# Serial Communication Guide

## Overview

The XIAO receiver communicates directly with the Raspberry Pi via serial connection, eliminating the need for WiFi and providing a more reliable, lower-latency connection.

## Hardware Connections

### XIAO Receiver to Raspberry Pi
```
XIAO Receiver          Raspberry Pi
┌─────────────┐        ┌─────────────┐
│      D6     │────────│   GPIO 14   │ (TXD)
│      D7     │────────│   GPIO 15   │ (RXD)
│     GND     │────────│     GND     │
│    3.3V     │────────│    3.3V     │ (optional power)
└─────────────┘        └─────────────┘
```

### Alternative Connection (USB-Serial)
If using a USB-Serial adapter:
```
XIAO Receiver          USB-Serial Adapter    Raspberry Pi
┌─────────────┐        ┌─────────────┐       ┌─────────────┐
│      D6     │────────│     TX      │       │   USB Port  │
│      D7     │────────│     RX      │       │             │
│     GND     │────────│     GND     │       │             │
└─────────────┘        └─────────────┘       └─────────────┘
```

## Serial Configuration

### XIAO Receiver Settings
```cpp
// Serial1 configuration in xiao_receiver.ino
Serial1.begin(115200, SERIAL_8N1, D6, D7); // TX=D6, RX=D7
```

### Pi Serial Settings
- **Baud Rate**: 115200
- **Data Bits**: 8
- **Parity**: None
- **Stop Bits**: 1
- **Flow Control**: None

## Communication Protocol

### Command Format
The XIAO receiver sends simple text commands to the Pi:

```
BTN1:PRESS\n    - Button 1 pressed
BTN1:HOLD\n     - Button 1 held (500ms+)
BTN2:PRESS\n    - Button 2 pressed
BTN2:HOLD\n     - Button 2 held (500ms+)
```

### Example Communication Flow
```
1. User presses Button 1 on XIAO Transmitter
2. XIAO Transmitter sends ESP-NOW message to XIAO Receiver
3. XIAO Receiver sends "BTN1:PRESS\n" via serial to Pi
4. Pi serial reader parses command and forwards to audio server
5. Audio server plays button1.wav
```

## Pi Serial Reader

### Automatic Port Detection
The Pi serial reader automatically tries common serial ports:
- `/dev/ttyUSB0` (USB-Serial adapters)
- `/dev/ttyUSB1` (Multiple USB-Serial adapters)
- `/dev/ttyACM0` (Arduino-style devices)
- `/dev/ttyACM1` (Multiple Arduino-style devices)

### Serial Reader Features
- **Auto-reconnection**: Automatically reconnects if connection is lost
- **Error handling**: Robust error handling and logging
- **Command parsing**: Validates and parses commands from XIAO
- **Pi server integration**: Forwards commands to audio server via HTTP

## Setup Instructions

### 1. Hardware Setup
1. Connect XIAO receiver D6 to Pi GPIO 14 (TXD)
2. Connect XIAO receiver D7 to Pi GPIO 15 (RXD)
3. Connect GND between devices
4. Optionally connect 3.3V for power

### 2. Pi Configuration
```bash
# Enable serial communication
sudo raspi-config
# Navigate to: Interfacing Options → Serial
# Enable serial port, disable login shell

# Install required packages
pip3 install pyserial

# Test serial connection
python3 -c "import serial; print('Serial library available')"
```

### 3. XIAO Configuration
1. Upload `xiao_receiver.ino` to XIAO receiver
2. Configure MAC addresses for allowed transmitters
3. Test ESP-NOW communication with transmitter

### 4. Test Communication
```bash
# Test serial communication
python3 pi_code/serial_reader.py

# Test full system
python3 pi_code/audio_server.py
```

## Troubleshooting

### Common Issues

1. **No serial device found**
   ```bash
   # Check available serial devices
   ls /dev/tty*
   
   # Check if device is connected
   dmesg | tail
   ```

2. **Permission denied**
   ```bash
   # Add user to dialout group
   sudo usermod -a -G dialout pi
   
   # Reboot or logout/login
   sudo reboot
   ```

3. **Wrong baud rate**
   - Ensure both XIAO and Pi use 115200 baud
   - Check Serial1.begin() in XIAO code
   - Check SerialReader baudrate in Pi code

4. **No commands received**
   - Check wiring connections
   - Verify ESP-NOW communication between XIAOs
   - Check serial port permissions
   - Monitor serial output with: `screen /dev/ttyUSB0 115200`

### Debug Commands

```bash
# Monitor serial communication
screen /dev/ttyUSB0 115200

# Check serial port status
sudo dmesg | grep tty

# Test serial communication
echo "BTN1:PRESS" > /dev/ttyUSB0

# Check Pi audio server logs
tail -f audio_server.log
```

## Advantages of Serial Communication

### **Reliability**
- Direct hardware connection
- No network dependencies
- No WiFi interference
- Consistent latency

### **Performance**
- Lower latency than WiFi
- No network overhead
- Direct communication
- No packet loss

### **Simplicity**
- No network configuration
- No IP addresses needed
- Simple command protocol
- Easy debugging

### **Power Efficiency**
- XIAO receiver doesn't need WiFi
- Lower power consumption
- No network scanning
- Direct connection

## Integration with Audio Server

The serial reader is automatically integrated with the audio server:

```python
# In audio_server.py
self.serial_reader = SerialReader()
self.serial_reader.start()  # Starts automatically
```

The serial reader forwards commands to the audio server via HTTP:
```python
# Command: "BTN1:PRESS"
payload = {
    "button_id": 1,
    "is_hold": False,
    "source": "xiao_receiver_serial"
}
```

This provides a seamless integration between the XIAO receiver and the Pi audio system while maintaining the flexibility of the HTTP API for other potential clients.
