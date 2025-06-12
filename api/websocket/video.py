#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Video WebSocket Event Handling Module
"""

import logging
import base64
from flask_socketio import emit

# Configure logging
logger = logging.getLogger(__name__)

def register_video_socketio_events(socketio, camera_manager):
    """
    Register video-related WebSocket event handlers
    
    Args:
        socketio: SocketIO instance
        camera_manager: Camera manager instance
    """
    
    @socketio.on('request_video_frame')
    def handle_video_frame_request():
        """Handle video frame request"""
        jpeg_data = camera_manager.get_jpeg_frame()
        if jpeg_data:
            # Convert binary data to Base64
            base64_data = base64.b64encode(jpeg_data).decode('utf-8')
            emit('video_frame', {
                'frame': base64_data,
                'status': 'ok'
            })
        else:
            emit('video_frame', {
                'status': 'error',
                'message': 'Unable to get video frame'
            })
    
    @socketio.on('start_recording')
    def handle_start_recording(data):
        """Handle start recording request"""
        output_dir = data.get('output_dir', 'videos')
        success = camera_manager.start_recording(output_dir)
        
        emit('recording_status', {
            'status': 'ok' if success else 'error',
            'action': 'start',
            'recording': success,
            'message': 'Started video recording' if success else 'Unable to start video recording'
        })
    
    @socketio.on('stop_recording')
    def handle_stop_recording():
        """Handle stop recording request"""
        camera_manager.stop_recording()
        
        emit('recording_status', {
            'status': 'ok',
            'action': 'stop',
            'recording': False,
            'message': 'Stopped video recording'
        }) 