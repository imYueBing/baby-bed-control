#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
心率WebSocket事件处理模块
"""

import logging
from datetime import datetime
from flask_socketio import emit, SocketIO
from mock_arduino_controller import MockArduinoController  # 导入模拟类

# 配置日志
logger = logging.getLogger(__name__)

def register_heart_rate_socketio_events(socketio, arduino_controller=None):
    """
    注册心率相关的WebSocket事件处理程序
    
    Args:
        socketio: SocketIO实例
        arduino_controller: Arduino控制器实例（可选）
    """
    
    # 如果没有提供 Arduino 控制器，使用模拟控制器
    if arduino_controller is None:
        logger.info("Arduino 控制器不可用，使用模拟控制器")
        arduino_controller = MockArduinoController()
    
    def heart_rate_callback(heart_rate):
        """
        心率数据回调函数
        
        Args:
            heart_rate (int): 心率值
        """
        socketio.emit('heart_rate_update', {
            'heart_rate': heart_rate,
            'timestamp': datetime.now().isoformat(),
            'status': 'ok'
        })
    
    # 添加心率回调到控制器
    arduino_controller.subscribe_heart_rate(heart_rate_callback)
    
    @socketio.on('request_heart_rate')
    def handle_heart_rate_request():
        """处理心率请求"""
        heart_rate = arduino_controller.get_heart_rate()
        emit('heart_rate_update', {
            'heart_rate': heart_rate,
            'timestamp': datetime.now().isoformat(),
            'status': 'ok' if heart_rate is not None else 'error'
        })

# 初始化 SocketIO
socketio = SocketIO()

# 注册 WebSocket 事件，假设没有实际的 Arduino 控制器
register_heart_rate_socketio_events(socketio) 