#!/bin/bash

# WRB Audio System - Dependency Installation Script
# Run this script on your Raspberry Pi to install all required dependencies

echo "🎵 WRB Audio System - Installing Dependencies..."
echo "================================================"

# Update system packages
echo "📦 Updating system packages..."
sudo apt update

# Install Python 3 and pip3 if not already installed
echo "🐍 Installing Python 3 and pip3..."
sudo apt install -y python3 python3-pip python3-venv

# Install system audio dependencies
echo "🔊 Installing audio system dependencies..."
sudo apt install -y alsa-utils pulseaudio python3-rpi.gpio alsa-tools

# Install Python packages from requirements.txt
echo "📚 Installing Python packages..."
pip3 install -r requirements.txt

# Enable serial communication
echo "🔌 Configuring serial communication..."
echo "Note: You may need to run 'sudo raspi-config' to enable serial port"
echo "Navigate to: Interfacing Options → Serial → Enable"

# Set up audio system
echo "🎧 Configuring audio system..."
echo "Available audio devices:"
aplay -l || echo "No audio devices found"

# Test if audio is working
if command -v speaker-test &> /dev/null; then
    echo "Testing audio system..."
    echo "You should hear test tones for 2 seconds..."
    timeout 2s speaker-test -t wav -c 2 || echo "Audio test completed"
else
    echo "Warning: speaker-test not found. Audio may not be properly configured."
fi

# USB Audio setup
echo "🔌 USB Audio Setup:"
echo "If you have a USB audio device, run: python3 usb_audio_setup.py"
echo "This will help configure USB audio as the default device."

# Check GPIO permissions
echo "🔧 Setting up GPIO permissions..."
sudo usermod -a -G gpio $USER
sudo usermod -a -G dialout $USER

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Reboot your Pi: sudo reboot"
echo "2. Test the audio server: python3 audio_server.py"
echo "3. Check the setup guide: cat ../SETUP_GUIDE.md"
echo ""
echo "🔍 If you encounter issues:"
echo "- Check audio: aplay -l"
echo "- Check serial: ls /dev/tty*"
echo "- Check GPIO: groups $USER"
echo ""
echo "🎉 Your WRB Audio System is ready to go!"
