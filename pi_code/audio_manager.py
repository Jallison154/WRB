#!/usr/bin/env python3
"""
Audio File Manager for Raspberry Pi
Handles audio file validation, conversion, and management
"""

import os
import subprocess
import logging
from pathlib import Path
from config import AUDIO_DIR, AUDIO_MAPPINGS

logger = logging.getLogger(__name__)

class AudioManager:
    def __init__(self):
        self.audio_dir = Path(AUDIO_DIR)
        self.ensure_audio_directory()
        
    def ensure_audio_directory(self):
        """Create audio directory if it doesn't exist"""
        self.audio_dir.mkdir(exist_ok=True)
        logger.info(f"Audio directory: {self.audio_dir}")
        
    def validate_audio_files(self):
        """Check if all required audio files exist"""
        missing_files = []
        existing_files = []
        
        for audio_file in AUDIO_MAPPINGS.values():
            file_path = self.audio_dir / audio_file
            if file_path.exists():
                existing_files.append(audio_file)
                logger.info(f"Found audio file: {audio_file}")
            else:
                missing_files.append(audio_file)
                logger.warning(f"Missing audio file: {audio_file}")
                
        return existing_files, missing_files
        
    def create_test_audio(self, filename, duration=2):
        """Create a test audio file using ffmpeg"""
        try:
            file_path = self.audio_dir / filename
            cmd = [
                'ffmpeg', '-f', 'lavfi', '-i', f'sine=frequency=440:duration={duration}',
                '-ar', '44100', '-ac', '2', '-sample_fmt', 's16',
                '-y', str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Created test audio file: {filename}")
                return True
            else:
                logger.error(f"Failed to create test audio: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("ffmpeg not found. Install with: sudo apt install ffmpeg")
            return False
        except Exception as e:
            logger.error(f"Error creating test audio: {e}")
            return False
            
    def convert_audio(self, input_file, output_file, sample_rate=44100, channels=2):
        """Convert audio file to required format"""
        try:
            input_path = Path(input_file)
            output_path = self.audio_dir / output_file
            
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-ar', str(sample_rate),
                '-ac', str(channels),
                '-sample_fmt', 's16',
                '-y', str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Converted audio: {input_file} -> {output_file}")
                return True
            else:
                logger.error(f"Audio conversion failed: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("ffmpeg not found. Install with: sudo apt install ffmpeg")
            return False
        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            return False
            
    def get_audio_info(self, filename):
        """Get information about an audio file"""
        try:
            file_path = self.audio_dir / filename
            if not file_path.exists():
                return None
                
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', str(file_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                return info
            else:
                logger.error(f"Failed to get audio info: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return None
            
    def setup_test_audio_files(self):
        """Create test audio files for all required mappings"""
        logger.info("Creating test audio files...")
        
        for key, filename in AUDIO_MAPPINGS.items():
            file_path = self.audio_dir / filename
            if not file_path.exists():
                # Create different tones for each button
                frequency = 440 + (hash(key) % 500)  # Different frequency for each file
                duration = 2
                
                cmd = [
                    'ffmpeg', '-f', 'lavfi', 
                    '-i', f'sine=frequency={frequency}:duration={duration}',
                    '-ar', '44100', '-ac', '2', '-sample_fmt', 's16',
                    '-y', str(file_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"Created test audio: {filename} (freq: {frequency}Hz)")
                else:
                    logger.error(f"Failed to create {filename}: {result.stderr}")
                    
    def list_audio_files(self):
        """List all audio files in the directory"""
        audio_files = []
        for file_path in self.audio_dir.glob("*.wav"):
            size = file_path.stat().st_size
            audio_files.append({
                'name': file_path.name,
                'size': size,
                'size_mb': round(size / (1024 * 1024), 2)
            })
        return audio_files

def main():
    """Test the audio manager"""
    manager = AudioManager()
    
    print("=== Audio File Manager ===")
    
    # Validate existing files
    existing, missing = manager.validate_audio_files()
    print(f"Existing files: {len(existing)}")
    print(f"Missing files: {len(missing)}")
    
    if missing:
        print("\nMissing files:")
        for file in missing:
            print(f"  - {file}")
            
        # Create test files if ffmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            print("\nCreating test audio files...")
            manager.setup_test_audio_files()
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("\nffmpeg not available. Please install with: sudo apt install ffmpeg")
            print("Or manually add your audio files to the audio_files/ directory.")
    
    # List all audio files
    print("\nAudio files in directory:")
    audio_files = manager.list_audio_files()
    for file_info in audio_files:
        print(f"  - {file_info['name']} ({file_info['size_mb']} MB)")

if __name__ == "__main__":
    main()
