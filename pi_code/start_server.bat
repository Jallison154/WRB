@echo off
REM Startup script for WRB Audio Server (Windows)

echo Starting WRB Audio Server...

REM Change to project directory
cd /d "%~dp0"

REM Check if Python dependencies are installed
python -c "import pygame, flask, requests" 2>nul
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
)

REM Check if audio files exist
if not exist "..\audio_files" (
    echo Creating audio_files directory...
    mkdir "..\audio_files"
)

REM Check for required audio files
set missing=0
for %%f in (button1_1.wav button1_2.wav button2_1.wav button2_2.wav) do (
    if not exist "..\audio_files\%%f" (
        echo Warning: Missing audio file: %%f
        set missing=1
    )
)

if %missing%==1 (
    echo Run 'python audio_manager.py' to create test files
)

REM Start the audio server
echo Starting audio server...
python audio_server.py

pause
