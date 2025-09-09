#!/usr/bin/env python3
"""
Button Audio Test - Direct serial to audio mapping
Based on working mattsfx listener.py
"""
import os
import time
import serial
import glob
import random

# ALSA device configuration (from working code)
os.environ.setdefault("SDL_AUDIODRIVER", "alsa")
os.environ.setdefault("AUDIODEV", "plughw:0,0")

# Audio settings
MIX_FREQ = 44100
MIX_BUF = 256
BAUD = 115200

# Audio file mappings
AUDIO_FILES = {
    "button1": "button1.wav",
    "button2": "button2.wav", 
    "hold1": "hold1.wav",
    "hold2": "hold2.wav"
}

def find_audio_files():
    """Find audio files in audio_files directory"""
    audio_dir = "audio_files"
    if not os.path.exists(audio_dir):
        print(f"❌ Audio directory {audio_dir} not found")
        return {}
    
    found_files = {}
    for key, filename in AUDIO_FILES.items():
        filepath = os.path.join(audio_dir, filename)
        if os.path.exists(filepath):
            found_files[key] = filepath
            print(f"✅ Found: {filename}")
        else:
            print(f"❌ Missing: {filename}")
    
    return found_files

def init_audio():
    """Initialize pygame audio"""
    try:
        import pygame
        pygame.mixer.init(frequency=MIX_FREQ, size=-16, channels=2, buffer=MIX_BUF)
        print("✅ Audio system initialized")
        return True
    except Exception as e:
        print(f"❌ Audio init failed: {e}")
        return False

def play_audio(filepath):
    """Play audio file"""
    try:
        import pygame
        if not os.path.exists(filepath):
            print(f"❌ Audio file not found: {filepath}")
            return False
        
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        print(f"🎵 Playing: {os.path.basename(filepath)}")
        
        # Wait for playback to complete
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        return True
    except Exception as e:
        print(f"❌ Audio playback failed: {e}")
        return False

def classify_command(line):
    """Classify button command"""
    line = line.strip().upper()
    
    # Support different formats
    if "BTN1" in line and "HOLD" in line:
        return "hold1"
    elif "BTN2" in line and "HOLD" in line:
        return "hold2"
    elif "BTN1" in line:
        return "button1"
    elif "BTN2" in line:
        return "button2"
    elif line == "1" or line == "BTN1":
        return "button1"
    elif line == "2" or line == "BTN2":
        return "button2"
    
    return None

def connect_serial():
    """Connect to serial port"""
    prefs = ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/serial0", "/dev/ttyAMA0", "/dev/ttyS0"]
    
    for port in prefs:
        try:
            ser = serial.Serial(port, BAUD, timeout=0.1)
            print(f"✅ Connected to {port}")
            return ser
        except Exception as e:
            print(f"❌ Failed to connect to {port}: {e}")
            continue
    
    print("❌ No serial ports available")
    return None

def main():
    print("🎵 WRB Button Audio Test")
    print("=" * 40)
    
    # Step 1: Find audio files
    print("\n1. Checking audio files...")
    audio_files = find_audio_files()
    if not audio_files:
        print("❌ No audio files found. Run: python3 create_test_audio.py")
        return
    
    # Step 2: Initialize audio
    print("\n2. Initializing audio system...")
    if not init_audio():
        return
    
    # Step 3: Connect to serial
    print("\n3. Connecting to serial port...")
    ser = connect_serial()
    if not ser:
        return
    
    # Step 4: Test audio files
    print("\n4. Testing audio files...")
    for key, filepath in audio_files.items():
        print(f"Testing {key}...")
        play_audio(filepath)
        time.sleep(0.5)
    
    # Step 5: Monitor for button presses
    print("\n5. Monitoring for button presses...")
    print("Press buttons on XIAO transmitter to test!")
    print("Expected commands: BTN1:PRESS, BTN2:PRESS, BTN1:HOLD, BTN2:HOLD")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            try:
                line = ser.readline().decode(errors="ignore").strip()
                if line:
                    print(f"📨 Received: {line}")
                    
                    # Classify command
                    command = classify_command(line)
                    if command and command in audio_files:
                        print(f"🎯 Playing: {command}")
                        play_audio(audio_files[command])
                    else:
                        print(f"❓ Unknown command: {line}")
                        
            except Exception as e:
                print(f"❌ Serial error: {e}")
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n👋 Test completed!")
    finally:
        if ser:
            ser.close()

if __name__ == "__main__":
    main()
