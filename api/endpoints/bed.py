#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
床体控制API端点模块 - 为前端应用提供床体控制接口
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
    
    @bed_api.route('/api/bed/up', methods=['POST'])
    def bed_up():
        """升高床"""
        success = arduino_controller.bed_up()
        logger.info(f"床体上升命令: {'成功' if success else '失败'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'up',
            'message': '已开始升高床' if success else 'Arduino未连接'
        })
    
    @bed_api.route('/api/bed/down', methods=['POST'])
    def bed_down():
        """降低床"""
        success = arduino_controller.bed_down()
        logger.info(f"床体下降命令: {'成功' if success else '失败'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'down',
            'message': '已开始降低床' if success else 'Arduino未连接'
        })
    
    @bed_api.route('/api/bed/stop', methods=['POST'])
    def bed_stop():
        """停止床体移动"""
        success = arduino_controller.bed_stop()
        logger.info(f"床体停止命令: {'成功' if success else '失败'}")
        return jsonify({
            'status': 'ok' if success else 'error',
            'action': 'stop',
            'message': '已停止床体移动' if success else 'Arduino未连接'
        })
    
    @bed_api.route('/api/bed/height', methods=['GET'])
    def get_bed_height():
        """获取床体高度"""
        height = arduino_controller.get_bed_height()
        return jsonify({
            'status': 'ok' if height is not None else 'error',
            'bed_height': height,
            'message': '获取床体高度成功' if height is not None else 'Arduino未连接'
        })
    
    # 返回蓝图
    return bed_api 