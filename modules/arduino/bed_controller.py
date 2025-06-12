#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bed Controller Module - Responsible for controlling baby bed lifting, supports independent left and right control
"""

import logging
from .base_controller import BaseArduinoController

# Configure logging
logger = logging.getLogger(__name__)

class BedController(BaseArduinoController):
    """Bed controller, supports whole bed control and independent left/right control"""
    
    def __init__(self, port, baud_rate=9600, timeout=1):
        """
        Initialize bed controller
        
        Args:
            port (str): Serial port (e.g., '/dev/ttyUSB0')
            baud_rate (int): Baud rate
            timeout (float): Read timeout (seconds)
        """
        super().__init__(port, baud_rate, timeout)
        self.last_bed_response = None
        self.left_status = "stopped"  # Left side status: "up", "down", "stopped"
        self.right_status = "stopped" # Right side status: "up", "down", "stopped"
    
    def _handle_specific_response(self, response_line):
        """Process bed-specific responses from Arduino"""
        if response_line.startswith("CONFIRMED:"):
            self.last_bed_response = response_line
            logger.info(f"BedController confirmation: {response_line}")
            
            # Update internal status
            action = response_line.replace("CONFIRMED:", "").strip()
            self._update_bed_status(action)
            
        elif response_line.startswith("UNKNOWN_CMD:"):
            logger.warning(f"BedController received unknown command reply: {response_line}")
        elif "STATUS" in response_line:
            logger.info(f"BedController status update: {response_line}")
            # Can parse status information here if needed
    
    def _update_bed_status(self, action):
        """Update bed status based on confirmed action"""
        if action == "UP":
            self.left_status = "up"
            self.right_status = "up"
        elif action == "DOWN":
            self.left_status = "down"
            self.right_status = "down"
        elif action == "STOP":
            self.left_status = "stopped"
            self.right_status = "stopped"
        elif action == "LEFT_UP":
            self.left_status = "up"
        elif action == "LEFT_DOWN":
            self.left_status = "down"
        elif action == "LEFT_STOP":
            self.left_status = "stopped"
        elif action == "RIGHT_UP":
            self.right_status = "up"
        elif action == "RIGHT_DOWN":
            self.right_status = "down"
        elif action == "RIGHT_STOP":
            self.right_status = "stopped"
    
    # --------- Whole Bed Control Methods ---------
    
    def bed_up(self):
        """
        Raise the entire bed
        
        Returns:
            bool: Whether the command was sent
        """
        logger.info("Sending whole bed up command UP")
        return self.send_command("UP")
    
    def bed_down(self):
        """
        Lower the entire bed
        
        Returns:
            bool: Whether the command was sent
        """
        logger.info("Sending whole bed down command DOWN")
        return self.send_command("DOWN")
    
    def bed_stop(self):
        """
        Stop all bed movement
        
        Returns:
            bool: Whether the command was sent
        """
        logger.info("Sending whole bed stop command STOP")
        return self.send_command("STOP")
    
    # --------- Left Side Control Methods ---------
    
    def left_up(self):
        """
        Raise the left side of the bed
        
        Returns:
            bool: Whether the command was sent
        """
        logger.info("Sending left side up command LEFT_UP")
        return self.send_command("LEFT_UP")
    
    def left_down(self):
        """
        Lower the left side of the bed
        
        Returns:
            bool: Whether the command was sent
        """
        logger.info("Sending left side down command LEFT_DOWN")
        return self.send_command("LEFT_DOWN")
    
    def left_stop(self):
        """
        Stop left side movement
        
        Returns:
            bool: Whether the command was sent
        """
        logger.info("Sending left side stop command LEFT_STOP")
        return self.send_command("LEFT_STOP")
    
    # --------- Right Side Control Methods ---------
    
    def right_up(self):
        """
        Raise the right side of the bed
        
        Returns:
            bool: Whether the command was sent
        """
        logger.info("Sending right side up command RIGHT_UP")
        return self.send_command("RIGHT_UP")
    
    def right_down(self):
        """
        Lower the right side of the bed
        
        Returns:
            bool: Whether the command was sent
        """
        logger.info("Sending right side down command RIGHT_DOWN")
        return self.send_command("RIGHT_DOWN")
    
    def right_stop(self):
        """
        Stop right side movement
        
        Returns:
            bool: Whether the command was sent
        """
        logger.info("Sending right side stop command RIGHT_STOP")
        return self.send_command("RIGHT_STOP")
    
    # --------- Status Methods ---------
    
    def get_last_response(self):
        """Get the last Arduino response"""
        return self.last_bed_response

    def get_bed_status(self):
        """
        Get current bed status
        
        Returns:
            dict: Dictionary containing left and right side status
        """
        return {
            "left": self.left_status,
            "right": self.right_status
        }
    
    def get_bed_height(self):
        """
        Get current bed height (kept for compatibility with old API)
        
        Returns:
            dict: Dictionary containing bed status information
        """
        logger.debug("Getting bed status")
        # Send GET_STATUS command to get latest status
        self.send_command("GET_STATUS")
        return self.get_bed_status() 