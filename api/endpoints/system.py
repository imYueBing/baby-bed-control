#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统信息API端点模块 - 为前端应用提供系统信息接口
"""

import logging
import platform
from datetime import datetime
from flask import Blueprint, jsonify

# 配置日志
logger = logging.getLogger(__name__)

# 创建蓝图
system_api = Blueprint('system_api', __name__)

def init_system_api(arduino_controller, camera_manager):
    """
    初始化系统信息API
    
    Args:
        arduino_controller: Arduino控制器实例
        camera_manager: 摄像头管理器实例
        
    Returns:
        Blueprint: 初始化后的蓝图对象
    """
    
    @system_api.route('/api/status', methods=['GET'])
    def get_status():
        """获取系统状态"""
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
        """获取系统信息"""
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
            # psutil可能不可用
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
    
    # 返回蓝图
    return system_api 