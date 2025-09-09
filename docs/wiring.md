# Wiring Diagram and Connections

## Hardware Overview

This project uses:
- 1x Raspberry Pi Zero (with WiFi)
- 1x USB Audio Card/DAC
- 2x Seeed XIAO ESP32C3 or ESP32S3 controllers
- 4x Push buttons (2 per XIAO)
- Jumper wires and breadboard

## Raspberry Pi Zero Connections

### USB Audio Card
- Connect USB audio card to Pi Zero's USB port
- Test audio output: `aplay -l` (should show USB audio device)

### Optional: Emergency Stop Button (on Pi)
- Connect button between GPIO 18 and GND
- Pull-up resistor (10kΩ) to 3.3V

## XIAO Controller 1 Connections

```
XIAO ESP32C3/S3 Pinout:
┌─────────────────┐
│  D0  D1  D2  D3 │
│  D4  D5  D6  D7 │
│  D8  D9  D10 A0 │
│  A1  A2  A3  A4 │
│  A5  A6  A7  A8 │
│  A9  A10 3V3 GND│
│  RST 5V  GND VIN│
└─────────────────┘
```

### Button Connections for XIAO 1:
- **Button 1**: Connect between D0 and GND
- **Button 2**: Connect between D1 and GND
- **Built-in LED**: D2 (status indicator)

### Wiring Diagram for XIAO 1:
```
XIAO1                    Button1    Button2
┌─────────┐              ┌─────┐    ┌─────┐
│    D0   │──────────────┤ 1   │    │     │
│    D1   │──────────────┤     │    │ 1   │
│    D2   │ (LED)        │ 2   │    │ 2   │
│   GND   │──────────────┤     │    │     │
│  3V3    │              └─────┘    └─────┘
└─────────┘                 │         │
                            │         │
                           GND       GND
```

## XIAO Controller 2 Connections

### Button Connections for XIAO 2:
- **Button 1**: Connect between D0 and GND
- **Button 2**: Connect between D1 and GND
- **Built-in LED**: D2 (status indicator)

### Wiring Diagram for XIAO 2:
```
XIAO2                    Button1    Button2
┌─────────┐              ┌─────┐    ┌─────┐
│    D0   │──────────────┤ 1   │    │     │
│    D1   │──────────────┤     │    │ 1   │
│    D2   │ (LED)        │ 2   │    │ 2   │
│   GND   │──────────────┤     │    │     │
│  3V3    │              └─────┘    └─────┘
└─────────┘                 │         │
                            │         │
                           GND       GND
```

## Power Supply

### Raspberry Pi Zero
- Use official Pi Zero power supply (5V, 2.5A minimum)
- Or USB power bank with 5V output

### XIAO Controllers
- Can be powered via USB during development
- For standalone operation, power via VIN pin (3.3V-5V)
- Or use 3.3V pin for direct 3.3V supply

## Network Configuration

### WiFi Setup
1. All devices (Pi + 2 XIAOs) must be on the same WiFi network
2. Configure static IP addresses for reliable communication:
   - Raspberry Pi: 192.168.1.100
   - XIAO 1: 192.168.1.101
   - XIAO 2: 192.168.1.102

### Router Configuration
- Ensure devices can communicate with each other
- Check firewall settings if having connection issues

## Testing Connections

### Test XIAO Buttons
```cpp
// Add this to XIAO code for testing
void testButtons() {
  Serial.println("Button 1: " + String(digitalRead(BUTTON1_PIN)));
  Serial.println("Button 2: " + String(digitalRead(BUTTON2_PIN)));
}
```

### Test Pi Audio
```bash
# Test USB audio device
aplay -l

# Test audio playback
aplay /path/to/test.wav
```

### Test Network Communication
```bash
# From Pi, test XIAO connectivity
ping 192.168.1.101
ping 192.168.1.102

# Test HTTP endpoint
curl -X POST http://localhost:8080/status
```

## Troubleshooting

### Common Issues

1. **Buttons not responding**
   - Check wiring connections
   - Verify pull-up resistors (internal pull-ups enabled in code)
   - Test with multimeter

2. **WiFi connection issues**
   - Verify SSID and password in XIAO code
   - Check network range and signal strength
   - Ensure all devices on same network

3. **Audio not playing**
   - Check USB audio card connection
   - Verify audio file format and location
   - Test with system audio tools

4. **HTTP requests failing**
   - Check IP addresses in configuration
   - Verify Pi server is running
   - Check firewall settings

### Debug Tools

- **Serial Monitor**: Use Arduino IDE Serial Monitor for XIAO debugging
- **Pi Logs**: Check `audio_server.log` for server issues
- **Network Tools**: Use `ping`, `curl`, and `netstat` for network debugging
