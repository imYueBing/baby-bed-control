#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Heart Rate Monitoring API Endpoint Module - Provides heart rate monitoring interfaces for frontend applications
"""

import logging
from datetime import datetime
from flask import Blueprint, jsonify, request

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
heart_rate_api = Blueprint('heart_rate_api', __name__)

def init_heart_rate_api(arduino_controller):
    """
    Initialize heart rate monitoring API
    
    Args:
        arduino_controller: Arduino controller instance
        
    Returns:
        Blueprint: Initialized blueprint object
    """
    
    @heart_rate_api.route('/api/heart-rate', methods=['GET'])
    def get_heart_rate():
        """Get heart rate"""
        logger.info("Received heart rate API request")
        
        if arduino_controller: # Check if arduino_controller is None
            try:
                heart_rate = arduino_controller.get_heart_rate()
                logger.info(f"Retrieved heart rate value: {heart_rate}")
                
                # If heart rate is None, try a few more times
                retry_count = 0
                while heart_rate is None and retry_count < 3:
                    logger.warning(f"Heart rate is empty, trying to retrieve again (attempt {retry_count+1}/3)")
                    heart_rate = arduino_controller.get_heart_rate()
                    retry_count += 1
                
                response = {
                    'status': 'ok' if heart_rate is not None else 'error',
                    'heart_rate': heart_rate,
                    'timestamp': datetime.now().isoformat(),
                    'message': 'Heart rate retrieved successfully' if heart_rate is not None else 'Arduino not connected or data unavailable',
                    'retry_count': retry_count
                }
                
                logger.info(f"Heart rate API response: {response}")
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"Error occurred while retrieving heart rate: {e}", exc_info=True)
                return jsonify({
                    'status': 'error',
                    'heart_rate': None,
                    'timestamp': datetime.now().isoformat(),
                    'message': f'Error occurred while retrieving heart rate: {str(e)}'
                }), 500
        else:
            logger.warning("Heart rate API request failed: Arduino controller unavailable")
            return jsonify({ # Response when Arduino is unavailable
                'status': 'error',
                'heart_rate': None,
                'timestamp': datetime.now().isoformat(),
                'message': 'Arduino controller unavailable (camera-only mode)'
            }), 503 # Service Unavailable
    
    # Return blueprint
    return heart_rate_api 