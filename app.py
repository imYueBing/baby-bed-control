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
import time
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
from modules.auto_face_tracker import AutoFaceTracker  # 导入自动人脸跟踪模块
from api.server import APIServer
from config.settings import get_config

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='婴儿智能监控系统')
    parser.add_argument('--debug-camera', action='store_true', 
                        help='启用摄像头调试窗口，在本地显示摄像头画面')
    parser.add_argument('--debug-window-name', type=str, default='摄像头调试',
                        help='调试窗口名称')
    parser.add_argument('--only-camera', action='store_true', 
                        help='仅测试摄像头，不启动完整系统')
    parser.add_argument('--no-arduino', action='store_true',  # <--- 确保这行在 app.py 的 parse_args 中
                        help='不使用Arduino控制器，以仅相机模式运行')
    parser.add_argument('--enable-face-detection', action='store_true',
                        help='启用AI人脸识别功能 (覆盖config.json的设置)')
    parser.add_argument('--disable-face-detection', action='store_true',
                        help='禁用AI人脸识别功能 (覆盖config.json的设置)')
    parser.add_argument('--enable-face-tracker', action='store_true',
                        help='启用自动人脸跟踪功能')
    return parser.parse_args()

def setup(args):
    """初始化系统组件"""
    logger.info("婴儿智能监控系统启动中...")

    config = get_config()

    arduino_controller = None
    camera_manager = None
    api_server = None
    face_tracker = None

    # 初始化 Arduino 控制器（如果未指定--no-arduino）
    if not args.no_arduino:
        try:
            arduino_controller = ArduinoController(
                port=config.get('arduino', 'port'),
                baud_rate=config.get('arduino', 'baud_rate', 9600)
            )
            logger.info("Arduino 控制器初始化成功")
        except Exception as e:
            logger.warning(f"Arduino 初始化失败: {e}")
    else:
        logger.info("以仅相机模式运行，不使用Arduino控制器")

    # 初始化 摄像头管理器
    try:
        # 决定是否启用AI人脸识别，命令行参数优先于配置文件
        enable_ai_detection_config = config.get('camera', 'enable_ai_face_detection', False)
        if args.enable_face_detection:
            final_enable_ai_detection = True
        elif args.disable_face_detection:
            final_enable_ai_detection = False
        else:
            final_enable_ai_detection = enable_ai_detection_config

        camera_manager = CameraManager(
            resolution=config.get('camera', 'resolution', [640, 480]),
            framerate=config.get('camera', 'framerate', 30),
            use_picamera=config.get('camera', 'use_picamera', True),
            enable_ai_face_detection=final_enable_ai_detection, # 使用最终确定的值
            cascade_path=config.get('camera', 'cascade_path', 'models/haarcascade_frontalface_default.xml'),
            tflite_model_path=config.get('camera', 'tflite_model_path', 'models/frontal_face_classifier.tflite')
        )
        logger.info("摄像头管理器初始化成功")
    except Exception as e:
        logger.warning(f"摄像头初始化失败: {e}")

    # 初始化自动人脸跟踪器（如果启用）
    if args.enable_face_tracker and camera_manager and arduino_controller:
        try:
            face_tracker = AutoFaceTracker(
                camera_manager=camera_manager,
                arduino_controller=arduino_controller,
                scan_interval=config.get('face_tracker', 'scan_interval', 3.0),
                movement_delay=config.get('face_tracker', 'movement_delay', 2.0),
                face_detection_threshold=config.get('face_tracker', 'face_detection_threshold', 3)
            )
            logger.info("自动人脸跟踪器初始化成功")
        except Exception as e:
            logger.warning(f"自动人脸跟踪器初始化失败: {e}")
    elif args.enable_face_tracker:
        if not camera_manager:
            logger.warning("无法初始化自动人脸跟踪器：摄像头未初始化")
        if not arduino_controller:
            logger.warning("无法初始化自动人脸跟踪器：Arduino控制器未初始化")

    # 初始化 API 服务器 - 这里应该只创建 APIServer 实例
    api_server_instance = APIServer(
        arduino_controller=arduino_controller,
        camera_manager=camera_manager,
        host=config.get('server', 'host', '0.0.0.0'),
        port=config.get('server', 'port', 5000)
    )
    logger.info("API 服务器对象创建成功")

    # 将自动人脸跟踪器添加到API服务器的应用上下文中
    api_server_instance.app.face_tracker = face_tracker

    return arduino_controller, camera_manager, api_server_instance, face_tracker

def cleanup(arduino_controller, camera_manager, api_server, face_tracker=None):
    """清理资源"""
    logger.info("系统正在关闭...")
    
    # 停止自动人脸跟踪
    if face_tracker:
        face_tracker.stop()
    
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
    args = parse_args()
    
    try:
        if args.only_camera:
            try:
                print("仅启动摄像头测试模式...")
                camera = CameraManager(
                    resolution=(640, 480),
                    framerate=30
                )
                camera.start_debug_window("摄像头测试")
                print("按ESC键退出")
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print(f"摄像头测试失败: {e}")
            finally:
                if 'camera' in locals():
                    camera.close()
                return

        components = setup(args)
        arduino_controller, camera_manager, api_server_instance, face_tracker = components
        
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, components))
        signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, components))
        
        if api_server_instance:
            api_server_instance.start()
        else:
            logger.error("API 服务器实例未能创建。")
            return
        
        if args.debug_camera and camera_manager:
            logger.info(f"启用摄像头调试窗口: {args.debug_window_name}")
            camera_manager.start_debug_window(args.debug_window_name)
            print(f"摄像头调试窗口已启动: {args.debug_window_name}")
            print("按ESC键可关闭调试窗口")
        
        # 如果启用了自动人脸跟踪，启动它
        if args.enable_face_tracker and face_tracker:
            face_tracker.start()
            print("自动人脸跟踪已启动")
        
        print("系统已启动" + ("（仅相机模式）" if args.no_arduino else ""))
        print("按Ctrl+C退出")
        while True:
            signal.pause()
            
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        if 'components' in locals() and len(components) >= 3:
            cleanup(*components)
        elif 'components' in locals():
            if components[0]: components[0].close()
            if components[1]: components[1].close()
        sys.exit(1)

if __name__ == "__main__":
    main() 