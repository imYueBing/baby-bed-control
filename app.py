#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
婴儿智能监控系统主程序
"""

import logging
import os
import signal
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('baby_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

# 导入模块
from modules.arduino.controller import ArduinoController
from modules.camera.camera_manager import CameraManager
from api.server import APIServer
from config.settings import get_config

def setup():
    """初始化系统组件"""
    logger.info("婴儿智能监控系统启动中...")
    
    # 加载配置
    config = get_config()
    
    # 初始化Arduino控制器
    arduino_controller = ArduinoController(
        port=config.get('arduino', 'port'),
        baud_rate=config.get('arduino', 'baud_rate', 9600)
    )
    
    # 初始化摄像头管理器
    camera_manager = CameraManager(
        resolution=config.get('camera', 'resolution', (640, 480)),
        framerate=config.get('camera', 'framerate', 30)
    )
    
    # 初始化API服务器
    api_server = APIServer(
        arduino_controller=arduino_controller,
        camera_manager=camera_manager,
        host=config.get('server', 'host', '0.0.0.0'),
        port=config.get('server', 'port', 5000)
    )
    
    # 返回初始化的组件
    return arduino_controller, camera_manager, api_server

def cleanup(arduino_controller, camera_manager, api_server):
    """清理资源"""
    logger.info("系统正在关闭...")
    
    # 关闭Arduino连接
    if arduino_controller:
        arduino_controller.close()
    
    # 关闭摄像头
    if camera_manager:
        camera_manager.close()
    
    # 关闭API服务器
    if api_server:
        api_server.stop()
    
    logger.info("系统已安全关闭")

def signal_handler(sig, frame, components=None):
    """处理系统信号"""
    if components:
        cleanup(*components)
    sys.exit(0)

def main():
    """主函数"""
    try:
        # 初始化组件
        components = setup()
        
        # 注册信号处理
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, components))
        signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, components))
        
        # 启动API服务器
        api_server = components[2]
        api_server.start()
        
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        if 'components' in locals():
            cleanup(*components)
        sys.exit(1)

if __name__ == "__main__":
    main() 