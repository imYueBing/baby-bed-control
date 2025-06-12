#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Auto Face Tracking API Endpoint
"""

from flask import Blueprint, jsonify, request, current_app
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
face_tracker_bp = Blueprint('face_tracker', __name__)

@face_tracker_bp.route('/api/face_tracker/start', methods=['POST'])
def start_face_tracker():
    """Start auto face tracking"""
    try:
        # Get auto face tracker from application context
        face_tracker = current_app.face_tracker
        if not face_tracker:
            return jsonify({
                'success': False,
                'message': 'Auto face tracker not initialized'
            }), 500
        
        # Get parameters from request (if any)
        data = request.get_json() or {}
        scan_interval = data.get('scan_interval', None)
        movement_delay = data.get('movement_delay', None)
        face_detection_threshold = data.get('face_detection_threshold', None)
        
        # If parameters were provided, update tracker configuration
        if scan_interval is not None:
            face_tracker.scan_interval = float(scan_interval)
        if movement_delay is not None:
            face_tracker.movement_delay = float(movement_delay)
        if face_detection_threshold is not None:
            face_tracker.face_detection_threshold = int(face_detection_threshold)
        
        # Start auto face tracking
        success = face_tracker.start()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Auto face tracking started',
                'config': {
                    'scan_interval': face_tracker.scan_interval,
                    'movement_delay': face_tracker.movement_delay,
                    'face_detection_threshold': face_tracker.face_detection_threshold
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to start auto face tracking'
            }), 500
            
    except Exception as e:
        logger.error(f"Error starting auto face tracking: {e}")
        return jsonify({
            'success': False,
            'message': f'Error occurred while starting auto face tracking: {str(e)}'
        }), 500

@face_tracker_bp.route('/api/face_tracker/stop', methods=['POST'])
def stop_face_tracker():
    """Stop auto face tracking"""
    try:
        # Get auto face tracker from application context
        face_tracker = current_app.face_tracker
        if not face_tracker:
            return jsonify({
                'success': False,
                'message': 'Auto face tracker not initialized'
            }), 500
        
        # Stop auto face tracking
        face_tracker.stop()
        
        return jsonify({
            'success': True,
            'message': 'Auto face tracking stopped'
        })
            
    except Exception as e:
        logger.error(f"Error stopping auto face tracking: {e}")
        return jsonify({
            'success': False,
            'message': f'Error occurred while stopping auto face tracking: {str(e)}'
        }), 500

@face_tracker_bp.route('/api/face_tracker/status', methods=['GET'])
def get_face_tracker_status():
    """Get auto face tracking status"""
    try:
        # Get auto face tracker from application context
        face_tracker = current_app.face_tracker
        if not face_tracker:
            return jsonify({
                'success': False,
                'message': 'Auto face tracker not initialized'
            }), 500
        
        return jsonify({
            'success': True,
            'status': {
                'is_running': face_tracker.is_running,
                'scan_interval': face_tracker.scan_interval,
                'movement_delay': face_tracker.movement_delay,
                'face_detection_threshold': face_tracker.face_detection_threshold,
                'no_face_count': face_tracker.no_face_count,
                'last_face_detected': face_tracker.last_face_detected,
                'current_sequence_index': face_tracker.current_sequence_index
            }
        })
            
    except Exception as e:
        logger.error(f"Error getting auto face tracking status: {e}")
        return jsonify({
            'success': False,
            'message': f'Error occurred while getting auto face tracking status: {str(e)}'
        }), 500

@face_tracker_bp.route('/api/face_tracker/config', methods=['POST'])
def update_face_tracker_config():
    """Update auto face tracking configuration"""
    try:
        # Get auto face tracker from application context
        face_tracker = current_app.face_tracker
        if not face_tracker:
            return jsonify({
                'success': False,
                'message': 'Auto face tracker not initialized'
            }), 500
        
        # Get parameters from request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No configuration parameters provided'
            }), 400
        
        # Update configuration
        if 'scan_interval' in data:
            face_tracker.scan_interval = float(data['scan_interval'])
        
        if 'movement_delay' in data:
            face_tracker.movement_delay = float(data['movement_delay'])
        
        if 'face_detection_threshold' in data:
            face_tracker.face_detection_threshold = int(data['face_detection_threshold'])
        
        if 'adjustment_sequence' in data:
            face_tracker.adjustment_sequence = data['adjustment_sequence']
            face_tracker.current_sequence_index = 0
        
        return jsonify({
            'success': True,
            'message': 'Auto face tracking configuration updated',
            'config': {
                'scan_interval': face_tracker.scan_interval,
                'movement_delay': face_tracker.movement_delay,
                'face_detection_threshold': face_tracker.face_detection_threshold,
                'current_sequence_index': face_tracker.current_sequence_index
            }
        })
            
    except Exception as e:
        logger.error(f"Error updating auto face tracking configuration: {e}")
        return jsonify({
            'success': False,
            'message': f'Error occurred while updating auto face tracking configuration: {str(e)}'
        }), 500 