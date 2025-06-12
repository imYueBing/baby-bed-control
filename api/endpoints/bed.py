#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bed Control API Endpoint Module - Provides bed control interfaces for frontend applications, supporting independent left and right control
"""

import logging
from flask import Blueprint, jsonify, request

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
bed_api = Blueprint('bed_api', __name__)

def init_bed_api(arduino_controller):
    """
    Initialize bed control API
    
    Args:
        arduino_controller: Arduino controller instance
        
    Returns:
        Blueprint: Initialized blueprint object
    """
    
    # --------- Overall Control ---------
    
    @bed_api.route('/api/bed/up', methods=['POST'])
    def bed_up():
        """Raise entire bed"""
        success = arduino_controller.bed_up()
        logger.info(f"Bed raise command: {'successful' if success else 'failed'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'up',
            'message': 'Started raising bed' if success else 'Arduino not connected'
        })
    
    @bed_api.route('/api/bed/down', methods=['POST'])
    def bed_down():
        """Lower entire bed"""
        success = arduino_controller.bed_down()
        logger.info(f"Bed lower command: {'successful' if success else 'failed'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'down',
            'message': 'Started lowering bed' if success else 'Arduino not connected'
        })
    
    @bed_api.route('/api/bed/stop', methods=['POST'])
    def bed_stop():
        """Stop all bed movement"""
        success = arduino_controller.bed_stop()
        logger.info(f"Bed stop command: {'successful' if success else 'failed'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'stop',
            'message': 'Stopped all bed movement' if success else 'Arduino not connected'
        })
    
    # --------- Left Side Control ---------
    
    @bed_api.route('/api/bed/left_up', methods=['POST'])
    def bed_left_up():
        """Raise left side of bed"""
        success = arduino_controller.left_up()
        logger.info(f"Left side raise command: {'successful' if success else 'failed'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'left_up',
            'message': 'Started raising left side' if success else 'Arduino not connected'
        })
    
    @bed_api.route('/api/bed/left_down', methods=['POST'])
    def bed_left_down():
        """Lower left side of bed"""
        success = arduino_controller.left_down()
        logger.info(f"Left side lower command: {'successful' if success else 'failed'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'left_down',
            'message': 'Started lowering left side' if success else 'Arduino not connected'
        })
    
    @bed_api.route('/api/bed/left_stop', methods=['POST'])
    def bed_left_stop():
        """Stop left side movement"""
        success = arduino_controller.left_stop()
        logger.info(f"Left side stop command: {'successful' if success else 'failed'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'left_stop',
            'message': 'Stopped left side movement' if success else 'Arduino not connected'
        })
    
    # --------- Right Side Control ---------
    
    @bed_api.route('/api/bed/right_up', methods=['POST'])
    def bed_right_up():
        """Raise right side of bed"""
        success = arduino_controller.right_up()
        logger.info(f"Right side raise command: {'successful' if success else 'failed'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'right_up',
            'message': 'Started raising right side' if success else 'Arduino not connected'
        })
    
    @bed_api.route('/api/bed/right_down', methods=['POST'])
    def bed_right_down():
        """Lower right side of bed"""
        success = arduino_controller.right_down()
        logger.info(f"Right side lower command: {'successful' if success else 'failed'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'right_down',
            'message': 'Started lowering right side' if success else 'Arduino not connected'
        })
    
    @bed_api.route('/api/bed/right_stop', methods=['POST'])
    def bed_right_stop():
        """Stop right side movement"""
        success = arduino_controller.right_stop()
        logger.info(f"Right side stop command: {'successful' if success else 'failed'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'right_stop',
            'message': 'Stopped right side movement' if success else 'Arduino not connected'
        })
    
    # --------- Status Query ---------
    
    @bed_api.route('/api/bed/status', methods=['GET'])
    def get_bed_status():
        """Get bed status"""
        status = arduino_controller.get_bed_status()
        return jsonify({
            'status': 'ok' if status else 'error',
            'bed_status': status,
            'message': 'Successfully retrieved bed status' if status else 'Arduino not connected'
        })
    
    @bed_api.route('/api/bed/height', methods=['GET'])
    def get_bed_height():
        """Get bed height (kept for backwards compatibility)"""
        status = arduino_controller.get_bed_status()
        return jsonify({
            'status': 'ok' if status else 'error',
            'bed_status': status,
            'message': 'Successfully retrieved bed status' if status else 'Arduino not connected'
        })
    
    # Return blueprint
    return bed_api 