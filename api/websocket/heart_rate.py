#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
心率WebSocket事件处理模块
"""

import logging
from datetime import datetime
from flask_socketio import emit
from mock_arduino import MockArduinoController


logger = logging.getLogger(__name__)

def register_heart_rate_socketio_events(socketio, arduino_controller=None):
    """
    注册心率相关的WebSocket事件处理程序
    
    Args:
        socketio: Flask-SocketIO实例
        arduino_controller: Arduino控制器实例（可选），如果未传入则使用模拟控制器
    """
    
    if arduino_controller is None:
        logger.info("Arduino 控制器不可用，使用模拟控制器")
        arduino_controller = MockArduinoController()
    
    def heart_rate_callback(heart_rate):
        logger.debug(f"推送心率数据: {heart_rate}")
        socketio.emit('heart_rate_update', {
            'heart_rate': heart_rate,
            'timestamp': datetime.now().isoformat(),
            'status': 'ok'
        })

    # 订阅心率数据更新回调
    arduino_controller.subscribe_heart_rate(heart_rate_callback)

    @socketio.on('request_heart_rate')
    def handle_heart_rate_request():
        heart_rate = arduino_controller.get_heart_rate()
        logger.info(f"客户端请求心率，当前值: {heart_rate}")
        emit('heart_rate_update', {
            'heart_rate': heart_rate,
            'timestamp': datetime.now().isoformat(),
            'status': 'ok' if heart_rate is not None else 'error'
        })
