#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Camera Debug Example - Display camera capture locally
"""

import sys
import os
import time
import signal
import logging

# Ensure project modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from modules.camera import CameraManager

def signal_handler(sig, frame):
    """Handle Ctrl+C signal"""
    print('\nStopping...')
    if camera:
        camera.close()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create camera manager instance
    camera = CameraManager(
        resolution=(800, 600),  # Higher resolution for better viewing
        framerate=30,
        use_picamera=True  # Use Raspberry Pi camera
    )
    
    # Start local debug window
    camera.start_debug_window(window_name="Raspberry Pi Camera Module 3")
    
    print("Camera debug window started")
    print("Press ESC key or Ctrl+C to exit")
    
    try:
        # Keep program running until user stops it
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        # Ensure camera is properly closed
        if camera:
            camera.stop_debug_window()
            camera.close()
            print("Camera closed") 