#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视频WebSocket事件处理模块
"""

import logging
import base64
from flask_socketio import emit

# 配置日志
logger = logging.getLogger(__name__)

def register_video_socketio_events(socketio, camera_manager):
    """
    注册视频相关的WebSocket事件处理程序
    
    Args:
        socketio: SocketIO实例
        camera_manager: 摄像头管理器实例
    """
    
    @socketio.on('request_video_frame')
    def handle_video_frame_request():
        """处理视频帧请求"""
        jpeg_data = camera_manager.get_jpeg_frame()
        if jpeg_data:
            # 将二进制数据转换为Base64
            base64_data = base64.b64encode(jpeg_data).decode('utf-8')
            emit('video_frame', {
                'frame': base64_data,
                'status': 'ok'
            })
        else:
            emit('video_frame', {
                'status': 'error',
                'message': '无法获取视频帧'
            })
    
    @socketio.on('start_recording')
    def handle_start_recording(data):
        """处理开始录制请求"""
        output_dir = data.get('output_dir', 'videos')
        success = camera_manager.start_recording(output_dir)
        
        emit('recording_status', {
            'status': 'ok' if success else 'error',
            'action': 'start',
            'recording': success,
            'message': '开始录制视频' if success else '无法开始录制视频'
        })
    
    @socketio.on('stop_recording')
    def handle_stop_recording():
        """处理停止录制请求"""
        camera_manager.stop_recording()
        
        emit('recording_status', {
            'status': 'ok',
            'action': 'stop',
            'recording': False,
            'message': '停止录制视频'
        }) 