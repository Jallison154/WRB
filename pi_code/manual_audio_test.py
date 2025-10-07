#!/usr/bin/env python3
"""
Manual Audio Test - Test audio system without XIAO communication
"""

import os
import sys
import pygame
import time
from config import *

def test_audio_system():
    """Test the audio system directly"""
    print("🧪 Manual Audio Test")
    print("=" * 50)
    
    # Set up pygame with ALSA configuration
    os.environ.setdefault("SDL_AUDIODRIVER", "alsa")
    os.environ.setdefault("AUDIODEV", "plughw:0,0")
    
    pygame.mixer.pre_init(frequency=SAMPLE_RATE, size=-16, channels=CHANNELS, buffer=BUFFER_SIZE)
    pygame.mixer.init()
    
    print(f"Audio device: {os.environ.get('AUDIODEV', 'default')}")
    print(f"Sample rate: {SAMPLE_RATE}")
    print(f"Channels: {CHANNELS}")
    print(f"Buffer size: {BUFFER_SIZE}")
    
    # Test each audio file
    audio_files = [
        "button1.wav",
        "button2.wav", 
        "hold1.wav",
        "hold2.wav"
    ]
    
    for audio_file in audio_files:
        file_path = os.path.join(AUDIO_DIR, audio_file)
        if os.path.exists(file_path):
            print(f"\n🎵 Testing {audio_file}...")
            try:
                sound = pygame.mixer.Sound(file_path)
                sound.play()
                print(f"✅ Playing {audio_file}")
                time.sleep(2)  # Wait for sound to finish
            except Exception as e:
                print(f"❌ Error playing {audio_file}: {e}")
        else:
            print(f"❌ Audio file not found: {file_path}")
    
    print("\n🎯 Manual test completed!")
    print("If you heard all sounds, the audio system is working correctly.")

if __name__ == "__main__":
    test_audio_system()
