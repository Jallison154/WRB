#!/usr/bin/env python3
"""
USB Auto-mounting Manager for Raspberry Pi
Handles USB drive detection, mounting, and LED status indication
"""

import os
import time
import subprocess
import logging
import threading
import RPi.GPIO as GPIO
from pathlib import Path
from config import *

logger = logging.getLogger(__name__)

class USBManager:
    def __init__(self):
        self.mounted_devices = {}
        self.usb_led_pin = USB_LED_PIN
        self.mount_point = USB_MOUNT_POINT
        self.audio_dir = USB_AUDIO_DIR
        self.running = False
        self.led_thread = None
        
        # Setup GPIO for LED
        self.setup_gpio()
        
        # Create mount point if it doesn't exist
        self.ensure_mount_point()
        
    def setup_gpio(self):
        """Setup GPIO for USB status LED"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.usb_led_pin, GPIO.OUT)
            GPIO.output(self.usb_led_pin, GPIO.LOW)
            logger.info(f"GPIO {self.usb_led_pin} configured for USB status LED")
        except Exception as e:
            logger.error(f"Failed to setup GPIO: {e}")
            
    def ensure_mount_point(self):
        """Create mount point directory if it doesn't exist"""
        try:
            Path(self.mount_point).mkdir(parents=True, exist_ok=True)
            logger.info(f"Mount point ready: {self.mount_point}")
        except Exception as e:
            logger.error(f"Failed to create mount point: {e}")
            
    def get_usb_devices(self):
        """Get list of connected USB storage devices"""
        try:
            # Use lsblk to find USB storage devices
            result = subprocess.run(['lsblk', '-o', 'NAME,TYPE,MOUNTPOINT,LABEL'], 
                                  capture_output=True, text=True)
            
            usb_devices = []
            for line in result.stdout.split('\n'):
                if 'disk' in line and '/dev/sd' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        device = f"/dev/{parts[0]}"
                        mount_point = parts[2] if len(parts) > 2 else ""
                        label = parts[3] if len(parts) > 3 else ""
                        usb_devices.append({
                            'device': device,
                            'mount_point': mount_point,
                            'label': label
                        })
            
            return usb_devices
        except Exception as e:
            logger.error(f"Failed to get USB devices: {e}")
            return []
            
    def is_mounted(self, device):
        """Check if device is already mounted"""
        try:
            result = subprocess.run(['mount'], capture_output=True, text=True)
            return device in result.stdout
        except Exception as e:
            logger.error(f"Failed to check mount status: {e}")
            return False
            
    def mount_device(self, device, label=""):
        """Mount a USB device"""
        try:
            # Create unique mount point for this device
            if label:
                mount_path = os.path.join(self.mount_point, label)
            else:
                device_name = os.path.basename(device)
                mount_path = os.path.join(self.mount_point, device_name)
                
            # Create mount directory
            Path(mount_path).mkdir(parents=True, exist_ok=True)
            
            # Mount the device
            cmd = ['sudo', 'mount', device, mount_path]
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  timeout=USB_MOUNT_TIMEOUT)
            
            if result.returncode == 0:
                logger.info(f"Successfully mounted {device} to {mount_path}")
                self.mounted_devices[device] = {
                    'mount_path': mount_path,
                    'label': label,
                    'mounted_at': time.time()
                }
                return True
            else:
                logger.error(f"Failed to mount {device}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Mount timeout for {device}")
            return False
        except Exception as e:
            logger.error(f"Error mounting {device}: {e}")
            return False
            
    def unmount_device(self, device):
        """Unmount a USB device"""
        try:
            if device in self.mounted_devices:
                mount_path = self.mounted_devices[device]['mount_path']
                
                cmd = ['sudo', 'umount', mount_path]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"Successfully unmounted {device}")
                    del self.mounted_devices[device]
                    
                    # Remove empty mount directory
                    try:
                        os.rmdir(mount_path)
                    except OSError:
                        pass  # Directory not empty or doesn't exist
                        
                    return True
                else:
                    logger.error(f"Failed to unmount {device}: {result.stderr}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error unmounting {device}: {e}")
            return False
            
    def get_audio_files_from_usb(self):
        """Get audio files from all mounted USB devices"""
        audio_files = {}
        
        for device, info in self.mounted_devices.items():
            mount_path = info['mount_path']
            audio_path = os.path.join(mount_path, self.audio_dir)
            
            if os.path.exists(audio_path):
                try:
                    for file in os.listdir(audio_path):
                        if file.lower().endswith(('.wav', '.mp3', '.ogg')):
                            # Use device label as prefix to avoid conflicts
                            key = f"{info['label']}_{file}" if info['label'] else file
                            audio_files[key] = os.path.join(audio_path, file)
                            logger.info(f"Found USB audio file: {key}")
                except Exception as e:
                    logger.error(f"Error reading audio files from {audio_path}: {e}")
                    
        return audio_files
        
    def led_blink_pattern(self, pattern_name):
        """Blink LED in specified pattern"""
        if pattern_name not in LED_PATTERNS:
            logger.error(f"Unknown LED pattern: {pattern_name}")
            return
            
        blinks, interval = LED_PATTERNS[pattern_name]
        
        try:
            for i in range(int(blinks)):
                GPIO.output(self.usb_led_pin, GPIO.HIGH)
                time.sleep(interval)
                GPIO.output(self.usb_led_pin, GPIO.LOW)
                time.sleep(interval)
        except Exception as e:
            logger.error(f"LED pattern error: {e}")
            
    def led_on(self):
        """Turn LED on"""
        try:
            GPIO.output(self.usb_led_pin, GPIO.HIGH)
        except Exception as e:
            logger.error(f"LED on error: {e}")
            
    def led_off(self):
        """Turn LED off"""
        try:
            GPIO.output(self.usb_led_pin, GPIO.LOW)
        except Exception as e:
            logger.error(f"LED off error: {e}")
            
    def check_usb_devices(self):
        """Check for USB devices and mount/unmount as needed"""
        if not USB_MOUNT_ENABLED:
            return
            
        current_devices = self.get_usb_devices()
        current_device_paths = {dev['device'] for dev in current_devices}
        mounted_device_paths = set(self.mounted_devices.keys())
        
        # Mount new devices
        for device_info in current_devices:
            device = device_info['device']
            if device not in mounted_device_paths and not self.is_mounted(device):
                logger.info(f"New USB device detected: {device}")
                if self.mount_device(device, device_info['label']):
                    self.led_blink_pattern("usb_mounted")
                else:
                    self.led_blink_pattern("usb_error")
                    
        # Unmount removed devices
        for device in mounted_device_paths:
            if device not in current_device_paths:
                logger.info(f"USB device removed: {device}")
                self.unmount_device(device)
                
    def start_monitoring(self):
        """Start USB monitoring in background thread"""
        if not USB_MOUNT_ENABLED:
            logger.info("USB monitoring disabled")
            return
            
        self.running = True
        
        def monitor_loop():
            logger.info("Starting USB monitoring...")
            self.led_blink_pattern("system_ready")
            
            while self.running:
                try:
                    self.check_usb_devices()
                    time.sleep(USB_CHECK_INTERVAL)
                except Exception as e:
                    logger.error(f"USB monitoring error: {e}")
                    self.led_blink_pattern("system_error")
                    time.sleep(USB_CHECK_INTERVAL)
                    
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop USB monitoring"""
        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
            
        # Unmount all devices
        for device in list(self.mounted_devices.keys()):
            self.unmount_device(device)
            
        # Turn off LED
        self.led_off()
        
    def get_status(self):
        """Get USB manager status"""
        return {
            'enabled': USB_MOUNT_ENABLED,
            'mounted_devices': len(self.mounted_devices),
            'devices': list(self.mounted_devices.keys()),
            'audio_files': len(self.get_audio_files_from_usb())
        }
        
    def cleanup(self):
        """Cleanup GPIO and resources"""
        try:
            self.stop_monitoring()
            GPIO.cleanup()
            logger.info("USB Manager cleaned up")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

def main():
    """Test the USB manager"""
    logging.basicConfig(level=logging.INFO)
    
    usb_manager = USBManager()
    
    try:
        print("Testing USB Manager...")
        usb_manager.start_monitoring()
        
        # Run for 30 seconds
        time.sleep(30)
        
        print("USB Manager Status:")
        status = usb_manager.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
            
    except KeyboardInterrupt:
        print("Stopping USB Manager...")
    finally:
        usb_manager.cleanup()

if __name__ == "__main__":
    main()
