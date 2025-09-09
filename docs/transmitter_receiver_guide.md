# XIAO Transmitter/Receiver Architecture Guide

## Overview

The system now uses a dedicated **Transmitter/Receiver** architecture where XIAO controllers have specialized roles:

- **XIAO Transmitter**: Handles button input and sends triggers
- **XIAO Receiver**: Receives triggers and forwards to Pi for audio playback
- **Raspberry Pi**: Handles audio playback and file management

## Architecture Diagram

```
┌─────────────────┐    WiFi    ┌─────────────────┐    WiFi    ┌─────────────────┐
│  XIAO Transmitter│◄──────────►│  XIAO Receiver  │◄──────────►│  Raspberry Pi   │
│                 │            │                 │            │                 │
│ • Button 1 (D0) │            │ • Web Server    │            │ • Audio Server  │
│ • Button 2 (D1) │            │ • Pi Forwarding │            │ • File Manager  │
│ • LED Status    │            │ • LED Status    │            │ • USB Audio     │
│ • WiFi Client   │            │ • WiFi Client   │            │ • Flask API     │
└─────────────────┘            └─────────────────┘            └─────────────────┘
```

## File Structure

```
xiao_code/
├── xiao_transmitter/
│   └── xiao_transmitter.ino    # Transmitter code
├── xiao_receiver/
│   └── xiao_receiver.ino       # Receiver code
└── xiao_controller/            # Legacy combined code
    ├── xiao_controller.ino
    ├── xiao_controller_v2.ino
    └── xiao_controller_simple.ino
```

## Transmitter XIAO

### **Role**: Button Input and Transmission
- **Hardware**: 2 buttons, 1 LED, WiFi
- **Function**: Monitors buttons, sends triggers to receiver
- **No Audio**: Pure input device

### **Features**:
- Button debouncing and reliable input
- WiFi connectivity with auto-reconnection
- Transmission statistics and error handling
- LED status indicators
- Target receiver configuration

### **Configuration**:
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* receiver_ip = "192.168.1.102";  // Receiver XIAO IP
const int receiver_port = 8081;
const int TRANSMITTER_ID = 1;
```

## Receiver XIAO

### **Role**: Trigger Reception and Pi Forwarding
- **Hardware**: 1 LED, optional status button, WiFi
- **Function**: Receives triggers, forwards to Pi
- **No Buttons**: Pure communication device

### **Features**:
- Web server for receiving triggers
- Pi server forwarding
- Statistics and monitoring
- Connection testing
- Optional status button for debugging

### **Configuration**:
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* pi_server = "http://192.168.1.100:8080";
const int RECEIVER_ID = 1;
const int receiver_port = 8081;
```

## Communication Flow

### **1. Button Press on Transmitter**
```
Transmitter Button → Transmitter XIAO → HTTP POST → Receiver XIAO
```

### **2. Receiver Processing**
```
Receiver XIAO → HTTP POST → Raspberry Pi → Audio Playback
```

### **3. Complete Flow**
```
Button Press → Transmitter → Receiver → Pi → Audio File → USB Audio Card
```

## API Endpoints

### **Transmitter → Receiver**
**POST** `/receive_trigger`
```json
{
  "transmitter_id": 1,
  "button_id": 1,
  "timestamp": 1234567890
}
```

### **Receiver → Pi**
**POST** `/trigger_audio`
```json
{
  "xiao_id": 1,
  "button_id": 1,
  "source": "xiao_transmitter",
  "receiver_id": 1
}
```

### **Status Endpoints**
- **GET** `/status` - Device status and statistics
- **GET** `/stats` - Transmission statistics
- **GET** `/test_pi` - Test Pi connectivity

## Setup Instructions

### **Step 1: Configure Network**
Update IP addresses in both transmitter and receiver code:

**Transmitter**:
```cpp
const char* receiver_ip = "192.168.1.102";  // Receiver XIAO IP
```

**Receiver**:
```cpp
const char* pi_server = "http://192.168.1.100:8080";  // Pi IP
```

### **Step 2: Set Device IDs**
**Transmitter**:
```cpp
const int TRANSMITTER_ID = 1;  // Unique transmitter ID
```

**Receiver**:
```cpp
const int RECEIVER_ID = 1;     // Unique receiver ID
```

### **Step 3: Upload Code**
1. Upload `xiao_transmitter.ino` to transmitter XIAO
2. Upload `xiao_receiver.ino` to receiver XIAO
3. Start Pi audio server

### **Step 4: Test System**
1. Check transmitter status: `curl http://192.168.1.101:8081/status`
2. Check receiver status: `curl http://192.168.1.102:8081/status`
3. Press transmitter buttons
4. Verify audio playback

## Hardware Connections

### **Transmitter XIAO**
```
XIAO Transmitter
┌─────────┐
│    D0   │────────────── Button 1
│    D1   │────────────── Button 2
│    D2   │ (LED)        Status LED
│   GND   │────────────── Button grounds
│  3V3    │
└─────────┘
```

### **Receiver XIAO**
```
XIAO Receiver
┌─────────┐
│    D0   │────────────── Optional Status Button
│    D1   │ (unused)
│    D2   │ (LED)        Status LED
│   GND   │
│  3V3    │
└─────────┘
```

## Advantages of Transmitter/Receiver Architecture

### **1. Specialization**
- Each XIAO has a clear, focused role
- Easier to debug and maintain
- Better performance optimization

### **2. Scalability**
- Easy to add more transmitters
- Multiple receivers possible
- Flexible network topology

### **3. Reliability**
- Transmitter failure doesn't affect audio system
- Receiver failure doesn't affect input system
- Independent error handling

### **4. Development**
- Easier to test individual components
- Clear separation of concerns
- Simpler code maintenance

## Troubleshooting

### **Common Issues**

1. **Transmitter can't reach receiver**
   - Check receiver IP address in transmitter code
   - Verify both devices on same WiFi network
   - Test with ping: `ping 192.168.1.102`

2. **Receiver can't reach Pi**
   - Check Pi IP address in receiver code
   - Verify Pi audio server is running
   - Test Pi connectivity: `curl http://192.168.1.100:8080/status`

3. **No audio playback**
   - Check audio files exist in `audio_files/` directory
   - Verify USB audio card connection
   - Check Pi audio server logs

### **Debug Commands**

```bash
# Test transmitter status
curl http://192.168.1.101:8081/status

# Test receiver status
curl http://192.168.1.102:8081/status

# Test receiver statistics
curl http://192.168.1.102:8081/stats

# Test Pi connection from receiver
curl http://192.168.1.102:8081/test_pi

# Test Pi audio server
curl http://192.168.1.100:8080/status
```

### **Serial Monitor Debugging**

**Transmitter Serial Output**:
- WiFi connection status
- Button press events
- Transmission attempts and results
- Statistics and error counts

**Receiver Serial Output**:
- WiFi connection status
- Received trigger events
- Pi forwarding attempts
- Statistics and success rates

## Performance Considerations

### **Latency**
- Transmitter → Receiver: ~10-50ms
- Receiver → Pi: ~10-50ms
- Total latency: ~20-100ms (acceptable for audio triggers)

### **Reliability**
- Built-in retry logic
- Error handling and statistics
- Automatic reconnection
- Status monitoring

### **Power Consumption**
- Transmitter: Higher (button monitoring)
- Receiver: Lower (mostly idle)
- Consider sleep modes for battery operation

## Advanced Configuration

### **Multiple Transmitters**
To add more transmitters:
1. Use different `TRANSMITTER_ID` values
2. Update receiver to handle multiple transmitters
3. Consider load balancing

### **Multiple Receivers**
To add more receivers:
1. Use different `RECEIVER_ID` values
2. Configure transmitters to send to multiple receivers
3. Implement failover logic

### **Custom Ports**
Change communication ports if needed:
```cpp
const int receiver_port = 8081;  // Change this
```

## Best Practices

1. **Use static IP addresses** for reliable communication
2. **Monitor statistics** for system health
3. **Test connectivity** regularly
4. **Keep firmware updated** for security
5. **Use proper error handling** in production
6. **Document device IDs** for maintenance
7. **Monitor power consumption** for battery operation
