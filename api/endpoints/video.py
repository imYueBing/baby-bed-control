#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Video Monitoring API Endpoint Module - Provides video monitoring interfaces for frontend applications
"""

import logging
import io
from flask import Blueprint, jsonify, request, Response, send_file

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
video_api = Blueprint('video_api', __name__)

def init_video_api(camera_manager):
    """
    Initialize video monitoring API
    
    Args:
        camera_manager: Camera manager instance
        
    Returns:
        Blueprint: Initialized blueprint object
    """
    
    @video_api.route('/api/video/snapshot', methods=['GET'])
    def get_snapshot():
        """Get video snapshot"""
        jpeg_data = camera_manager.get_jpeg_frame()
        if jpeg_data:
            return Response(jpeg_data, mimetype='image/jpeg')
        else:
            return jsonify({
                'status': 'error',
                'message': 'Unable to get video snapshot'
            }), 500
    
    @video_api.route('/api/video/stream')
    def video_stream():
        """Video stream endpoint (MJPEG)"""
        return Response(
            _generate_mjpeg_stream(camera_manager),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    
    @video_api.route('/api/video/recording', methods=['POST'])
    def control_recording():
        """Control video recording"""
        action = request.json.get('action')
        
        if action == 'start':
            output_dir = request.json.get('output_dir', 'videos')
            success = camera_manager.start_recording(output_dir)
            return jsonify({
                'status': 'ok' if success else 'error',
                'action': 'start',
                'message': 'Started video recording' if success else 'Unable to start video recording'
            })
        
        elif action == 'stop':
            camera_manager.stop_recording()
            return jsonify({
                'status': 'ok',
                'action': 'stop',
                'message': 'Stopped video recording'
            })
        
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid operation'
            }), 400
    
    # Return blueprint
    return video_api

def _generate_mjpeg_stream(camera_manager):
    """
    Generate MJPEG stream
    
    Args:
        camera_manager: Camera manager instance
        
    Yields:
        bytes: JPEG frame data
    """
    while True:
        frame = camera_manager.get_jpeg_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # If unable to get frame, return empty image
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n') 