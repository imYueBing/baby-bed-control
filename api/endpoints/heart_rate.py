#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
心率监测API端点模块 - 为前端应用提供心率监测接口
"""

import logging
from datetime import datetime
from flask import Blueprint, jsonify, request

# 配置日志
logger = logging.getLogger(__name__)

# 创建蓝图
heart_rate_api = Blueprint('heart_rate_api', __name__)

def init_heart_rate_api(arduino_controller):
    """
    初始化心率监测API
    
    Args:
        arduino_controller: Arduino控制器实例
        
    Returns:
        Blueprint: 初始化后的蓝图对象
    """
    
    @heart_rate_api.route('/api/heart-rate', methods=['GET'])
    def get_heart_rate():
        """获取心率"""
        if arduino_controller: # 检查 arduino_controller 是否为 None
            heart_rate = arduino_controller.get_heart_rate()
            return jsonify({
                'status': 'ok' if heart_rate is not None else 'error',
                'heart_rate': heart_rate,
                'timestamp': datetime.now().isoformat(),
                'message': '获取心率成功' if heart_rate is not None else 'Arduino未连接或数据不可用'
            })
        else:
            return jsonify({ # Arduino 不可用时的响应
                'status': 'error',
                'heart_rate': None,
                'timestamp': datetime.now().isoformat(),
                'message': 'Arduino控制器不可用 (仅相机模式)'
            }), 503 # Service Unavailable
    
    # 返回蓝图
    return heart_rate_api 