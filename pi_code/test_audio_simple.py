#!/usr/bin/env python3
"""
Simple audio test script based on working mattsfx code
"""
import os
import time
import serial

# ALSA device configuration (from working code)
os.environ.setdefault("SDL_AUDIODRIVER", "alsa")
os.environ.setdefault("AUDIODEV", "plughw:0,0")

# Audio settings
MIX_FREQ = 44100
MIX_BUF = 256

def test_audio():
    """Test audio playback"""
    try:
        import pygame
        pygame.mixer.init(frequency=MIX_FREQ, size=-16, channels=2, buffer=MIX_BUF)
        print("✅ Pygame mixer initialized")
        
        # Test with a simple tone
        pygame.mixer.music.load('audio_files/button1.wav')
        pygame.mixer.music.play()
        print("✅ Playing audio...")
        
        # Wait for playback
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        print("✅ Audio test completed")
        return True
        
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
        return False

def test_serial():
    """Test serial communication"""
    try:
        # Try to connect to serial port
        prefs = ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyUSB0", "/dev/ttyUSB1"]
        
        for port in prefs:
            try:
                ser = serial.Serial(port, 115200, timeout=0.1)
                print(f"✅ Connected to {port}")
                
                # Read a few lines
                for i in range(5):
                    line = ser.readline().decode(errors="ignore").strip()
                    if line:
                        print(f"📨 Received: {line}")
                    time.sleep(0.1)
                
                ser.close()
                return True
                
            except Exception as e:
                print(f"❌ Failed to connect to {port}: {e}")
                continue
        
        print("❌ No serial ports available")
        return False
        
    except Exception as e:
        print(f"❌ Serial test failed: {e}")
        return False

def main():
    print("🧪 WRB Audio System Test")
    print("=" * 30)
    
    # Test 1: Audio files
    print("\n1. Checking audio files...")
    if os.path.exists('audio_files/button1.wav'):
        print("✅ Audio files exist")
    else:
        print("❌ Audio files missing - creating them...")
        os.system('python3 create_test_audio.py')
    
    # Test 2: Audio system
    print("\n2. Testing audio system...")
    test_audio()
    
    # Test 3: Serial communication
    print("\n3. Testing serial communication...")
    test_serial()
    
    print("\n🎯 Test completed!")
    print("If audio test passed, try running: python3 audio_server.py")

if __name__ == "__main__":
    main()
