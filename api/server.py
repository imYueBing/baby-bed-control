#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Server Module - Provides HTTP and WebSocket interfaces for frontend applications
"""

import logging
import threading
import time
from flask import Flask
from flask_socketio import SocketIO
import argparse
import signal
import sys

# Import API endpoints
from .endpoints.bed import bed_api, init_bed_api
from .endpoints.heart_rate import heart_rate_api, init_heart_rate_api
from .endpoints.video import video_api, init_video_api
from .endpoints.system import system_api, init_system_api
from .endpoints.face_tracker import face_tracker_bp  # Import auto face tracking API endpoint

# Import WebSocket event handlers
from .websocket.bed import register_bed_socketio_events
from .websocket.heart_rate import register_heart_rate_socketio_events
from .websocket.video import register_video_socketio_events

from .websocket.mock_arduino import MockArduinoController



# Configure logging
logger = logging.getLogger(__name__)

class APIServer:
    """API Server class, provides interfaces for frontend applications"""
    
    def __init__(self, arduino_controller, camera_manager, host='0.0.0.0', port=5000, debug=False):
        """
        Initialize API server
        
        Args:
            arduino_controller: Arduino controller instance, can be None to indicate not using Arduino
            camera_manager: Camera manager instance
            host (str): Host to listen on
            port (int): Port to listen on
            debug (bool): Whether to enable debug mode
        """
        self.arduino_controller = arduino_controller
        self.camera_manager = camera_manager
        self.host = host
        self.port = port
        self.debug = debug
        self.server_thread = None
        self.is_running = False
        
        # Add a flag to indicate whether Arduino controller is available
        self.arduino_available = arduino_controller is not None
        
        # Log a warning if Arduino controller is not available
        if not self.arduino_available:
            logger.warning("Arduino controller not provided, will run in 'camera-only mode'. All Arduino-related functions will be unavailable or return simulated data.")
        
        # Initialize Flask application
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        
        # Configure API blueprints
        self._setup_blueprints()
        
        # Configure WebSocket events
        self._setup_socketio_events()
    
    def _setup_blueprints(self):
        """Configure API blueprints"""
        # Register bed control API
        self.app.register_blueprint(init_bed_api(self.arduino_controller))
        
        # Register heart rate monitoring API
        self.app.register_blueprint(init_heart_rate_api(self.arduino_controller))
        
        # Register video monitoring API
        self.app.register_blueprint(init_video_api(self.camera_manager))
        
        # Register system information API
        self.app.register_blueprint(init_system_api(self.arduino_controller, self.camera_manager))
        
        # Register auto face tracking API
        self.app.register_blueprint(face_tracker_bp)
    
    def _setup_socketio_events(self):
        """Configure WebSocket events"""
        # Connection and disconnection events
        @self.socketio.on('connect')
        def handle_connect():
            """Handle WebSocket connection"""
            logger.info("New WebSocket client connected")
            self.socketio.emit('welcome', {'message': 'Connected to Baby Monitoring System'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle WebSocket disconnection"""
            logger.info("WebSocket client disconnected")
        
        # Register video-related WebSocket events (these don't depend on Arduino)
        register_video_socketio_events(self.socketio, self.camera_manager)
        
        # Only register Arduino-dependent WebSocket events if Arduino is available
        if self.arduino_available:
            logger.info("Arduino available, registering Arduino-related WebSocket events...")
            register_bed_socketio_events(self.socketio, self.arduino_controller)
            register_heart_rate_socketio_events(self.socketio, self.arduino_controller)
        else:
            logger.warning("Arduino not available, skipping registration of Arduino-related WebSocket events.")
            # Optional: Here you can register some simulated/informative WebSocket events for bed and heart rate
            # For example, return "Arduino not connected" when client requests
            self._setup_mock_arduino_socketio_events()
        
        # Register auto face tracking related WebSocket events
        self._setup_face_tracker_socketio_events()
    
    def _setup_mock_arduino_socketio_events(self):
        """Configure mock WebSocket event handlers when Arduino is not available"""
        @self.socketio.on('request_bed_status') # Assuming this event exists
        def handle_mock_bed_status():
            self.socketio.emit('bed_status_update', {
                'status': 'error',
                'message': 'Arduino not connected',
                'bed_height': None
            })
        
        @self.socketio.on('request_heart_rate')
        def handle_mock_heart_rate():
            self.socketio.emit('heart_rate_update', {
                'status': 'error',
                'message': 'Arduino not connected',
                'heart_rate': None
            })
    
    def _setup_face_tracker_socketio_events(self):
        """Configure auto face tracking related WebSocket events"""
        @self.socketio.on('request_face_tracker_status')
        def handle_face_tracker_status():
            """Handle request for auto face tracking status"""
            face_tracker = self.app.face_tracker if hasattr(self.app, 'face_tracker') else None
            
            if not face_tracker:
                self.socketio.emit('face_tracker_status_update', {
                    'status': 'error',
                    'message': 'Face tracker not initialized',
                    'is_running': False
                })
                return
            
            self.socketio.emit('face_tracker_status_update', {
                'status': 'success',
                'is_running': face_tracker.is_running,
                'scan_interval': face_tracker.scan_interval,
                'movement_delay': face_tracker.movement_delay,
                'face_detection_threshold': face_tracker.face_detection_threshold,
                'no_face_count': face_tracker.no_face_count,
                'last_face_detected': face_tracker.last_face_detected
            })
        
        @self.socketio.on('start_face_tracker')
        def handle_start_face_tracker(data=None):
            """Handle request to start auto face tracking"""
            face_tracker = self.app.face_tracker if hasattr(self.app, 'face_tracker') else None
            
            if not face_tracker:
                self.socketio.emit('face_tracker_response', {
                    'status': 'error',
                    'message': 'Face tracker not initialized'
                })
                return
            
            # Update configuration (if provided)
            if data:
                if 'scan_interval' in data:
                    face_tracker.scan_interval = float(data['scan_interval'])
                if 'movement_delay' in data:
                    face_tracker.movement_delay = float(data['movement_delay'])
                if 'face_detection_threshold' in data:
                    face_tracker.face_detection_threshold = int(data['face_detection_threshold'])
            
            # Start tracker
            success = face_tracker.start()
            
            if success:
                self.socketio.emit('face_tracker_response', {
                    'status': 'success',
                    'message': 'Face tracker started',
                    'is_running': True
                })
            else:
                self.socketio.emit('face_tracker_response', {
                    'status': 'error',
                    'message': 'Failed to start face tracker',
                    'is_running': False
                })
        
        @self.socketio.on('stop_face_tracker')
        def handle_stop_face_tracker():
            """Handle request to stop auto face tracking"""
            face_tracker = self.app.face_tracker if hasattr(self.app, 'face_tracker') else None
            
            if not face_tracker:
                self.socketio.emit('face_tracker_response', {
                    'status': 'error',
                    'message': 'Face tracker not initialized'
                })
                return
            
            # Stop tracker
            face_tracker.stop()
            
            self.socketio.emit('face_tracker_response', {
                'status': 'success',
                'message': 'Face tracker stopped',
                'is_running': False
            })
    
    def start(self):
        """Start server"""
        if self.is_running:
            logger.warning("Server is already running")
            return
        
        logger.info(f"Starting API server: {self.host}:{self.port}")
        
        # Run server in a thread
        self.is_running = True
        self.server_thread = threading.Thread(
            target=self._run_server
        )
        self.server_thread.daemon = True
        self.server_thread.start()
        
        logger.info("API server started")
    
    def _run_server(self):
        """Run server (in thread)"""
        try:
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=self.debug,
                use_reloader=False  # Disable reloader to avoid issues when starting in a thread
            )
        except Exception as e:
            logger.error(f"Error running API server: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop server"""
        if not self.is_running:
            logger.warning("Server is not running")
            return
        
        logger.info("Stopping API server")
        self.is_running = False
        
        # Stop the server
        try:
            # Request shutdown
            import requests
            try:
                requests.get(f"http://localhost:{self.port}/shutdown", timeout=0.1)
            except requests.exceptions.RequestException:
                pass  # Expected to fail as server shuts down
            
            # Wait for thread to finish
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5.0)
        except Exception as e:
            logger.error(f"Error stopping API server: {e}")
        
        logger.info("API server stopped")
    
    def start_camera_debug(self, window_name="Camera Debug"):
        """Start camera debug window"""
        if not self.camera_manager:
            logger.warning("Cannot start camera debug: Camera manager not available")
            return False
        
        try:
            self.camera_manager.start_debug_window(window_name)
            logger.info(f"Camera debug window started: {window_name}")
            return True
        except Exception as e:
            logger.error(f"Error starting camera debug window: {e}")
            return False
    
    def stop_camera_debug(self):
        """Stop camera debug window"""
        if not self.camera_manager:
            return
        
        self.camera_manager.close_debug_window()
        logger.info("Camera debug window closed")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Baby Monitoring System API Server")
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to listen on')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--debug-camera', action='store_true', help='Enable camera debug window')
    parser.add_argument('--no-arduino', action='store_true', help='Run without Arduino controller')
    return parser.parse_args()

def setup(args=None):
    """Set up the API server"""
    if args is None:
        args = parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Setting up API server")
    
    # Initialize Arduino controller (if not disabled)
    arduino_controller = None
    if not args.no_arduino:
        try:
            from modules.arduino.controller import ArduinoController
            from utils.device_discovery import discover_arduino_device
            
            # Try to discover Arduino device
            port = discover_arduino_device()
            if port:
                arduino_controller = ArduinoController(port=port)
                logger.info(f"Arduino controller initialized on port {port}")
            else:
                logger.warning("No Arduino device found, running in camera-only mode")
        except Exception as e:
            logger.error(f"Error initializing Arduino controller: {e}")
    else:
        logger.info("Arduino controller disabled by command line argument")
    
    # Initialize camera manager
    camera_manager = None
    try:
        from modules.camera.camera_manager import CameraManager
        camera_manager = CameraManager()
        logger.info("Camera manager initialized")
    except Exception as e:
        logger.error(f"Error initializing camera manager: {e}")
    
    # Create API server
    api_server = APIServer(
        arduino_controller=arduino_controller,
        camera_manager=camera_manager,
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    
    # Start camera debug window if requested
    if args.debug_camera and camera_manager:
        api_server.start_camera_debug()
    
    return api_server

def main():
    """Main entry point"""
    args = parse_args()
    api_server = setup(args)
    
    # Set up signal handlers
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        api_server.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start server
    api_server.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        api_server.stop()

if __name__ == "__main__":
    main() 