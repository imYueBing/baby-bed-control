#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
心率WebSocket事件处理模块
"""

import logging
from datetime import datetime
from flask_socketio import emit
from .mock_arduino import MockArduinoController


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
        from .mock_arduino import MockArduinoController
        arduino_controller = MockArduinoController()
    
    def heart_rate_callback(heart_rate):
        logger.info(f"推送心率数据: {heart_rate}")
        try:
            socketio.emit('heart_rate_update', {
                'heart_rate': heart_rate,
                'timestamp': datetime.now().isoformat(),
                'status': 'ok'
            })
            logger.debug("心率数据推送成功")
        except Exception as e:
            logger.error(f"推送心率数据时出错: {e}")

    # 订阅心率数据更新回调
    try:
        arduino_controller.subscribe_heart_rate(heart_rate_callback)
        logger.info("已订阅心率数据更新")
    except Exception as e:
        logger.error(f"订阅心率数据更新失败: {e}")

    @socketio.on('request_heart_rate')
    def handle_heart_rate_request():
        logger.info("收到WebSocket心率请求")
        try:
            heart_rate = arduino_controller.get_heart_rate()
            logger.info(f"WebSocket请求的心率值: {heart_rate}")
            
            # 如果心率为None，多尝试几次
            retry_count = 0
            while heart_rate is None and retry_count < 3:
                logger.warning(f"WebSocket心率为空，尝试重新获取 (尝试 {retry_count+1}/3)")
                heart_rate = arduino_controller.get_heart_rate()
                retry_count += 1
            
            response = {
                'heart_rate': heart_rate,
                'timestamp': datetime.now().isoformat(),
                'status': 'ok' if heart_rate is not None else 'error',
                'retry_count': retry_count
            }
            
            emit('heart_rate_update', response)
            logger.info(f"已发送WebSocket心率响应: {response}")
        except Exception as e:
            logger.error(f"处理WebSocket心率请求时出错: {e}")
            emit('heart_rate_update', {
                'heart_rate': None,
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'message': f'获取心率时发生错误: {str(e)}'
            })
