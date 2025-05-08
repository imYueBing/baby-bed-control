#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API测试脚本 - 测试模块化后的API结构
"""

import logging
import sys
from flask import Flask
from flask_socketio import SocketIO

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 导入必要的模块
from modules.arduino.controller import ArduinoController
from api.endpoints.bed import init_bed_api
from api.endpoints.heart_rate import init_heart_rate_api
from api.endpoints.system import init_system_api
from api.websocket.bed import register_bed_socketio_events
from api.websocket.heart_rate import register_heart_rate_socketio_events

def test_api():
    """测试API初始化"""
    try:
        # 创建测试用的Arduino控制器（使用模拟设备）
        arduino_controller = ArduinoController(port=None)
        
        # 创建Flask应用
        app = Flask(__name__)
        socketio = SocketIO(app, cors_allowed_origins="*")
        
        # 注册API蓝图
        app.register_blueprint(init_bed_api(arduino_controller))
        app.register_blueprint(init_heart_rate_api(arduino_controller))
        app.register_blueprint(init_system_api(arduino_controller, None))
        
        # 注册WebSocket事件
        register_bed_socketio_events(socketio, arduino_controller)
        register_heart_rate_socketio_events(socketio, arduino_controller)
        
        # 打印已注册的路由
        logger.info("已注册的API路由:")
        for rule in app.url_map.iter_rules():
            if not str(rule).startswith('/static'):
                logger.info(f"  {rule} ({', '.join(rule.methods)})")
        
        logger.info("API初始化测试成功!")
        return True
        
    except Exception as e:
        logger.error(f"API初始化测试失败: {e}")
        return False

if __name__ == "__main__":
    if test_api():
        sys.exit(0)
    else:
        sys.exit(1) 