"""
Configuration settings for the Raspberry Pi audio server
"""

import os

# Audio settings
AUDIO_DIR = "audio_files"
DEFAULT_VOLUME = 0.7
SAMPLE_RATE = 44100
CHANNELS = 2
BUFFER_SIZE = 1024

# Network settings
PI_IP = "192.168.1.100"  # Change to your Pi's IP address
PI_PORT = 8080

# ESP-NOW Communication settings (XIAOs use MAC addresses, not IP)
ESP_NOW_ENABLED = True  # Enable ESP-NOW communication
TRANSMITTER_ID = 1      # Transmitter ID for audio mapping
RECEIVER_ID = 1         # Receiver ID for logging

# Audio file mappings
AUDIO_MAPPINGS = {
    "button1": "button1.wav",
    "button2": "button2.wav",
    "hold1": "hold1.wav",
    "hold2": "hold2.wav"
}

# Button hold settings
HOLD_DETECTION_ENABLED = True
HOLD_DELAY_MS = 500  # 500ms hold delay (matches XIAO transmitter)

# GPIO settings (if using physical buttons on Pi)
BUTTON_PINS = {
    "emergency_stop": 18,  # GPIO pin for emergency stop button
}

# USB Auto-mounting settings
USB_MOUNT_ENABLED = True
USB_MOUNT_POINT = "/media/usb"  # Where USB drives will be mounted
USB_AUDIO_DIR = "audio_files"   # Audio directory on USB drive
USB_LED_PIN = 21                # GPIO pin for USB status LED
USB_CHECK_INTERVAL = 5          # Check for USB every 5 seconds
USB_MOUNT_TIMEOUT = 10          # Timeout for mount operations in seconds

# System Status LED settings
STATUS_LED_PIN = 20             # GPIO pin for system status LED
STATUS_LED_READY_BRIGHTNESS = 128  # 50% brightness (128/255)
STATUS_LED_BLINK_DURATION = 0.2    # 200ms blink duration

# LED Status patterns
LED_PATTERNS = {
    "system_ready": (1, 0.5),      # 1 blink, 0.5s interval
    "usb_mounted": (2, 0.3),       # 2 blinks, 0.3s interval  
    "usb_error": (3, 0.2),         # 3 blinks, 0.2s interval
    "audio_playing": (0.1, 0.1),   # Fast blink while playing
    "system_error": (5, 0.1),      # 5 blinks, 0.1s interval
}

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "audio_server.log"
