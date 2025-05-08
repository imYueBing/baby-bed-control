#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API服务模块初始化文件

提供所有API接口和WebSocket事件处理
"""

from flask import Flask
from flask_socketio import SocketIO

# 导出API服务器类
from .server import APIServer

# 导出API蓝图初始化函数
from .endpoints.bed import bed_api, init_bed_api
from .endpoints.heart_rate import heart_rate_api, init_heart_rate_api
from .endpoints.video import video_api, init_video_api
from .endpoints.system import system_api, init_system_api

# 导出WebSocket事件注册函数
from .websocket.bed import register_bed_socketio_events
from .websocket.heart_rate import register_heart_rate_socketio_events
from .websocket.video import register_video_socketio_events

__all__ = [
    'APIServer',
    'bed_api', 'init_bed_api',
    'heart_rate_api', 'init_heart_rate_api', 
    'video_api', 'init_video_api',
    'system_api', 'init_system_api',
    'register_bed_socketio_events',
    'register_heart_rate_socketio_events',
    'register_video_socketio_events'
] 