#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arduino Controller Module - Integrates bed control and heart rate monitoring functions
"""

import logging
from .bed_controller import BedController
from .heart_rate_controller import HeartRateController
from utils.device_discovery import discover_arduino_device

# Configure logging
logger = logging.getLogger(__name__)

class ArduinoController:
    """
    Arduino Controller Class, integrates bed control and heart rate monitoring functions
    
    This class is a façade (Facade pattern), simplifying interactions with Arduino,
    using specialized controllers internally to handle different types of functionality
    """
    
    def __init__(self, port=None, baud_rate=9600, timeout=1):
        """
        Initialize Arduino controller
        
        Args:
            port (str, optional): Serial port, if None will auto-discover
            baud_rate (int): Baud rate
            timeout (float): Read timeout (seconds)
        """
        # If no port specified, try auto-discovery
        if port is None:
            port = discover_arduino_device(baud_rate)
            if port:
                logger.info(f"Auto-discovered Arduino device: {port}")
            else:
                logger.warning("No Arduino device found, will use simulated device")
                port = "/dev/ttyNONEXISTENT"  # Use non-existent port, controller will enter offline mode
        
        # Create specialized controllers
        self.bed_controller = BedController(port, baud_rate, timeout)
        self.heart_rate_controller = HeartRateController(port, baud_rate, timeout)
        
        # Controller connection status
        self.is_connected = (self.bed_controller.is_connected and 
                            self.heart_rate_controller.is_connected)
    
    # --------- Bed Control Related Methods ---------
    
    def bed_up(self):
        """
        Raise the entire bed
        
        Returns:
            bool: Whether the command was sent
        """
        return self.bed_controller.bed_up()
    
    def bed_down(self):
        """
        Lower the entire bed
        
        Returns:
            bool: Whether the command was sent
        """
        return self.bed_controller.bed_down()
    
    def bed_stop(self):
        """
        Stop all bed movement
        
        Returns:
            bool: Whether the command was sent
        """
        return self.bed_controller.bed_stop()
    
    def left_up(self):
        """
        Raise the left side of the bed
        
        Returns:
            bool: Whether the command was sent
        """
        return self.bed_controller.left_up()
    
    def left_down(self):
        """
        Lower the left side of the bed
        
        Returns:
            bool: Whether the command was sent
        """
        return self.bed_controller.left_down()
    
    def left_stop(self):
        """
        Stop left side bed movement
        
        Returns:
            bool: Whether the command was sent
        """
        return self.bed_controller.left_stop()
    
    def right_up(self):
        """
        Raise the right side of the bed
        
        Returns:
            bool: Whether the command was sent
        """
        return self.bed_controller.right_up()
    
    def right_down(self):
        """
        Lower the right side of the bed
        
        Returns:
            bool: Whether the command was sent
        """
        return self.bed_controller.right_down()
    
    def right_stop(self):
        """
        Stop right side bed movement
        
        Returns:
            bool: Whether the command was sent
        """
        return self.bed_controller.right_stop()
    
    def get_bed_status(self):
        """
        Get current bed status
        
        Returns:
            dict: Bed status information
        """
        return self.bed_controller.get_bed_status()
    
    def get_bed_height(self):
        """
        Get current bed height (kept for compatibility with old API)
        
        Returns:
            dict: Bed status information
        """
        return self.get_bed_status()
    
    # --------- Heart Rate Monitoring Related Methods ---------
    
    def get_heart_rate(self):
        """
        Get current heart rate
        
        Returns:
            int or None: Current heart rate, or None if unknown
        """
        return self.heart_rate_controller.get_heart_rate()
    
    def subscribe_heart_rate(self, callback):
        """
        Subscribe to heart rate data
        
        Args:
            callback (callable): Callback function to call when new heart rate data is received, with heart rate as parameter
        """
        self.heart_rate_controller.subscribe_heart_rate(callback)
    
    def unsubscribe_heart_rate(self, callback):
        """
        Unsubscribe from heart rate data
        
        Args:
            callback (callable): Previously registered callback function
        """
        self.heart_rate_controller.unsubscribe_heart_rate(callback)
    
    # --------- General Methods ---------
    
    def close(self):
        """Close all controller connections"""
        self.bed_controller.close()
        self.heart_rate_controller.close()
    
    def get_system_status(self):
        """
        Get system status
        
        Returns:
            dict: System status information
        """
        return {
            'bed_height': self.get_bed_height(),
            'heart_rate': self.get_heart_rate()
        } 