#!/bin/bash
# Startup script for WRB Audio Server

echo "Starting WRB Audio Server..."

# Change to project directory
cd "$(dirname "$0")"

# Check if Python dependencies are installed
if ! python3 -c "import pygame, flask, requests" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Check if audio files exist
if [ ! -d "../audio_files" ]; then
    echo "Creating audio_files directory..."
    mkdir -p ../audio_files
fi

# Check for required audio files
missing_files=()
for file in "button1_1.wav" "button1_2.wav" "button2_1.wav" "button2_2.wav"; do
    if [ ! -f "../audio_files/$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "Warning: Missing audio files:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    echo "Run 'python3 audio_manager.py' to create test files"
fi

# Check USB audio device
if ! aplay -l | grep -q "USB"; then
    echo "Warning: No USB audio device detected"
    echo "Check USB audio card connection"
fi

# Start the audio server
echo "Starting audio server..."
python3 audio_server.py
