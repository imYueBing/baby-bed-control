#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
婴儿智能监控系统主程序
"""

import logging
import os
import signal
import sys
import argparse
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

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='婴儿智能监控系统')
    parser.add_argument('--debug-camera', action='store_true', 
                        help='启用摄像头调试窗口，在本地显示摄像头画面')
    parser.add_argument('--debug-window-name', type=str, default='摄像头调试',
                        help='调试窗口名称')
    return parser.parse_args()

def setup():
    """初始化系统组件"""
    logger.info("婴儿智能监控系统启动中...")

    config = get_config()

    arduino_controller = None
    camera_manager = None
    api_server = None

    # 初始化 Arduino 控制器
    try:
        arduino_controller = ArduinoController(
            port=config.get('arduino', 'port'),
            baud_rate=config.get('arduino', 'baud_rate', 9600)
        )
        logger.info("Arduino 控制器初始化成功")
    except Exception as e:
        logger.warning(f"Arduino 初始化失败: {e}")

    # 初始化 摄像头管理器
    try:
        camera_manager = CameraManager(
            resolution=config.get('camera', 'resolution', [640, 480]),
            framerate=config.get('camera', 'framerate', 30)
        )
        logger.info("摄像头管理器初始化成功")
    except Exception as e:
        logger.warning(f"摄像头初始化失败: {e}")

    # 初始化 API 服务器（不依赖上面两个是否成功）
    try:
        api_server = APIServer(
            arduino_controller=arduino_controller,
            camera_manager=camera_manager,
            host=config.get('server', 'host', '0.0.0.0'),
            port=config.get('server', 'port', 5000)
        )
        logger.info("API 服务器初始化成功")
    except Exception as e:
        logger.error(f"API 服务器初始化失败: {e}")
        raise

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
    # 解析命令行参数
    args = parse_args()
    
    try:
        # 初始化组件
        components = setup()
        arduino_controller, camera_manager, api_server = components
        
        # 注册信号处理
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, components))
        signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, components))
        
        # 启动API服务器
        api_server.start()
        
        # 如果启用了摄像头调试，打开调试窗口
        if args.debug_camera:
            logger.info(f"启用摄像头调试窗口: {args.debug_window_name}")
            if camera_manager:
                camera_manager.start_debug_window(args.debug_window_name)
            print(f"摄像头调试窗口已启动: {args.debug_window_name}")
            print("按ESC键可关闭调试窗口")
        
        # 保持主线程运行
        print("系统已启动，按Ctrl+C退出")
        while True:
            signal.pause()
            
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        if 'components' in locals():
            cleanup(*components)
        sys.exit(1)

if __name__ == "__main__":
    main() 