#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自动人脸跟踪API端点
"""

from flask import Blueprint, jsonify, request, current_app
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 创建蓝图
face_tracker_bp = Blueprint('face_tracker', __name__)

@face_tracker_bp.route('/api/face_tracker/start', methods=['POST'])
def start_face_tracker():
    """启动自动人脸跟踪"""
    try:
        # 获取应用上下文中的自动人脸跟踪器
        face_tracker = current_app.face_tracker
        if not face_tracker:
            return jsonify({
                'success': False,
                'message': '自动人脸跟踪器未初始化'
            }), 500
        
        # 从请求中获取参数（如果有）
        data = request.get_json() or {}
        scan_interval = data.get('scan_interval', None)
        movement_delay = data.get('movement_delay', None)
        face_detection_threshold = data.get('face_detection_threshold', None)
        
        # 如果提供了参数，更新跟踪器的配置
        if scan_interval is not None:
            face_tracker.scan_interval = float(scan_interval)
        if movement_delay is not None:
            face_tracker.movement_delay = float(movement_delay)
        if face_detection_threshold is not None:
            face_tracker.face_detection_threshold = int(face_detection_threshold)
        
        # 启动自动人脸跟踪
        success = face_tracker.start()
        
        if success:
            return jsonify({
                'success': True,
                'message': '自动人脸跟踪已启动',
                'config': {
                    'scan_interval': face_tracker.scan_interval,
                    'movement_delay': face_tracker.movement_delay,
                    'face_detection_threshold': face_tracker.face_detection_threshold
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '启动自动人脸跟踪失败'
            }), 500
            
    except Exception as e:
        logger.error(f"启动自动人脸跟踪出错: {e}")
        return jsonify({
            'success': False,
            'message': f'启动自动人脸跟踪时发生错误: {str(e)}'
        }), 500

@face_tracker_bp.route('/api/face_tracker/stop', methods=['POST'])
def stop_face_tracker():
    """停止自动人脸跟踪"""
    try:
        # 获取应用上下文中的自动人脸跟踪器
        face_tracker = current_app.face_tracker
        if not face_tracker:
            return jsonify({
                'success': False,
                'message': '自动人脸跟踪器未初始化'
            }), 500
        
        # 停止自动人脸跟踪
        face_tracker.stop()
        
        return jsonify({
            'success': True,
            'message': '自动人脸跟踪已停止'
        })
            
    except Exception as e:
        logger.error(f"停止自动人脸跟踪出错: {e}")
        return jsonify({
            'success': False,
            'message': f'停止自动人脸跟踪时发生错误: {str(e)}'
        }), 500

@face_tracker_bp.route('/api/face_tracker/status', methods=['GET'])
def get_face_tracker_status():
    """获取自动人脸跟踪状态"""
    try:
        # 获取应用上下文中的自动人脸跟踪器
        face_tracker = current_app.face_tracker
        if not face_tracker:
            return jsonify({
                'success': False,
                'message': '自动人脸跟踪器未初始化'
            }), 500
        
        return jsonify({
            'success': True,
            'status': {
                'is_running': face_tracker.is_running,
                'scan_interval': face_tracker.scan_interval,
                'movement_delay': face_tracker.movement_delay,
                'face_detection_threshold': face_tracker.face_detection_threshold,
                'no_face_count': face_tracker.no_face_count,
                'last_face_detected': face_tracker.last_face_detected,
                'current_sequence_index': face_tracker.current_sequence_index
            }
        })
            
    except Exception as e:
        logger.error(f"获取自动人脸跟踪状态出错: {e}")
        return jsonify({
            'success': False,
            'message': f'获取自动人脸跟踪状态时发生错误: {str(e)}'
        }), 500

@face_tracker_bp.route('/api/face_tracker/config', methods=['POST'])
def update_face_tracker_config():
    """更新自动人脸跟踪配置"""
    try:
        # 获取应用上下文中的自动人脸跟踪器
        face_tracker = current_app.face_tracker
        if not face_tracker:
            return jsonify({
                'success': False,
                'message': '自动人脸跟踪器未初始化'
            }), 500
        
        # 从请求中获取参数
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '未提供配置参数'
            }), 400
        
        # 更新配置
        if 'scan_interval' in data:
            face_tracker.scan_interval = float(data['scan_interval'])
        
        if 'movement_delay' in data:
            face_tracker.movement_delay = float(data['movement_delay'])
        
        if 'face_detection_threshold' in data:
            face_tracker.face_detection_threshold = int(data['face_detection_threshold'])
        
        if 'adjustment_sequence' in data:
            face_tracker.adjustment_sequence = data['adjustment_sequence']
            face_tracker.current_sequence_index = 0
        
        return jsonify({
            'success': True,
            'message': '自动人脸跟踪配置已更新',
            'config': {
                'scan_interval': face_tracker.scan_interval,
                'movement_delay': face_tracker.movement_delay,
                'face_detection_threshold': face_tracker.face_detection_threshold,
                'current_sequence_index': face_tracker.current_sequence_index
            }
        })
            
    except Exception as e:
        logger.error(f"更新自动人脸跟踪配置出错: {e}")
        return jsonify({
            'success': False,
            'message': f'更新自动人脸跟踪配置时发生错误: {str(e)}'
        }), 500 