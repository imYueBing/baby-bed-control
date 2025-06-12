#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arduino Base Controller Module - Responsible for basic serial communication with Arduino
"""

import json
import logging
import queue
import serial
import threading
import time

# Configure logging
logger = logging.getLogger(__name__)

class BaseArduinoController:
    """Arduino Base Controller Class, handles basic serial communication"""
    
    def __init__(self, port, baud_rate=9600, timeout=1):
        """
        Initialize Arduino base controller
        
        Args:
            port (str): Serial port (e.g., '/dev/ttyUSB0')
            baud_rate (int): Baud rate
            timeout (float): Read timeout (seconds)
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial = None
        self.is_connected = False
        self.read_thread = None
        self.running = False
        
        # Command queue
        self.command_queue = queue.Queue()
        
        # Try to connect
        self._connect()
    
    def _connect(self):
        """Try to connect to Arduino"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout
                # Try adding dsrdtr=False if experiencing connection issues
                # dsrdtr=False 
            )
            
            # For many Arduino boards, opening the serial port causes a reset.
            # This delay gives the Arduino enough time to complete the reset and be ready to receive data.
            logger.info("Waiting for Arduino board reset and initialization (typically takes 1-2 seconds)...")
            time.sleep(2) 
            
            self.serial.flushInput() # Clear any initial data Arduino might have sent before Python was ready
            
            # Try to read Arduino's initial ready message (optional)
            # This helps confirm two-way communication, but it's not a critical error if Arduino didn't send one or it was cleared by flushInput
            try:
                initial_message = self.serial.readline().decode('utf-8').strip()
                if initial_message:
                    logger.info(f"Received initial message from Arduino: {initial_message}")
                else:
                    logger.debug("No initial ready message received from Arduino (might have been cleared or not sent).")
            except Exception as e:
                logger.debug(f"Error reading initial message (can be ignored): {e}")


            logger.info(f"Connected to Arduino: {self.port}")
            self.is_connected = True
            
            # Start read thread
            self.running = True
            self.read_thread = threading.Thread(target=self._read_loop)
            self.read_thread.daemon = True
            self.read_thread.start()
            
            # Start command processing thread
            self.command_thread = threading.Thread(target=self._command_loop)
            self.command_thread.daemon = True
            self.command_thread.start()
            
            # Request system status
            self.get_system_status()
            
        except serial.SerialException as e:
            logger.error(f"Could not connect to Arduino (port: {self.port}, baud rate: {self.baud_rate}): Detailed error: {e}")
            self.is_connected = False
        except Exception as ex:
            logger.error(f"Unexpected error while connecting to Arduino (port: {self.port}): {ex}", exc_info=True)
            self.is_connected = False
    
    def reconnect(self):
        """Reconnect to Arduino"""
        if self.is_connected:
            self.close()
        self._connect()
    
    def close(self):
        """Close connection"""
        self.running = False
        
        if self.read_thread:
            if self.read_thread.is_alive():
                self.read_thread.join(timeout=1)
        
        if self.command_thread:
            if self.command_thread.is_alive():
                self.command_thread.join(timeout=1)
        
        if self.serial and self.serial.is_open:
            self.serial.close()
            logger.info("Arduino connection closed")
        
        self.is_connected = False
    
    def _read_loop(self):
        """Loop for reading data from Arduino"""
        while self.running and self.serial and self.serial.is_open:
            try:
                if self.serial.in_waiting > 0:
                    line = self.serial.readline().decode('utf-8').strip()
                    if line:
                        logger.debug(f"Raw received from Arduino: {line}") # Add raw data log
                        self._process_response(line) # Pass the raw line directly to the processing function
            except serial.SerialException as e:
                logger.error(f"Serial read error: {e}")
                self.is_connected = False
                break
            except Exception as e:
                logger.error(f"Error in read loop: {e}")
            
            # Brief pause to avoid high CPU usage
            time.sleep(0.01)
    
    def _command_loop(self):
        """Command processing loop - get commands from queue and send them"""
        while self.running and self.serial and self.serial.is_open:
            try:
                # Get command from queue (blocking, wait 1 second)
                try:
                    # command_to_send should now be a complete string, including \n
                    command_to_send = self.command_queue.get(timeout=1) 
                except queue.Empty:
                    continue
                
                # Send command
                if self.serial and self.serial.is_open:
                    encoded_command = command_to_send.encode('utf-8')
                    self.serial.write(encoded_command)
                    logger.debug(f"Command sent to Arduino: {command_to_send.strip()}")
                    logger.debug(f"Bytes sent: {[b for b in encoded_command]}")
                
                self.command_queue.task_done()
                time.sleep(0.1) # Brief wait to avoid sending commands too quickly
                
            except serial.SerialException as e:
                logger.error(f"Serial write error: {e}")
                self.is_connected = False
                break
            except Exception as e:
                logger.error(f"Error in command loop: {e}")
    
    def _process_response(self, response_line):
        """
        Process response from Arduino (simplified to directly process string)
        Subclasses can override this method for more specific processing.
        """
        logger.info(f"Arduino response: {response_line}")
        # In this simplified version, we just log the response.
        # In a real application, you would parse the response and trigger appropriate events or update state here.
        # For example, you could check response_line.startswith("CONFIRMED:") etc.
        
        # To allow subcontrollers to handle, we still call a method that can be overridden
        self._handle_specific_response(response_line)

    def _handle_specific_response(self, response_line):
        """
        Implemented by subclasses to handle specific responses.
        """
        pass # Subclasses will implement this

    def send_command(self, command_string): # Modified parameter to simple string
        """
        Send a simple string command to Arduino, ensuring it ends with a newline.
        
        Args:
            command_string (str): Command string to send (e.g., "UP", "DOWN")
        
        Returns:
            bool: Whether the command was successfully added to the send queue
        """
        if not self.is_connected:
            logger.warning(f"Arduino not connected, cannot send command: {command_string}")
            return False
        
        # Ensure command ends with a newline
        if not command_string.endswith('\n'):
            command_to_send = command_string + '\n'
        else:
            command_to_send = command_string
            
        self.command_queue.put(command_to_send) # Put modified command in queue
        # Note: _command_loop will take it from the queue and .encode('utf-8') to send
        logger.debug(f"Command '{command_string}' added to send queue.")
        return True
    
    def get_system_status(self):
        """Get system status (simplified test, sends a specific command)"""
        return self.send_command("GET_STATUS") # Modified to single command, send_command will add newline automatically 