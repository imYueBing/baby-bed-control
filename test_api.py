#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Test Script - Tests the modularized API structure
"""

import logging
import sys
from flask import Flask
from flask_socketio import SocketIO

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import necessary modules
from modules.arduino.controller import ArduinoController
from api.endpoints.bed import init_bed_api
from api.endpoints.heart_rate import init_heart_rate_api
from api.endpoints.system import init_system_api
from api.websocket.bed import register_bed_socketio_events
from api.websocket.heart_rate import register_heart_rate_socketio_events

def test_api():
    """Test API initialization"""
    try:
        # Create test Arduino controller (using simulated device)
        arduino_controller = ArduinoController(port=None)
        
        # Create Flask application
        app = Flask(__name__)
        socketio = SocketIO(app, cors_allowed_origins="*")
        
        # Register API blueprints
        app.register_blueprint(init_bed_api(arduino_controller))
        app.register_blueprint(init_heart_rate_api(arduino_controller))
        app.register_blueprint(init_system_api(arduino_controller, None))
        
        # Register WebSocket events
        register_bed_socketio_events(socketio, arduino_controller)
        register_heart_rate_socketio_events(socketio, arduino_controller)
        
        # Print registered routes
        logger.info("Registered API routes:")
        for rule in app.url_map.iter_rules():
            if not str(rule).startswith('/static'):
                logger.info(f"  {rule} ({', '.join(rule.methods)})")
        
        logger.info("API initialization test successful!")
        return True
        
    except Exception as e:
        logger.error(f"API initialization test failed: {e}")
        return False

if __name__ == "__main__":
    if test_api():
        sys.exit(0)
    else:
        sys.exit(1) 