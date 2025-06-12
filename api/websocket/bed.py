#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bed Control WebSocket Event Handling Module
"""

import logging
from flask_socketio import emit

# Configure logging
logger = logging.getLogger(__name__)

def register_bed_socketio_events(socketio, arduino_controller):
    """
    Register bed control related WebSocket event handlers
    
    Args:
        socketio: SocketIO instance
        arduino_controller: Arduino controller instance
    """
    
    @socketio.on('bed_control')
    def handle_bed_control(data):
        """Handle bed control events"""
        action = data.get('action')
        
        if action == 'up':
            success = arduino_controller.bed_up()
            logger.info(f"WebSocket bed up command: {'successful' if success else 'failed'}")
        elif action == 'down':
            success = arduino_controller.bed_down()
            logger.info(f"WebSocket bed down command: {'successful' if success else 'failed'}")
        elif action == 'stop':
            success = arduino_controller.bed_stop()
            logger.info(f"WebSocket bed stop command: {'successful' if success else 'failed'}")
        else:
            emit('error', {'message': 'Invalid bed control operation'})
            return
        
        emit('bed_control_response', {
            'status': 'ok' if success else 'error',
            'action': action,
            'message': f'Bed {action} operation ' + ('successful' if success else 'failed')
        })
        
        # Send updated status
        emit_bed_status_update(arduino_controller)

def emit_bed_status_update(arduino_controller):
    """
    Send bed status update
    
    Args:
        arduino_controller: Arduino controller instance
    """
    bed_height = arduino_controller.get_bed_height()
    
    emit('bed_status_update', {
        'bed_height': bed_height,
        'status': 'ok' if bed_height is not None else 'error'
    }) 