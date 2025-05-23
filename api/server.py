#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API服务器模块 - 为前端应用提供HTTP和WebSocket接口
"""

import logging
import threading
import time
from flask import Flask
from flask_socketio import SocketIO
import argparse
import signal
import sys

# 导入API端点
from .endpoints.bed import bed_api, init_bed_api
from .endpoints.heart_rate import heart_rate_api, init_heart_rate_api
from .endpoints.video import video_api, init_video_api
from .endpoints.system import system_api, init_system_api

# 导入WebSocket事件处理
from .websocket.bed import register_bed_socketio_events
from .websocket.heart_rate import register_heart_rate_socketio_events
from .websocket.video import register_video_socketio_events

# 配置日志
logger = logging.getLogger(__name__)

class APIServer:
    """API服务器类，为前端应用提供接口"""
    
    def __init__(self, arduino_controller, camera_manager, host='0.0.0.0', port=5000, debug=False):
        """
        初始化API服务器
        
        Args:
            arduino_controller: Arduino控制器实例，可以为None表示不使用Arduino
            camera_manager: 摄像头管理器实例
            host (str): 监听主机
            port (int): 监听端口
            debug (bool): 是否启用调试模式
        """
        self.arduino_controller = arduino_controller
        self.camera_manager = camera_manager
        self.host = host
        self.port = port
        self.debug = debug
        self.server_thread = None
        self.is_running = False
        
        # 添加一个标志，表示Arduino控制器是否可用
        self.arduino_available = arduino_controller is not None
        
        # 如果Arduino控制器不可用，记录警告日志
        if not self.arduino_available:
            logger.warning("Arduino控制器未提供，将以'仅相机模式'运行。所有与Arduino相关的功能将不可用或返回模拟数据。")
        
        # 初始化Flask应用
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        
        # 配置API蓝图
        self._setup_blueprints()
        
        # 配置WebSocket事件
        self._setup_socketio_events()
    
    def _setup_blueprints(self):
        """配置API蓝图"""
        # 注册床体控制API
        self.app.register_blueprint(init_bed_api(self.arduino_controller))
        
        # 注册心率监测API
        self.app.register_blueprint(init_heart_rate_api(self.arduino_controller))
        
        # 注册视频监控API
        self.app.register_blueprint(init_video_api(self.camera_manager))
        
        # 注册系统信息API
        self.app.register_blueprint(init_system_api(self.arduino_controller, self.camera_manager))
    
    def _setup_socketio_events(self):
        """配置WebSocket事件"""
        # 连接和断开事件
        @self.socketio.on('connect')
        def handle_connect():
            """处理WebSocket连接"""
            logger.info("新的WebSocket客户端已连接")
            self.socketio.emit('welcome', {'message': '已连接到婴儿监控系统'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """处理WebSocket断开连接"""
            logger.info("WebSocket客户端已断开连接")
        
        # 注册功能模块的WebSocket事件
        register_bed_socketio_events(self.socketio, self.arduino_controller)
        register_heart_rate_socketio_events(self.socketio, self.arduino_controller)
        register_video_socketio_events(self.socketio, self.camera_manager)
    
    def start(self):
        """启动服务器"""
        if self.is_running:
            logger.warning("服务器已经在运行")
            return
        
        logger.info(f"启动API服务器: {self.host}:{self.port}")
        
        # 使用线程运行服务器
        self.is_running = True
        self.server_thread = threading.Thread(
            target=self._run_server
        )
        self.server_thread.daemon = True
        self.server_thread.start()
        
        logger.info("API服务器已启动")
    
    def _run_server(self):
        """运行服务器（在线程中）"""
        try:
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=self.debug,
                use_reloader=False  # 禁用重载器，避免在线程中启动时的问题
            )
        except Exception as e:
            logger.error(f"API服务器运行错误: {e}")
            self.is_running = False
    
    def stop(self):
        """停止服务器"""
        if not self.is_running:
            logger.warning("服务器未运行")
            return
        
        logger.info("停止API服务器")
        
        # 标记为停止
        self.is_running = False
        
        # 关闭socket.io
        self.socketio.stop()
        
        # 等待线程结束
        if self.server_thread and self.server_thread.is_alive():
            # 最多等待5秒
            self.server_thread.join(timeout=5)
        
        logger.info("API服务器已停止")
        
    def start_camera_debug(self, window_name="摄像头调试"):
        """
        启动摄像头调试窗口
        
        Args:
            window_name (str): 窗口名称
            
        Returns:
            bool: 是否成功启动调试窗口
        """
        if not self.camera_manager:
            logger.error("摄像头管理器未初始化")
            return False
            
        return self.camera_manager.start_debug_window(window_name=window_name)
        
    def stop_camera_debug(self):
        """停止摄像头调试窗口"""
        if not self.camera_manager:
            logger.error("摄像头管理器未初始化")
            return
            
        self.camera_manager.stop_debug_window()

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='婴儿智能监控系统')
    parser.add_argument('--debug-camera', action='store_true', 
                        help='启用摄像头调试窗口，在本地显示摄像头画面')
    parser.add_argument('--debug-window-name', type=str, default='摄像头调试',
                        help='调试窗口名称')
    parser.add_argument('--only-camera', action='store_true', 
                        help='仅测试摄像头，不启动完整系统')
    parser.add_argument('--no-arduino', action='store_true',
                        help='不使用Arduino控制器，以仅相机模式运行')
    return parser.parse_args()

def setup(args=None):
    """初始化系统组件"""
    logger.info("婴儿智能监控系统启动中...")

    config = get_config()

    arduino_controller = None
    camera_manager = None
    api_server = None

    # 初始化 Arduino 控制器（如果未指定--no-arduino）
    if not (args and args.no_arduino):
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
        camera_manager = CameraManager(
            resolution=config.get('camera', 'resolution', [640, 480]),
            framerate=config.get('camera', 'framerate', 30)
        )
        logger.info("摄像头管理器初始化成功")
    except Exception as e:
        logger.warning(f"摄像头初始化失败: {e}")

    # 初始化 API 服务器
    try:
        api_server = APIServer(
            arduino_controller=arduino_controller,  # 可能为None
            camera_manager=camera_manager,
            host=config.get('server', 'host', '0.0.0.0'),
            port=config.get('server', 'port', 5000)
        )
        logger.info("API 服务器初始化成功")
    except Exception as e:
        logger.error(f"API 服务器初始化失败: {e}")
        raise

    return arduino_controller, camera_manager, api_server 

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    try:
        # 如果仅测试摄像头
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

        # 初始化组件
        components = setup(args)  # 传递args参数
        arduino_controller, camera_manager, api_server = components
        
        # 注册信号处理
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, components))
        signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, components))
        
        # 启动API服务器
        api_server.start()
        
        # 如果启用了摄像头调试，打开调试窗口
        if args.debug_camera and camera_manager:
            logger.info(f"启用摄像头调试窗口: {args.debug_window_name}")
            camera_manager.start_debug_window(args.debug_window_name)
            print(f"摄像头调试窗口已启动: {args.debug_window_name}")
            print("按ESC键可关闭调试窗口")
        
        # 保持主线程运行
        print("系统已启动" + ("（仅相机模式）" if args.no_arduino else ""))
        print("按Ctrl+C退出")
        while True:
            signal.pause()
            
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        if 'components' in locals():
            cleanup(*components)
        sys.exit(1) 