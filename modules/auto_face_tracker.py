#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Auto Face Tracking Module - Automatically adjusts bed position to recognize faces
"""

import logging
import threading
import time
import cv2
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

class AutoFaceTracker:
    """
    Auto Face Tracking Class, automatically adjusts bed position to recognize faces
    """
    
    def __init__(self, camera_manager, arduino_controller, 
                 scan_interval=3.0, 
                 movement_delay=2.0,
                 face_detection_threshold=3,
                 adjustment_sequence=None):
        """
        Initialize auto face tracker
        
        Args:
            camera_manager: Camera manager instance
            arduino_controller: Arduino controller instance
            scan_interval (float): Scan interval time (seconds)
            movement_delay (float): Wait time after movement (seconds)
            face_detection_threshold (int): How many consecutive times without face detection before triggering adjustment
            adjustment_sequence (list): Custom adjustment sequence, if None uses default sequence
        """
        self.camera_manager = camera_manager
        self.arduino_controller = arduino_controller
        self.scan_interval = scan_interval
        self.movement_delay = movement_delay
        self.face_detection_threshold = face_detection_threshold
        
        # Adjustment sequence: each element is a dictionary containing action and duration
        self.adjustment_sequence = adjustment_sequence or [
            {"action": "left_up", "duration": 1.0},
            {"action": "stop", "duration": 0.5},
            {"action": "right_up", "duration": 1.0},
            {"action": "stop", "duration": 0.5},
            {"action": "left_down", "duration": 1.0},
            {"action": "stop", "duration": 0.5},
            {"action": "right_down", "duration": 1.0},
            {"action": "stop", "duration": 0.5},
            {"action": "up", "duration": 1.0},
            {"action": "stop", "duration": 0.5},
            {"action": "down", "duration": 1.0},
            {"action": "stop", "duration": 0.5}
        ]
        
        self.is_running = False
        self.tracker_thread = None
        self.current_sequence_index = 0
        self.no_face_count = 0
        self.last_face_detected = False
        
    def start(self):
        """Start auto face tracking"""
        if self.is_running:
            logger.warning("Auto face tracking is already running")
            return False
        
        if not self.camera_manager or not self.camera_manager.is_running:
            logger.error("Camera is not initialized or not running")
            return False
        
        if not self.arduino_controller or not self.arduino_controller.is_connected:
            logger.error("Arduino controller is not initialized or not connected")
            return False
        
        self.is_running = True
        self.tracker_thread = threading.Thread(target=self._tracking_loop)
        self.tracker_thread.daemon = True
        self.tracker_thread.start()
        
        logger.info("Auto face tracking started")
        return True
    
    def stop(self):
        """Stop auto face tracking"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.tracker_thread and self.tracker_thread.is_alive():
            self.tracker_thread.join(timeout=2)
        
        # Stop all bed movement
        if self.arduino_controller and self.arduino_controller.is_connected:
            self.arduino_controller.bed_stop()
        
        logger.info("Auto face tracking stopped")
    
    def _tracking_loop(self):
        """Face tracking main loop"""
        logger.info("Face tracking loop started")
        
        while self.is_running:
            try:
                # Get current frame and detect faces
                frame = self.camera_manager.get_frame()
                faces_detected = self._detect_faces(frame)
                
                if faces_detected:
                    # Face detected, reset counter
                    self.no_face_count = 0
                    if not self.last_face_detected:
                        logger.info("Face detected")
                        self.last_face_detected = True
                else:
                    # No face detected, increment counter
                    self.no_face_count += 1
                    if self.last_face_detected:
                        logger.info("No face detected")
                        self.last_face_detected = False
                
                # If multiple consecutive times without face detection, start adjusting bed position
                if self.no_face_count >= self.face_detection_threshold:
                    logger.info(f"No face detected for {self.no_face_count} consecutive scans, starting bed position adjustment")
                    self._adjust_bed_position()
                    # Reset counter
                    self.no_face_count = 0
                
                # Wait for next scan
                time.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"Error in face tracking loop: {e}")
                time.sleep(1)
    
    def _detect_faces(self, frame):
        """
        Detect faces in frame
        
        Args:
            frame: Video frame in BGR format
            
        Returns:
            bool: Whether a face was detected
        """
        if frame is None:
            return False
        
        # If the camera has AI face detection enabled, we can determine by analyzing green rectangles in the frame
        # This is a simple method, assuming AI face detection draws green rectangles around detected faces
        if self.camera_manager.enable_ai_face_detection:
            # Extract green channel
            green_channel = frame[:, :, 1].copy()
            
            # Threshold processing to extract bright green areas
            _, thresh = cv2.threshold(green_channel, 200, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # If found contours are large enough, they might be green rectangles around faces
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Area threshold, can be adjusted based on actual conditions
                    return True
            
            return False
        else:
            # If AI face detection is not enabled, use OpenCV's Haar cascade classifier
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.1, 5)
                return len(faces) > 0
            except Exception as e:
                logger.error(f"Error in face detection: {e}")
                return False
    
    def _adjust_bed_position(self):
        """Adjust bed position to find faces"""
        logger.info("Starting bed position adjustment")
        
        # Get current action from sequence
        action_info = self.adjustment_sequence[self.current_sequence_index]
        action = action_info["action"]
        duration = action_info["duration"]
        
        # Execute action
        logger.info(f"Executing action: {action}, duration: {duration} seconds")
        self._execute_bed_action(action)
        
        # Wait for specified duration
        time.sleep(duration)
        
        # If action is not stop, stop bed movement
        if action != "stop":
            logger.info("Stopping bed movement")
            self.arduino_controller.bed_stop()
        
        # Wait for bed to stabilize
        time.sleep(self.movement_delay)
        
        # Update sequence index
        self.current_sequence_index = (self.current_sequence_index + 1) % len(self.adjustment_sequence)
    
    def _execute_bed_action(self, action):
        """
        Execute bed action
        
        Args:
            action (str): Action name
        """
        if not self.arduino_controller or not self.arduino_controller.is_connected:
            logger.warning("Arduino controller is not initialized or not connected, cannot execute action")
            return
        
        action_methods = {
            "up": self.arduino_controller.bed_up,
            "down": self.arduino_controller.bed_down,
            "stop": self.arduino_controller.bed_stop,
            "left_up": self.arduino_controller.left_up,
            "left_down": self.arduino_controller.left_down,
            "left_stop": self.arduino_controller.left_stop,
            "right_up": self.arduino_controller.right_up,
            "right_down": self.arduino_controller.right_down,
            "right_stop": self.arduino_controller.right_stop
        }
        
        if action in action_methods:
            try:
                action_methods[action]()
                logger.info(f"Executed bed action: {action}")
            except Exception as e:
                logger.error(f"Error executing bed action {action}: {e}")
        else:
            logger.warning(f"Unknown bed action: {action}") 