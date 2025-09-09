#!/usr/bin/env python3
"""
Create test audio files for WRB system
Generates simple tone-based WAV files for testing
"""

import numpy as np
import wave
import os

def create_tone(frequency, duration, sample_rate=44100, amplitude=0.3):
    """Create a sine wave tone"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave_data = amplitude * np.sin(2 * np.pi * frequency * t)
    return (wave_data * 32767).astype(np.int16)

def save_wav(filename, wave_data, sample_rate=44100):
    """Save wave data as WAV file"""
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wave_data.tobytes())

def main():
    """Create test audio files"""
    # Create audio_files directory if it doesn't exist
    audio_dir = "audio_files"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
        print(f"Created directory: {audio_dir}")
    
    # Audio file specifications
    audio_files = {
        "button1.wav": {"freq": 440, "duration": 0.5, "desc": "Button 1 press (A4 note)"},
        "button2.wav": {"freq": 523, "duration": 0.5, "desc": "Button 2 press (C5 note)"},
        "hold1.wav": {"freq": 330, "duration": 2.0, "desc": "Button 1 hold (E4 note)"},
        "hold2.wav": {"freq": 392, "duration": 2.0, "desc": "Button 2 hold (G4 note)"}
    }
    
    print("Creating test audio files...")
    
    for filename, specs in audio_files.items():
        filepath = os.path.join(audio_dir, filename)
        
        # Create tone
        wave_data = create_tone(specs["freq"], specs["duration"])
        
        # Save WAV file
        save_wav(filepath, wave_data)
        
        print(f"✓ Created {filename} - {specs['desc']} ({specs['freq']}Hz, {specs['duration']}s)")
    
    print(f"\n✅ All test audio files created in '{audio_dir}/' directory")
    print("\nAudio file mapping:")
    print("- button1.wav: Quick press sound (440Hz)")
    print("- button2.wav: Quick press sound (523Hz)")
    print("- hold1.wav: Long hold sound (330Hz)")
    print("- hold2.wav: Long hold sound (392Hz)")
    
    print(f"\nTo use these files:")
    print(f"1. Copy the '{audio_dir}' folder to your Pi")
    print(f"2. Or copy individual .wav files to your Pi's audio_files directory")
    print(f"3. Start the audio server: python3 audio_server.py")

if __name__ == "__main__":
    main()
