# Audio Files Directory

Place your audio files in this directory with the following naming convention:

## Required Audio Files

- `button1.wav` - Button 1 press audio
- `button2.wav` - Button 2 press audio  
- `hold1.wav` - Button 1 hold audio (plays after 500ms hold)
- `hold2.wav` - Button 2 hold audio (plays after 500ms hold)

## Audio File Requirements

- **Format**: WAV files recommended for best compatibility
- **Sample Rate**: 44.1kHz (44100 Hz)
- **Channels**: Stereo (2 channels) or Mono (1 channel)
- **Bit Depth**: 16-bit recommended
- **File Size**: Keep under 10MB per file for Pi Zero performance

## Supported Formats

The system supports these audio formats:
- WAV (recommended)
- MP3 (requires additional setup)
- OGG (requires additional setup)

## Converting Audio Files

Use ffmpeg to convert your audio files:

```bash
# Convert to WAV format
ffmpeg -i input.mp3 -ar 44100 -ac 2 -sample_fmt s16 output.wav

# Convert to mono WAV
ffmpeg -i input.mp3 -ar 44100 -ac 1 -sample_fmt s16 output.wav
```

## Button Behavior

### **Press vs Hold:**
- **Quick Press**: Plays `button1.wav` or `button2.wav`
- **Hold (500ms+)**: Plays `hold1.wav` or `hold2.wav` instead
- **Hold bypasses press**: If you hold a button, only the hold sound plays

### **Hold Detection:**
- Hold detection is enabled by default
- 500ms hold delay (matches XIAO transmitter timing)
- Can be disabled in `config.py` by setting `HOLD_DETECTION_ENABLED = False`

## Testing Audio Files

You can test audio files on the Pi using:

```bash
# Test with pygame
python3 -c "import pygame; pygame.mixer.init(); pygame.mixer.music.load('button1.wav'); pygame.mixer.music.play()"

# Test with aplay (if available)
aplay button1.wav
```
