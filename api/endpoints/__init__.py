#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API端点包初始化文件

导出所有API端点蓝图
"""

# 导出端点蓝图
from .bed import bed_api, init_bed_api
from .heart_rate import heart_rate_api, init_heart_rate_api
from .video import video_api, init_video_api
from .system import system_api, init_system_api

__all__ = [
    'bed_api', 'init_bed_api',
    'heart_rate_api', 'init_heart_rate_api',
    'video_api', 'init_video_api',
    'system_api', 'init_system_api'
] 