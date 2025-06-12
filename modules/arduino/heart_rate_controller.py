#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Heart Rate Controller Module - Responsible for obtaining and processing baby heart rate data
"""

import logging
import threading
import time
from .base_controller import BaseArduinoController

# Configure logging
logger = logging.getLogger(__name__)

class HeartRateController(BaseArduinoController):
    """Simplified heart rate monitor that periodically requests and processes simple responses"""
    
    def __init__(self, port, baud_rate=9600, timeout=1):
        """
        Initialize heart rate controller
        
        Args:
            port (str): Serial port (e.g., '/dev/ttyUSB0')
            baud_rate (int): Baud rate
            timeout (float): Read timeout (seconds)
        """
        super().__init__(port, baud_rate, timeout)
        self.current_heart_rate = None
        self.last_heart_rate_response = None
        self._subscribers = []
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event() # Event to signal thread to stop
        self.consecutive_failures = 0
        self.max_failures = 5
        self.monitoring_interval = 10 # seconds
    
    def _handle_specific_response(self, response_line):
        """Process heart rate specific responses from Arduino"""
        logger.debug(f"Processing heart rate response: '{response_line}'")
        
        # Try multiple possible response formats
        if response_line.startswith("HEART_RATE_DATA:"):
            try:
                rate_str = response_line.split(":")[1].strip()
                self.current_heart_rate = int(rate_str)
                self.last_heart_rate_response = response_line
                self.consecutive_failures = 0 # Reset failures on successful response
                logger.info(f"Heart rate updated: {self.current_heart_rate} BPM")
                self._notify_subscribers(self.current_heart_rate)
            except (IndexError, ValueError) as e:
                logger.warning(f"Failed to parse heart rate data '{response_line}': {e}")
                self.consecutive_failures += 1
        # Check other possible response formats (e.g., [BPM] format)
        elif response_line.startswith("[BPM]"):
            try:
                rate_str = response_line.replace("[BPM]", "").strip()
                self.current_heart_rate = int(rate_str)
                self.last_heart_rate_response = response_line
                self.consecutive_failures = 0
                logger.info(f"Detected [BPM] format heart rate: {self.current_heart_rate} BPM")
                self._notify_subscribers(self.current_heart_rate)
            except (ValueError) as e:
                logger.warning(f"Failed to parse [BPM] format heart rate data '{response_line}': {e}")
                self.consecutive_failures += 1
        # New: Check [HEART] format
        elif response_line.startswith("[HEART]"):
            try:
                rate_str = response_line.replace("[HEART]", "").strip()
                self.current_heart_rate = int(rate_str)
                self.last_heart_rate_response = response_line
                self.consecutive_failures = 0
                logger.info(f"Detected [HEART] format heart rate: {self.current_heart_rate} BPM")
                self._notify_subscribers(self.current_heart_rate)
            except (ValueError) as e:
                logger.warning(f"Failed to parse [HEART] format heart rate data '{response_line}': {e}")
                self.consecutive_failures += 1
        elif response_line.startswith("UNKNOWN_CMD:"):
            logger.warning(f"HeartRateController received unknown command reply: {response_line}")
            self.consecutive_failures += 1
        else:
            # If it's another response, try to find heart rate data in the response
            logger.debug(f"HeartRateController received unexpected response: {response_line}")
            
            # Try to find heart rate data patterns - e.g., "HEART_RATE=XX" or "HEART=XX"
            if "HEART_RATE=" in response_line:
                try:
                    parts = response_line.split("HEART_RATE=")
                    rate_str = parts[1].split(",")[0].strip() if "," in parts[1] else parts[1].strip()
                    self.current_heart_rate = int(rate_str)
                    self.last_heart_rate_response = response_line
                    self.consecutive_failures = 0
                    logger.info(f"Extracted heart rate from status response: {self.current_heart_rate} BPM")
                    self._notify_subscribers(self.current_heart_rate)
                    return
                except (IndexError, ValueError) as e:
                    logger.warning(f"Failed to extract heart rate from status response '{response_line}': {e}")
            # New: Check HEART= format (for STATUS responses)
            elif "HEART=" in response_line:
                try:
                    parts = response_line.split("HEART=")
                    rate_str = parts[1].split(",")[0].strip() if "," in parts[1] else parts[1].strip()
                    self.current_heart_rate = int(rate_str)
                    self.last_heart_rate_response = response_line
                    self.consecutive_failures = 0
                    logger.info(f"Extracted heart rate from status response: {self.current_heart_rate} BPM")
                    self._notify_subscribers(self.current_heart_rate)
                    return
                except (IndexError, ValueError) as e:
                    logger.warning(f"Failed to extract heart rate from status response '{response_line}': {e}")
            
            self.consecutive_failures += 1
    
    def _notify_subscribers(self, heart_rate):
        """
        Notify all heart rate subscribers
        
        Args:
            heart_rate (int): Heart rate value
        """
        for callback in self._subscribers:
            try:
                callback(heart_rate)
            except Exception as e:
                logger.error(f"Error calling heart rate subscriber callback: {e}")
    
    def get_heart_rate(self):
        """Get current heart rate (will be updated by background thread)"""
        # Add detailed logging
        logger.info("Requesting heart rate data...")
        
        # Send command and ensure it was sent successfully
        success = self.send_command("GET_HEART_RATE")
        if success:
            logger.info("GET_HEART_RATE command sent, waiting for response...")
            # Wait a short time to receive response
            time.sleep(0.5)
        else:
            logger.error("Failed to send GET_HEART_RATE command")
        
        # Log the returned heart rate value for debugging
        logger.info(f"Current heart rate value: {self.current_heart_rate}")
        return self.current_heart_rate
    
    def subscribe_heart_rate(self, callback):
        """
        Subscribe to heart rate data
        
        Args:
            callback (callable): Callback function to call when new heart rate data is received, with heart rate as parameter
        """
        if callback not in self._subscribers:
            self._subscribers.append(callback)
        self.start_monitoring() # Start monitoring when first subscriber is added
    
    def unsubscribe_heart_rate(self, callback):
        """
        Unsubscribe from heart rate data
        
        Args:
            callback (callable): Previously registered callback function
        """
        if callback in self._subscribers:
            self._subscribers.remove(callback)
        if not self._subscribers: # Stop monitoring if no subscribers left
            self.stop_monitoring()
    
    def _monitoring_loop(self):
        logger.info("Starting heart rate monitoring loop...")
        while not self._stop_monitoring.is_set():
            if not self.is_connected:
                logger.warning("Heart rate monitoring: Arduino not connected, pausing.")
                self.consecutive_failures +=1 # Increment failures if not connected
            else:
                logger.debug("Heart rate monitoring: Sending GET_HEART_RATE command")
                success = self.send_command("GET_HEART_RATE")
                if not success:
                    self.consecutive_failures += 1
                # Response processing and failure counting will happen in _handle_specific_response
            
            if self.consecutive_failures >= self.max_failures:
                logger.error(f"Failed to get valid heart rate response {self.max_failures} consecutive times, stopping monitoring.")
                self.stop_monitoring() # This will set the event and loop will exit
                break # Exit loop immediately

            # Wait for the next interval, checking the stop event frequently
            self._stop_monitoring.wait(self.monitoring_interval)
        logger.info("Heart rate monitoring loop has stopped.")

    def start_monitoring(self):
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            logger.debug("Heart rate monitoring is already running.")
            return
        if not self.is_connected:
            logger.warning("Cannot start heart rate monitoring: Arduino not connected.")
            return
            
        self._stop_monitoring.clear() # Clear stop event before starting
        self.consecutive_failures = 0 # Reset failure counter
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self._monitoring_thread.daemon = True
        self._monitoring_thread.start()

    def stop_monitoring(self):
        logger.info("Stopping heart rate monitoring...")
        self._stop_monitoring.set() # Signal the thread to stop
        # Joining the thread will be handled by the main close() method if necessary

    def close(self):
        self.stop_monitoring() # Ensure monitoring stops
        if self._monitoring_thread and self._monitoring_thread.is_alive():
             logger.debug("Waiting for heart rate monitoring thread to end...")
             self._monitoring_thread.join(timeout=2) # Wait for thread to finish
        super().close() # Call parent's close method 