#!/usr/bin/env python3
"""
Serial Reader for Raspberry Pi
Reads commands from XIAO receiver via serial connection
"""

import serial
import threading
import time
import logging
import requests
from config import *

logger = logging.getLogger(__name__)

class SerialReader:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.running = False
        self.reader_thread = None
        self.pi_server_url = f"http://localhost:{PI_PORT}"
        
    def connect(self):
        """Connect to serial port"""
        # Try multiple serial ports like the working code
        prefs = [self.port, "/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/serial0", "/dev/ttyAMA0", "/dev/ttyS0"]
        
        for port in prefs:
            try:
                self.serial_conn = serial.Serial(
                    port=port,
                    baudrate=self.baudrate,
                    timeout=0.1,  # Match working code timeout
                    write_timeout=1
                )
                logger.info(f"Connected to serial port: {port}")
                self.port = port  # Update the port to the working one
                return True
            except Exception as e:
                logger.debug(f"Failed to connect to {port}: {e}")
                continue
        
        logger.error(f"Failed to connect to any serial port")
        return False
            
    def disconnect(self):
        """Disconnect from serial port"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info("Disconnected from serial port")
            
    def send_to_pi_server(self, button_id, is_hold):
        """Send command to Pi audio server"""
        try:
            url = f"{self.pi_server_url}/trigger_audio"
            payload = {
                "button_id": button_id,
                "is_hold": is_hold,
                "source": "xiao_receiver_serial"
            }
            
            response = requests.post(url, json=payload, timeout=2)
            if response.status_code == 200:
                logger.info(f"Successfully sent to Pi server: Button{button_id} {'HOLD' if is_hold else 'PRESS'}")
                return True
            else:
                logger.error(f"Pi server returned error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send to Pi server: {e}")
            return False
            
    def parse_command(self, command):
        """Parse command from XIAO receiver"""
        try:
            command = command.strip()
            if not command:
                return None, None
                
            # Expected format: "BTN1:PRESS" or "BTN2:HOLD"
            if command.startswith("BTN") and ":" in command:
                parts = command.split(":")
                if len(parts) == 2:
                    button_part = parts[0]  # "BTN1" or "BTN2"
                    action_part = parts[1]  # "PRESS" or "HOLD"
                    
                    # Extract button ID
                    if button_part.startswith("BTN"):
                        button_id = int(button_part[3:])  # Extract number after "BTN"
                        is_hold = (action_part == "HOLD")
                        return button_id, is_hold
                        
            logger.warning(f"Unknown command format: {command}")
            return None, None
            
        except Exception as e:
            logger.error(f"Error parsing command '{command}': {e}")
            return None, None
            
    def reader_loop(self):
        """Main reading loop"""
        logger.info("Serial reader started")
        
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.is_open:
                    # Read line from serial
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore')
                    
                    if line:
                        logger.info(f"Received from XIAO: {line.strip()}")
                        
                        # Parse and forward command
                        button_id, is_hold = self.parse_command(line)
                        if button_id is not None:
                            self.send_to_pi_server(button_id, is_hold)
                else:
                    # Try to reconnect
                    logger.warning("Serial connection lost, attempting to reconnect...")
                    if self.connect():
                        time.sleep(1)
                    else:
                        time.sleep(5)  # Wait before retry
                        
            except Exception as e:
                logger.error(f"Error in serial reader loop: {e}")
                time.sleep(1)
                
        logger.info("Serial reader stopped")
        
    def start(self):
        """Start serial reader"""
        if self.running:
            logger.warning("Serial reader already running")
            return False
            
        if not self.connect():
            return False
            
        self.running = True
        self.reader_thread = threading.Thread(target=self.reader_loop, daemon=True)
        self.reader_thread.start()
        
        logger.info("Serial reader started successfully")
        return True
        
    def stop(self):
        """Stop serial reader"""
        if not self.running:
            return
            
        self.running = False
        
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=5)
            
        self.disconnect()
        logger.info("Serial reader stopped")

def main():
    """Test the serial reader"""
    logging.basicConfig(level=logging.INFO)
    
    # Try different common serial ports
    ports_to_try = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
    
    reader = None
    for port in ports_to_try:
        reader = SerialReader(port=port)
        if reader.connect():
            logger.info(f"Found XIAO receiver on {port}")
            break
        reader.disconnect()
        
    if not reader or not reader.serial_conn:
        logger.error("Could not find XIAO receiver on any serial port")
        return
        
    try:
        reader.start()
        
        # Run for 60 seconds
        time.sleep(60)
        
    except KeyboardInterrupt:
        logger.info("Stopping serial reader...")
    finally:
        reader.stop()

if __name__ == "__main__":
    main()
