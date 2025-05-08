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
            arduino_controller: Arduino控制器实例
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