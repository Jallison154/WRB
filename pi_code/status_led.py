#!/usr/bin/env python3
"""
Status LED Manager for Raspberry Pi
Handles system status LED indication
"""

import time
import threading
import logging
import RPi.GPIO as GPIO
from config import *

logger = logging.getLogger(__name__)

class StatusLED:
    def __init__(self):
        self.led_pin = STATUS_LED_PIN
        self.ready_brightness = STATUS_LED_READY_BRIGHTNESS
        self.blink_duration = STATUS_LED_BLINK_DURATION
        self.is_ready = False
        self.blink_thread = None
        self.blink_active = False
        
        # Setup GPIO
        self.setup_gpio()
        
    def setup_gpio(self):
        """Setup GPIO for status LED"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.led_pin, GPIO.OUT)
            
            # Use PWM for brightness control
            self.pwm = GPIO.PWM(self.led_pin, 1000)  # 1kHz frequency
            self.pwm.start(0)  # Start with 0% duty cycle
            
            logger.info(f"Status LED initialized on GPIO {self.led_pin}")
        except Exception as e:
            logger.error(f"Failed to setup status LED GPIO: {e}")
            
    def set_brightness(self, brightness):
        """Set LED brightness (0-100)"""
        try:
            # Clamp brightness to 0-100 range
            brightness = max(0, min(100, brightness))
            self.pwm.ChangeDutyCycle(brightness)
        except Exception as e:
            logger.error(f"Failed to set LED brightness: {e}")
            
    def turn_on(self, brightness=None):
        """Turn LED on with specified brightness"""
        if brightness is None:
            brightness = self.ready_brightness
        self.set_brightness(brightness)
        
    def turn_off(self):
        """Turn LED off"""
        self.set_brightness(0)
        
    def blink_once(self, brightness=None, duration=None):
        """Blink LED once"""
        if brightness is None:
            brightness = 100  # Full brightness for blink
        if duration is None:
            duration = self.blink_duration
            
        try:
            self.set_brightness(brightness)
            time.sleep(duration)
            self.set_brightness(0)
        except Exception as e:
            logger.error(f"Failed to blink LED: {e}")
            
    def blink_thread_func(self, count, brightness=None, duration=None):
        """Thread function for blinking"""
        if brightness is None:
            brightness = 100
        if duration is None:
            duration = self.blink_duration
            
        try:
            for i in range(count):
                if not self.blink_active:
                    break
                self.set_brightness(brightness)
                time.sleep(duration)
                self.set_brightness(0)
                if i < count - 1:  # Don't sleep after last blink
                    time.sleep(duration)
        except Exception as e:
            logger.error(f"Blink thread error: {e}")
        finally:
            self.blink_active = False
            # Return to ready state if system is ready
            if self.is_ready:
                self.turn_on()
                
    def start_blink(self, count=1, brightness=None, duration=None):
        """Start blinking in background thread"""
        if self.blink_active:
            return  # Already blinking
            
        self.blink_active = True
        self.blink_thread = threading.Thread(
            target=self.blink_thread_func,
            args=(count, brightness, duration),
            daemon=True
        )
        self.blink_thread.start()
        
    def stop_blink(self):
        """Stop current blinking"""
        self.blink_active = False
        if self.blink_thread and self.blink_thread.is_alive():
            self.blink_thread.join(timeout=1)
            
    def set_ready_state(self, ready=True):
        """Set system ready state"""
        self.is_ready = ready
        if ready and not self.blink_active:
            self.turn_on()
        elif not ready:
            self.turn_off()
            
    def indicate_button_received(self):
        """Indicate that a button command was received"""
        if self.is_ready:
            self.start_blink(count=1, brightness=100, duration=0.1)
            
    def indicate_audio_playing(self):
        """Indicate that audio is playing"""
        if self.is_ready:
            self.start_blink(count=1, brightness=100, duration=0.05)
            
    def indicate_system_error(self):
        """Indicate system error"""
        self.start_blink(count=5, brightness=100, duration=0.1)
        
    def cleanup(self):
        """Cleanup GPIO resources"""
        try:
            self.stop_blink()
            self.pwm.stop()
            GPIO.cleanup(self.led_pin)
            logger.info("Status LED cleaned up")
        except Exception as e:
            logger.error(f"Status LED cleanup error: {e}")

def main():
    """Test the status LED"""
    logging.basicConfig(level=logging.INFO)
    
    led = StatusLED()
    
    try:
        print("Testing Status LED...")
        
        # Test ready state
        print("Setting ready state...")
        led.set_ready_state(True)
        time.sleep(2)
        
        # Test button indication
        print("Testing button indication...")
        led.indicate_button_received()
        time.sleep(1)
        
        # Test audio playing indication
        print("Testing audio playing indication...")
        led.indicate_audio_playing()
        time.sleep(1)
        
        # Test error indication
        print("Testing error indication...")
        led.indicate_system_error()
        time.sleep(3)
        
        print("Status LED test complete")
        
    except KeyboardInterrupt:
        print("Stopping Status LED test...")
    finally:
        led.cleanup()

if __name__ == "__main__":
    main()
