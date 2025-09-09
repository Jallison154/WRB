# Required Arduino Libraries

Install these libraries in Arduino IDE before uploading the XIAO code:

## Required Libraries

1. **WiFi** (usually included with ESP32 board package)
2. **HTTPClient** (usually included with ESP32 board package)  
3. **ArduinoJson** by Benoit Blanchon
   - Install via Library Manager: Tools → Manage Libraries → Search "ArduinoJson"

## Board Setup

1. Install ESP32 board package:
   - File → Preferences → Additional Board Manager URLs
   - Add: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board → Boards Manager → Search "ESP32" → Install

2. Select correct board:
   - For XIAO ESP32C3: Tools → Board → ESP32 Arduino → XIAO_ESP32C3
   - For XIAO ESP32S3: Tools → Board → ESP32 Arduino → XIAO_ESP32S3

3. Configure upload settings:
   - Upload Speed: 921600
   - CPU Frequency: 160MHz
   - Flash Frequency: 80MHz
   - Flash Mode: QIO
   - Flash Size: 4MB
   - Partition Scheme: Default 4MB with spiffs
