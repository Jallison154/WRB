# XIAO-to-XIAO Communication Guide

## Overview

The XIAO controllers can now communicate directly with each other, creating a more robust and flexible system. This guide explains the different communication modes and how to set them up.

## Communication Modes

### 1. Simple XIAO-to-XIAO Mode (Recommended)

**File**: `xiao_controller_simple.ino`

**How it works**:
- XIAO1 button press → XIAO1 sends to XIAO2 → XIAO2 forwards to Pi → Audio plays
- XIAO2 button press → XIAO2 sends to XIAO1 → XIAO1 forwards to Pi → Audio plays

**Benefits**:
- Simple and reliable
- XIAOs communicate directly
- Pi still handles audio playback
- Easy to debug and troubleshoot

### 2. Advanced Multi-Mode

**File**: `xiao_controller_v2.ino`

**Communication modes**:
- `COMM_PI_ONLY`: Send directly to Pi (original behavior)
- `COMM_XIAO_ONLY`: Send to other XIAO only
- `COMM_BOTH`: Send to both Pi and other XIAO

**Benefits**:
- Maximum flexibility
- Can switch modes dynamically
- Good for testing and development

## Network Architecture

```
┌─────────────┐    WiFi    ┌─────────────┐
│   XIAO 1    │◄──────────►│   XIAO 2    │
│ (192.168.1.101) │         │ (192.168.1.102) │
└─────────────┘             └─────────────┘
       │                           │
       │                           │
       ▼                           ▼
┌─────────────────────────────────────────┐
│           Raspberry Pi                   │
│        (192.168.1.100:8080)            │
│         Audio Server                    │
└─────────────────────────────────────────┘
```

## Setup Instructions

### Step 1: Configure Network Settings

Update these values in your XIAO code:

```cpp
// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Pi server address
const char* pi_server = "http://192.168.1.100:8080";

// XIAO IP addresses
const char* xiao1_ip = "192.168.1.101";
const char* xiao2_ip = "192.168.1.102";

// XIAO communication port
const int xiao_communication_port = 8081;
```

### Step 2: Set XIAO IDs

For XIAO 1:
```cpp
const int XIAO_ID = 1;
```

For XIAO 2:
```cpp
const int XIAO_ID = 2;
```

### Step 3: Upload Code

1. **For Simple Mode**: Upload `xiao_controller_simple.ino` to both XIAOs
2. **For Advanced Mode**: Upload `xiao_controller_v2.ino` to both XIAOs

### Step 4: Test Communication

1. **Check XIAO Status**:
   ```bash
   curl http://192.168.1.101:8081/status
   curl http://192.168.1.102:8081/status
   ```

2. **Test Button Presses**:
   - Press button on XIAO1
   - Check XIAO2 serial monitor for received message
   - Verify audio plays on Pi

## API Endpoints

### XIAO-to-XIAO Communication

**POST** `/xiao_trigger`
```json
{
  "xiao_id": 1,
  "button_id": 1
}
```

**GET** `/status`
```json
{
  "xiao_id": 1,
  "wifi_connected": true,
  "ip_address": "192.168.1.101",
  "button1_state": 1,
  "button2_state": 1
}
```

### Advanced Mode Only

**POST** `/set_mode`
```json
{
  "mode": 0  // 0=PI_ONLY, 1=XIAO_ONLY, 2=BOTH
}
```

## Troubleshooting

### Common Issues

1. **XIAOs can't find each other**
   - Check IP addresses in code
   - Verify both XIAOs are on same WiFi network
   - Test with ping: `ping 192.168.1.101`

2. **Audio not playing**
   - Check Pi server is running
   - Verify XIAO-to-Pi communication
   - Check audio files exist

3. **Buttons not responding**
   - Check wiring connections
   - Verify pull-up resistors
   - Test with Serial Monitor

### Debug Commands

```bash
# Test XIAO connectivity
curl http://192.168.1.101:8081/status
curl http://192.168.1.102:8081/status

# Test Pi server
curl http://192.168.1.100:8080/status

# Test XIAO-to-XIAO communication
curl -X POST http://192.168.1.101:8081/xiao_trigger \
  -H "Content-Type: application/json" \
  -d '{"xiao_id":1,"button_id":1}'
```

### Serial Monitor Debugging

Enable Serial Monitor in Arduino IDE to see:
- WiFi connection status
- Button press events
- HTTP request/response logs
- Error messages

## Performance Considerations

### Network Latency
- XIAO-to-XIAO communication adds ~50-100ms latency
- Still fast enough for audio triggers
- Consider Pi-only mode for lowest latency

### Reliability
- XIAO-to-XIAO mode is more reliable than Pi-only
- If one XIAO fails, the other can still trigger audio
- Built-in retry logic and error handling

### Power Consumption
- XIAO-to-XIAO communication uses more power
- Consider sleep modes for battery operation
- LED indicators show connection status

## Advanced Configuration

### Custom Ports
Change the communication port if needed:
```cpp
const int xiao_communication_port = 8081;  // Change this
```

### Multiple XIAOs
To add more XIAOs:
1. Add new IP addresses to the code
2. Update the target selection logic
3. Add new audio file mappings

### Security
For production use, consider:
- WPA3 WiFi security
- HTTPS communication
- Authentication tokens
- Network isolation

## Best Practices

1. **Use Simple Mode** for most applications
2. **Set static IP addresses** for reliable communication
3. **Monitor Serial output** during development
4. **Test thoroughly** before deployment
5. **Keep firmware updated** for security and stability
