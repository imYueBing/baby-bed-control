#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视频监控API端点模块 - 为前端应用提供视频监控接口
"""

import logging
import io
from flask import Blueprint, jsonify, request, Response, send_file

# 配置日志
logger = logging.getLogger(__name__)

# 创建蓝图
video_api = Blueprint('video_api', __name__)

def init_video_api(camera_manager):
    """
    初始化视频监控API
    
    Args:
        camera_manager: 摄像头管理器实例
        
    Returns:
        Blueprint: 初始化后的蓝图对象
    """
    
    @video_api.route('/api/video/snapshot', methods=['GET'])
    def get_snapshot():
        """获取视频快照"""
        jpeg_data = camera_manager.get_jpeg_frame()
        if jpeg_data:
            return Response(jpeg_data, mimetype='image/jpeg')
        else:
            return jsonify({
                'status': 'error',
                'message': '无法获取视频快照'
            }), 500
    
    @video_api.route('/api/video/stream')
    def video_stream():
        """视频流端点（MJPEG）"""
        return Response(
            _generate_mjpeg_stream(camera_manager),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    
    @video_api.route('/api/video/recording', methods=['POST'])
    def control_recording():
        """控制视频录制"""
        action = request.json.get('action')
        
        if action == 'start':
            output_dir = request.json.get('output_dir', 'videos')
            success = camera_manager.start_recording(output_dir)
            return jsonify({
                'status': 'ok' if success else 'error',
                'action': 'start',
                'message': '开始录制视频' if success else '无法开始录制视频'
            })
        
        elif action == 'stop':
            camera_manager.stop_recording()
            return jsonify({
                'status': 'ok',
                'action': 'stop',
                'message': '停止录制视频'
            })
        
        else:
            return jsonify({
                'status': 'error',
                'message': '无效的操作'
            }), 400
    
    # 返回蓝图
    return video_api

def _generate_mjpeg_stream(camera_manager):
    """
    生成MJPEG流
    
    Args:
        camera_manager: 摄像头管理器实例
        
    Yields:
        bytes: JPEG帧数据
    """
    while True:
        frame = camera_manager.get_jpeg_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # 如果无法获取帧，返回空图像
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n') 