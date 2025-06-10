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
        logger.info("收到心率API请求")
        
        if arduino_controller: # 检查 arduino_controller 是否为 None
            try:
                heart_rate = arduino_controller.get_heart_rate()
                logger.info(f"获取到心率值: {heart_rate}")
                
                # 如果心率为None，多尝试几次
                retry_count = 0
                while heart_rate is None and retry_count < 3:
                    logger.warning(f"心率为空，尝试重新获取 (尝试 {retry_count+1}/3)")
                    heart_rate = arduino_controller.get_heart_rate()
                    retry_count += 1
                
                response = {
                    'status': 'ok' if heart_rate is not None else 'error',
                    'heart_rate': heart_rate,
                    'timestamp': datetime.now().isoformat(),
                    'message': '获取心率成功' if heart_rate is not None else 'Arduino未连接或数据不可用',
                    'retry_count': retry_count
                }
                
                logger.info(f"心率API响应: {response}")
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"获取心率时发生错误: {e}", exc_info=True)
                return jsonify({
                    'status': 'error',
                    'heart_rate': None,
                    'timestamp': datetime.now().isoformat(),
                    'message': f'获取心率时发生错误: {str(e)}'
                }), 500
        else:
            logger.warning("心率API请求失败: Arduino控制器不可用")
            return jsonify({ # Arduino 不可用时的响应
                'status': 'error',
                'heart_rate': None,
                'timestamp': datetime.now().isoformat(),
                'message': 'Arduino控制器不可用 (仅相机模式)'
            }), 503 # Service Unavailable
    
    # 返回蓝图
    return heart_rate_api 