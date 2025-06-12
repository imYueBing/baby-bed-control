#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Heart Rate WebSocket Event Handling Module
"""

import logging
from datetime import datetime
from flask_socketio import emit
from .mock_arduino import MockArduinoController


logger = logging.getLogger(__name__)

def register_heart_rate_socketio_events(socketio, arduino_controller=None):
    """
    Register heart rate related WebSocket event handlers
    
    Args:
        socketio: Flask-SocketIO instance
        arduino_controller: Arduino controller instance (optional), if not provided a mock controller will be used
    """
    
    if arduino_controller is None:
        logger.info("Arduino controller not available, using mock controller")
        from .mock_arduino import MockArduinoController
        arduino_controller = MockArduinoController()
    
    def heart_rate_callback(heart_rate):
        logger.info(f"Pushing heart rate data: {heart_rate}")
        try:
            socketio.emit('heart_rate_update', {
                'heart_rate': heart_rate,
                'timestamp': datetime.now().isoformat(),
                'status': 'ok'
            })
            logger.debug("Heart rate data pushed successfully")
        except Exception as e:
            logger.error(f"Error pushing heart rate data: {e}")

    # Subscribe to heart rate data update callback
    try:
        arduino_controller.subscribe_heart_rate(heart_rate_callback)
        logger.info("Subscribed to heart rate updates")
    except Exception as e:
        logger.error(f"Failed to subscribe to heart rate updates: {e}")

    @socketio.on('request_heart_rate')
    def handle_heart_rate_request():
        logger.info("Received WebSocket heart rate request")
        try:
            heart_rate = arduino_controller.get_heart_rate()
            logger.info(f"WebSocket requested heart rate value: {heart_rate}")
            
            # If heart rate is None, try a few more times
            retry_count = 0
            while heart_rate is None and retry_count < 3:
                logger.warning(f"WebSocket heart rate is empty, trying to retrieve again (attempt {retry_count+1}/3)")
                heart_rate = arduino_controller.get_heart_rate()
                retry_count += 1
            
            response = {
                'heart_rate': heart_rate,
                'timestamp': datetime.now().isoformat(),
                'status': 'ok' if heart_rate is not None else 'error',
                'retry_count': retry_count
            }
            
            emit('heart_rate_update', response)
            logger.info(f"Sent WebSocket heart rate response: {response}")
        except Exception as e:
            logger.error(f"Error handling WebSocket heart rate request: {e}")
            emit('heart_rate_update', {
                'heart_rate': None,
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'message': f'Error occurred while retrieving heart rate: {str(e)}'
            })
