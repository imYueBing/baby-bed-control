#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Baby Monitoring System - Test Script
For testing component connections and basic functionality
"""

import argparse
import json
import logging
import os
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_system")

def test_arduino():
    """Test Arduino connection and functionality"""
    logger.info("===== Testing Arduino Connection =====")
    
    try:
        from utils.device_discovery import discover_arduino_device
        from modules.arduino.controller import ArduinoController
        
        # Discover Arduino device
        port = discover_arduino_device()
        
        if not port:
            logger.error("Unable to find Arduino device")
            return False
        
        logger.info(f"Found Arduino device: {port}")
        
        # Initialize controller
        controller = ArduinoController(port=port)
        
        if not controller.is_connected:
            logger.error("Arduino controller initialization failed")
            return False
        
        # Test getting heart rate
        logger.info("Testing heart rate retrieval...")
        heart_rate = controller.get_heart_rate()
        logger.info(f"Current heart rate: {heart_rate if heart_rate is not None else 'Unknown'}")
        
        # Test getting bed height
        logger.info("Testing bed height retrieval...")
        height = controller.get_bed_height()
        logger.info(f"Current bed height: {height if height is not None else 'Unknown'}")
        
        # Test bed control
        logger.info("Testing bed control...")
        
        logger.info("Raising bed (1 second)...")
        controller.bed_up()
        time.sleep(1)
        
        logger.info("Stopping bed...")
        controller.bed_stop()
        time.sleep(0.5)
        
        logger.info("Lowering bed (1 second)...")
        controller.bed_down()
        time.sleep(1)
        
        logger.info("Stopping bed...")
        controller.bed_stop()
        
        # Close controller
        controller.close()
        logger.info("Arduino test completed")
        
        return True
        
    except Exception as e:
        logger.error(f"Arduino test failed: {e}")
        return False

def test_camera():
    """Test camera functionality"""
    logger.info("===== Testing Camera =====")
    
    try:
        from modules.camera.camera_manager import CameraManager
        import cv2
        
        # Initialize camera
        camera = CameraManager(resolution=(640, 480), framerate=30)
        
        if not camera.is_running:
            logger.error("Camera initialization failed")
            return False
        
        # Get and display frames
        for i in range(5):
            logger.info(f"Getting frame {i+1}/5...")
            frame = camera.get_frame()
            
            if frame is None:
                logger.error("Unable to get video frame")
                break
            
            # Get frame size
            height, width = frame.shape[:2]
            logger.info(f"Frame size: {width}x{height}")
            
            # Save frame as JPEG
            jpg_file = f"test_frame_{i+1}.jpg"
            cv2.imwrite(jpg_file, frame)
            logger.info(f"Frame saved to {jpg_file}")
            
            time.sleep(1)
        
        # Test recording
        logger.info("Testing video recording (3 seconds)...")
        camera.start_recording("test_videos")
        time.sleep(3)
        camera.stop_recording()
        logger.info("Recording complete")
        
        # Close camera
        camera.close()
        logger.info("Camera test completed")
        
        return True
        
    except Exception as e:
        logger.error(f"Camera test failed: {e}")
        return False

def test_api_server():
    """Test API server"""
    logger.info("===== Testing API Server =====")
    
    try:
        from utils.device_discovery import discover_arduino_device
        from modules.arduino.controller import ArduinoController
        from modules.camera.camera_manager import CameraManager
        from api.server import APIServer
        
        # Discover Arduino device
        port = discover_arduino_device()
        
        if not port:
            logger.warning("Unable to find Arduino device, will use simulated device")
            # Use a non-existent port to put the controller in offline mode
            port = "/dev/ttyNONEXISTENT"
        
        # Initialize components
        arduino_controller = ArduinoController(port=port)
        camera_manager = CameraManager(resolution=(640, 480), framerate=30)
        
        # Initialize API server
        api_server = APIServer(
            arduino_controller=arduino_controller,
            camera_manager=camera_manager,
            host='127.0.0.1',  # Listen on localhost only
            port=5000
        )
        
        # Start server
        logger.info("Starting API server...")
        api_server.start()
        
        # Wait for server to fully start
        time.sleep(2)
        
        # Test API
        import requests
        
        logger.info("Testing API: GET /api/status")
        response = requests.get("http://127.0.0.1:5000/api/status")
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # Wait for a while to view server logs
        logger.info("API server started and test completed")
        logger.info("Press Ctrl+C to stop server...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        # Close server and components
        logger.info("Stopping API server...")
        api_server.stop()
        arduino_controller.close()
        camera_manager.close()
        
        return True
        
    except Exception as e:
        logger.error(f"API server test failed: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Baby Monitoring System Test Script")
    parser.add_argument("--arduino", action="store_true", help="Test Arduino connection")
    parser.add_argument("--camera", action="store_true", help="Test camera")
    parser.add_argument("--api", action="store_true", help="Test API server")
    parser.add_argument("--all", action="store_true", help="Test all components")
    
    args = parser.parse_args()
    
    # If no parameters specified, show help
    if not (args.arduino or args.camera or args.api or args.all):
        parser.print_help()
        return
    
    # Test Arduino
    if args.arduino or args.all:
        test_arduino()
    
    # Test camera
    if args.camera or args.all:
        test_camera()
    
    # Test API server
    if args.api or args.all:
        test_api_server()

if __name__ == "__main__":
    main() 