#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
床体控制WebSocket事件处理模块
"""

import logging
from flask_socketio import emit

# 配置日志
logger = logging.getLogger(__name__)

def register_bed_socketio_events(socketio, arduino_controller):
    """
    注册床体控制相关的WebSocket事件处理程序
    
    Args:
        socketio: SocketIO实例
        arduino_controller: Arduino控制器实例
    """
    
    @socketio.on('bed_control')
    def handle_bed_control(data):
        """处理床控制事件"""
        action = data.get('action')
        
        if action == 'up':
            success = arduino_controller.bed_up()
            logger.info(f"WebSocket床体上升命令: {'成功' if success else '失败'}")
        elif action == 'down':
            success = arduino_controller.bed_down()
            logger.info(f"WebSocket床体下降命令: {'成功' if success else '失败'}")
        elif action == 'stop':
            success = arduino_controller.bed_stop()
            logger.info(f"WebSocket床体停止命令: {'成功' if success else '失败'}")
        else:
            emit('error', {'message': '无效的床控制操作'})
            return
        
        emit('bed_control_response', {
            'status': 'ok' if success else 'error',
            'action': action,
            'message': f'床体{action}操作' + ('成功' if success else '失败')
        })
        
        # 发送更新后的状态
        emit_bed_status_update(arduino_controller)

def emit_bed_status_update(arduino_controller):
    """
    发送床体状态更新
    
    Args:
        arduino_controller: Arduino控制器实例
    """
    bed_height = arduino_controller.get_bed_height()
    
    emit('bed_status_update', {
        'bed_height': bed_height,
        'status': 'ok' if bed_height is not None else 'error'
    }) 