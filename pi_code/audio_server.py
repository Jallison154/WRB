#!/usr/bin/env python3
"""
Raspberry Pi Audio Server
Handles audio playback triggered by Seeed XIAO controllers
"""

import pygame
import threading
import time
import logging
import os
import json
from flask import Flask, request, jsonify
from config import *
from usb_manager import USBManager
from status_led import StatusLED
from serial_reader import SerialReader

# Initialize pygame mixer for audio playback
pygame.mixer.pre_init(frequency=SAMPLE_RATE, size=-16, channels=CHANNELS, buffer=BUFFER_SIZE)
pygame.mixer.init()

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AudioServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.audio_queue = []
        self.current_audio = None
        self.volume = DEFAULT_VOLUME
        self.usb_manager = USBManager()
        self.status_led = StatusLED()
        self.serial_reader = SerialReader()
        self.setup_routes()
        self.setup_audio_directory()
        
    def setup_audio_directory(self):
        """Create audio directory if it doesn't exist"""
        if not os.path.exists(AUDIO_DIR):
            os.makedirs(AUDIO_DIR)
            logger.info(f"Created audio directory: {AUDIO_DIR}")
            
        # Create placeholder audio files if they don't exist
        for audio_file in AUDIO_MAPPINGS.values():
            file_path = os.path.join(AUDIO_DIR, audio_file)
            if not os.path.exists(file_path):
                logger.warning(f"Audio file not found: {file_path}")
                
    def setup_routes(self):
        """Setup Flask routes for XIAO communication"""
        
        @self.app.route('/trigger_audio', methods=['POST'])
        def trigger_audio():
            """Handle audio trigger requests from XIAO controllers"""
            try:
                data = request.get_json()
                button_id = data.get('button_id')
                is_hold = data.get('is_hold', False)  # New: indicates if this is a hold event
                source = data.get('source', 'direct')  # 'direct', 'xiao_to_xiao', or 'xiao_transmitter'
                
                if not button_id:
                    return jsonify({'error': 'Missing button_id'}), 400
                
                # Determine audio file based on button and hold state
                if is_hold and HOLD_DETECTION_ENABLED:
                    audio_key = f"hold{button_id}"
                else:
                    audio_key = f"button{button_id}"
                    
                audio_file = AUDIO_MAPPINGS.get(audio_key)
                
                if not audio_file:
                    logger.error(f"No audio mapping found for {audio_key}")
                    return jsonify({'error': 'No audio file mapped'}), 404
                    
                # Play audio in separate thread
                threading.Thread(
                    target=self.play_audio, 
                    args=(audio_file,),
                    daemon=True
                ).start()
                
                # Indicate button received on status LED
                if hasattr(self, 'status_led'):
                    self.status_led.indicate_button_received()
                
                event_type = "hold" if is_hold else "press"
                logger.info(f"Triggered audio: {audio_file} from Button{button_id} {event_type} (source: {source})")
                return jsonify({'status': 'success', 'audio_file': audio_file, 'source': source, 'event_type': event_type})
                
            except Exception as e:
                logger.error(f"Error handling audio trigger: {e}")
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/status', methods=['GET'])
        def get_status():
            """Get server status"""
            usb_status = self.usb_manager.get_status()
            return jsonify({
                'status': 'running',
                'current_audio': self.current_audio,
                'volume': self.volume,
                'audio_files': list(AUDIO_MAPPINGS.keys()),
                'esp_now_enabled': ESP_NOW_ENABLED,
                'usb_status': usb_status
            })
            
        @self.app.route('/set_volume', methods=['POST'])
        def set_volume():
            """Set audio volume"""
            try:
                data = request.get_json()
                volume = float(data.get('volume', DEFAULT_VOLUME))
                volume = max(0.0, min(1.0, volume))  # Clamp between 0 and 1
                self.volume = volume
                pygame.mixer.music.set_volume(volume)
                return jsonify({'status': 'success', 'volume': volume})
            except Exception as e:
                return jsonify({'error': str(e)}), 400
                
    def play_audio(self, audio_file):
        """Play audio file"""
        try:
            # First try local audio directory
            file_path = os.path.join(AUDIO_DIR, audio_file)
            
            # If not found locally, check USB drives
            if not os.path.exists(file_path):
                usb_audio_files = self.usb_manager.get_audio_files_from_usb()
                if audio_file in usb_audio_files:
                    file_path = usb_audio_files[audio_file]
                    logger.info(f"Playing audio from USB: {file_path}")
                else:
                    logger.error(f"Audio file not found: {audio_file}")
                    return
            
            # Stop any currently playing audio
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                
            # Set volume and play
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            self.current_audio = audio_file
            logger.info(f"Playing audio: {audio_file}")
            
            # LED indication while playing
            if USB_MOUNT_ENABLED:
                self.usb_manager.led_on()
            
            # Status LED indication while playing
            self.status_led.indicate_audio_playing()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            self.current_audio = None
            logger.info(f"Finished playing: {audio_file}")
            
            # Turn off LEDs after playing
            if USB_MOUNT_ENABLED:
                self.usb_manager.led_off()
            
        except Exception as e:
            logger.error(f"Error playing audio {audio_file}: {e}")
            self.current_audio = None
            if USB_MOUNT_ENABLED:
                self.usb_manager.led_off()
            
    def run(self):
        """Start the audio server"""
        logger.info("Starting Audio Server...")
        logger.info(f"Audio directory: {AUDIO_DIR}")
        logger.info(f"Available audio files: {list(AUDIO_MAPPINGS.keys())}")
        
        # Start USB monitoring
        if USB_MOUNT_ENABLED:
            logger.info("Starting USB auto-mounting...")
            self.usb_manager.start_monitoring()
        
        # Start serial reader for XIAO receiver
        logger.info("Starting serial reader for XIAO receiver...")
        if self.serial_reader.start():
            logger.info("Serial reader started successfully")
        else:
            logger.warning("Failed to start serial reader - XIAO receiver not connected")
        
        # Set status LED to ready state
        self.status_led.set_ready_state(True)
        logger.info("Status LED set to ready state")
        
        # Test audio system
        try:
            pygame.mixer.music.set_volume(self.volume)
            logger.info("Audio system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize audio system: {e}")
            self.status_led.indicate_system_error()
            
        # Start Flask server
        try:
            self.app.run(host='0.0.0.0', port=PI_PORT, debug=False)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        finally:
            if USB_MOUNT_ENABLED:
                self.usb_manager.cleanup()
            self.serial_reader.stop()
            self.status_led.cleanup()

def main():
    """Main function"""
    try:
        server = AudioServer()
        server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    main()
