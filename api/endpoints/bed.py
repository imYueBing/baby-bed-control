#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
床体控制API端点模块 - 为前端应用提供床体控制接口，支持左右独立控制
"""

import logging
from flask import Blueprint, jsonify, request

# 配置日志
logger = logging.getLogger(__name__)

# 创建蓝图
bed_api = Blueprint('bed_api', __name__)

def init_bed_api(arduino_controller):
    """
    初始化床体控制API
    
    Args:
        arduino_controller: Arduino控制器实例
        
    Returns:
        Blueprint: 初始化后的蓝图对象
    """
    
    # --------- 整体控制 ---------
    
    @bed_api.route('/api/bed/up', methods=['POST'])
    def bed_up():
        """整体升高床"""
        success = arduino_controller.bed_up()
        logger.info(f"床体整体上升命令: {'成功' if success else '失败'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'up',
            'message': '已开始整体升高床' if success else 'Arduino未连接'
        })
    
    @bed_api.route('/api/bed/down', methods=['POST'])
    def bed_down():
        """整体降低床"""
        success = arduino_controller.bed_down()
        logger.info(f"床体整体下降命令: {'成功' if success else '失败'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'down',
            'message': '已开始整体降低床' if success else 'Arduino未连接'
        })
    
    @bed_api.route('/api/bed/stop', methods=['POST'])
    def bed_stop():
        """整体停止床体移动"""
        success = arduino_controller.bed_stop()
        logger.info(f"床体整体停止命令: {'成功' if success else '失败'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'stop',
            'message': '已整体停止床体移动' if success else 'Arduino未连接'
        })
    
    # --------- 左侧控制 ---------
    
    @bed_api.route('/api/bed/left_up', methods=['POST'])
    def bed_left_up():
        """左侧升高床"""
        success = arduino_controller.left_up()
        logger.info(f"床体左侧上升命令: {'成功' if success else '失败'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'left_up',
            'message': '已开始左侧升高床' if success else 'Arduino未连接'
        })
    
    @bed_api.route('/api/bed/left_down', methods=['POST'])
    def bed_left_down():
        """左侧降低床"""
        success = arduino_controller.left_down()
        logger.info(f"床体左侧下降命令: {'成功' if success else '失败'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'left_down',
            'message': '已开始左侧降低床' if success else 'Arduino未连接'
        })
    
    @bed_api.route('/api/bed/left_stop', methods=['POST'])
    def bed_left_stop():
        """左侧停止床体移动"""
        success = arduino_controller.left_stop()
        logger.info(f"床体左侧停止命令: {'成功' if success else '失败'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'left_stop',
            'message': '已左侧停止床体移动' if success else 'Arduino未连接'
        })
    
    # --------- 右侧控制 ---------
    
    @bed_api.route('/api/bed/right_up', methods=['POST'])
    def bed_right_up():
        """右侧升高床"""
        success = arduino_controller.right_up()
        logger.info(f"床体右侧上升命令: {'成功' if success else '失败'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'right_up',
            'message': '已开始右侧升高床' if success else 'Arduino未连接'
        })
    
    @bed_api.route('/api/bed/right_down', methods=['POST'])
    def bed_right_down():
        """右侧降低床"""
        success = arduino_controller.right_down()
        logger.info(f"床体右侧下降命令: {'成功' if success else '失败'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'right_down',
            'message': '已开始右侧降低床' if success else 'Arduino未连接'
        })
    
    @bed_api.route('/api/bed/right_stop', methods=['POST'])
    def bed_right_stop():
        """右侧停止床体移动"""
        success = arduino_controller.right_stop()
        logger.info(f"床体右侧停止命令: {'成功' if success else '失败'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'right_stop',
            'message': '已右侧停止床体移动' if success else 'Arduino未连接'
        })
    
    # --------- 状态查询 ---------
    
    @bed_api.route('/api/bed/status', methods=['GET'])
    def get_bed_status():
        """获取床体状态"""
        status = arduino_controller.get_bed_status()
        return jsonify({
            'status': 'ok' if status else 'error',
            'bed_status': status,
            'message': '获取床体状态成功' if status else 'Arduino未连接'
        })
    
    @bed_api.route('/api/bed/height', methods=['GET'])
    def get_bed_height():
        """获取床体高度 (为兼容旧API保留)"""
        status = arduino_controller.get_bed_status()
        return jsonify({
            'status': 'ok' if status else 'error',
            'bed_status': status,
            'message': '获取床体状态成功' if status else 'Arduino未连接'
        })
    
    # 返回蓝图
    return bed_api 