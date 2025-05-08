#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WebSocket事件处理包初始化文件

导出所有WebSocket事件处理函数
"""

# 导出WebSocket事件注册函数
from .bed import register_bed_socketio_events
from .heart_rate import register_heart_rate_socketio_events
from .video import register_video_socketio_events

__all__ = [
    'register_bed_socketio_events',
    'register_heart_rate_socketio_events',
    'register_video_socketio_events'
] 