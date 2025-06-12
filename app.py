#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Baby Intelligent Monitoring System Main Program
"""

import logging
import os
import signal
import sys
import argparse
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('baby_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

# Import modules
from modules.arduino.controller import ArduinoController
from modules.camera.camera_manager import CameraManager
from modules.auto_face_tracker import AutoFaceTracker  # Import auto face tracking module
from api.server import APIServer
from config.settings import get_config

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Baby Intelligent Monitoring System')
    parser.add_argument('--debug-camera', action='store_true', 
                        help='Enable camera debug window to display camera feed locally')
    parser.add_argument('--debug-window-name', type=str, default='Camera Debug',
                        help='Debug window name')
    parser.add_argument('--only-camera', action='store_true', 
                        help='Test camera only, do not start the full system')
    parser.add_argument('--no-arduino', action='store_true',  
                        help='Do not use Arduino controller, run in camera-only mode')
    parser.add_argument('--enable-face-detection', action='store_true',
                        help='Enable AI face recognition (overrides config.json setting)')
    parser.add_argument('--disable-face-detection', action='store_true',
                        help='Disable AI face recognition (overrides config.json setting)')
    parser.add_argument('--enable-face-tracker', action='store_true',
                        help='Enable automatic face tracking')
    return parser.parse_args()

def setup(args):
    """Initialize system components"""
    logger.info("Baby Intelligent Monitoring System starting...")

    config = get_config()

    arduino_controller = None
    camera_manager = None
    api_server = None
    face_tracker = None

    # Initialize Arduino controller (if --no-arduino is not specified)
    if not args.no_arduino:
        try:
            arduino_controller = ArduinoController(
                port=config.get('arduino', 'port'),
                baud_rate=config.get('arduino', 'baud_rate', 9600)
            )
            logger.info("Arduino controller initialized successfully")
        except Exception as e:
            logger.warning(f"Arduino initialization failed: {e}")
    else:
        logger.info("Running in camera-only mode, not using Arduino controller")

    # Initialize camera manager
    try:
        # Decide whether to enable AI face recognition, command line parameters take precedence over config file
        enable_ai_detection_config = config.get('camera', 'enable_ai_face_detection', False)
        if args.enable_face_detection:
            final_enable_ai_detection = True
        elif args.disable_face_detection:
            final_enable_ai_detection = False
        else:
            final_enable_ai_detection = enable_ai_detection_config

        camera_manager = CameraManager(
            resolution=config.get('camera', 'resolution', [640, 480]),
            framerate=config.get('camera', 'framerate', 30),
            use_picamera=config.get('camera', 'use_picamera', True),
            enable_ai_face_detection=final_enable_ai_detection, # Use the final determined value
            cascade_path=config.get('camera', 'cascade_path', 'models/haarcascade_frontalface_default.xml'),
            tflite_model_path=config.get('camera', 'tflite_model_path', 'models/frontal_face_classifier.tflite')
        )
        logger.info("Camera manager initialized successfully")
    except Exception as e:
        logger.warning(f"Camera initialization failed: {e}")

    # Initialize auto face tracker (if enabled)
    if args.enable_face_tracker and camera_manager and arduino_controller:
        try:
            face_tracker = AutoFaceTracker(
                camera_manager=camera_manager,
                arduino_controller=arduino_controller,
                scan_interval=config.get('face_tracker', 'scan_interval', 3.0),
                movement_delay=config.get('face_tracker', 'movement_delay', 2.0),
                face_detection_threshold=config.get('face_tracker', 'face_detection_threshold', 3)
            )
            logger.info("Auto face tracker initialized successfully")
        except Exception as e:
            logger.warning(f"Auto face tracker initialization failed: {e}")
    elif args.enable_face_tracker:
        if not camera_manager:
            logger.warning("Cannot initialize auto face tracker: Camera not initialized")
        if not arduino_controller:
            logger.warning("Cannot initialize auto face tracker: Arduino controller not initialized")

    # Initialize API server - This should only create an APIServer instance
    api_server_instance = APIServer(
        arduino_controller=arduino_controller,
        camera_manager=camera_manager,
        host=config.get('server', 'host', '0.0.0.0'),
        port=config.get('server', 'port', 5000)
    )
    logger.info("API server object created successfully")

    # Add the auto face tracker to the API server's application context
    api_server_instance.app.face_tracker = face_tracker

    return arduino_controller, camera_manager, api_server_instance, face_tracker

def cleanup(arduino_controller, camera_manager, api_server, face_tracker=None):
    """Clean up resources"""
    logger.info("System shutting down...")
    
    # Stop auto face tracking
    if face_tracker:
        face_tracker.stop()
    
    # Close Arduino connection
    if arduino_controller:
        arduino_controller.close()
    
    # Close camera
    if camera_manager:
        camera_manager.close()
    
    # Close API server
    if api_server:
        api_server.stop()
    
    logger.info("System has been safely shut down")

def signal_handler(sig, frame, components=None):
    """Handle system signals"""
    if components:
        cleanup(*components)
    sys.exit(0)

def main():
    """Main function"""
    args = parse_args()
    
    try:
        if args.only_camera:
            try:
                print("Starting camera test mode only...")
                camera = CameraManager(
                    resolution=(640, 480),
                    framerate=30
                )
                camera.start_debug_window("Camera Test")
                print("Press ESC key to exit")
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print(f"Camera test failed: {e}")
            finally:
                if 'camera' in locals():
                    camera.close()
                return

        components = setup(args)
        arduino_controller, camera_manager, api_server_instance, face_tracker = components
        
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, components))
        signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, components))
        
        if api_server_instance:
            api_server_instance.start()
        else:
            logger.error("API server instance could not be created.")
            return
        
        if args.debug_camera and camera_manager:
            logger.info(f"Enabling camera debug window: {args.debug_window_name}")
            camera_manager.start_debug_window(args.debug_window_name)
            print(f"Camera debug window started: {args.debug_window_name}")
            print("Press ESC key to close the debug window")
        
        # If auto face tracking is enabled, start it
        if args.enable_face_tracker and face_tracker:
            face_tracker.start()
            print("Auto face tracking started")
        
        print("System started" + (" (camera-only mode)" if args.no_arduino else ""))
        print("Press Ctrl+C to exit")
        while True:
            signal.pause()
            
    except Exception as e:
        logger.error(f"System startup failed: {e}")
        if 'components' in locals() and len(components) >= 3:
            cleanup(*components)
        elif 'components' in locals():
            if components[0]: components[0].close()
            if components[1]: components[1].close()
        sys.exit(1)

if __name__ == "__main__":
    main() 