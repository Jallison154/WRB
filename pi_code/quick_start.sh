#!/bin/bash

# WRB Audio System - Quick Start Script
# Run this after installing dependencies

echo "🚀 WRB Audio System - Quick Start"
echo "================================="

# Check if we're in the right directory
if [ ! -f "audio_server.py" ]; then
    echo "❌ Error: audio_server.py not found!"
    echo "Please run this script from the pi_code directory"
    exit 1
fi

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "❌ pygame not found. Installing dependencies..."
    chmod +x install_dependencies.sh
    ./install_dependencies.sh
    echo "Please reboot and run this script again."
    exit 1
fi

if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ flask not found. Installing dependencies..."
    chmod +x install_dependencies.sh
    ./install_dependencies.sh
    echo "Please reboot and run this script again."
    exit 1
fi

echo "✅ All dependencies found!"

# Check audio system
echo "🔊 Checking audio system..."
if command -v aplay &> /dev/null; then
    echo "Audio system: ✅ Available"
    aplay -l | head -3
else
    echo "Audio system: ❌ Not available"
fi

# Check serial ports
echo "🔌 Checking serial ports..."
if ls /dev/tty* 2>/dev/null | grep -q "ttyUSB\|ttyACM"; then
    echo "Serial ports: ✅ Available"
    ls /dev/tty* | grep "ttyUSB\|ttyACM"
else
    echo "Serial ports: ⚠️  No USB/ACM devices found"
    echo "Make sure your XIAO receiver is connected"
fi

# Check GPIO
echo "🔧 Checking GPIO access..."
if groups $USER | grep -q "gpio"; then
    echo "GPIO access: ✅ Available"
else
    echo "GPIO access: ⚠️  User not in gpio group"
    echo "Run: sudo usermod -a -G gpio $USER && sudo reboot"
fi

echo ""
echo "🎵 Starting Audio Server..."
echo "Press Ctrl+C to stop"
echo ""

# Start the audio server
python3 audio_server.py
