#!/usr/bin/env python3
"""
USB Audio Device Setup and Configuration
Helps configure USB audio devices on Raspberry Pi
"""

import subprocess
import os
import sys

def run_command(cmd, capture_output=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def list_audio_devices():
    """List all available audio devices"""
    print("🔍 Scanning for audio devices...")
    
    # List ALSA devices
    success, stdout, stderr = run_command("aplay -l")
    if success:
        print("\n📱 ALSA Playback Devices:")
        print(stdout)
    else:
        print(f"❌ Error listing ALSA devices: {stderr}")
    
    # List PulseAudio devices
    success, stdout, stderr = run_command("pactl list short sinks")
    if success and stdout.strip():
        print("\n🔊 PulseAudio Sinks:")
        print(stdout)
    else:
        print("\n⚠️  PulseAudio not available or no sinks found")
    
    # List USB devices
    success, stdout, stderr = run_command("lsusb | grep -i audio")
    if success and stdout.strip():
        print("\n🔌 USB Audio Devices:")
        print(stdout)
    else:
        print("\n⚠️  No USB audio devices detected")

def test_audio_device(device_name=None):
    """Test audio output on specified device"""
    print(f"\n🎵 Testing audio output...")
    
    if device_name:
        print(f"Testing device: {device_name}")
        cmd = f"speaker-test -D {device_name} -t wav -c 2 -l 1"
    else:
        print("Testing default device")
        cmd = "speaker-test -t wav -c 2 -l 1"
    
    print(f"Running: {cmd}")
    print("You should hear test tones for 2 seconds...")
    
    success, stdout, stderr = run_command(cmd, capture_output=False)
    
    if success:
        print("✅ Audio test completed successfully")
    else:
        print(f"❌ Audio test failed: {stderr}")

def configure_usb_audio():
    """Configure USB audio as default"""
    print("\n⚙️  Configuring USB audio...")
    
    # Check if USB audio device exists
    success, stdout, stderr = run_command("aplay -l | grep -i usb")
    if not success or not stdout.strip():
        print("❌ No USB audio device found")
        return False
    
    print("✅ USB audio device detected")
    
    # Create ALSA configuration
    # From your output, USB audio is on card 0
    alsa_config = """
# USB Audio Configuration for WRB System
pcm.!default {
    type hw
    card 0
    device 0
}

ctl.!default {
    type hw
    card 0
}
"""
    
    # Write ALSA configuration
    try:
        # Get the home directory dynamically
        home_dir = os.path.expanduser("~")
        asoundrc_path = os.path.join(home_dir, ".asoundrc")
        
        # Ensure the home directory exists
        os.makedirs(home_dir, exist_ok=True)
        
        with open(asoundrc_path, "w") as f:
            f.write(alsa_config)
        print(f"✅ Created {asoundrc_path} configuration")
    except Exception as e:
        print(f"❌ Failed to create ALSA config: {e}")
        print("Try running with sudo or check permissions")
        return False
    
    # Test the configuration
    print("\n🧪 Testing USB audio configuration...")
    test_audio_device()
    
    return True

def create_audio_test_script():
    """Create a script to test audio devices"""
    test_script = """#!/bin/bash
# Audio Device Test Script

echo "=== WRB Audio Device Test ==="
echo ""

echo "1. Listing audio devices:"
aplay -l
echo ""

echo "2. Testing default device:"
speaker-test -t wav -c 2 -l 1
echo ""

echo "3. Testing USB device (if available):"
if aplay -l | grep -i usb; then
    speaker-test -D hw:1,0 -t wav -c 2 -l 1
else
    echo "No USB audio device found"
fi
echo ""

echo "4. Testing with pygame (Python):"
python3 -c "
import pygame
pygame.mixer.init()
pygame.mixer.music.load('audio_files/button1.wav')
pygame.mixer.music.play()
import time
time.sleep(2)
print('Audio test completed')
"
"""
    
    try:
        with open("test_audio.sh", "w") as f:
            f.write(test_script)
        os.chmod("test_audio.sh", 0o755)
        print("✅ Created test_audio.sh script")
        return True
    except Exception as e:
        print(f"❌ Failed to create test script: {e}")
        return False

def main():
    """Main function"""
    print("🎵 WRB USB Audio Setup")
    print("=" * 30)
    
    # List all audio devices
    list_audio_devices()
    
    # Ask user what to do
    print("\n📋 Options:")
    print("1. Test current audio setup")
    print("2. Configure USB audio as default")
    print("3. Create audio test script")
    print("4. Exit")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            test_audio_device()
        elif choice == "2":
            configure_usb_audio()
        elif choice == "3":
            create_audio_test_script()
        elif choice == "4":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
