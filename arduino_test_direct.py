#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Direct Arduino Communication Test Script
Sends simple commands and checks responses
"""

import serial
import time
import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Arduino Communication Test')
    parser.add_argument('--port', type=str, default='/dev/ttyACM0', 
                        help='Arduino serial device (typically /dev/ttyACM0 on Raspberry Pi, /dev/tty.usbmodem* on macOS)')
    parser.add_argument('--baud', type=int, default=9600, help='Baud rate')
    parser.add_argument('--debug', action='store_true', help='Display debug information')
    return parser.parse_args()

def main():
    args = parse_args()
    
    print(f"Attempting to connect to {args.port} (baud rate: {args.baud})...")
    
    try:
        # Open serial connection
        ser = serial.Serial(
            port=args.port,
            baudrate=args.baud,
            timeout=1  # 1 second read timeout
        )
        
        # Wait for Arduino reset (opening serial connection causes Arduino to reset)
        print("Waiting for Arduino reset and initialization...")
        time.sleep(2)
        
        # Clear any data that might be in the buffer
        ser.flushInput()
        
        print("Connection successful! Starting command tests...")
        print("-" * 50)
        
        # Define list of test commands
        commands = [
            "UP",
            "DOWN",
            "STOP",
            "GET_HEART_RATE",
            "GET_STATUS",
            "INVALID_COMMAND"  # Test unknown command handling
        ]
        
        # Test each command
        for cmd in commands:
            print(f"\nSending command: '{cmd}'")
            
            # Ensure command ends with newline
            if not cmd.endswith('\n'):
                cmd_to_send = cmd + '\n'
            else:
                cmd_to_send = cmd
                
            # Send command
            ser.write(cmd_to_send.encode('utf-8'))
            
            # Debug info: show raw bytes sent
            if args.debug:
                print(f"Sent bytes: {[b for b in cmd_to_send.encode('utf-8')]}")
            
            # Wait and read response
            print("Waiting for response...")
            timeout_start = time.time()
            response_received = False
            
            # Try to read response, wait up to 3 seconds
            while time.time() - timeout_start < 3:
                if ser.in_waiting > 0:
                    response = ser.readline().decode('utf-8').strip()
                    print(f"Received response: '{response}'")
                    response_received = True
                    break
                time.sleep(0.1)
            
            if not response_received:
                print("No response received (timeout)")
            
            # Wait a short time between commands
            time.sleep(0.5)
        
        print("\nTests completed!")
        
        # Close connection
        ser.close()
        print("Serial connection closed")
        
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nUser interrupted, closing connection...")
        try:
            ser.close()
        except:
            pass
        return 0
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 