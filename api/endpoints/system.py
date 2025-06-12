#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
System Information API Endpoint Module - Provides system information interfaces for frontend applications
"""

import logging
import platform
from datetime import datetime
from flask import Blueprint, jsonify

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
system_api = Blueprint('system_api', __name__)

def init_system_api(arduino_controller, camera_manager):
    """
    Initialize system information API
    
    Args:
        arduino_controller: Arduino controller instance
        camera_manager: Camera manager instance
        
    Returns:
        Blueprint: Initialized blueprint object
    """
    
    @system_api.route('/api/status', methods=['GET'])
    def get_status():
        """Get system status"""
        bed_height = arduino_controller.get_bed_height()
        heart_rate = arduino_controller.get_heart_rate()
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'bed_height': bed_height,
            'heart_rate': heart_rate,
            'camera_active': camera_manager.is_running if camera_manager else False,
            'recording': camera_manager.is_recording if camera_manager else False
        })
    
    @system_api.route('/api/system/info', methods=['GET'])
    def get_system_info():
        """Get system information"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            resource_info = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent
            }
        except ImportError:
            # psutil may not be available
            resource_info = {
                'cpu_percent': 'N/A',
                'memory_percent': 'N/A',
                'disk_percent': 'N/A'
            }
        
        return jsonify({
            'status': 'ok',
            'system': {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'hostname': platform.node()
            },
            'resources': resource_info,
            'timestamp': datetime.now().isoformat()
        })
    
    # Return blueprint
    return system_api 