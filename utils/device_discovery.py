#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Device Discovery Utility - Helps discover Arduino devices connected to Raspberry Pi
"""

import logging
import os
import glob
import serial
import time
import json

# Configure logging
logger = logging.getLogger(__name__)

def find_arduino_ports():
    """
    Find possible Arduino serial ports
    
    Returns:
        list: List of possible Arduino serial ports
    """
    # Serial device path patterns for different platforms
    if os.name == 'nt':  # Windows
        ports = ['COM%s' % (i + 1) for i in range(256)]
    else:  # Linux/Mac
        ports = glob.glob('/dev/tty[A-Za-z]*')
    
    # Arduino typically uses these device names
    arduino_patterns = [
        'ttyUSB', 'ttyACM', 'cu.usbmodem', 'cu.usbserial'
    ]
    
    # Filter possible Arduino devices
    result = []
    for port in ports:
        for pattern in arduino_patterns:
            if pattern in port:
                result.append(port)
                break
    
    return result

def test_arduino_port(port, baud_rate=9600, timeout=2):
    """
    Test if port is a valid Arduino device
    
    Args:
        port (str): Serial port to test
        baud_rate (int): Baud rate
        timeout (float): Read timeout in seconds
        
    Returns:
        bool: Whether the port is a valid Arduino device
    """
    try:
        # Try to open the serial port
        ser = serial.Serial(port, baud_rate, timeout=timeout)
        
        # Wait for Arduino reset
        time.sleep(2)
        
        # Flush input buffer
        ser.flushInput()
        
        # Send system status request
        command = json.dumps({'command': 'SYSTEM_STATUS'})
        ser.write(f"{command}\n".encode('utf-8'))
        
        # Read response
        start_time = time.time()
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').strip()
                try:
                    data = json.loads(response)
                    # If response contains type field, consider it a valid Arduino device
                    if 'type' in data:
                        ser.close()
                        return True
                except json.JSONDecodeError:
                    # Ignore non-JSON responses
                    pass
            
            time.sleep(0.1)
        
        # Timeout, close port
        ser.close()
        return False
        
    except (serial.SerialException, OSError) as e:
        logger.debug(f"Error testing port {port}: {e}")
        return False

def discover_arduino_device(baud_rate=9600):
    """
    Automatically discover and test connected Arduino devices
    
    Args:
        baud_rate (int): Baud rate
        
    Returns:
        str or None: Valid Arduino port found, or None if not found
    """
    logger.info("Searching for Arduino devices...")
    
    # Get possible ports
    possible_ports = find_arduino_ports()
    logger.info(f"Found {len(possible_ports)} possible serial ports: {possible_ports}")
    
    # Test each port
    for port in possible_ports:
        logger.info(f"Testing port {port}...")
        if test_arduino_port(port, baud_rate):
            logger.info(f"Found valid Arduino device on port {port}")
            return port
    
    logger.warning("No valid Arduino device found")
    return None

if __name__ == "__main__":
    # If run as standalone script, perform device discovery
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Discover device
    port = discover_arduino_device()
    if port:
        print(f"Arduino device found: {port}")
    else:
        print("No Arduino device found") 